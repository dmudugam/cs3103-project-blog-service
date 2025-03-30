import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import threading
from flask import current_app
import sys
import textwrap

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

    app_context = current_app._get_current_object()
    
    smtp_server = current_app.config['SMTP_SERVER']
    smtp_port = current_app.config['SMTP_PORT']
    smtp_username = current_app.config['SMTP_USERNAME']
    smtp_password = current_app.config['SMTP_PASSWORD']
    
    # Sending the email
    def send_email_thread():
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
    subject = "Verify Your Blog Service Email"
    
    body = textwrap.dedent(f"""
    Hello {username},
    
    Please verify your email using the following OTP code:
    
    Your OTP: {otp}
    
    This code will expire in 15 minutes.
    
    Best regards,
    The Blog Service Team
    """).strip()
    
    return send_email(email, subject, body)

def send_password_reset_otp(email, username, otp):
    subject = "Reset Your Blog Service Password"
    
    body = textwrap.dedent(f"""
    Hello {username},
    
    You have requested to reset your password for the Blog Service.
    
    Please use the following OTP code to reset your password:
    
    Your OTP: {otp}
    
    This code will expire in 1 hour.
    
    If you did not request a password reset, please ignore this email.
    
    Best regards,
    The Blog Service Team
    """).strip()
    
    return send_email(email, subject, body)

def send_blog_notification(blog, author_name, subscribers):
    if not subscribers or len(subscribers) == 0:
        return
    
    app_context = current_app._get_current_object()
    
    def send_notification_thread():
        with app_context.app_context():
            try:
                for subscriber_email in subscribers:
                    subject = f"New Blog Post: {blog['title']}"
                    body = textwrap.dedent(f"""
                    Hi there,
                    
                    {author_name} just published a new blog post:
                    
                    {blog['title']}
                    
                    {blog['content'][:200]}... (continue reading on the website)
                    
                    Visit our blog service to read the full post.
                    
                    To manage your notification preferences, visit your profile page.
                    
                    Best regards,
                    The Blog Service Team
                    """).strip()
                    
                    send_email(subscriber_email, subject, body)
                
                return True
            except Exception as e:
                print(f"Failed to send blog notification: {e}", file=sys.stderr)
                return False
    
    # Start the sending
    thread = threading.Thread(target=send_notification_thread)
    thread.start()
    return True

def send_comment_notification(comment, blog_title, comment_author, blog_author_email):
    if not blog_author_email:
        return
    
    app_context = current_app._get_current_object()
    
    def send_notification_thread():
        with app_context.app_context():
            try:
                subject = f"New Comment on Your Blog: {blog_title}"
                body = textwrap.dedent(f"""
                Hi there,
                
                {comment_author} just commented on your blog post "{blog_title}":
                
                "{comment['content'][:200]}" 
                
                Visit our blog service to view the comment and respond.
                
                To manage your notification preferences, visit your profile page.
                
                Best regards,
                The Blog Service Team
                """).strip()
                
                send_email(blog_author_email, subject, body)
                return True
            except Exception as e:
                print(f"Failed to send comment notification: {e}", file=sys.stderr)
                return False
    
    # Start the sending
    thread = threading.Thread(target=send_notification_thread)
    thread.start()
    return True