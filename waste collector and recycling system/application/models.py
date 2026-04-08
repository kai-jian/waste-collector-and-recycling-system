from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from application import db, login_manager

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(100), nullable=False, default='default.jpg')
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='resident')
    points = db.Column(db.Integer, default=0)
    address = db.Column(db.Text, nullable=True)  # Delivery address for rewards
    
    # --- PROXIMITY COORDINATES ---
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)

    # Relationships
    point_requests = db.relationship('PointRequest', backref='resident', lazy=True)
    redemptions = db.relationship('Redemption', backref='resident', lazy=True)
    
    # This relationship tracks complaints created BY this user (as a resident)
    my_reports = db.relationship(
        'Complaint', 
        foreign_keys='Complaint.user_id', 
        backref='author', 
        lazy=True
    )

    # This relationship tracks complaints assigned TO this user (as a collector)
    assigned_tasks = db.relationship(
        'Complaint', 
        foreign_keys='Complaint.collector_id', 
        backref='collector', 
        lazy=True
    )

    def get_tier_data(self):
        """Returns name, color class, and icon based on current points"""
        if self.points >= 5000:
            return {'name': 'Platinum', 'color': 'text-info', 'icon': 'bi-gem'}
        elif self.points >= 1500:
            return {'name': 'Gold', 'color': 'text-warning', 'icon': 'bi-award'}
        elif self.points >= 500:
            return {'name': 'Silver', 'color': 'text-secondary', 'icon': 'bi-shield-shaded'}
        else:
            return {'name': 'Bronze', 'color': 'text-success', 'icon': 'bi-star'}

    def set_password(self, password):
        from application import bcrypt 
        hashed = bcrypt.generate_password_hash(password)
        self.password_hash = hashed.decode('utf-8') if isinstance(hashed, bytes) else hashed

    def check_password(self, password):
        from application import bcrypt
        return bcrypt.check_password_hash(self.password_hash, password)
    

class Complaint(db.Model):
    __tablename__ = 'complaints'
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    photo = db.Column(db.String(100), nullable=True)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='Pending')
    weight = db.Column(db.Float, nullable=True)  # The amount collected in kg
    hub_name = db.Column(db.String(100), nullable=True)  # The hub it was delivered to
    
    # Foreign Keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    collector_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)


class News(db.Model):
    __tablename__ = 'news' 
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(20), default='General')
    
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    author = db.relationship('User', backref='news_posts', lazy=True)


class Feedback(db.Model):
    __tablename__ = 'feedbacks'
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Link to the user who sent it
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationship to get user details easily
    author = db.relationship('User', backref='user_feedback', lazy=True)

    def __repr__(self):
        return f"Feedback('{self.subject}', '{self.date_posted}')"


class PointRequest(db.Model):
    __tablename__ = 'point_requests'
    id = db.Column(db.Integer, primary_key=True)
    weight = db.Column(db.Float, nullable=False)
    waste_type = db.Column(db.String(20), nullable=False)
    points_earned = db.Column(db.Integer, nullable=False)
    image_file = db.Column(db.String(100), nullable=False)
    date_submitted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    status = db.Column(db.String(20), nullable=False, default='Pending')
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)


class Redemption(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reward_name = db.Column(db.String(100), nullable=False)
    points_spent = db.Column(db.Integer, nullable=False)
    date_redeemed = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    delivery_address = db.Column(db.Text, nullable=True)  # Address where item was sent
    received = db.Column(db.Boolean, default=False)  # Has user confirmed receipt
    date_received = db.Column(db.DateTime, nullable=True)  # When user confirmed receipt
    
    # Tracking if the prize has been claimed/shipped
    status = db.Column(db.String(20), nullable=False, default='Processing')
    
    # Link to the user
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def __repr__(self):
        return f"Redemption('{self.reward_name}', '{self.points_spent}pts')"
    

class SystemSetting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), unique=True, nullable=False)  
    value = db.Column(db.String(255), nullable=False)            

    @staticmethod
    def get_val(key, default=None):
        setting = SystemSetting.query.filter_by(key=key).first()
        return setting.value if setting else default
    

class FAQ(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(255), nullable=False)
    answer = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"FAQ('{self.question}')"
    

class ChatChannel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False) 
    description = db.Column(db.String(255))         
    is_active = db.Column(db.Boolean, default=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship to messages
    messages = db.relationship('Message', backref='channel', lazy=True, cascade='all, delete-orphan')


class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    is_admin = db.Column(db.Boolean, default=False)  # True if sender is admin/support staff
    is_read_by_admin = db.Column(db.Boolean, default=False)  # True if admin has viewed this message
    
    # Foreign Keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    channel_id = db.Column(db.Integer, db.ForeignKey('chat_channel.id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # Who the message is for (for admin messages)
    
    # Relationships
    sender = db.relationship('User', backref='chat_messages', lazy=True, foreign_keys=[user_id])
    recipient = db.relationship('User', backref='received_chat_messages', lazy=True, foreign_keys=[recipient_id])
    
    def __repr__(self):
        return f"Message('{self.sender.username}', '{self.date_posted}')"


class Mail(db.Model):
    __tablename__ = 'mail'
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(150), nullable=False)
    content = db.Column(db.Text, nullable=False)
    mail_type = db.Column(db.String(50), nullable=False)  
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)
    
    # Link to the recipient user
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    recipient = db.relationship('User', backref='mailbox', lazy=True)
    
    # Optional link to related records 
    related_id = db.Column(db.Integer, nullable=True)
    
    # Optional channel_id for chat replies
    channel_id = db.Column(db.Integer, db.ForeignKey('chat_channel.id'), nullable=True)
    channel = db.relationship('ChatChannel', backref='mail_notifications', lazy=True)
    
    def __repr__(self):
        return f"Mail('{self.subject}', '{self.mail_type}')"