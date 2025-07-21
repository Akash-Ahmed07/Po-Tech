from flask_mail import Message
from app import mail
import os

def send_verification_email(email, token):
    """Send email verification link"""
    try:
        # Skip email sending in development mode
        from flask import current_app
        if current_app.config.get('MAIL_SUPPRESS_SEND', False) or not current_app.config.get('MAIL_SERVER'):
            print(f"Email sending disabled - Verification email would be sent to: {email}")
            print(f"Verification token: {token}")
            return True
            
        msg = Message(
            'Verify Your Email - Po-Tech',
            recipients=[email]
        )
        
        verification_url = f"http://localhost:5000/verify/{token}"
        
        msg.html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; text-align: center;">
                <h1>Po-Tech Educational Platform</h1>
            </div>
            <div style="padding: 20px; background: #f8f9fa;">
                <h2>Welcome to Po-Tech!</h2>
                <p>Thank you for registering with Po-Tech Educational Platform. To complete your registration, please click the button below to verify your email address.</p>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{verification_url}" style="background: #28a745; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">
                        Verify Email Address
                    </a>
                </div>
                
                <p>If the button doesn't work, you can also copy and paste this link into your browser:</p>
                <p style="word-break: break-all; color: #666;">{verification_url}</p>
                
                <hr style="margin: 30px 0; border: none; border-top: 1px solid #ddd;">
                <p style="color: #666; font-size: 14px;">
                    If you didn't create an account with Po-Tech, please ignore this email.
                </p>
            </div>
        </div>
        """
        
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Failed to send verification email: {e}")
        return False

def send_contact_notification(contact_data):
    """Send notification when contact form is submitted"""
    try:
        # Skip email sending in development mode
        from flask import current_app
        if current_app.config.get('MAIL_SUPPRESS_SEND', False) or not current_app.config.get('MAIL_SERVER'):
            print(f"Email sending disabled - Contact notification would be sent")
            print(f"Contact data: {contact_data}")
            return True
            
        msg = Message(
            f'New Contact Message: {contact_data["subject"]}',
            recipients=[os.environ.get("EMAIL_USERNAME", "groweasy25@gmail.com")]
        )
        
        msg.html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2>New Contact Message</h2>
            <p><strong>Name:</strong> {contact_data['name']}</p>
            <p><strong>Email:</strong> {contact_data['email']}</p>
            <p><strong>Subject:</strong> {contact_data['subject']}</p>
            <div style="background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 15px 0;">
                <strong>Message:</strong><br>
                {contact_data['message']}
            </div>
        </div>
        """
        
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Failed to send contact notification: {e}")
        return False
