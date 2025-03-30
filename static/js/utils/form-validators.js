// Validatation
const FormValidators = {
    // Validating the email
    isValidEmail(email) {
        const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return regex.test(email);
    },

    isValidPhone(phone) {
        return phone.startsWith('+') && /^\+\d+$/.test(phone);
    },
    
    validatePassword(password) {
        let result = {
            isValid: false,
            score: 0,
            feedback: ''
        };
        
        // If no password was inputted or the length of the password is less than 4
        if (!password || password.length < 4) {
            result.feedback = 'Password is too short';
            return result;
        }

        if (password.length < 8) {
            result.feedback = 'Password must be at least 8 characters';
            return result;
        }
        
        if (!/[A-Za-z]/.test(password) || !/[0-9]/.test(password)) {
            result.feedback = 'Password must contain both letters and numbers';
            return result;
        }
        
        result.score++;
        if (password.length >= 10) result.score++;
        
        // Adding points for complexity
        if (/[A-Z]/.test(password)) result.score++;
        if (/[a-z]/.test(password)) result.score++;
        if (/[0-9]/.test(password)) result.score++;
        if (/[^A-Za-z0-9]/.test(password)) result.score++;
        
        if (result.score < 3) {
            result.feedback = 'Weak - Consider using a stronger password';
        } else if (result.score < 5) {
            result.feedback = 'Medium - Decent password strength';
        } else {
            result.feedback = 'Strong - Excellent password strength';
        }
        
        result.isValid = true;
        return result;
    },
    
    validateForm(form, rules) {
        const errors = {};
        
        Object.keys(rules).forEach(field => {
            const value = form[field];
            const fieldRules = rules[field];
            
            if (fieldRules.required && (!value || value.trim() === '')) {
                errors[field] = `${fieldRules.label || field} is required`;
                return;
            }
            
            if (value) {
                if (fieldRules.minLength && value.length < fieldRules.minLength) {
                    errors[field] = `${fieldRules.label || field} must be at least ${fieldRules.minLength} characters`;
                    return;
                }
                
                // Checking email format
                if (fieldRules.email && !this.isValidEmail(value)) {
                    errors[field] = `Please enter a valid email address`;
                    return;
                }
                
                // Checking phone format
                if (fieldRules.phone && !this.isValidPhone(value)) {
                    errors[field] = `Phone number must be in E.164 format (e.g., +1234567890)`;
                    return;
                }
                
                // Checking password strength
                if (fieldRules.password) {
                    const passwordResult = this.validatePassword(value);
                    if (!passwordResult.isValid) {
                        errors[field] = passwordResult.feedback;
                        return;
                    }
                }
                
                // Checking matching fields
                if (fieldRules.match && form[fieldRules.match] !== value) {
                    errors[field] = `${fieldRules.label || field} does not match ${fieldRules.matchLabel || fieldRules.match}`;
                    return;
                }
            }
        });
        
        return {
            isValid: Object.keys(errors).length === 0,
            errors
        };
    }
};

window.FormValidators = FormValidators;