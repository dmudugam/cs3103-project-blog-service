// Authentication services
const AuthService = {
    checkAuth(app) {
        app.loading.auth = true;
        
        axios.get(`${app.baseURL}/auth/login`, {
            headers: { 'Accept': 'application/json' },
            withCredentials: true
        })
        .then(response => {
            if (response.data && response.data.status === 'success') {
                app.authenticated = true;
                app.userId = response.data.userId;
                app.username = response.data.username;
                app.verified = response.data.verified;
                app.mobileVerified = response.data.mobileVerified;
                app.userType = response.data.userType || 'ldap';
                
                // Handle email data
                app.userEmail = response.data.email;
                app.hasEmail = Boolean(response.data.email);
                
                // Handle phone data
                app.userPhone = response.data.phoneNumber;
                app.hasPhone = Boolean(response.data.phoneNumber);
                
                // Store phone number in state
                if (app.userPhone) {
                    localStorage.setItem('userPhone', app.userPhone);
                    localStorage.setItem('userId', app.userId);
                }
                
                // Mark phone as added if mobile is verified
                if (response.data.mobileVerified) {
                    app.hasPhone = true;
                }
                
                app.smsEnabled = response.data.smsEnabled;
                
                // Get notification preferences if authenticated
                app.getNotificationPreferences();
            } else {
                this.resetUserState(app);
            }
        })
        .catch(error => {
            console.log("Auth check error:", error);
            this.resetUserState(app);
        })
        .finally(() => {
            app.loading.auth = false;
        });
    },
    
    resetUserState(app) {
        app.authenticated = false;
        app.userId = null;
        app.username = null;
        app.verified = false;
        app.mobileVerified = false;
        app.userEmail = null;
        app.userPhone = null;
        app.hasEmail = false;
        app.hasPhone = false;
        app.smsEnabled = false;
        app.userType = null;
    },
    
    login(app) {
        // Clear previous error
        app.loginForm.error = null;
        
        if (!app.loginForm.username || !app.loginForm.password) {
            app.loginForm.error = "Username and password are required";
            return;
        }
        
        app.loading.auth = true;
        axios.post(`${app.baseURL}/auth/login`, 
            JSON.stringify({
                username: app.loginForm.username,
                password: app.loginForm.password,
                type: app.loginForm.type
            }), 
            {
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                withCredentials: true
            }
        )
        .then(response => {
            app.authenticated = true;
            app.userId = response.data.userId;
            app.username = response.data.username;
            app.verified = response.data.verified;
            app.mobileVerified = response.data.mobileVerified;
            app.userType = response.data.userType || 'ldap';
            
            // Handle email data
            app.userEmail = response.data.email;
            app.hasEmail = Boolean(response.data.email);
            
            // Handle phone data
            app.userPhone = response.data.phoneNumber;
            app.hasPhone = Boolean(response.data.phoneNumber);
            
            if (response.data.mobileVerified && !response.data.phoneNumber) {
                // Restoring phone from state
                const savedUserId = localStorage.getItem('userId');
                const savedPhone = localStorage.getItem('userPhone');
                
                if (savedUserId && savedUserId == app.userId && savedPhone) {
                    console.log("Restored phone number from localStorage:", savedPhone);
                    app.userPhone = savedPhone;
                    app.phoneForm.phone = savedPhone;
                }
                
                // Mark phone as added if mobile was verified
                app.hasPhone = true;
            }
            
            app.smsEnabled = response.data.smsEnabled;
            
            app.showLoginModal = false;
            app.loginForm.password = "";
            app.showNotification("success", "Login successful");
            
            // Get notification preferences
            app.getNotificationPreferences();
            
            // If user doesn't have email or phone, show messages
            if (!app.hasEmail && !app.hasPhone && app.smsEnabled) {
                setTimeout(() => {
                    app.showNotification("warning", "Please add your email address or phone number for verification");
                    app.openEmailModal();
                }, 1000);
            } else if (!app.hasEmail && !app.smsEnabled) {
                setTimeout(() => {
                    app.showNotification("warning", "Please add your email address");
                    app.openEmailModal();
                }, 1000);
            }
            
            // Refresh blogs
            app.getBlogs();
            
            // If we don't have a phone number but we're mobile verified, 
            // trigger a refresh from the server after a short delay
            if (response.data.mobileVerified && !app.userPhone) {
                setTimeout(() => {
                    window.UserService.refreshUserData(app);
                }, 1000);
            }
        })
        .catch(error => {
            console.log("Login error:", error);
            let message = "Login failed";
            if (error.response && error.response.data && error.response.data.message) {
                message = error.response.data.message;
            }
            // Display error
            app.loginForm.error = message;
        })
        .finally(() => {
            app.loading.auth = false;
        });
    },
    
    register(app) {
        // Clear previous error
        app.registerForm.error = null;
        
        // Validate form using FormValidators
        const validationResult = window.FormValidators.validateForm(app.registerForm, {
            username: { required: true, label: "Username" },
            email: { required: true, email: true, label: "Email" },
            password: { required: true, password: true, minLength: 8, label: "Password" },
            passwordConfirm: { required: true, match: "password", matchLabel: "Password", label: "Password confirmation" }
        });
        
        if (!validationResult.isValid) {
            app.registerForm.error = Object.values(validationResult.errors)[0];
            return;
        }
        
        app.loading.auth = true;
        axios.post(`${app.baseURL}/auth/register`, 
            JSON.stringify({
                username: app.registerForm.username,
                email: app.registerForm.email,
                password: app.registerForm.password
            }), 
            {
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                withCredentials: true
            }
        )
        .then(response => {
            // Show success notification
            app.showNotification("success", "Registration successful! Please check your email for verification.");
            
            // Get user ID from response
            const userId = response.data.userId;
            
            // Clear form and close modal
            app.registerForm = {
                username: "",
                email: "",
                password: "",
                passwordConfirm: "",
                error: null
            };
            app.showRegisterModal = false;
            
            // Set up and show the email OTP verification modal
            app.emailOtpForm.userId = userId;
            app.showEmailOtpModal = true;
        })
        .catch(error => {
            console.log("Registration error:", error);
            let message = "Registration failed";
            if (error.response && error.response.data && error.response.data.message) {
                message = error.response.data.message;
            }
            app.registerForm.error = message;
        })
        .finally(() => {
            app.loading.auth = false;
        });
    },
    
    logout(app) {
        app.loading.auth = true;
        axios.post(`${app.baseURL}/auth/logout`, {}, {
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            withCredentials: true
        })
        .then(response => {
            this.resetUserState(app);
            
            // Clear state on logout
            localStorage.removeItem('userPhone');
            localStorage.removeItem('userId');
            
            app.showNotification("success", "Logout successful");
        })
        .catch(error => {
            console.log("Logout error:", error);
            app.showNotification("error", "Logout failed");
        })
        .finally(() => {
            app.loading.auth = false;
        });
    },
    
    requestEmailVerification(app) {
        // Clear previous error
        if (app.emailOtpForm) {
            app.emailOtpForm.error = null;
        }
        
        if (!app.authenticated) {
            app.showNotification("error", "Please login first");
            return;
        }
        
        if (!app.hasEmail) {
            app.showNotification("error", "Please add an email address first");
            app.openEmailModal();
            return;
        }
        
        app.loading.verification = true;
        axios.post(`${app.baseURL}/auth/request-otp`, {}, {
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            withCredentials: true
        })
        .then(response => {
            app.emailOtpForm.userId = app.userId;
            app.showEmailOtpModal = true;
            app.showNotification("success", "Verification OTP sent to your email.");
        })
        .catch(error => {
            console.log("Request email verification error:", error);
            let message = "Failed to send email verification OTP";
            if (error.response && error.response.data && error.response.data.message) {
                message = error.response.data.message;
            }
            
            // Display error within the modal if it's open, otherwise show notification
            if (app.showEmailOtpModal) {
                app.emailOtpForm.error = message;
            } else {
                app.showNotification("error", message);
            }
        })
        .finally(() => {
            app.loading.verification = false;
        });
    },
    
    verifyEmailOTP(app) {
        // Clear previous error
        app.emailOtpForm.error = null;
        
        if (!app.emailOtpForm.otp) {
            app.emailOtpForm.error = "OTP is required";
            return;
        }
        
        if (!app.emailOtpForm.userId) {
            app.emailOtpForm.error = "User ID is missing";
            return;
        }
        
        app.loading.verification = true;
        axios.post(`${app.baseURL}/auth/verify-otp`, 
            JSON.stringify({
                userId: app.emailOtpForm.userId,
                otp: app.emailOtpForm.otp
            }), 
            {
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                withCredentials: true
            }
        )
        .then(response => {
            app.showEmailOtpModal = false;
            app.emailOtpForm.otp = "";
            app.emailOtpForm.error = null;
            
            if (app.authenticated) {
                app.verified = true;
            }
            
            app.showNotification("success", "Email verified successfully!");
            
            // If user is already logged in, refresh auth status
            if (app.authenticated) {
                this.checkAuth(app);
            }
        })
        .catch(error => {
            console.log("Email verification error:", error);
            let message = "Email verification failed";
            if (error.response && error.response.data && error.response.data.message) {
                message = error.response.data.message;
            }
    
            app.emailOtpForm.error = message;
        })
        .finally(() => {
            app.loading.verification = false;
        });
    },
    
    requestMobileVerification(app) {
        // Clear previous error
        if (app.mobileOtpForm) {
            app.mobileOtpForm.error = null;
        }
        
        if (!app.authenticated) {
            app.showNotification("error", "Please login first");
            return;
        }
        
        if (!app.hasPhone) {
            app.showNotification("error", "Please add a phone number first");
            app.openPhoneModal();
            return;
        }
        
        if (!app.smsEnabled) {
            app.showNotification("warning", "SMS functionality is not enabled on the server");
            return;
        }
        
        app.loading.verification = true;
        axios.post(`${app.baseURL}/auth/request-mobile-otp`, {}, {
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            withCredentials: true
        })
        .then(response => {
            app.mobileOtpForm.userId = app.userId;
            app.showMobileOtpModal = true;
            app.showNotification("success", "Verification OTP sent to your phone.");
        })
        .catch(error => {
            console.log("Request mobile verification error:", error);
            let message = "Failed to send mobile verification OTP";
            if (error.response && error.response.data && error.response.data.message) {
                message = error.response.data.message;
            }
            
            // Display error within the modal if it's open, otherwise show notification
            if (app.showMobileOtpModal) {
                app.mobileOtpForm.error = message;
            } else {
                app.showNotification("error", message);
            }
        })
        .finally(() => {
            app.loading.verification = false;
        });
    },
    
    verifyMobileOTP(app) {
        // Clear previous error
        app.mobileOtpForm.error = null;
        
        if (!app.mobileOtpForm.otp) {
            app.mobileOtpForm.error = "OTP is required";
            return;
        }
        
        if (!app.mobileOtpForm.userId) {
            app.mobileOtpForm.error = "User ID is missing";
            return;
        }
        
        app.loading.verification = true;
        axios.post(`${app.baseURL}/auth/verify-mobile-otp`, 
            JSON.stringify({
                userId: app.mobileOtpForm.userId,
                otp: app.mobileOtpForm.otp
            }), 
            {
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                withCredentials: true
            }
        )
        .then(response => {
            app.showMobileOtpModal = false;
            app.mobileOtpForm.otp = "";
            app.mobileOtpForm.error = null;
            
            if (app.authenticated) {
                app.mobileVerified = true;
            }
            
            app.showNotification("success", "Phone number verified successfully!");
            
            // If user is already logged in, refresh auth status
            if (app.authenticated) {
                this.checkAuth(app);
            }
        })
        .catch(error => {
            console.log("Mobile verification error:", error);
            let message = "Mobile verification failed";
            if (error.response && error.response.data && error.response.data.message) {
                message = error.response.data.message;
            }
        
            app.mobileOtpForm.error = message;
        })
        .finally(() => {
            app.loading.verification = false;
        });
    },
    
    requestPasswordReset(app) {
        // Clear previous messages
        app.forgotPasswordForm.error = null;
        
        if (!app.forgotPasswordForm.email) {
            app.forgotPasswordForm.error = "Email is required";
            return;
        }
        
        // Validate email format
        if (!window.FormValidators.isValidEmail(app.forgotPasswordForm.email)) {
            app.forgotPasswordForm.error = "Please enter a valid email address";
            return;
        }
        
        app.loading.auth = true;
        axios.post(`${app.baseURL}/auth/forgot-password`, 
            JSON.stringify({
                email: app.forgotPasswordForm.email
            }), 
            {
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                }
            }
        )
        .then(response => {
            // Mark OTP as sent and show success message
            app.forgotPasswordForm.otpSent = true;
            app.forgotPasswordForm.success = "If an account with that email exists, a password reset OTP has been sent.";
            // Clear success message after 3 seconds so form continues to next step
            setTimeout(() => {
                app.forgotPasswordForm.success = null;
            }, 3000);
        })
        .catch(error => {
            console.log("Password reset error:", error);
            let message = "Request failed";
            if (error.response && error.response.data && error.response.data.message) {
                message = error.response.data.message;
            }
            app.forgotPasswordForm.error = message;
        })
        .finally(() => {
            app.loading.auth = false;
        });
    },
    
    verifyResetOTP(app) {
        // Clear previous messages
        app.forgotPasswordForm.error = null;
        
        if (!app.forgotPasswordForm.otp) {
            app.forgotPasswordForm.error = "OTP is required";
            return;
        }
        
        if (app.forgotPasswordForm.otp.length !== 6 || !/^\d+$/.test(app.forgotPasswordForm.otp)) {
            app.forgotPasswordForm.error = "OTP must be 6 digits";
            return;
        }
        
        app.loading.auth = true;
        axios.post(`${app.baseURL}/auth/verify-reset-otp`, 
            JSON.stringify({
                email: app.forgotPasswordForm.email,
                otp: app.forgotPasswordForm.otp
            }), 
            {
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                }
            }
        )
        .then(response => {
            app.forgotPasswordForm.otpVerified = true;
            app.forgotPasswordForm.username = response.data.username;
        })
        .catch(error => {
            console.log("OTP verification error:", error);
            let message = "Invalid or expired OTP";
            if (error.response && error.response.data && error.response.data.message) {
                message = error.response.data.message;
            }
            app.forgotPasswordForm.error = message;
        })
        .finally(() => {
            app.loading.auth = false;
        });
    },
    
    resetPassword(app) {
        // Clear previous messages
        app.forgotPasswordForm.error = null;
        
        // Validate form
        if (!app.forgotPasswordForm.password || !app.forgotPasswordForm.passwordConfirm) {
            app.forgotPasswordForm.error = "All fields are required";
            return;
        }
        
        // Validate password strength
        const passwordResult = window.FormValidators.validatePassword(app.forgotPasswordForm.password);
        if (!passwordResult.isValid) {
            app.forgotPasswordForm.error = passwordResult.feedback;
            return;
        }
        
        // Check if passwords match
        if (app.forgotPasswordForm.password !== app.forgotPasswordForm.passwordConfirm) {
            app.forgotPasswordForm.error = "Passwords do not match";
            return;
        }
        
        app.loading.auth = true;
        axios.post(`${app.baseURL}/auth/reset-password`, 
            JSON.stringify({
                email: app.forgotPasswordForm.email,
                otp: app.forgotPasswordForm.otp,
                password: app.forgotPasswordForm.password
            }), 
            {
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                }
            }
        )
        .then(response => {
            app.forgotPasswordForm.success = response.data.message;
            // Clear the form except for success message
            app.forgotPasswordForm = {
                ...app.forgotPasswordForm,
                email: "",
                otp: "",
                password: "",
                passwordConfirm: "",
                error: null,
                success: response.data.message
            };
        })
        .catch(error => {
            console.log("Password reset error:", error);
            let message = "Password reset failed";
            if (error.response && error.response.data && error.response.data.message) {
                message = error.response.data.message;
            }
            app.forgotPasswordForm.error = message;
        })
        .finally(() => {
            app.loading.auth = false;
        });
    }
};

window.AuthService = AuthService;