# Blog Service Application

![ScreenShot](./static/images/unb-logo.png)

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

## API Endpoints

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
  - `POST /blogs`: Create a new blog
  - `PUT /blogs/{id}`: Update a blog
  - `DELETE /blogs/{id}`: Delete a blog

- **Comments**
  - `GET /blogs/{id}/comments`: Get comments for a blog
  - `POST /blogs/{id}/comments`: Add a comment
  - `DELETE /comments/{id}`: Delete a comment

- **Users**
  - `GET /users/profile`: Get user profile
  - `PUT /users/email`: Update email
  - `PUT /users/phone`: Update phone number
  - `GET /users/notifications`: Get notification preferences
  - `PUT /users/notifications`: Update notification preferences

- **AI**
  - `POST /ai/generate`: Generate or enhance content with AI

## Usage

1. Register a new account
2. Verify your email address using the OTP sent
3. Browse existing blogs or create your own
4. Comment on blogs and engage with other users
5. Try the AI assistant to help generate blog content

## License



## Contributors

- :raised_hands: :raised_hands: **Team Brute-Force!!!** :raised_hands: :raised_hands:
- Iresh Issarsing
- Toushtee Pharishma Bhatoolaul
- Dineth Mudugamuwa Hewage