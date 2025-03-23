import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import threading
from flask import current_app
import sys

def send_email(to_email, subject, body):
    """Generic email sending function"""
    if not to_email:
        print("Cannot send email: No email address provided", file=sys.stderr)
        return False
        
    msg = MIMEMultipart()
    msg['From'] = current_app.config['EMAIL_FROM']
    msg['To'] = to_email
    msg['Subject'] = subject
    
    msg.attach(MIMEText(body, 'plain'))
    
    # Getting the current application context for the thread
    app_context = current_app._get_current_object()
    
    # Getting config values before passing to thread
    smtp_server = current_app.config['SMTP_SERVER']
    smtp_port = current_app.config['SMTP_PORT']
    smtp_username = current_app.config['SMTP_USERNAME']
    smtp_password = current_app.config['SMTP_PASSWORD']
    
    # Sending the email in a separate thread
    def send_email_thread():
        # Use the application context in the thread
        with app_context.app_context():
            try:
                server = smtplib.SMTP(smtp_server, smtp_port)
                server.starttls()
                server.login(smtp_username, smtp_password)
                server.send_message(msg)
                server.quit()
                print(f"Email sent to {to_email}")
                return True
            except Exception as e:
                print(f"Failed to send email: {e}", file=sys.stderr)
                return False
    
    thread = threading.Thread(target=send_email_thread)
    thread.start()
    return True

def send_verification_email(email, username, otp):
    """Send verification email with OTP to user"""
    subject = "Verify Your Blog Service Email"
    
    body = f"""
    Hello {username},
    
    Please verify your email using the following OTP code:
    
    Your OTP: {otp}
    
    This code will expire in 15 minutes.
    
    Best regards,
    The Blog Service Team
    """
    
    return send_email(email, subject, body)

def send_password_reset_otp(email, username, otp):
    """Send password reset email with OTP to user"""
    subject = "Reset Your Blog Service Password"
    
    body = f"""
    Hello {username},
    
    You have requested to reset your password for the Blog Service.
    
    Please use the following OTP code to reset your password:
    
    Your OTP: {otp}
    
    This code will expire in 1 hour.
    
    If you did not request a password reset, please ignore this email.
    
    Best regards,
    The Blog Service Team
    """
    
    return send_email(email, subject, body)

def send_blog_notification(blog, author_name, subscribers):
    """Send notification email when a new blog is created"""
    if not subscribers:
        return False
        
    subject = f"New Blog Post: {blog['title']}"
    
    body = f"""
    Hello,
    
    A new blog post has been published by {author_name}:
    
    Title: {blog['title']}
    
    Visit our blog service to read the full post.
    
    Best regards,
    The Blog Service Team
    """
    
    # For multiple recipients, we need a different approach
    msg = MIMEMultipart()
    msg['From'] = current_app.config['EMAIL_FROM']
    msg['Subject'] = subject
    
    # Use BCC for privacy
    msg['Bcc'] = ", ".join(subscribers)
    
    msg.attach(MIMEText(body, 'plain'))
    
    # Send the email in a separate thread
    def send_email_thread():
        try:
            server = smtplib.SMTP(current_app.config['SMTP_SERVER'], current_app.config['SMTP_PORT'])
            server.starttls()
            server.login(current_app.config['SMTP_USERNAME'], current_app.config['SMTP_PASSWORD'])
            server.send_message(msg)
            server.quit()
            print(f"Blog notification sent to {len(subscribers)} subscribers")
            return True
        except Exception as e:
            print(f"Failed to send blog notification: {e}", file=sys.stderr)
            return False
    
    thread = threading.Thread(target=send_email_thread)
    thread.start()
    return True

def send_comment_notification(comment, blog_title, comment_author, blog_author_email):
    """Send notification email when a comment is added to a blog post"""
    subject = f"New Comment on Your Blog: {blog_title}"
    
    body = f"""
    Hello,
    
    {comment_author} has commented on your blog post "{blog_title}".
    
    Visit our blog service to view the comment and respond.
    
    Best regards,
    The Blog Service Team
    """
    
    return send_email(blog_author_email, subject, body)