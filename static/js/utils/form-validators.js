// Validatation
const FormValidators = {
    // Validating the email format
    isValidEmail(email) {
        const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return regex.test(email);
    },
    
    // Validating the phone number
    isValidPhone(phone) {
        return phone.startsWith('+') && /^\+\d+$/.test(phone);
    },
    
    // Validating the password strength
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
        
        // Checking minimum length requirement
        if (password.length < 8) {
            result.feedback = 'Password must be at least 8 characters';
            return result;
        }
        
        // Checking if password contain both numbers and letters
        if (!/[A-Za-z]/.test(password) || !/[0-9]/.test(password)) {
            result.feedback = 'Password must contain both letters and numbers';
            return result;
        }
        
        // Adding points for length
        result.score++;
        if (password.length >= 10) result.score++;
        
        // Adding points for complexity
        if (/[A-Z]/.test(password)) result.score++;  // Has uppercase
        if (/[a-z]/.test(password)) result.score++;  // Has lowercase
        if (/[0-9]/.test(password)) result.score++;  // Has numbers
        if (/[^A-Za-z0-9]/.test(password)) result.score++;  // Has special chars
        
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
    
    // Validate form fields
    validateForm(form, rules) {
        const errors = {};
        
        Object.keys(rules).forEach(field => {
            const value = form[field];
            const fieldRules = rules[field];
            
            // Checking required rule
            if (fieldRules.required && (!value || value.trim() === '')) {
                errors[field] = `${fieldRules.label || field} is required`;
                return;
            }
            
            // Only continue validation if we have a value
            if (value) {
                // Checking min length
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
                
                // Checking matching fields (password confirmation)
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