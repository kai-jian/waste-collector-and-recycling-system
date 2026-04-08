import os
import secrets
import math
from datetime import datetime, timezone
from flask import render_template, url_for, flash, redirect, request, Blueprint, current_app, abort, session
from flask_babel import gettext as _
from application import db, bcrypt, socketio
from application.form import (RegistrationForm, LoginForm, 
                               ComplaintForm, FeedbackForm, RequestPointsForm, UpdateAccountForm, NewsForm, FAQForm, ChatChannelForm)
from application.models import ChatChannel, SystemSetting, User, Complaint, News, Feedback, PointRequest, FAQ, Message, Mail
from flask_login import login_user, current_user, logout_user, login_required
from flask_socketio import join_room, leave_room, emit
from sqlalchemy import func, or_

main = Blueprint('main', __name__)

def save_proof(form_picture, folder):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static', folder, picture_fn)
    form_picture.save(picture_path)
    return picture_fn


def calculate_distance(lat1, lon1, lat2, lon2):
    # Radius of the Earth in kilometers
    R = 6371.0
    
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c # Distance in KM


def get_nearby_collectors(complaint_lat, complaint_lon):
    # 1. Get all users who are waste collectors
    all_collectors = User.query.filter_by(role='collector').all()
    collector_data = []

    for collector in all_collectors:
        # Skip if collector hasn't shared their location yet
        if collector.latitude is None or collector.longitude is None:
            continue

        # 2. Haversine Formula Logic
        R = 6371  # Earth's radius in kilometers
        phi1, phi2 = math.radians(complaint_lat), math.radians(collector.latitude)
        dphi = math.radians(collector.latitude - complaint_lat)
        dlambda = math.radians(collector.longitude - complaint_lon)

        a = math.sin(dphi / 2)**2 + \
            math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2)**2
        
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance = round(R * c, 2)  # Distance in km

        # 3. Store the user object and the calculated distance
        collector_data.append({
            'obj': collector,
            'distance': distance
        })

    # 4. Sort by distance (closest first)
    return sorted(collector_data, key=lambda x: x['distance'])


@main.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        # Save photo or use default
        pic_file = save_proof(form.picture.data, 'profile_pics') if form.picture.data else 'default.jpg'
        hashed_pw = bcrypt.generate_password_hash(form.password.data)
        if isinstance(hashed_pw, bytes):
            hashed_pw = hashed_pw.decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, 
                    password_hash=hashed_pw, role=form.role.data, image_file=pic_file)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created!', 'success')
        return redirect(url_for('main.login'))
    return render_template('sign_up.html', form=form)

@main.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
        
    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        # Verify user exists and password is correct
        if user and bcrypt.check_password_hash(user.password_hash, form.password.data):
            # We removed remember=form.remember.data from here
            login_user(user) 
            
            # Handle redirection if they were trying to access a protected page
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
            
    return render_template('login.html', title='Login', form=form)

@main.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('main.home'))

# --- Main Application Routes ---

@main.route("/")
@main.route("/home")
@login_required
def home():
    # --- 1. RESIDENT DASHBOARD ---
    if current_user.role == 'resident':
        # Summary counts for cards
        pending = Complaint.query.filter_by(user_id=current_user.id, status='Pending').count()
        in_action = Complaint.query.filter_by(user_id=current_user.id, status='In Action').count()
        completed = Complaint.query.filter_by(user_id=current_user.id, status='Completed').count()
        
        # Lists for dashboard feed
        my_complaints = Complaint.query.filter_by(user_id=current_user.id).order_by(Complaint.date_posted.desc()).limit(5).all()
        community_complaints = Complaint.query.order_by(Complaint.date_posted.desc()).limit(4).all()
        news = News.query.order_by(News.date_posted.desc()).limit(3).all()

        return render_template('resident/home_resident.html', 
                               my_complaints=my_complaints, 
                               community_complaints=community_complaints,
                               pending=pending, 
                               in_action=in_action, 
                               completed=completed, 
                               news=news)

    # --- 2. ADMIN DASHBOARD ---
    elif current_user.role == 'admin':
        # Stats for Admin header cards
        total_users = User.query.filter_by(role='resident').count()
        pending_complaints = Complaint.query.filter_by(status='Pending').count()
        # Count unread messages from residents (not admin messages)
        unresponded_messages = Message.query.filter_by(is_admin=False, is_read_by_admin=False).count()
        total_completed = Complaint.query.filter_by(status='Completed').count()

        # Recent reports (Showing 'Pending' first is more helpful for Admins)
        recent_complaints = Complaint.query.order_by(Complaint.status == 'Pending').order_by(Complaint.date_posted.desc()).limit(5).all()

        return render_template('admin/home_admin.html', 
                               total_users=total_users,
                               pending_complaints=pending_complaints,
                               unresponded_messages=unresponded_messages,
                               total_completed=total_completed,
                               recent_complaints=recent_complaints)

    # --- 3. COLLECTOR DASHBOARD ---
    elif current_user.role == 'collector':
        
        assigned_tasks = Complaint.query.filter_by(collector_id=current_user.id, status='In Action').all()
        
       
        return render_template('waste_collector/home_collector.html', tasks=assigned_tasks)
            
   
    return render_template('home_guest.html')

# --- News Routes ---

@main.route("/news")
def news():
    news_list = News.query.order_by(News.date_posted.desc()).all()
    return render_template('resident/news.html', news_list=news_list)

@main.route("/news/<int:news_id>")
def news_detail(news_id):
    post = News.query.get_or_404(news_id)
    return render_template('resident/news_detail.html', post=post)

# --- Complaint Routes ---

@main.route("/complaint_hub")
@login_required
def complaint_hub():
    return render_template('resident/complaint.html')

@main.route("/make_complaint", methods=['GET', 'POST'])
@login_required
def make_complaint():
    form = ComplaintForm()
    if form.validate_on_submit():
        pic_file = save_proof(form.photo.data, 'complaint_pics')
        complaint = Complaint(type=form.type.data, content=form.content.data, photo=pic_file,
                            latitude=form.latitude.data, longitude=form.longitude.data, author=current_user)
        db.session.add(complaint)
        db.session.commit()
        flash('Complaint submitted successfully!', 'success')
        return redirect(url_for('main.home'))
    return render_template('resident/make_complaint.html', form=form)

@main.route("/view_status")
@login_required
def view_status():
    complaints = Complaint.query.filter_by(author=current_user).order_by(Complaint.date_posted.desc()).all()
    return render_template('resident/view_status.html', complaints=complaints)

# --- Feedback Route ---

@main.route("/feedback", methods=['GET', 'POST'])
@login_required
def feedback():
    form = FeedbackForm()
    if form.validate_on_submit():
        fb = Feedback(
            category=form.category.data,
            subject=form.subject.data,
            message=form.message.data,
            author=current_user
        )
        db.session.add(fb)
        db.session.commit()
        flash('Thank you for your feedback!', 'success')
        return redirect(url_for('main.home'))
    return render_template('resident/feedback.html', form=form)


@main.route("/terminology")
@login_required
def terminology():
    return render_template('resident/terminology.html')


@main.route("/rewards")
@login_required
def rewards():
    from application.models import PointRequest, Redemption
    
    # 1. Fetch current requests
    requests = PointRequest.query.filter_by(user_id=current_user.id)\
                                 .order_by(PointRequest.date_submitted.desc()).all()
    
    # 2. Fetch all redemptions for this user
    redemptions = Redemption.query.filter_by(user_id=current_user.id)\
                                  .order_by(Redemption.date_redeemed.desc()).all()
    
    # 3. Create a unified history combining both additions and deductions
    history = []
    
    # Add point requests (additions)
    for req in requests:
        if req.status == 'Approved':
            history.append({
                'type': 'addition',
                'date': req.date_submitted,
                'description': f'{req.weight}kg {req.waste_type.capitalize()}',
                'points': req.points_earned,
                'status': req.status
            })
    
    # Add redemptions (deductions)
    for redemption in redemptions:
        history.append({
            'type': 'deduction',
            'date': redemption.date_redeemed,
            'description': redemption.reward_name,
            'points': redemption.points_spent,
            'status': redemption.status
        })
    
    # Sort by date (most recent first)
    history.sort(key=lambda x: x['date'], reverse=True)
    
    # 4. Calculate sum of points for requests that are STILL pending
    pending_total = sum(r.points_earned for r in requests if r.status == 'Pending')
    
    return render_template('resident/rewards.html', 
                           recent_requests=requests, 
                           pending_total=pending_total,
                           point_history=history,
                           redemptions=redemptions)


@main.route("/rewards/request", methods=['GET', 'POST'])
@login_required
def request_points():
    form = RequestPointsForm()
    if form.validate_on_submit():
        if form.photo.data:
            pic_file = save_proof(form.photo.data, 'point_request_pics')
        else:
            pic_file = 'default.jpg'

        waste_type = form.material_type.data
        weight = float(form.quantity.data)
        multiplier = 10 if waste_type == 'recyclable' else 2
        earned_points = int(weight * multiplier)

        # Create the entry with status 'Pending'
        # Points are NOT added to current_user yet
        new_entry = PointRequest(
            weight=weight,
            waste_type=waste_type,
            points_earned=earned_points,
            image_file=pic_file,
            user_id=current_user.id,
            status='Pending' # Explicitly set to Pending
        )

        db.session.add(new_entry)
        db.session.commit()

        flash(f'Request submitted! Points will be added once an admin verifies your photo.', 'info')
        return redirect(url_for('main.rewards'))

    return render_template('resident/request_points.html', title='Request Points', form=form)


# 1. The Store Page (Keep this as redeem_points)
@main.route("/rewards/redeem")
@login_required
def redeem_points():
    prizes = [
        {"id": 1, "name": "Eco Tote Bag", "cost": 100, "icon": "bi-bag-heart", "color": "text-success"},
        {"id": 2, "name": "RM10 Cash Voucher", "cost": 250, "icon": "bi-ticket-perforated", "color": "text-primary"},
        {"id": 3, "name": "Recycling Bin Kit", "cost": 500, "icon": "bi-trash3", "color": "text-warning"}
    ]
    has_address = current_user.address and current_user.address.strip() != ''
    return render_template('resident/redeem_points.html', title='Redeem Points', prizes=prizes, has_address=has_address)


# 2. The Logic to Confirm Redemption
@main.route("/rewards/redeem/<int:prize_id>", methods=['POST'])
@login_required
def confirm_redemption(prize_id): 
    prizes = {
        1: {"name": "Eco Tote Bag", "cost": 100},
        2: {"name": "RM10 Cash Voucher", "cost": 250},
        3: {"name": "Recycling Bin Kit", "cost": 500}
    }
    
    selected_prize = prizes.get(prize_id)

    if selected_prize and current_user.points >= selected_prize['cost']:
        current_user.points -= selected_prize['cost']
        
        from application.models import Redemption, Mail
        new_redemption = Redemption(
            reward_name=selected_prize['name'],
            points_spent=selected_prize['cost'],
            delivery_address=current_user.address,  # Store the user's delivery address
            user_id=current_user.id,
            status='Processing'
        )
        
        db.session.add(new_redemption)
        db.session.commit()
        
        # Create a mail notification for the redemption
        redemption_mail = Mail(
            subject=f'Your {selected_prize["name"]} is on the way!',
            content=f'Thank you for redeeming {selected_prize["name"]}! Your item will be delivered to your address in approximately 7 days. Your delivery address: {current_user.address}',
            mail_type='redemption',
            user_id=current_user.id,
            related_id=new_redemption.id
        )
        db.session.add(redemption_mail)
        db.session.commit()
        
        flash(f'Success! {selected_prize["name"]} has been redeemed and will be sent to your address.', 'success')
        return redirect(url_for('main.rewards')) 
    
    else:
        flash('Insufficient points or invalid selection.', 'danger')
        return redirect(url_for('main.redeem_points'))


@main.route("/rewards/confirm-receipt/<int:redemption_id>", methods=['POST'])
@login_required
def confirm_receipt(redemption_id):
    from application.models import Redemption
    from datetime import datetime
    
    redemption = Redemption.query.get_or_404(redemption_id)
    
    # Verify that the current user owns this redemption
    if redemption.user_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('main.rewards'))
    
    # Mark as received
    redemption.received = True
    redemption.date_received = datetime.utcnow()
    db.session.commit()
    
    flash(f'Thank you! You confirmed receipt of {redemption.reward_name}.', 'success')
    return redirect(url_for('main.rewards'))


@main.route("/profile")
@login_required
def profile():
    
    return render_template('resident/profile_resident.html', title='My Profile')



@main.route("/profile/edit", methods=['GET', 'POST'])
@login_required
def edit_profile():
    # Initialize the form object
    form = UpdateAccountForm()

    if form.validate_on_submit():
        # Update user with data from the form object
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.address = form.address.data
        
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        
        # Logic to send user back to their specific profile page
        if current_user.role == 'admin':
            return redirect(url_for('main.profile_admin'))
        elif current_user.role == 'collector':
            return redirect(url_for('main.collector_profile')) 
        else:
            return redirect(url_for('main.profile'))

    # Pre-fill the fields with current data
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.address.data = current_user.address

    # Determine back link for the "Cancel" button in the UI
    if current_user.role == 'admin':
        back_url = url_for('main.profile_admin')
    elif current_user.role == 'collector':
        back_url = url_for('main.collector_profile')
    else:
        back_url = url_for('main.profile')
    
    return render_template('resident/edit_profile.html', back_url=back_url, form=form)

@main.route("/mailbox")
@login_required
def mailbox():
    # Fetch all mail for current user, ordered by date (newest first)
    mail = Mail.query.filter_by(user_id=current_user.id).order_by(Mail.date_created.desc()).all()
    
    # Count unread mail
    unread_count = Mail.query.filter_by(user_id=current_user.id, is_read=False).count()
    
    # For admin chat replies, get sender info so we can link to admin_chat_room with resident_id
    mail_data = []
    for item in mail:
        mail_info = {
            'mail': item,
            'sender_id': None
        }
        # If this is a chat reply for an admin, find the sender
        if current_user.role == 'admin' and item.mail_type == 'chat_reply' and item.related_id:
            message = Message.query.get(item.related_id)
            if message:
                mail_info['sender_id'] = message.user_id
        mail_data.append(mail_info)
    
    return render_template('resident/mailbox.html', mail=mail_data, unread_count=unread_count, is_admin=(current_user.role == 'admin'))


@main.route("/mail/<int:mail_id>/read", methods=['POST'])
@login_required
def mark_mail_read(mail_id):
    mail = Mail.query.get_or_404(mail_id)
    
    # Verify ownership
    if mail.user_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('main.mailbox'))
    
    mail.is_read = True
    db.session.commit()
    
    return redirect(url_for('main.mailbox'))


@main.route("/mail/<int:mail_id>/delete", methods=['POST'])
@login_required
def delete_mail(mail_id):
    mail = Mail.query.get_or_404(mail_id)
    
    # Verify ownership
    if mail.user_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('main.mailbox'))
    
    # If this is a chat reply, delete all related chat notifications for this conversation
    if mail.mail_type == 'chat_reply' and mail.channel_id:
        Mail.query.filter_by(
            user_id=current_user.id,
            mail_type='chat_reply',
            channel_id=mail.channel_id
        ).delete()
    else:
        db.session.delete(mail)
    
    db.session.commit()
    flash(_('Mail deleted.'), 'success')
    
    # Redirect to next URL if provided, otherwise go to mailbox
    next_url = request.args.get('next')
    if next_url:
        return redirect(next_url)
    return redirect(url_for('main.mailbox'))

@main.route("/change-language")
def change_language():
    return render_template('change_language.html', title='Language Settings')


@main.route("/set-language/<language>")
def set_language(language):
    """Set the user's language preference"""
    from flask import session
    valid_languages = ['en', 'ms', 'zh']
    if language in valid_languages:
        session['language'] = language
        session.permanent = True
        lang_names = {'en': 'English', 'ms': 'Bahasa Melayu', 'zh': '中文'}
        flash(_('Language changed to') + ' ' + lang_names.get(language, language), 'success')
    return redirect(request.referrer or url_for('main.home'))


@main.route("/helpline")
@login_required
def helpline():
    # Fetch from DB, use "Not Set" as a fallback if the DB is empty
    hotline = SystemSetting.get_val('hotline', 'Not Set')
    email = SystemSetting.get_val('email', 'support@ecoapp.com')
    
    return render_template('resident/helpline.html', 
                           hotline=hotline, 
                           support_email=email, 
                           title='Helpline')

@main.route("/helpline/faq")
@login_required
def faq():
    faqs = FAQ.query.order_by(FAQ.date_posted.desc()).all()
    return render_template('resident/faq.html', faqs=faqs)


@main.route("/helpline/faq/<int:faq_id>")
@login_required
def faq_detail(faq_id):
    # Fetch the specific FAQ or return a 404 error if not found
    faq = FAQ.query.get_or_404(faq_id)
    return render_template('resident/faq_detail.html', faq=faq, title=faq.question)


@main.route("/helpline/live-chat")
@login_required
def live_chat():
    channels = ChatChannel.query.filter_by(is_active=True).all()
    return render_template('resident/live_chat.html', channels=channels, title='Live Chat Hub')



@main.route("/helpline/live-chat/<int:channel_id>", methods=['GET', 'POST'])
@login_required
def chat_room(channel_id):
    channel = ChatChannel.query.get_or_404(channel_id)
    
    if request.method == 'POST':
        content = request.form.get('message', '').strip()
        if content:
            message = Message(
                content=content,
                user_id=current_user.id,
                channel_id=channel_id,
                is_admin=current_user.role == 'admin'
            )
            db.session.add(message)
            db.session.commit()
            
            # If resident sends a message, notify all admins
            if current_user.role != 'admin':
                admins = User.query.filter_by(role='admin').all()
                for admin in admins:
                    mail = Mail(
                        subject=f'New message from {current_user.username} in {channel.name}',
                        content=content,
                        mail_type='chat_reply',
                        user_id=admin.id,
                        related_id=message.id,
                        channel_id=channel_id
                    )
                    db.session.add(mail)
                if admins:  # Only commit if there are admins
                    db.session.commit()
            
            flash('Message sent!', 'success')
            return redirect(url_for('main.chat_room', channel_id=channel_id))
    
    # Fetch messages for this channel filtered by current user (privacy)
    # Residents only see their own messages and admin replies TO THEM
    # This prevents residents from seeing other residents' conversations
    if current_user.role == 'admin':
        # Admins see all messages in the channel
        messages = Message.query.filter_by(channel_id=channel_id).order_by(Message.date_posted.asc()).all()
    else:
        # Residents see their own messages AND admin messages directed to them
        messages = Message.query.filter(
            Message.channel_id == channel_id,
            or_(
                Message.user_id == current_user.id,
                (Message.is_admin == True) & (Message.recipient_id == current_user.id)
            )
        ).order_by(Message.date_posted.asc()).all()
    
    return render_template('resident/chat_room.html', channel=channel, messages=messages, title=channel.name)


@main.route("/admin/dashboard")
@login_required
def home_admin():
    if current_user.role != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('main.home'))

    # Gathering Stats
    total_users = User.query.filter_by(role='resident').count()
    pending_complaints = Complaint.query.filter_by(status='Pending').count()
    pending_points = PointRequest.query.filter_by(status='Pending').count()
    total_completed = Complaint.query.filter_by(status='Completed').count()
    
    # Getting the 5 most recent complaints to show in the table
    recent_complaints = Complaint.query.order_by(Complaint.date_posted.desc()).limit(5).all()

    return render_template('admin/home_admin.html', 
                           total_users=total_users,
                           pending_complaints=pending_complaints,
                           pending_points=pending_points,
                           total_completed=total_completed,
                           recent_complaints=recent_complaints)


@main.route("/admin/manage_complaints/<int:complaint_id>", methods=['GET', 'POST'])
@login_required
def manage_complaints(complaint_id):
    if current_user.role != 'admin':
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('main.home'))
    
    # 1. Fetch the specific complaint by the ID passed in the URL
    complaint = Complaint.query.get_or_404(complaint_id)
    
    # 2. Handle the "Confirm Assignment" POST request
    if request.method == 'POST':
        selected_collector_id = request.form.get('collector_id')
        
        if selected_collector_id:
            # Update the Model columns
            complaint.collector_id = int(selected_collector_id)
            complaint.status = 'In Action' # Auto-update status
            
            db.session.commit()
            flash(f'Task assigned to collector successfully!', 'success')
            
            # Redirect back to the Hub or the list view after success
            return redirect(url_for('main.assign_hub'))
        else:
            flash('Please select a collector before confirming.', 'warning')

    # 3. Fetch collectors (use your existing proximity/distance logic here)
    # This is passed to the template for the dropdown menu
    collectors = get_nearby_collectors(complaint.latitude, complaint.longitude)
        
    return render_template('admin/manage_complaints.html', 
                           complaint=complaint, 
                           collectors=collectors)




@main.route("/admin/complaint/<int:id>")
@login_required
def complaint_detail(id):
    if current_user.role != 'admin':
        return redirect(url_for('main.home'))
    
    complaint = Complaint.query.get_or_404(id)
    return render_template('admin/complaint_detail.html', complaint=complaint)


@main.route("/collector/verify_points")
@login_required
def collector_verify_points():
    if current_user.role != 'collector':
        flash('Access denied. Only collectors can verify points.', 'danger')
        return redirect(url_for('main.home'))
    
    # Fetch all point requests that are still 'Pending'
    requests = PointRequest.query.filter_by(status='Pending').order_by(PointRequest.date_submitted.desc()).all()
    return render_template('waste_collector/verify_points.html', requests=requests)

@main.route("/collector/verify_points/<int:request_id>/<string:action>", methods=['POST'])
@login_required
def collector_update_point_status(request_id, action):
    if current_user.role != 'collector':
        return redirect(url_for('main.home'))
    
    point_request = PointRequest.query.get_or_404(request_id)
    resident = User.query.get(point_request.user_id)
    
    if action == 'approve':
        point_request.status = 'Approved'
        resident.points += point_request.points_earned  # Award the points to the user
        flash(f'Request approved! {point_request.points_earned} points added to {resident.username}.', 'success')
    elif action == 'reject':
        point_request.status = 'Rejected'
        flash('Request has been rejected.', 'info')
    
    db.session.commit()
    return redirect(url_for('main.collector_verify_points'))


@main.route("/admin/manage_users")
@login_required
def manage_users():
    if current_user.role != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('main.home'))
    
    # Fetch all residents 
    users = User.query.filter_by(role='resident').order_by(User.username).all()
    return render_template('admin/manage_users.html', users=users)


@main.route("/admin/manage_news", methods=['GET', 'POST'])
@login_required
def manage_news():
    if current_user.role != 'admin':
        return redirect(url_for('main.home'))
    
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        category = request.form.get('category')
        
        new_post = News(title=title, content=content, category=category)
        db.session.add(new_post)
        db.session.commit()
        flash('News article published!', 'success')
        return redirect(url_for('main.manage_news'))
        
    all_news = News.query.order_by(News.date_posted.desc()).all()
    return render_template('admin/manage_news.html', news=all_news)

@main.route("/admin/manage_news/add", methods=['GET', 'POST'])
@main.route("/admin/manage_news/edit/<int:id>", methods=['GET', 'POST'])
@login_required
def news_action(id=None):
    if current_user.role != 'admin':
        return redirect(url_for('main.home'))

    post = News.query.get(id) if id else None
    form = NewsForm(obj=post)
    
    if form.validate_on_submit():
        if post: # Update existing record
            post.title = form.title.data
            post.category = form.category.data
            post.content = form.content.data
            flash('Announcement updated!', 'success')
        else: # Create new record
            new_news = News(
                title=form.title.data,
                content=form.content.data,
                category=form.category.data,
                user_id=current_user.id 
            )
            db.session.add(new_news)
            flash('News published!', 'success')
        
        db.session.commit()
        return redirect(url_for('main.manage_news'))

    return render_template('admin/edit_news.html', form=form, post=post)


@main.route("/admin/manage_news/delete/<int:id>")
@login_required
def delete_news(id):
    if current_user.role == 'admin':
        post = News.query.get_or_404(id)
        db.session.delete(post)
        db.session.commit()
        flash('Article deleted successfully.', 'info')
    return redirect(url_for('main.manage_news'))


@main.route("/admin/manage_feedback")
@login_required
def manage_feedback():
    if current_user.role != 'admin':
        return redirect(url_for('main.home'))
    
    # Fetching all feedback, most recent first
    feedbacks = Feedback.query.order_by(Feedback.date_posted.desc()).all()
    return render_template('admin/manage_feedback.html', feedbacks=feedbacks)

@main.route("/admin/feedback/<int:id>")
@login_required
def feedback_detail(id):
    if current_user.role != 'admin':
        return redirect(url_for('main.home'))
    
    # Using your model fields: category, subject, message, author
    item = Feedback.query.get_or_404(id)
    return render_template('admin/feedback_detail.html', feedback=item)


@main.route("/admin/assign_hub")
@login_required
def assign_hub():
    if current_user.role != 'admin':
        abort(403)
    
    # Show all complaints, most recent first
    complaints = Complaint.query.order_by(Complaint.date_posted.desc()).all()
    return render_template('admin/assign_hub.html', complaints=complaints)


@main.route("/admin/manage_complaint/<int:id>", methods=['GET', 'POST'])
@login_required
def manage_complaint(id):
    if current_user.role != 'admin':
        abort(403)

    complaint = Complaint.query.get_or_404(id)
    all_collectors = User.query.filter_by(role='collector').all()
    
    # Create a list of collectors with their calculated distance
    collectors_with_distance = []
    for c in all_collectors:
        # Check if collector has location data 
        if c.latitude and c.longitude:
            dist = calculate_distance(complaint.latitude, complaint.longitude, c.latitude, c.longitude)
            collectors_with_distance.append({
                'obj': c,
                'distance': round(dist, 2)
            })
        else:
            collectors_with_distance.append({'obj': c, 'distance': None})

    # Sort collectors: Nearest first
    collectors_with_distance.sort(key=lambda x: (x['distance'] is None, x['distance']))

    
    return render_template('admin/manage_complaints.html', 
                           complaint=complaint, 
                           collectors=collectors_with_distance)


@main.route("/admin/manage-helpline")
@login_required
def manage_helpline():
    if current_user.role != 'admin':
        abort(403)
    return render_template('admin/manage_helpline.html')


@main.route("/admin/edit_helpline/<string:key>", methods=['GET', 'POST'])
@login_required
def edit_helpline(key):
    if current_user.role != 'admin':
        abort(403)
    
    # 1. Try to find the existing setting
    setting = SystemSetting.query.filter_by(key=key).first()
    
    # 2. If it doesn't exist, create a new instance (but don't save yet)
    if not setting:
        setting = SystemSetting(key=key, value="Not set yet")
    
    if request.method == 'POST':
        # 3. Update the value from the form
        setting.value = request.form.get('value')
        
        # 4. If this was a new record, add it to the session
        db.session.add(setting) 
        db.session.commit()
        
        flash(f'{key.replace("_", " ").capitalize()} saved successfully!', 'success')
        return redirect(url_for('main.home')) 
    
    return render_template('admin/edit_helpline.html', setting=setting)


# 1. VIEW ALL FAQs (Management Dashboard)
@main.route("/admin/manage_faq")
@login_required
def manage_faq():
    if current_user.role != 'admin':
        abort(403)
    # Get all FAQs from the database
    faqs = FAQ.query.all()
    return render_template('admin/manage_faq.html', faqs=faqs)

# 2. ADD or EDIT FAQ (Combined Route)
@main.route("/admin/faq/new", methods=['GET', 'POST'])
@main.route("/admin/faq/edit/<int:id>", methods=['GET', 'POST'])
@login_required
def edit_faq(id=None):
    if current_user.role != 'admin':
        abort(403)
    
    faq = FAQ.query.get(id) if id else None
    
    form = FAQForm(obj=faq)
    
    if form.validate_on_submit():
        if not faq:
            faq = FAQ()
            db.session.add(faq)
        
        # Update model with form data
        faq.question = form.question.data
        faq.answer = form.answer.data
        
        db.session.commit()
        flash('FAQ saved successfully!', 'success')
        return redirect(url_for('main.manage_faq'))
    
    # Passing 'faq' here helps the template know if it's an "Edit" or "Add"
    return render_template('admin/edit_faq.html', form=form, faq=faq)

# 3. DELETE FAQ
@main.route("/admin/faq/delete/<int:id>", methods=['POST'])
@login_required
def delete_faq(id):
    if current_user.role != 'admin':
        abort(403)
    
    faq = FAQ.query.get_or_404(id)
    db.session.delete(faq)
    db.session.commit()
    flash('FAQ has been removed.', 'info')
    return redirect(url_for('main.manage_faq'))


@main.route("/admin/manage_chat")
@login_required
def manage_chat():
    if current_user.role != 'admin': abort(403)
    channels = ChatChannel.query.order_by(ChatChannel.date_created.desc()).all()
    return render_template('admin/manage_chat.html', channels=channels)

@main.route("/admin/chat/new", methods=['GET', 'POST'])
@main.route("/admin/chat/edit/<int:id>", methods=['GET', 'POST'])
@login_required
def edit_chat(id=None):
    if current_user.role != 'admin': abort(403)
    
    channel = ChatChannel.query.get(id) if id else None
    form = ChatChannelForm(obj=channel)
    
    if form.validate_on_submit():
        if not channel:
            channel = ChatChannel()
            db.session.add(channel)
        
        form.populate_obj(channel)
        db.session.commit()
        flash('Chat channel saved successfully!', 'success')
        return redirect(url_for('main.manage_chat'))
    
    return render_template('admin/edit_chat.html', form=form, channel=channel)

@main.route("/admin/chat/delete/<int:id>", methods=['POST'])
@login_required
def delete_chat(id):
    if current_user.role != 'admin': abort(403)
    channel = ChatChannel.query.get_or_404(id)
    db.session.delete(channel)
    db.session.commit()
    flash('Channel deleted.', 'info')
    return redirect(url_for('main.manage_chat'))


@main.route("/admin/live-chat/<int:channel_id>", methods=['GET', 'POST'])
@main.route("/admin/live-chat/<int:channel_id>/resident/<int:resident_id>", methods=['GET', 'POST'])
@login_required
def admin_chat_room(channel_id, resident_id=None):
    if current_user.role != 'admin': abort(403)
    channel = ChatChannel.query.get_or_404(channel_id)
    
    if request.method == 'POST':
        content = request.form.get('message', '').strip()
        if content:
            # Only allow messaging if a specific resident is selected
            if not resident_id:
                flash('Please select a resident to message.', 'warning')
            else:
                message = Message(
                    content=content,
                    user_id=current_user.id,
                    channel_id=channel_id,
                    is_admin=True,
                    recipient_id=resident_id  # Set recipient to the selected resident
                )
                db.session.add(message)
                db.session.commit()
                
                # Create a mail notification for the resident
                mail = Mail(
                    subject=f'New reply in {channel.name}',
                    content=content,
                    mail_type='chat_reply',
                    user_id=resident_id,
                    related_id=message.id,
                    channel_id=channel_id  # Store the channel_id for navigation
                )
                db.session.add(mail)
                db.session.commit()
                
                flash('Response sent!', 'success')
            return redirect(url_for('main.admin_chat_room', channel_id=channel_id, resident_id=resident_id))
    
    # Get all unique residents who messaged in this channel
    resident_messages = Message.query.filter_by(channel_id=channel_id, is_admin=False).all()
    residents = sorted(list(set([msg.sender for msg in resident_messages])), key=lambda x: x.username)
    
    # If a specific resident is selected, show only their conversation
    if resident_id:
        resident = User.query.get_or_404(resident_id)
        # Mark all unread messages from this resident as read
        Message.query.filter_by(channel_id=channel_id, user_id=resident_id, is_admin=False, is_read_by_admin=False).update({'is_read_by_admin': True})
        db.session.commit()
        
        # Show messages from this resident and admin responses directed to this resident
        messages = Message.query.filter(
            Message.channel_id == channel_id,
            ((Message.user_id == resident_id) | ((Message.is_admin == True) & (Message.recipient_id == resident_id)))
        ).order_by(Message.date_posted.asc()).all()
    else:
        # Show all messages in the channel (overview mode) - but disable messaging
        messages = Message.query.filter_by(channel_id=channel_id).order_by(Message.date_posted.asc()).all()
        resident = None
    
    # Get unread message counts per resident
    unread_counts = {}
    for res in residents:
        unread_count = Message.query.filter_by(channel_id=channel_id, user_id=res.id, is_admin=False, is_read_by_admin=False).count()
        unread_counts[res.id] = unread_count
    
    return render_template('admin/admin_chat_room.html', channel=channel, messages=messages, residents=residents, 
                         selected_resident=resident, resident_id=resident_id, unread_counts=unread_counts, title=f'Chat - {channel.name}')


@main.route("/admin/dashboard-summary")
@login_required
def dashboard_summary():
    if current_user.role != 'admin':
        abort(403)

    # 1. Total Waste Volume (Sum of weight from 'Completed' Complaints)
    total_w = db.session.query(func.sum(Complaint.weight)).filter_by(status='Completed').scalar() or 0
    
    # 2. Total Weight in Reward System (Sum of all 'Approved' PointRequests)
    # This includes both 'recyclable' and 'non-recyclable'
    total_reward_w = db.session.query(func.sum(PointRequest.weight)).filter_by(status='Approved').scalar() or 0
    
    # 3. Only Recyclable Weight 
    recycled_w = db.session.query(func.sum(PointRequest.weight))\
        .filter(PointRequest.status == 'Approved')\
        .filter(PointRequest.waste_type == 'recyclable').scalar() or 0
    
    # 4. Calculate Internal Recycling Rate
    # (Recyclable weight / Total weight in Reward system) * 100
    calc_rate = (float(recycled_w) / float(total_reward_w) * 100) if total_reward_w > 0 else 0

    # 5. Task Completion (Complaints status tracking)
    total_tasks = Complaint.query.count()
    completed_tasks = Complaint.query.filter_by(status='Completed').count()
    comp_pct = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0

    stats = {
        'total_volume': float(total_w),
        'recycling_rate': round(calc_rate, 1),
        'completion_percent': round(comp_pct, 1)
    }

    from datetime import datetime
    current_date = datetime.now().strftime('%B %Y')

    return render_template('admin/dashboard_summary.html', stats=stats, current_date=current_date)


@main.route("/admin/waste-volume")
@login_required
def waste_volume():
    if current_user.role != 'admin': 
        abort(403)
    
    # 1. Sum weight from all complaints marked as 'Completed'
    total_volume = db.session.query(func.sum(Complaint.weight)).filter(
        Complaint.status == 'Completed'
    ).scalar() or 0
    
    # 2. Fetch the logs to show in the table
    logs = Complaint.query.filter(Complaint.status == 'Completed')\
                          .order_by(Complaint.date_posted.desc()).all()
    
    # 3. Get list of unique hubs that have received waste
    hub_stats = db.session.query(Complaint.hub_name).distinct().all()

    return render_template('admin/waste_volume.html', 
                           total_volume=total_volume, 
                           logs=logs,
                           hub_stats=hub_stats)

from sqlalchemy import func

@main.route("/admin/recycling-analysis")
@login_required
def recycling_rates():
    if current_user.role != 'admin':
        abort(403)

    # 1. Calculate ONLY Recyclable Weight
    # This feeds the "Verified Recyclables" card
    total_recyclable_weight = db.session.query(func.sum(PointRequest.weight))\
        .filter(PointRequest.status == 'Approved', PointRequest.waste_type == 'recyclable').scalar() or 0
    
    # 2. Total Points 
    total_points = db.session.query(func.sum(PointRequest.points_earned)).filter_by(status='Approved').scalar() or 0
    
    # 3. Count Unique Residents (Active Recyclers)
    active_recyclers = db.session.query(PointRequest.user_id).filter_by(status='Approved').distinct().count()

    # 4. Top Sustainability Heroes (Ranking based on 'recyclable' weight)
    top_heroes = db.session.query(
        User.username, 
        func.sum(PointRequest.weight).label('total_w'),
        func.sum(PointRequest.points_earned).label('total_p')
    ).join(PointRequest).filter(PointRequest.status == 'Approved', PointRequest.waste_type == 'recyclable')\
     .group_by(User.id).order_by(func.sum(PointRequest.weight).desc()).limit(5).all()

    # 5. Recent Verified Contributions (Shows both for the table)
    recent_contributions = PointRequest.query.filter_by(status='Approved')\
        .order_by(PointRequest.date_submitted.desc()).limit(10).all()

    return render_template('admin/recycling_rates.html', 
                           weight=total_recyclable_weight,
                           points=total_points,
                           count=active_recyclers,
                           heroes=top_heroes,
                           contributions=recent_contributions)

@main.route("/admin/collection-progress")
@login_required
def collection_progress():
    if current_user.role != 'admin':
        abort(403)

    # 1. Get specific counts for the UI boxes
    completed_count = Complaint.query.filter_by(status='Completed').count()
    in_progress_count = Complaint.query.filter_by(status='In Progress').count()
    pending_count = Complaint.query.filter_by(status='Pending').count()
    
    # 2. FIX: Use the total count of the whole table to match the dashboard
    total_tasks = Complaint.query.count()
    
    # 3. Calculate percentage (using float to be safe)
    overall_value = (float(completed_count) / total_tasks * 100) if total_tasks > 0 else 0

    all_tasks = Complaint.query.order_by(Complaint.date_posted.desc()).all()

    return render_template('admin/collection_progress.html', 
                           completed=completed_count,
                           progress=in_progress_count,
                           pending=pending_count,
                           overall=round(overall_value), 
                           tasks=all_tasks)


@main.route("/admin/profile")
@login_required
def profile_admin():
    if current_user.role != 'admin':
        abort(403)
        
    # Count of all point requests approved by the system (or specific to this admin)
    completed_count = Complaint.query.filter_by(status='Completed').count()
    
    # Get the date the admin joined
    joined_date = current_user.created_at.strftime('%B %Y') if hasattr(current_user, 'created_at') else "February 2026"

    return render_template('admin/profile_admin.html', 
                           completed_count=completed_count, 
                           joined_date=joined_date)


@main.route("/collector/assignments")
@login_required
def collector_assignments():
    if current_user.role != 'collector':
        abort(403)
        
    # Get all complaints assigned to this collector
    # Filter by 'In Action' or 'Pending' if you only want active ones
    assigned_tasks = Complaint.query.filter_by(collector_id=current_user.id).order_by(Complaint.date_posted.desc()).all()
    
    return render_template('waste_collector/update_complaint_status.html', tasks=assigned_tasks)


@main.route("/complaint/detail/<int:complaint_id>", methods=['GET', 'POST'])
@login_required
def collector_complaint_detail(complaint_id):
    complaint = Complaint.query.get_or_404(complaint_id)
    
    if current_user.role != 'collector':
        abort(403)
        
    if request.method == 'POST':
        new_status = request.form.get('status')
        weight = request.form.get('weight')
        file = request.files.get('evidence_photo')
        
        # 1. Update the Basic Fields
        complaint.status = new_status
        if weight:
            complaint.weight = float(weight)
            
        # 2. Handle Image Upload if provided
        if file and file.filename != '':
            random_hex = secrets.token_hex(8)
            _, f_ext = os.path.splitext(file.filename)
            picture_fn = random_hex + f_ext
            picture_path = os.path.join(current_app.root_path, 'static/evidence_pics', picture_fn)
            file.save(picture_path)
            complaint.evidence_photo = picture_fn
            
        db.session.commit()
        flash('Task updated successfully!', 'success')
        
        # Redirect back to home if they marked it completed
        if new_status == 'Completed':
            return redirect(url_for('main.home'))
            
        return redirect(url_for('main.collector_complaint_detail', complaint_id=complaint.id))

    return render_template('waste_collector/collector_complaint_detail.html', complaint=complaint)

@main.route("/update_location", methods=['POST'])
@login_required
def update_location():
    data = request.get_json()
    if data:
        current_user.latitude = data.get('latitude')
        current_user.longitude = data.get('longitude')
        db.session.commit()
        return {"message": "Location updated"}, 200
    return {"message": "Invalid data"}, 400


@main.route("/collector/profile")
@login_required
def collector_profile():
    if current_user.role != 'collector':
        abort(403)
    
    # Get all completed tasks for this collector
    completed_tasks = Complaint.query.filter_by(
        collector_id=current_user.id, 
        status='Completed'
    ).all()
    
    total_tasks = len(completed_tasks)
    # Summing up the weight from completed complaints
    total_weight = sum(task.weight for task in completed_tasks if task.weight)

    return render_template('waste_collector/profile_waste_collector.html', 
                           total_tasks=total_tasks, 
                           total_weight=total_weight)


# ===== WEBSOCKET HANDLERS FOR LIVE CHAT =====

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    pass

@socketio.on('join_chat')
def on_join_chat(data):
    """Handle joining a chat room"""
    channel_id = data.get('channel_id')
    room = f'chat_{channel_id}'
    join_room(room)
    
    # Emit a notification that user joined
    emit('user_joined', {
        'username': current_user.username,
        'user_id': current_user.id,
        'role': current_user.role
    }, room=room)

@socketio.on('send_message')
def on_send_message(data):
    """Handle incoming messages"""
    content = data.get('content', '').strip()
    channel_id = data.get('channel_id')
    recipient_id = data.get('recipient_id')
    
    if not content or not channel_id:
        return
    
    # Save message to database
    is_admin = current_user.role == 'admin'
    message = Message(
        content=content,
        user_id=current_user.id,
        channel_id=channel_id,
        is_admin=is_admin,
        is_read_by_admin=is_admin,  # Admin messages are automatically marked as read
        recipient_id=recipient_id
    )
    db.session.add(message)
    db.session.commit()
    
    room = f'chat_{channel_id}'
    
    # Convert UTC datetime to Unix timestamp in milliseconds for JavaScript
    # The datetime is stored as UTC, so we need to mark it as such before converting
    dt_utc = message.date_posted.replace(tzinfo=timezone.utc)
    timestamp_ms = int(dt_utc.timestamp() * 1000)
    
    # Broadcast message to all users in the room
    emit('new_message', {
        'id': message.id,
        'sender_username': current_user.username,
        'sender_id': current_user.id,
        'is_admin': current_user.role == 'admin',
        'content': content,
        'timestamp': timestamp_ms,
        'recipient_id': recipient_id
    }, room=room)
    
    # If resident sends a message, notify all admins
    if current_user.role != 'admin':
        admins = User.query.filter_by(role='admin').all()
        for admin in admins:
            mail = Mail(
                subject=f'New message from {current_user.username} in Chat',
                content=content,
                mail_type='chat_reply',
                user_id=admin.id,
                related_id=message.id,
                channel_id=channel_id
            )
            db.session.add(mail)
        db.session.commit()
    
    # If admin sends a replied message, create mail notification
    if current_user.role == 'admin' and recipient_id:
        mail = Mail(
            subject=f'Reply from admin in Chat',
            content=content,
            mail_type='chat_reply',
            user_id=recipient_id,
            related_id=message.id,
            channel_id=channel_id
        )
        db.session.add(mail)
        db.session.commit()

@socketio.on('leave_chat')
def on_leave_chat(data):
    """Handle leaving a chat room"""
    channel_id = data.get('channel_id')
    room = f'chat_{channel_id}'
    leave_room(room)
    
    emit('user_left', {
        'username': current_user.username,
        'user_id': current_user.id
    }, room=room)

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnect"""
    pass