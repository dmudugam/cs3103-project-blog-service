/**
 * Authentication Service
 */
const AuthService = {

    checkAuth(app) {
        app.loading.auth = true;
        
        return axios.get(`${app.baseURL}/auth/login`, {
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
                app.userType = response.data.userType || 'local';
                app.userEmail = response.data.email;
                app.hasEmail = Boolean(response.data.email);
                app.userPhone = response.data.phoneNumber;
                app.hasPhone = Boolean(response.data.phoneNumber);
                
                // Store phone number
                if (app.userPhone) {
                    localStorage.setItem('userPhone', app.userPhone);
                    localStorage.setItem('userId', app.userId);
                }
                
                // Bugfix after Bug Bash 2 - Mark phone as added if mobile is verified
                if (response.data.mobileVerified) {
                    app.hasPhone = true;
                }
                
                app.smsEnabled = response.data.smsEnabled;
                
                app.getNotificationPreferences();
            } else {
                this.resetUserState(app);
            }
            return response;
        })
        .catch(error => {
            console.log("Auth check error:", error);
            this.resetUserState(app);
            return Promise.reject(error);
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
            app.userEmail = response.data.email;
            app.hasEmail = Boolean(response.data.email);
            app.userPhone = response.data.phoneNumber;
            app.hasPhone = Boolean(response.data.phoneNumber);
            
            if (response.data.mobileVerified && !response.data.phoneNumber) {
                const savedUserId = localStorage.getItem('userId');
                const savedPhone = localStorage.getItem('userPhone');
                
                if (savedUserId && savedUserId == app.userId && savedPhone) {
                    app.userPhone = savedPhone;
                    app.phoneForm.phone = savedPhone;
                }

                app.hasPhone = true;
            }
            
            app.smsEnabled = response.data.smsEnabled;
            
            app.showLoginModal = false;
            app.loginForm.password = "";
            app.showNotification("success", "Login successful");
            
            app.getNotificationPreferences();

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
            
            app.getBlogs();
            
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
            app.loginForm.error = message;
        })
        .finally(() => {
            app.loading.auth = false;
        });
    },
    
    // End user session
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
    
    
    // Register a new user
    register(app) {
        app.registerForm.error = null;
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
            app.showNotification("success", "Registration successful! Please check your email for verification.");
            
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
    
    
    // Request email verification OTP
    requestEmailVerification(app) {
        if (app.emailOtpForm) {
            app.emailOtpForm.error = null;
        }
        
        if (app.userType === 'ldap' && app.showEmailOtpModal && app.emailForm && app.emailForm.email) {
            app.loading.verification = true;
            
            axios.put(`${app.baseURL}/users/email`, 
                JSON.stringify({
                    email: app.emailForm.email
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
                app.emailOtpForm.userId = response.data.userId;
                
                // Update app state with the email info
                app.userEmail = app.emailForm.email;
                app.hasEmail = true;
                
                app.showNotification("success", "Verification OTP sent to your email.");
            })
            .catch(error => {
                console.log("Request email verification error:", error);
                let message = "Failed to send email verification OTP";
                if (error.response && error.response.data && error.response.data.message) {
                    message = error.response.data.message;
                }
                
                if (app.showEmailOtpModal) {
                    app.emailOtpForm.error = message;
                } else {
                    app.showNotification("error", message);
                }
            })
            .finally(() => {
                app.loading.verification = false;
            });
            
            return;
        }
        
        const userId = app.emailOtpForm.userId || app.userId;
        
        if (!userId) {
            app.showNotification("error", "User ID not found. Please try again.");
            return;
        }
        
        const isEmailUpdate = app.showEmailOtpModal && app.hasEmail;
        
        const requestData = {
            userId: userId,
            updatingEmail: isEmailUpdate
        };
        
        app.loading.verification = true;
        
        axios.post(`${app.baseURL}/auth/request-otp`, 
            JSON.stringify(requestData), 
            {
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                withCredentials: true
            }
        )
        .then(response => {
            // Make sure we have the userId set for verification
            app.emailOtpForm.userId = userId;
            
            app.showEmailOtpModal = true;
            app.showNotification("success", "Verification OTP sent to your email.");
        })
        .catch(error => {
            let message = "Failed to send email verification OTP";
            if (error.response && error.response.data && error.response.data.message) {
                message = error.response.data.message;
            }
            
            if (message.includes("Please add an email") && (app.userEmail || (app.emailForm && app.emailForm.email))) {
                const emailToUse = app.userEmail || app.emailForm.email;
                
                axios.put(`${app.baseURL}/users/email`, 
                    JSON.stringify({
                        email: emailToUse
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
                    app.emailOtpForm.userId = response.data.userId;
                    
                    // Update app state with the email info
                    app.userEmail = emailToUse;
                    app.hasEmail = true;
                    
                    app.showNotification("success", "Verification OTP sent to your email.");
                })
                .catch(innerError => {
                    
                    let innerMessage = "Failed to send verification OTP";
                    if (innerError.response && innerError.response.data && innerError.response.data.message) {
                        innerMessage = innerError.response.data.message;
                    }
                    
                    if (app.showEmailOtpModal) {
                        app.emailOtpForm.error = innerMessage;
                    } else {
                        app.showNotification("error", innerMessage);
                    }
                })
                .finally(() => {
                    app.loading.verification = false;
                });
                
                return;
            }
            
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
    
    // Verify email with OTP
    verifyEmailOTP(app) {
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
            
            if (app.authenticated) {
                this.checkAuth(app);
            }
        })
        .catch(error => {
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
    
    // Request mobile verification OTP
    requestMobileVerification(app) {
        if (app.mobileOtpForm) {
            app.mobileOtpForm.error = null;
        }
        
        if (!app.authenticated) {
            app.showNotification("error", "Please login first");
            return;
        }
        
        if (!app.smsEnabled) {
            app.showNotification("warning", "SMS functionality is not enabled on the server");
            return;
        }
        
        app.loading.verification = true;
        
        const requestData = {
            updatingPhone: app.hasPhone
        };
        
        if (app.phoneForm && app.phoneForm.phone) {
            requestData.phone = app.phoneForm.phone;
        } else if (app.userPhone) {
            requestData.phone = app.userPhone;
        }
        
        axios.post(`${app.baseURL}/auth/request-mobile-otp`, 
            JSON.stringify(requestData), 
            {
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                withCredentials: true
            }
        )
        .then(response => {
            app.mobileOtpForm.userId = app.userId;
            app.showMobileOtpModal = true;
            
            // Store the phone in case we need it later
            if (response.data.phoneUsed) {
                app.userPhone = response.data.phoneUsed;
                app.hasPhone = true;
                localStorage.setItem('userPhone', app.userPhone);
            }
            
            app.showNotification("success", "Verification OTP sent to your phone.");
        })
        .catch(error => {
            console.log("Request mobile verification error:", error);
            let message = "Failed to send mobile verification OTP";
            if (error.response && error.response.data && error.response.data.message) {
                message = error.response.data.message;
            }
            
            // If we get "No phone number found" error, open phone modal
            if (message.includes("No phone number found")) {
                app.showNotification("error", "Please add a phone number first");
                app.openPhoneModal();
            } else if (app.showMobileOtpModal) {
                app.mobileOtpForm.error = message;
            } else {
                app.showNotification("error", message);
            }
        })
        .finally(() => {
            app.loading.verification = false;
        });
    },
    
    // Verify mobile OTP
    verifyMobileOTP(app) {
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
    
    // Request password reset
    requestPasswordReset(app) {
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
    
    // password reset
    resetPassword(app) {
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
        
        // Check if this may be the same as the old password
        if (app.loginForm && app.loginForm.password && 
            app.loginForm.password === app.forgotPasswordForm.password &&
            app.loginForm.username === app.forgotPasswordForm.username) {
            app.forgotPasswordForm.error = "New password must be different from your last five passwords.";
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