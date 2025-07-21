#!/usr/bin/env python3
"""
Script to display admin credentials for Po-Tech Educational Platform
"""

from app import app, db
from models import User

def get_admin_credentials():
    """Get admin user credentials"""
    with app.app_context():
        admin_user = User.query.filter_by(username='admin').first()
        
        if admin_user:
            print("🔐 Po-Tech Admin Login Credentials")
            print("=" * 50)
            print(f"Username: admin")
            print(f"Email: {admin_user.email}")
            print(f"Password: Unitedsylhet90")  # From app.py line 83
            print("=" * 50)
            print(f"Admin Status: {'✓ Active' if admin_user.is_admin else '✗ Not Admin'}")
            print(f"Email Verified: {'✓ Verified' if admin_user.is_verified else '✗ Not Verified'}")
            print(f"Account Created: {admin_user.created_at}")
            print("=" * 50)
            print("\nℹ️  Access the admin panel at: /admin")
            print("🔗 Full admin URL: http://localhost:5000/admin")
            print("\n⚠️  SECURITY NOTE: Change this password after first login!")
            return admin_user
        else:
            print("❌ No admin user found!")
            return None

if __name__ == "__main__":
    get_admin_credentials()