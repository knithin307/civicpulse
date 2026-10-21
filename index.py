import os
from app import create_app
from app.extensions import db

env = os.environ.get('FLASK_ENV', 'production')
app = create_app(env)

# Ensure database tables exist on cold start
with app.app_context():
    try:
        db.create_all()
    except Exception as e:
        print(f"Database initialization notice: {e}")

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
