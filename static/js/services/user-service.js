/**
 * User Service
 */
const UserService = {

    updateEmail(app) {
        app.emailForm.error = null;
        
        // Validate email
        if (!app.emailForm.email) {
            app.emailForm.error = "Email is required";
            return;
        }
        
        // Validate email
        if (!window.FormValidators.isValidEmail(app.emailForm.email)) {
            app.emailForm.error = "Please enter a valid email address";
            return;
        }
        
        // Submit request to update email
        app.loading.auth = true;
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
            app.showEmailModal = false;
            app.emailOtpForm.userId = response.data.userId;
            app.showEmailOtpModal = true;
            
            const action = app.emailForm.email === app.userEmail ? "updated" : "added";
            app.showNotification("success", `Email ${action}! Please verify your email with the OTP sent to your inbox.`);
        })
        .catch(error => {
            console.log("Update email error:", error);
            let message = "Failed to update email";
            if (error.response && error.response.data && error.response.data.message) {
                message = error.response.data.message;
            }
            app.emailForm.error = message;
        })
        .finally(() => {
            app.loading.auth = false;
        });
    },
    
    updatePhone(app) {
        app.phoneForm.error = null;
        
        // Validate phone
        if (!app.phoneForm.phone) {
            app.phoneForm.error = "Phone number is required";
            return;
        }
        
        // Validate phone
        if (!window.FormValidators.isValidPhone(app.phoneForm.phone)) {
            app.phoneForm.error = "Phone number must be in format (e.g., +1234567890)";
            return;
        }
        
        // Submit request to update phone
        app.loading.auth = true;
        axios.put(`${app.baseURL}/users/phone`, 
            JSON.stringify({
                phone: app.phoneForm.phone
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
            app.showPhoneModal = false;
            

            app.userPhone = response.data.pendingPhone || response.data.phone_number || app.phoneForm.phone;
            app.hasPhone = true; 
            app.mobileVerified = false;
            
            localStorage.setItem('userPhone', app.userPhone);
            localStorage.setItem('userId', app.userId);
            
            app.mobileOtpForm.userId = response.data.userId;
            
            // Check if SMS was successfully sent
            const smsSent = response.data.sms_sent;
            
            if (smsSent) {
                app.showMobileOtpModal = true;
                
                const action = app.phoneForm.phone === app.userPhone ? "updated" : "added";
                app.showNotification("success", `Phone number ${action}! Please verify your phone with the OTP sent via SMS.`);
            } else {
                // If SMS couldn't be sent
                app.showNotification("warning", "Phone number is not on the whitelist. Please reach out to support for assistance.");
                app.checkAuth()
                .then(() => {
                })
                .catch(error => {
                });
            }
        })
        .catch(error => {
            console.log("Update phone error:", error);
            let message = "Failed to update phone number";
            if (error.response && error.response.data && error.response.data.message) {
                message = error.response.data.message;
            }
            app.phoneForm.error = message;
        })
        .finally(() => {
            app.loading.auth = false;
        });
    },

    getNotificationPreferences(app) {
        if (!app.authenticated) {
            return;
        }
        
        axios.get(`${app.baseURL}/users/notification-preferences`, {
            headers: {
                'Accept': 'application/json'
            },
            withCredentials: true
        })
        .then(response => {
            if (response.data) {
                app.notificationPrefsForm.notifyOnBlog = response.data.notifyOnBlog;
                app.notificationPrefsForm.notifyOnComment = response.data.notifyOnComment;
            }
        })
        .catch(error => {
            console.log("Error fetching notification preferences:", error);
        });
    },
    
    updateNotificationPreferences(app) {
        app.notificationPrefsForm.error = null;
        
        app.loading.auth = true;
        axios.put(`${app.baseURL}/users/notification-preferences`, 
            JSON.stringify({
                notifyOnBlog: app.notificationPrefsForm.notifyOnBlog,
                notifyOnComment: app.notificationPrefsForm.notifyOnComment
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
            app.showNotificationPrefsModal = false;
            app.showNotification("success", "Notification preferences updated");
        })
        .catch(error => {
            console.log("Update notification preferences error:", error);
            let message = "Failed to update notification preferences";
            if (error.response && error.response.data && error.response.data.message) {
                message = error.response.data.message;
            }
            app.notificationPrefsForm.error = message;
        })
        .finally(() => {
            app.loading.auth = false;
        });
    },
    
    refreshUserData(app) {
        axios.get(`${app.baseURL}/auth/login`, {
            headers: {
                'Accept': 'application/json'
            },
            withCredentials: true
        })
        .then(response => {
            if (response.data && response.data.status === 'success') {
                // Update phone number data if returned
                if (response.data.phoneNumber) {
                    console.log("Refreshed user data, got phone:", response.data.phoneNumber);
                    app.userPhone = response.data.phoneNumber;
                    app.phoneForm.phone = response.data.phoneNumber;
                    localStorage.setItem('userPhone', response.data.phoneNumber);
                    localStorage.setItem('userId', app.userId);
                }
            }
        })
        .catch(error => {
            console.log("Error refreshing user data:", error);
        });
    }
};

window.UserService = UserService;