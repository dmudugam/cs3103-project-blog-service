const CommentService = {
    getComments(app, blogId) {
        app.loading.comments = true;
        // For GET requests, only set Accept header, not Content-Type
        axios.get(`${app.baseURL}/blogs/${blogId}/comments`, {
            headers: {
                'Accept': 'application/json'
            },
            withCredentials: true
        })
        .then(response => {
            app.selectedComments = response.data;
        })
        .catch(error => {
            console.log("Error fetching comments:", error);
            app.showNotification("error", "Failed to load comments");
        })
        .finally(() => {
            app.loading.comments = false;
        });
    },
    
    createComment(app, commentData) {
        if (!app.authenticated) {
            app.showNotification("error", "Please login first");
            return;
        }
        
        if (!app.verified && !app.mobileVerified) {
            app.showBlogModal = false;
            
            if (app.hasEmail && !app.verified) {
                window.AuthService.requestEmailVerification(app);
            } else if (app.hasPhone && !app.mobileVerified && app.smsEnabled) {
                window.AuthService.requestMobileVerification(app);
            } else if (!app.hasEmail && !app.hasPhone) {
                if (app.smsEnabled) {
                    app.showNotification("info", "Add an email or phone number for verification");
                    app.showBlogModal = false;
                    app.openEmailModal("Please add and verify your email to comment on blogs");
                } else {
                    app.showBlogModal = false;
                    app.openEmailModal("Please add and verify your email to comment on blogs");
                }
            }
            return;
        }
        
        if (!app.selectedBlog) {
            app.showNotification("error", "No blog selected");
            return;
        }
        
        if (!commentData.content) {
            app.showNotification("error", "Comment content is required");
            return;
        }
        
        app.loading.comments = true;
        
        // Check if this is a direct comment or a reply
        const endpoint = commentData.parentCommentId
            ? `${app.baseURL}/comments/${commentData.parentCommentId}/replies/create`
            : `${app.baseURL}/blogs/${app.selectedBlog.blogId}/comments/create`;
        
        axios.post(endpoint, 
            JSON.stringify({
                content: commentData.content.trim()
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
            app.showNotification("success", "Comment added successfully");
            
            // Clear the comment form
            if (app.$refs.blogDetail) {
                app.$refs.blogDetail.showCommentForm = false;
                app.$refs.blogDetail.newComment = {
                    content: "",
                    parentCommentId: null
                };
            }
            
            // Also clear the app-level form
            app.showCommentForm = false;
            app.newComment = {
                content: "",
                parentCommentId: null
            };
            
            // Refresh comments
            this.getComments(app, app.selectedBlog.blogId);
        })
        .catch(error => {
            console.log("Error creating comment:", error);
            let message = "Failed to add comment";
            if (error.response && error.response.data && error.response.data.message) {
                message = error.response.data.message;
            }
            app.showNotification("error", message);
        })
        .finally(() => {
            app.loading.comments = false;
        });
    },
    
    replyToComment(app, commentId) {
        if (!app.verified && !app.mobileVerified) {
            
            if (app.hasEmail && !app.verified) {
                window.AuthService.requestEmailVerification(app);
            } else if (app.hasPhone && !app.mobileVerified && app.smsEnabled) {
                window.AuthService.requestMobileVerification(app);
            } else if (!app.hasEmail && !app.hasPhone) {
                if (app.smsEnabled) {
                    app.showBlogModal = false;
                    app.openEmailModal("Please add and verify your email to reply to comments");
                } else {
                    app.openEmailModal("Please add and verify your email to reply to comments");
                }
            }
            return;
        }
        
        app.newComment.parentCommentId = commentId;
        app.showCommentForm = true;
    },
    
    deleteComment(app, commentId) {
        if (!app.authenticated) {
            app.showNotification("error", "Please login first");
            return;
        }
        
        if (!app.verified && !app.mobileVerified) {
            app.showNotification("warning", "Please verify your email or phone before deleting comments");
            
            if (app.hasEmail && !app.verified) {
                window.AuthService.requestEmailVerification(app);
            } else if (app.hasPhone && !app.mobileVerified && app.smsEnabled) {
                window.AuthService.requestMobileVerification(app);
            } else if (!app.hasEmail && !app.hasPhone) {
                if (app.smsEnabled) {
                    app.showNotification("info", "Add an email or phone number for verification");
                    app.openEmailModal();
                } else {
                    app.openEmailModal();
                }
            }
            return;
        }
        
        if (!confirm("Are you sure you want to delete this comment?")) {
            return;
        }
        
        app.loading.comments = true;
        axios.delete(`${app.baseURL}/comments/${commentId}/delete`, {
            headers: {
                'Accept': 'application/json'
            },
            withCredentials: true
        })
        .then(response => {
            app.showNotification("success", "Comment deleted successfully");
            
            // Refresh comments
            this.getComments(app, app.selectedBlog.blogId);
        })
        .catch(error => {
            console.log("Error deleting comment:", error);
            let message = "Failed to delete comment";
            if (error.response && error.response.data && error.response.data.message) {
                message = error.response.data.message;
            }
            app.showNotification("error", message);
        })
        .finally(() => {
            app.loading.comments = false;
        });
    }
};

window.CommentService = CommentService;