from application import create_app, db, socketio
import os

app = create_app()

if __name__ == "__main__":
    # This block checks if the database exists; if not, it creates it
    with app.app_context():
        # This checks the URI path from your config to see if the file exists
        db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
        if not os.path.exists(db_path):
            db.create_all()
            print("Database created successfully!")
        else:
            print("Database already exists.")
            
    socketio.run(app, debug=True, host='127.0.0.1', port=5000)