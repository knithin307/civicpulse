import os
from app import create_app
from app.extensions import db

env = os.environ.get('FLASK_ENV', 'development')
app = create_app(env)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    print("=" * 60)
    print(" CivicPulse — Smart City Issue Reporting & Resolution Platform")
    print(" Aligned with UN Sustainable Development Goal 11")
    print(" Access URL: http://127.0.0.1:5000")
    print("=" * 60)
    app.run(host='127.0.0.1', port=5000, debug=True)
