/**
 * Blog Service
 */
const BlogService = {
    
    getBlogs(app, options = {}) {
        app.loading.blogs = true;
        
        let params = new URLSearchParams();
        if (options.newerThan) params.append('newerThan', options.newerThan);
        if (options.author) params.append('author', options.author);
        if (options.limit) params.append('limit', options.limit);
        else params.append('limit', app.pagination.limit);
        if (options.offset) params.append('offset', options.offset);
        else params.append('offset', app.pagination.offset);
        
        axios.get(`${app.baseURL}/blogs-api?${params.toString()}`, {
            headers: {
                'Accept': 'application/json'
            },
            withCredentials: true
        })
        .then(response => {
            if (options.append) {
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
    
    // Get blogs for the current user
    getUserBlogs(app) {
        if (!app.authenticated) {
            app.showNotification("error", "Please login first");
            return;
        }
        
        app.loading.blogs = true;
        axios.get(`${app.baseURL}/users-api/${app.userId}/blogs`, {
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
    
    // Get details for a specific blog
    getBlogDetails(app, blogId) {
        app.loading.blog = true;
        axios.get(`${app.baseURL}/blogs-api/${blogId}`, {
            headers: {
                'Accept': 'application/json'
            },
            withCredentials: true
        })
        .then(response => {
            app.selectedBlog = response.data;
            window.CommentService.getComments(app, blogId);
            app.showUserBlogsModal = false;
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
    

    // Create a new blog post
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
        
        // Validate required fields
        if (!app.newBlog.title || !app.newBlog.content) {
            app.showNotification("error", "Title and content are required");
            return;
        }
        
        // Create the blog post
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
            
            // Close the modal
            app.showCreateBlogModal = false;
            
            app.newBlog = {
                title: "",
                content: ""
            };
            
            if (app.pagination.offset > 0) {
                app.pagination.offset = 0;
                
                // Get first page
                axios.get(`${app.baseURL}/blogs?limit=${app.pagination.limit}&offset=0`, {
                    headers: {
                        'Accept': 'application/json'
                    },
                    withCredentials: true
                })
                .then(firstPageResponse => {
                    app.blogs = firstPageResponse.data;
                    
                    // If we previously had more pages, fetch them recursively
                    this.loadRemainingPages(app, app.pagination.limit);
                });
            } else {
                this.getBlogs(app);
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
    
    // Prepare blog for editing
    prepareEditBlog(app, blog) {
        if (!app.authenticated || blog.userId !== app.userId) {
            app.showNotification("error", "You don't have permission to edit this blog");
            return;
        }
        
        if (!app.verified && !app.mobileVerified) {
            app.showNotification("warning", "Please verify your email or phone before editing a blog");
            return;
        }
        
        app.editBlog = {
            title: blog.title,
            content: blog.content
        };
        
        // Bug Fix - BuG Bash 3: Close both user blogs modal and blog detail modal before showing edit modal
        app.showUserBlogsModal = false;
        app.showBlogModal = false;
        app.showEditBlogModal = true;
    },
    
    // Update an existing blog
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
        
        // Validate required fields and selection
        if (!app.selectedBlog) {
            app.showNotification("error", "No blog selected");
            return;
        }
        
        if (!app.editBlog.title || !app.editBlog.content) {
            app.showNotification("error", "Title and content are required");
            return;
        }
        
        // Update the blog
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
    
    // Delete a blog
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
        
        // Determine which blog to delete
        if (!blog) {
            blog = app.selectedBlog;
        }
        
        if (!blog) {
            app.showNotification("error", "No blog selected");
            return;
        }
        
        // Check ownership
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
            
            app.showBlogModal = false;
            app.showEditBlogModal = false;
            
            this.getBlogs(app);
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
    },
    
    // Recursively load remaining pages when refreshing blog list after a change
    loadRemainingPages(app, pageSize, currentOffset = pageSize) {
        axios.get(`${app.baseURL}/blogs?limit=${pageSize}&offset=${currentOffset}`, {
            headers: {
                'Accept': 'application/json'
            },
            withCredentials: true
        })
        .then(response => {
            if (response.data && response.data.length > 0) {
                app.blogs = [...app.blogs, ...response.data];
                
                app.pagination.hasMore = response.data.length >= pageSize;
                if (response.data.length >= pageSize) {
                    this.loadRemainingPages(app, pageSize, currentOffset + pageSize);
                }
            }
        })
        .catch(error => {
            console.log("Error loading additional pages:", error);
        });
    }
};

window.BlogService = BlogService;