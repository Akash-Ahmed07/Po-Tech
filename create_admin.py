#!/usr/bin/env python3
"""
Script to create an admin user for Po-Tech Educational Platform
"""

import os
import sys
from app import app, db
from models import User
from werkzeug.security import generate_password_hash

def create_admin_user():
    """Create an admin user with predefined credentials"""
    
    # Admin credentials
    admin_username = "admin"
    admin_email = "admin@potech.edu"
    admin_password = "PoTech2025!"  # Strong password for admin
    
    with app.app_context():
        # Check if admin user already exists
        existing_admin = User.query.filter_by(username=admin_username).first()
        if existing_admin:
            print(f"Admin user '{admin_username}' already exists!")
            print(f"Email: {existing_admin.email}")
            print(f"Admin status: {existing_admin.is_admin}")
            print(f"Verified status: {existing_admin.is_verified}")
            return existing_admin
        
        # Create new admin user
        admin_user = User(
            username=admin_username,
            email=admin_email,
            is_admin=True,
            is_verified=True  # Auto-verify admin user
        )
        admin_user.set_password(admin_password)
        
        try:
            db.session.add(admin_user)
            db.session.commit()
            
            print("✓ Admin user created successfully!")
            print("=" * 50)
            print("ADMIN LOGIN CREDENTIALS:")
            print("=" * 50)
            print(f"Username: {admin_username}")
            print(f"Email: {admin_email}")
            print(f"Password: {admin_password}")
            print("=" * 50)
            print("⚠️  IMPORTANT: Save these credentials securely!")
            print("   Change the password after first login.")
            print("=" * 50)
            
            return admin_user
            
        except Exception as e:
            print(f"❌ Error creating admin user: {e}")
            db.session.rollback()
            return None

def list_all_users():
    """List all users in the system"""
    with app.app_context():
        users = User.query.all()
        print(f"\n📋 Total users in system: {len(users)}")
        print("-" * 60)
        for user in users:
            print(f"ID: {user.id:3d} | {user.username:15s} | Admin: {'✓' if user.is_admin else '✗'} | Verified: {'✓' if user.is_verified else '✗'}")
        print("-" * 60)

if __name__ == "__main__":
    print("🚀 Po-Tech Admin User Creation Script")
    print("=" * 50)
    
    # Create admin user
    admin_user = create_admin_user()
    
    if admin_user:
        # List all users
        list_all_users()
        
        print("\n🎉 Admin setup complete!")
        print("You can now log in to the admin panel with the credentials above.")
    else:
        print("\n❌ Failed to create admin user. Check the error messages above.")
        sys.exit(1)