// AI services
const AiService = {
    useAI(app) {
        if (!app.authenticated) {
            app.showNotification('error', 'Please log in to use AI features');
            return;
        }
        
        if (!app.verified && !app.mobileVerified) {
            app.showNotification('error', 'Please verify your account to use AI features');
            return;
        }
        
        let content = null;
        
        // If in enhance mode, get content based on current context
        if (app.aiHelper.mode === 'enhance') {
            if (app.showCreateBlogModal) {
                content = app.newBlog.content;
            } else if (app.showEditBlogModal) {
                content = app.editBlog.content;
            }
            
            if (!content) {
                app.aiHelper.error = "No content to enhance";
                return;
            }
        }
        
        app.aiHelper.loading = true;
        app.aiHelper.error = null;
        
        axios.post(`${app.baseURL}/ai/generate`, 
            JSON.stringify({
                prompt: app.aiHelper.prompt,
                mode: app.aiHelper.mode,
                content: content
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
            app.aiHelper.generatedContent = response.data.generatedContent;
            
            // Ask user to use the AI content in blog if editing or creating

            if (app.showCreateBlogModal || app.showEditBlogModal) {
                if (confirm("Would you like to apply the AI-generated content to your blog?")) {
                    this.applyAiContent(app);
                }
            }
        })
        .catch(error => {
            console.error("AI generation error:", error);
            app.aiHelper.error = error.response?.data?.message || "Failed to generate content";
        })
        .finally(() => {
            app.aiHelper.loading = false;
        });
    },
    
    openAiHelperModal(app, mode = 'generate') {
        if (!app.authenticated) {
            app.showNotification('error', 'Please log in to use AI features');
            return;
        }
        
        if (!app.verified && !app.mobileVerified) {
            app.showNotification('error', 'Please verify your account to use AI features');
            return;
        }
        
        app.aiHelper = {
            prompt: "",
            mode: mode,
            loading: false,
            error: null,
            generatedContent: ""
        };
        
        app.showAiHelperModal = true;
    },
    
    applyAiContent(app) {
        if (!app.aiHelper.generatedContent) {
            return;
        }
        
        if (app.showCreateBlogModal) {
            app.newBlog.content = app.aiHelper.generatedContent;
        } else if (app.showEditBlogModal) {
            app.editBlog.content = app.aiHelper.generatedContent;
        }
        
        app.showAiHelperModal = false;
    }
};

window.AiService = AiService;