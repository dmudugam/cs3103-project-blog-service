// Date and text formatters
const Formatters = {
    formatDate(dateString) {
        if (!dateString) return '';
        
        // Creating a date object from the string
        const date = new Date(dateString);
        
        // Add 3 hours to adjust for Atlantic Time (UTC-4)
        // The server appears to be storing times in UTC-7 or similar
        const adjustedDate = new Date(date.getTime() + (3 * 60 * 60 * 1000));
        
        return adjustedDate.toLocaleDateString() + ' ' + adjustedDate.toLocaleTimeString([], { 
            hour: '2-digit', 
            minute: '2-digit' 
        });
    }
};

window.Formatters = Formatters;