// Date and text formatters
const Formatters = {
    formatDate(dateString) {
        if (!dateString) return '';
        
        const date = new Date(dateString);
        
        // Add 3 hours to adjust for Atlantic Time
        const adjustedDate = new Date(date.getTime() + (3 * 60 * 60 * 1000));
        
        return adjustedDate.toLocaleDateString() + ' ' + adjustedDate.toLocaleTimeString([], { 
            hour: '2-digit', 
            minute: '2-digit' 
        });
    }
};

window.Formatters = Formatters;