// Blog services
const BlogService = {
    getBlogs(app, options = {}) {
        app.loading.blogs = true;
        
        // Build query parameters
        let params = new URLSearchParams();
        if (options.newerThan) params.append('newerThan', options.newerThan);
        if (options.author) params.append('author', options.author);
        if (options.limit) params.append('limit', options.limit);
        else params.append('limit', app.pagination.limit);
        if (options.offset) params.append('offset', options.offset);
        else params.append('offset', app.pagination.offset);
        
        // For GET requests, only set Accept header, not Content-Type
        axios.get(`${app.baseURL}/blogs?${params.toString()}`, {
            headers: {
                'Accept': 'application/json'
            },
            withCredentials: true
        })
        .then(response => {
            if (options.append) {
                // Append to existing blogs
                app.blogs = [...app.blogs, ...response.data];
            } else {
                app.blogs = response.data;
            }
            
            // Check if we have more blogs to load
            app.pagination.hasMore = response.data.length >= app.pagination.limit;
        })
        .catch(error => {
            console.log("Error fetching blogs:", error);
            app.showNotification("error", "Failed to load blogs");
        })
        .finally(() => {
            app.loading.blogs = false;
        });
    },
    
    loadMoreBlogs(app) {
        app.pagination.offset += app.pagination.limit;
        this.getBlogs(app, {
            offset: app.pagination.offset,
            append: true
        });
    },
    
    getUserBlogs(app) {
        if (!app.authenticated) {
            app.showNotification("error", "Please login first");
            return;
        }
        
        app.loading.blogs = true;
        axios.get(`${app.baseURL}/users/${app.userId}/blogs`, {
            headers: {
                'Accept': 'application/json'
            },
            withCredentials: true
        })
        .then(response => {
            app.userBlogs = response.data;
            app.showUserBlogsModal = true;
        })
        .catch(error => {
            console.log("Error fetching user blogs:", error);
            app.showNotification("error", "Failed to load your blogs");
        })
        .finally(() => {
            app.loading.blogs = false;
        });
    },
    
    getBlogDetails(app, blogId) {
        app.loading.blog = true;
        axios.get(`${app.baseURL}/blogs/${blogId}`, {
            headers: {
                'Accept': 'application/json'
            },
            withCredentials: true
        })
        .then(response => {
            app.selectedBlog = response.data;
            window.CommentService.getComments(app, blogId);
            app.showBlogModal = true;
        })
        .catch(error => {
            console.log("Error fetching blog details:", error);
            app.showNotification("error", "Failed to load blog details");
        })
        .finally(() => {
            app.loading.blog = false;
        });
    },
    
    createBlog(app) {
        if (!app.authenticated) {
            app.showNotification("error", "Please login first");
            return;
        }
        
        if (!app.verified && !app.mobileVerified) {
            app.showNotification("warning", "Please verify your email or phone before creating a blog");
            
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
        
        if (!app.newBlog.title || !app.newBlog.content) {
            app.showNotification("error", "Title and content are required");
            return;
        }
        
        app.loading.blog = true;
        axios.post(`${app.baseURL}/blogs/create`, 
            JSON.stringify({
                title: app.newBlog.title,
                content: app.newBlog.content
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
            app.showNotification("success", "Blog created successfully");
            app.showCreateBlogModal = false;
            app.newBlog = {
                title: "",
                content: ""
            };
            
            // Refresh blogs
            this.getBlogs(app);
            
            // Refresh user blogs if modal is open
            if (app.showUserBlogsModal) {
                this.getUserBlogs(app);
            }
        })
        .catch(error => {
            console.log("Error creating blog:", error);
            let message = "Failed to create blog";
            if (error.response && error.response.data && error.response.data.message) {
                message = error.response.data.message;
            }
            app.showNotification("error", message);
        })
        .finally(() => {
            app.loading.blog = false;
        });
    },
    
    prepareEditBlog(app, blog) {
        if (!app.authenticated || blog.userId !== app.userId) {
            app.showNotification("error", "You don't have permission to edit this blog");
            return;
        }
        
        if (!app.verified && !app.mobileVerified) {
            app.showNotification("warning", "Please verify your email or phone before editing a blog");
            
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
        
        app.editBlog = {
            title: blog.title,
            content: blog.content
        };
        app.showEditBlogModal = true;
        app.showBlogModal = false;
    },
    
    updateBlog(app) {
        if (!app.authenticated) {
            app.showNotification("error", "Please login first");
            return;
        }
        
        if (!app.verified && !app.mobileVerified) {
            app.showNotification("warning", "Please verify your email or phone before updating a blog");
            
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
        
        if (!app.selectedBlog) {
            app.showNotification("error", "No blog selected");
            return;
        }
        
        if (!app.editBlog.title || !app.editBlog.content) {
            app.showNotification("error", "Title and content are required");
            return;
        }
        
        app.loading.blog = true;
        axios.put(`${app.baseURL}/blogs/${app.selectedBlog.blogId}/update`, 
            JSON.stringify({
                title: app.editBlog.title,
                content: app.editBlog.content
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
            // Update selected blog with new data
            app.selectedBlog = response.data;
            
            app.showNotification("success", "Blog updated successfully");
            app.showEditBlogModal = false;
            
            // Refresh blogs
            this.getBlogs(app);
            
            // Refresh user blogs if modal is open
            if (app.showUserBlogsModal) {
                this.getUserBlogs(app);
            }
        })
        .catch(error => {
            console.log("Error updating blog:", error);
            let message = "Failed to update blog";
            if (error.response && error.response.data && error.response.data.message) {
                message = error.response.data.message;
            }
            app.showNotification("error", message);
        })
        .finally(() => {
            app.loading.blog = false;
        });
    },
    
    deleteBlog(app, blog) {
        if (!app.authenticated) {
            app.showNotification("error", "Please login first");
            return;
        }
        
        if (!app.verified && !app.mobileVerified) {
            app.showNotification("warning", "Please verify your email or phone before deleting a blog");
            
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
        
        if (!blog) {
            blog = app.selectedBlog;
        }
        
        if (!blog) {
            app.showNotification("error", "No blog selected");
            return;
        }
        
        if (blog.userId !== app.userId) {
            app.showNotification("error", "You don't have permission to delete this blog");
            return;
        }
        
        app.loading.blog = true;
        axios.delete(`${app.baseURL}/blogs/${blog.blogId}/delete`, {
            headers: {
                'Accept': 'application/json'
            },
            withCredentials: true
        })
        .then(response => {
            app.showNotification("success", "Blog deleted successfully");
            
            // Close modals
            app.showBlogModal = false;
            app.showEditBlogModal = false;
            
            // Refresh blogs
            this.getBlogs(app);
            
            // Refresh user blogs if modal is open
            if (app.showUserBlogsModal) {
                this.getUserBlogs(app);
            }
        })
        .catch(error => {
            console.log("Error deleting blog:", error);
            let message = "Failed to delete blog";
            if (error.response && error.response.data && error.response.data.message) {
                message = error.response.data.message;
            }
            app.showNotification("error", message);
        })
        .finally(() => {
            app.loading.blog = false;
        });
    }
};

window.BlogService = BlogService;