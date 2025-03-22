const NotificationUtils = {
    // Show notification
    show(app, type, message, duration = 5000) {
        app.notification = {
            show: true,
            type: type, 
            message: message
        };
        
        // timeout for the notification
        if (duration > 0) {
            setTimeout(() => {
                app.notification.show = false;
            }, duration);
        }
    },
    
    // Hiding the notification
    hide(app) {
        app.notification.show = false;
    },
    
    showError(app, message, duration = 5000) {
        this.show(app, 'error', message, duration);
    },
    
    showSuccess(app, message, duration = 5000) {
        this.show(app, 'success', message, duration);
    },
    
    showWarning(app, message, duration = 5000) {
        this.show(app, 'warning', message, duration);
    },
    
    showInfo(app, message, duration = 5000) {
        this.show(app, 'info', message, duration);
    }
};

window.NotificationUtils = NotificationUtils;