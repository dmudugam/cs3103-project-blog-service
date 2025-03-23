// Initialize Vue application
document.addEventListener('DOMContentLoaded', function() {
    var app = new Vue({
        el: "#app",
        
        data: {
            baseURL: "https://cs3103.cs.unb.ca:8006",
            authenticated: false,
            verified: false,
            mobileVerified: false,
            hasEmail: false,
            hasPhone: false,
            smsEnabled: false,
            userId: null,
            username: null,
            userEmail: null,
            userPhone: null,
            userType: null,
            
            blogs: [],
            userBlogs: [],
            selectedBlog: null,
            selectedComments: [],
            
            newBlog: {
                title: "",
                content: ""
            },
            editBlog: {
                title: "",
                content: ""
            },
            
            newComment: {
                content: "",
                parentCommentId: null
            },
            
            loginForm: {
                username: "",
                password: "",
                type: "ldap",
                error: null
            },
            
            registerForm: {
                username: "",
                email: "",
                password: "",
                passwordConfirm: "",
                error: null
            },
            
            emailForm: {
                email: "",
                error: null
            },
            
            phoneForm: {
                phone: "",
                error: null
            },
            
            notificationPrefsForm: {
                notifyOnBlog: true,
                notifyOnComment: true,
                error: null
            },
            
            emailOtpForm: {
                otp: "",
                userId: null,
                error: null
            },
            
            mobileOtpForm: {
                otp: "",
                userId: null,
                error: null
            },
            
            pagination: {
                limit: 20,
                offset: 0,
                hasMore: false
            },
            
            // Modals
            showLoginModal: false,
            showRegisterModal: false,
            showEmailModal: false,
            showPhoneModal: false,
            showNotificationPrefsModal: false,
            showBlogModal: false,
            showEditBlogModal: false,
            showCreateBlogModal: false,
            showUserBlogsModal: false,
            showCommentForm: false,
            showEmailOtpModal: false,
            showMobileOtpModal: false,
            showForgotPasswordModal: false,
            showResetPasswordModal: false,
            
            // Notifications and alerts
            notification: {
                show: false,
                type: "", // success, error, info, warning
                message: ""
            },
            
            // Loading states
            loading: {
                blogs: false,
                blog: false,
                comments: false,
                auth: false,
                verification: false
            },
            
            passwordStrength: {
                score: 0,
                feedback: ''
            },
            
            aiHelper: {
                prompt: "",
                mode: "generate", // 'generate' or 'enhance'
                loading: false,
                error: null,
                generatedContent: ""
            },
            showAiHelperModal: false,
            
            forgotPasswordForm: {
                email: "",
                otp: "",
                password: "",
                passwordConfirm: "",
                username: "",
                otpSent: false,
                otpVerified: false,
                error: null,
                success: null
            },
            resetPasswordForm: {
                token: null,
                username: "",
                password: "",
                passwordConfirm: "",
                verified: false,
                error: null,
                success: null
            },
            appReady: false // Add this flag
        },
        
        computed: {
            // Returns true if the user is verified by either email or mobile
            isVerified() {
                return this.verified || this.mobileVerified;
            },
            
            passwordStrengthClass() {
                if (!this.registerForm.password) return '';
                if (this.passwordStrength.score === 0) return '';
                if (this.passwordStrength.score < 2) return 'weak';
                if (this.passwordStrength.score < 4) return 'medium';
                return 'strong';
            }
        },
        
        created() {
            // First check auth, then set appReady to true, and handle any errors
            this.checkAuth()
                .then(() => {
                    this.appReady = true;
                })
                .catch(() => {
                    // Still set appReady to true even on auth failure
                    this.appReady = true;
                });
            this.getBlogs();
            
            // Check for password reset token in URL
            const urlParams = new URLSearchParams(window.location.search);
            const resetToken = urlParams.get('token');
            if (resetToken) {
                this.openResetPasswordModal(resetToken);
                
                // Remove the token from the URL
                window.history.replaceState({}, document.title, window.location.pathname);
            }
        },
        
        methods: {
            // Authentication Methods
            checkAuth() {
                return window.AuthService.checkAuth(this);
            },
            
            login() {
                window.AuthService.login(this);
            },
            
            register() {
                window.AuthService.register(this);
            },
            
            logout() {
                window.AuthService.logout(this);
            },
            
            // Blog Methods
            getBlogs(options = {}) {
                window.BlogService.getBlogs(this, options);
            },
            
            loadMoreBlogs() {
                window.BlogService.loadMoreBlogs(this);
            },
            
            getUserBlogs() {
                window.BlogService.getUserBlogs(this);
            },
            
            getBlogDetails(blogId) {
                window.BlogService.getBlogDetails(this, blogId);
            },
            
            createBlog() {
                window.BlogService.createBlog(this);
            },
            
            prepareEditBlog(blog) {
                window.BlogService.prepareEditBlog(this, blog);
            },
            
            updateBlog() {
                window.BlogService.updateBlog(this);
            },
            
            deleteBlog(blog) {
                window.BlogService.deleteBlog(this, blog);
            },
            
            // Comment Methods
            getComments(blogId) {
                window.CommentService.getComments(this, blogId);
            },
            
            createComment() {
                window.CommentService.createComment(this, {
                    content: this.newComment.content,
                    parentCommentId: this.newComment.parentCommentId
                });
            },
            
            replyToComment(commentId) {
                window.CommentService.replyToComment(this, commentId);
            },
            
            deleteComment(commentId) {
                window.CommentService.deleteComment(this, commentId);
            },
            
            // User Methods
            updateEmail() {
                window.UserService.updateEmail(this);
            },
            
            updatePhone() {
                window.UserService.updatePhone(this);
            },
            
            getNotificationPreferences() {
                window.UserService.getNotificationPreferences(this);
            },
            
            updateNotificationPreferences() {
                window.UserService.updateNotificationPreferences(this);
            },
            
            // Verification Methods 
            requestEmailVerification() {
                window.AuthService.requestEmailVerification(this);
            },
            
            verifyEmailOTP() {
                window.AuthService.verifyEmailOTP(this);
            },
            
            requestMobileVerification() {
                window.AuthService.requestMobileVerification(this);
            },
            
            verifyMobileOTP() {
                window.AuthService.verifyMobileOTP(this);
            },
            
            // Password Reset Methods
            requestPasswordReset() {
                window.AuthService.requestPasswordReset(this);
            },
            
            verifyResetOTP() {
                window.AuthService.verifyResetOTP(this);
            },
            
            resetPassword() {
                window.AuthService.resetPassword(this);
            },
            
            // AI Methods
            useAI() {
                window.AiService.useAI(this);
            },
            
            openAiHelperModal(mode = 'generate') {
                window.AiService.openAiHelperModal(this, mode);
            },
            
            applyAiContent() {
                window.AiService.applyAiContent(this);
            },
            
            // Helper Methods 
            showNotification(type, message) {
                window.NotificationUtils.show(this, type, message);
            },
            
            formatDate(dateString) {
                return window.Formatters.formatDate(dateString);
            },
            
            // Modal Control Methods
            openLoginModal(type = null) {
                this.resetForms();
                if (type) {
                    this.loginForm.type = type;
                }
                this.showLoginModal = true;
            },
            
            openRegisterModal() {
                this.resetForms();
                this.showRegisterModal = true;
            },
            
            openEmailModal(errorMessage = null) {
                // Ignore if it is an event object
                if (errorMessage && errorMessage instanceof Event) {
                    errorMessage = null;
                }
                
                // If user already has an email, fill the form already
                if (this.hasEmail && this.userEmail) {
                    this.emailForm.email = this.userEmail;
                } else {
                    this.emailForm.email = "";
                }
                
                // Set error message
                this.emailForm.error = errorMessage;
                this.showEmailModal = true;
            },
            
            openPhoneModal() {
                // clear phine form error
                this.phoneForm.error = null;
                
                // prefill the user phone
                if (this.userPhone) {
                    this.phoneForm.phone = this.userPhone;
                } else {
                    // try to get saved phone number
                    const savedUserId = localStorage.getItem('userId');
                    const savedPhone = localStorage.getItem('userPhone');
                    
                    if (savedUserId && savedUserId == this.userId && savedPhone) {
                        console.log("Using saved phone number for form:", savedPhone);
                        this.phoneForm.phone = savedPhone;
                        this.userPhone = savedPhone;
                    } else {
                        // no phone saved
                        this.phoneForm.phone = "";
                    }
                }
                
                this.showPhoneModal = true;
            },
            
            openNotificationPrefsModal() {
                if (!this.authenticated) {
                    this.showNotification("error", "Please login first");
                    return;
                }
                
                if (!this.hasEmail) {
                    this.showNotification("warning", "Please add an email address first");
                    this.openEmailModal();
                    return;
                }
                
                // Get current notification preferences
                this.getNotificationPreferences();
                
                this.notificationPrefsForm.error = null;
                this.showNotificationPrefsModal = true;
            },
            
            openCreateBlogModal() {
                if (!this.authenticated) {
                    this.showNotification("error", "Please login first");
                    return;
                }
                
                if (!this.verified && !this.mobileVerified) {
                    if (!this.hasEmail && !this.hasPhone) {
                        if (this.smsEnabled) {
                            this.showNotification("warning", "Please add and verify your email or phone before creating a blog");
                            this.openEmailModal();
                        } else {
                            this.showNotification("warning", "Please add and verify your email before creating a blog");
                            this.openEmailModal();
                        }
                    } else if (this.hasEmail && !this.verified) {
                        this.showNotification("warning", "Please verify your email before creating a blog");
                        this.requestEmailVerification();
                    } else if (this.hasPhone && !this.mobileVerified && this.smsEnabled) {
                        this.showNotification("warning", "Please verify your phone before creating a blog");
                        this.requestMobileVerification();
                    }
                    return;
                }
                
                this.resetForms();
                this.showCreateBlogModal = true;
            },
            
            openForgotPasswordModal() {
                console.log("openForgotPasswordModal called");
                
                // Close all modals
                this.closeModals();
                
                // Reset the form state
                this.forgotPasswordForm = {
                    email: "",
                    otp: "",
                    password: "",
                    passwordConfirm: "",
                    username: "",
                    otpSent: false,
                    otpVerified: false,
                    error: null,
                    success: null
                };
                
                // Force a DOM update before showing the new modal
                this.$nextTick(() => {
                    console.log("Opening forgot password modal...");
                    this.showForgotPasswordModal = true;
                    
                    // Debug after setting
                    console.log("After setting showForgotPasswordModal:", this.showForgotPasswordModal);
                    
                    // Fallback: If the modal still no show
                    setTimeout(() => {
                        if (!this.showForgotPasswordModal) {
                            console.log("Forcing modal open with timeout");
                            this.showForgotPasswordModal = true;
                            this.debugModalState();
                        }
                    }, 100);
                });
                
                this.debugModalState();
            },
            
            forceOpenForgotPassword() {
                console.log("Force opening forgot password modal");
                // Close all modals
                this.closeModals();
                // Reset the form
                this.forgotPasswordForm = {
                    email: "",
                    otp: "",
                    password: "",
                    passwordConfirm: "",
                    username: "",
                    otpSent: false,
                    otpVerified: false,
                    error: null,
                    success: null
                };
                // Open the forgot password modal
                this.showForgotPasswordModal = true;
            },
            
            openResetPasswordModal(token) {
                this.resetPasswordForm = {
                    token: token,
                    username: "",
                    password: "",
                    passwordConfirm: "",
                    verified: false,
                    error: null,
                    success: null
                };
                this.showResetPasswordModal = true;
            },
            
            closeModals() {
                this.showLoginModal = false;
                this.showRegisterModal = false;
                this.showEmailModal = false;
                this.showPhoneModal = false;
                this.showNotificationPrefsModal = false;
                this.showBlogModal = false;
                this.showEditBlogModal = false;
                this.showCreateBlogModal = false;
                this.showUserBlogsModal = false;
                this.showCommentForm = false;
                this.showEmailOtpModal = false;
                this.showMobileOtpModal = false;
                this.showForgotPasswordModal = false;
                this.showResetPasswordModal = false;
            },
            
            resetForms() {
                this.loginForm = {
                    username: "",
                    password: "",
                    type: "ldap",
                    error: null
                };
                
                this.registerForm = {
                    username: "",
                    email: "",
                    password: "",
                    passwordConfirm: "",
                    error: null
                };
                
                this.emailForm = {
                    email: "",
                    error: null
                };
                
                this.phoneForm = {
                    phone: "",
                    error: null
                };
                
                this.notificationPrefsForm = {
                    notifyOnBlog: true,
                    notifyOnComment: true,
                    error: null
                };
                
                this.newBlog = {
                    title: "",
                    content: ""
                };
                
                this.editBlog = {
                    title: "",
                    content: ""
                };
                
                this.newComment = {
                    content: "",
                    parentCommentId: null
                };
                
                this.emailOtpForm = {
                    otp: "",
                    userId: null,
                    error: null
                };
                
                this.mobileOtpForm = {
                    otp: "",
                    userId: null,
                    error: null
                };
    
                this.forgotPasswordForm = {
                    email: "",
                    otp: "",
                    password: "",
                    passwordConfirm: "",
                    username: "",
                    otpSent: false,
                    otpVerified: false,
                    error: null,
                    success: null
                };
    
                this.resetPasswordForm = {
                    token: null,
                    username: "",
                    password: "",
                    passwordConfirm: "",
                    verified: false,
                    error: null,
                    success: null
                };
            },
            
            updatePasswordStrength() {
                const password = this.registerForm.password;
                const result = window.FormValidators.validatePassword(password);
                this.passwordStrength.score = result.score || 0;
                this.passwordStrength.feedback = result.feedback || '';
            },
            
            debugModalState() {
                console.log("Modal States:", {
                    showLoginModal: this.showLoginModal,
                    showForgotPasswordModal: this.showForgotPasswordModal,
                    showRegisterModal: this.showRegisterModal,
                    showEmailModal: this.showEmailModal,
                    showPhoneModal: this.showPhoneModal,
                    showNotificationPrefsModal: this.showNotificationPrefsModal,
                    showBlogModal: this.showBlogModal,
                    showEditBlogModal: this.showEditBlogModal,
                    showCreateBlogModal: this.showCreateBlogModal,
                    showUserBlogsModal: this.showUserBlogsModal,
                    showEmailOtpModal: this.showEmailOtpModal,
                    showMobileOtpModal: this.showMobileOtpModal,
                    showResetPasswordModal: this.showResetPasswordModal
                });
            }
        }
    });
});