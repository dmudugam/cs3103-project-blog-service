# Blog Service Application

![ScreenShot](./static/images/logo.png)

## Overview

A full-featured blog service built with Flask and Vue.js that enables users to create, read, update, and delete blog posts. The application includes advanced features such as user authentication, comment threads, email/SMS verification, and AI-assisted content generation.

## Features

- **User Authentication**
  - Email/password registration
  - Email verification with OTP
  - SMS verification (optional)
  - LDAP authentication support
  - Password reset functionality

- **Blog Management**
  - Create and publish blog posts
  - Edit existing posts
  - Delete posts
  - View personal blog collection

- **Comment System**
  - Comment on blog posts
  - Reply to existing comments
  - Nested comment threads
  - Comment moderation

- **User Profiles**
  - Email management
  - Phone number management
  - Notification preferences

- **AI Content Generation**
  - Generate blog content using Gemini AI
  - Enhance existing content
  - Intelligent content suggestions

- **Notifications**
  - Email notifications for new blogs/comments
  - Configurable notification preferences

## Technologies

- **Backend**
  - Python 3.x
  - Flask
  - Flask-RESTful
  - Flask-Session

- **Frontend**
  - Vue.js
  - Bootstrap 4
  - Axios

- **Authentication**
  - Session-based authentication
  - OTP verification

- **External Services**
  - Email service
  - SMS service
  - Google Gemini AI API

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/dmudugam/cs3103-project-blog-service
   cd cs3103-project-blog-service
   ```

3. Creating Certificates and Setting Up Permissions:
   ```bash
   chmod +x makeCert.sh
   ./makeCert.sh
   ```

4. Install dependencies (If you do step 3, you can skip this):
   ```bash
   pip install -r requirements.txt
   ```

5. Generate or obtain SSL certificates (If you do step 3, you can skip this):
   ```bash
   # For development purposes only
   openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365
   ```

## Configuration

After cloning the repository, you need to update the configuration settings:

1. Open `config/settings.py` and update the following values:
   ```python
   # Database configuration
   DB_USER = 'your_database_username'
   DB_PASSWD = 'your_database_password'
   DB_DATABASE = 'your_database_name'
   
   # Security
   SECRET_KEY = 'your_secret_key'  # Generate a strong random key
   
   # LDAP configuration
   LDAP_HOST = 'your_ldap_host'
   
   # Email configuration
   SMTP_PASSWORD = 'your_email_password'
   
   # Twilio configuration (for SMS verification)
   TWILIO_ACCOUNT_SID = 'your_twilio_account_sid'
   TWILIO_AUTH_TOKEN = 'your_twilio_auth_token'
   
   # Google Gemini AI configuration
   GEMINI_API_KEY = 'your_gemini_api_key'
   ```

2. Update the port number:
   ```python
   APP_HOST = 'cs3013.cs.unb.ca'
   APP_PORT = your_assigned_port_number
   ```

## Running the Application

1. Initialize the database:
   ```bash
   mysql -u your_db_user -p your_db_name < database/schema.sql
   ```

2. Start the application:
   ```bash
   python run.py
   ```

3. Access the application:
   - The frontend and backend will be available at: `https://cs3013.cs.unb.ca:your_port_number`
   - For example, if your port number is 8006: `https://cs3013.cs.unb.ca:8006`

- **Auth**
  - `POST /auth/register`: Register a new user
  - `POST /auth/login`: Login
  - `POST /auth/logout`: Logout
  - `POST /auth/request-otp`: Request email verification
  - `POST /auth/verify-otp`: Verify email OTP
  - `POST /auth/forgot-password`: Initiate password reset

- **Blogs**
  - `GET /blogs`: List all blogs
  - `GET /blogs/{id}`: Get a specific blog
  - `POST /blogs/create`: Create a new blog
  - `PUT /blogs/{id}/update`: Update a blog
  - `DELETE /blogs/{id}/delete`: Delete a blog

- **Comments**
  - `GET /blogs/{id}/comments`: Get comments for a blog
  - `POST /blogs/{id}/comments/create`: Add a comment
  - `DELETE /comments/{id}/delete`: Delete a comment

- **Users**
  - `GET /users-api/{id}`: Get user profile
  - `PUT /users/email`: Update email
  - `PUT /users/phone`: Update phone number
  - `GET /users/notification-preferences`: Get notification preferences
  - `PUT /users/notification-preferences`: Update notification preferences

- **AI**
  - `POST /ai/generate`: Generate or enhance content with AI

## Development Notes

- The application uses session-based authentication with cookies
- SSL certificate and secure connections are required
- For a production environment, use proper SSL certificates and secure database credentials

## Troubleshooting

Common issues:
- **Database Connection Error**: Ensure your database credentials in `settings.py` are correct
- **Email/SMS Not Working**: Verify the email and Twilio credentials
- **CORS Issues**: For local development, you may need to modify CORS settings in `__init__.py`
- **SSL Certificate Problems**: Make sure certificate files are in the correct location

## Usage

1. Register a new account
2. Verify your email address using the OTP sent
3. Browse existing blogs or create your own
4. Comment on blogs and engage with other users
5. Try the AI assistant to help generate blog content

## Contributors

- :raised_hands: :raised_hands: **Team Brute-Force!!!** :raised_hands: :raised_hands:
- Iresh Issarsing
- Toushtee Pharishma Bhatoolaul
- Dineth Mudugamuwa Hewage
