import os
from app import create_app
from app.extensions import db

env = os.environ.get('FLASK_ENV', 'production' if (os.environ.get('VERCEL') or os.environ.get('VERCEL_ENV')) else 'development')
app = create_app(env)

# Ensure database tables exist on cold start in serverless environment
with app.app_context():
    try:
        db.create_all()
    except Exception:
        pass

if __name__ == '__main__':
    print("=" * 60)
    print(" CivicPulse — Smart City Issue Reporting & Resolution Platform")
    print(" Aligned with UN Sustainable Development Goal 11")
    print(" Access URL: http://127.0.0.1:5000")
    print("=" * 60)
    app.run(host='127.0.0.1', port=5000, debug=True)
