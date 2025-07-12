-- DATABASE CONFIGURATION

-- CLEANUP
DROP TABLE IF EXISTS comments CASCADE;
DROP TABLE IF EXISTS blogs CASCADE;
DROP TABLE IF EXISTS verification CASCADE;
DROP TABLE IF EXISTS mobile_verification CASCADE;
DROP TABLE IF EXISTS verified_users CASCADE;
DROP TABLE IF EXISTS mobile_verified_users CASCADE;
DROP TABLE IF EXISTS notification_preferences CASCADE;
DROP TABLE IF EXISTS password_reset CASCADE;
DROP TABLE IF EXISTS pending_email_changes CASCADE;
DROP TABLE IF EXISTS pending_phone_changes CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- Create user type enum
CREATE TYPE user_type AS ENUM ('ldap', 'local');

-- TABLE DEFINITIONS

-- User tables
CREATE TABLE users(
    userId SERIAL PRIMARY KEY,
    user_type user_type NOT NULL DEFAULT 'ldap',
    username VARCHAR(25) NOT NULL UNIQUE,
    email VARCHAR(100) UNIQUE NULL,
    password_hash VARCHAR(128) NULL,
    password_salt VARCHAR(32) NULL,
    phone_number VARCHAR(20) NULL,
    joinDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Verification related tables
CREATE TABLE verified_users(
    userId INTEGER NOT NULL PRIMARY KEY,
    verifiedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (userId) REFERENCES users(userId) ON DELETE CASCADE
);

CREATE TABLE mobile_verified_users(
    userId INTEGER NOT NULL PRIMARY KEY,
    verifiedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (userId) REFERENCES users(userId) ON DELETE CASCADE
);

CREATE TABLE verification(
    userId INTEGER NOT NULL PRIMARY KEY,
    verificationToken VARCHAR(64) NOT NULL UNIQUE,
    createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expiresAt TIMESTAMP DEFAULT (CURRENT_TIMESTAMP + INTERVAL '15 minutes'),
    FOREIGN KEY (userId) REFERENCES users(userId) ON DELETE CASCADE
);

CREATE TABLE mobile_verification(
    userId INTEGER NOT NULL PRIMARY KEY,
    verificationToken VARCHAR(6) NOT NULL,
    createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expiresAt TIMESTAMP DEFAULT (CURRENT_TIMESTAMP + INTERVAL '15 minutes'),
    FOREIGN KEY (userId) REFERENCES users(userId) ON DELETE CASCADE
);

-- Pending verification changes
CREATE TABLE pending_email_changes (
    userId INTEGER PRIMARY KEY,
    newEmail VARCHAR(100) NOT NULL,
    createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expiresAt TIMESTAMP DEFAULT (CURRENT_TIMESTAMP + INTERVAL '24 hours'),
    FOREIGN KEY (userId) REFERENCES users(userId) ON DELETE CASCADE
);

CREATE TABLE pending_phone_changes (
    userId INTEGER PRIMARY KEY,
    newPhone VARCHAR(20) NOT NULL,
    createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expiresAt TIMESTAMP DEFAULT (CURRENT_TIMESTAMP + INTERVAL '24 hours'),
    FOREIGN KEY (userId) REFERENCES users(userId) ON DELETE CASCADE
);

-- User preferences
CREATE TABLE notification_preferences(
    userId INTEGER NOT NULL PRIMARY KEY,
    notifyOnBlog BOOLEAN DEFAULT TRUE,
    notifyOnComment BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (userId) REFERENCES users(userId) ON DELETE CASCADE
);

-- Password reset
CREATE TABLE password_reset (
    userId INTEGER NOT NULL PRIMARY KEY,
    resetOTP VARCHAR(6) NOT NULL UNIQUE,
    createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expiresAt TIMESTAMP DEFAULT (CURRENT_TIMESTAMP + INTERVAL '1 hour'),
    FOREIGN KEY (userId) REFERENCES users(userId) ON DELETE CASCADE
);

-- Content tables
CREATE TABLE blogs(
    blogId SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    dateCreated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    userId INTEGER NOT NULL,
    FOREIGN KEY (userId) REFERENCES users(userId) ON DELETE CASCADE
);

CREATE TABLE comments(
    commentId SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    dateCreated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    blogId INTEGER NOT NULL,
    userId INTEGER NOT NULL,
    parentCommentId INTEGER NULL,
    FOREIGN KEY (userId) REFERENCES users(userId) ON DELETE CASCADE,
    FOREIGN KEY (blogId) REFERENCES blogs(blogId) ON DELETE CASCADE,
    FOREIGN KEY (parentCommentId) REFERENCES comments(commentId) ON DELETE CASCADE
);

-- USER MANAGEMENT PROCEDURES

-- User retrieval procedures
CREATE OR REPLACE FUNCTION getUserById(userIdIn INTEGER)
RETURNS TABLE(
    userId INTEGER, 
    username VARCHAR(25),
    email VARCHAR(100),
    phone_number VARCHAR(20),
    joinDate TIMESTAMP,
    user_type user_type,
    verified BOOLEAN,
    mobile_verified BOOLEAN
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        u.userId, 
        u.username, 
        u.email, 
        u.phone_number,
        u.joinDate,
        u.user_type,
        CASE WHEN vu.userId IS NOT NULL THEN TRUE ELSE FALSE END AS verified,
        CASE WHEN mvu.userId IS NOT NULL THEN TRUE ELSE FALSE END AS mobile_verified
    FROM users u
    LEFT JOIN verified_users vu ON u.userId = vu.userId
    LEFT JOIN mobile_verified_users mvu ON u.userId = mvu.userId
    WHERE u.userId = userIdIn;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION getUserByUsername(usernameIn VARCHAR(25))
RETURNS TABLE(
    userId INTEGER, 
    username VARCHAR(25),
    email VARCHAR(100),
    phone_number VARCHAR(20),
    joinDate TIMESTAMP,
    user_type user_type,
    verified BOOLEAN,
    mobile_verified BOOLEAN
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        u.userId, 
        u.username, 
        u.email, 
        u.phone_number,
        u.joinDate,
        u.user_type,
        CASE WHEN vu.userId IS NOT NULL THEN TRUE ELSE FALSE END AS verified,
        CASE WHEN mvu.userId IS NOT NULL THEN TRUE ELSE FALSE END AS mobile_verified
    FROM users u
    LEFT JOIN verified_users vu ON u.userId = vu.userId
    LEFT JOIN mobile_verified_users mvu ON u.userId = mvu.userId
    WHERE u.username = usernameIn;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION getUserByEmail(emailIn VARCHAR(100))
RETURNS TABLE(
    userId INTEGER, 
    username VARCHAR(25),
    email VARCHAR(100),
    phone_number VARCHAR(20),
    joinDate TIMESTAMP,
    user_type user_type,
    verified BOOLEAN,
    mobile_verified BOOLEAN
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        u.userId, 
        u.username, 
        u.email, 
        u.phone_number,
        u.joinDate,
        u.user_type,
        CASE WHEN vu.userId IS NOT NULL THEN TRUE ELSE FALSE END AS verified,
        CASE WHEN mvu.userId IS NOT NULL THEN TRUE ELSE FALSE END AS mobile_verified
    FROM users u
    LEFT JOIN verified_users vu ON u.userId = vu.userId
    LEFT JOIN mobile_verified_users mvu ON u.userId = mvu.userId
    WHERE u.email = emailIn;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION getUsers(limitIn INTEGER, offsetIn INTEGER)
RETURNS TABLE(
    userId INTEGER, 
    username VARCHAR(25),
    email VARCHAR(100),
    phone_number VARCHAR(20),
    joinDate TIMESTAMP,
    user_type user_type,
    verified BOOLEAN,
    mobile_verified BOOLEAN
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        u.userId, 
        u.username, 
        u.email, 
        u.phone_number,
        u.joinDate,
        u.user_type,
        CASE WHEN vu.userId IS NOT NULL THEN TRUE ELSE FALSE END AS verified,
        CASE WHEN mvu.userId IS NOT NULL THEN TRUE ELSE FALSE END AS mobile_verified
    FROM users u
    LEFT JOIN verified_users vu ON u.userId = vu.userId
    LEFT JOIN mobile_verified_users mvu ON u.userId = mvu.userId
    ORDER BY u.joinDate DESC
    LIMIT limitIn OFFSET offsetIn;
END;
$$ LANGUAGE plpgsql;

-- User creation procedures
CREATE OR REPLACE FUNCTION createLdapUser(usernameIn VARCHAR(25))
RETURNS TABLE(
    userId INTEGER, 
    username VARCHAR(25),
    email VARCHAR(100),
    phone_number VARCHAR(20),
    joinDate TIMESTAMP,
    user_type VARCHAR(4),
    verified BOOLEAN,
    mobile_verified BOOLEAN
) AS $$
DECLARE
    new_id INTEGER;
    rows_affected INTEGER;
BEGIN
    -- Insert if not exists
    INSERT INTO users (username, user_type) 
    VALUES(usernameIn, 'ldap')
    ON CONFLICT (username) DO NOTHING
    RETURNING users.userId INTO new_id;
    
    GET DIAGNOSTICS rows_affected = ROW_COUNT;
    
    -- Insert default notification preferences if this is a new user
    IF rows_affected > 0 THEN
        INSERT INTO notification_preferences (userId)
        VALUES (new_id);
    ELSE
        -- Get the existing user ID if no insert happened
        SELECT userId INTO new_id FROM users WHERE username = usernameIn;
    END IF;
    
    RETURN QUERY
    SELECT 
        u.userId, 
        u.username, 
        u.email, 
        u.phone_number,
        u.joinDate,
        'ldap'::VARCHAR(4) as user_type,
        CASE WHEN vu.userId IS NOT NULL THEN TRUE ELSE FALSE END AS verified,
        CASE WHEN mvu.userId IS NOT NULL THEN TRUE ELSE FALSE END AS mobile_verified
    FROM users u
    LEFT JOIN verified_users vu ON u.userId = vu.userId
    LEFT JOIN mobile_verified_users mvu ON u.userId = mvu.userId
    WHERE u.username = usernameIn;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION createLocalUser(
    usernameIn VARCHAR(25),
    emailIn VARCHAR(100),
    passwordHashIn VARCHAR(128),
    passwordSaltIn VARCHAR(32)
)
RETURNS TABLE(
    userId INTEGER, 
    username VARCHAR(25),
    email VARCHAR(100),
    phone_number VARCHAR(20),
    joinDate TIMESTAMP,
    user_type VARCHAR(5),
    verified BOOLEAN,
    mobile_verified BOOLEAN
) AS $$
DECLARE
    new_id INTEGER;
BEGIN
    INSERT INTO users (username, user_type, email, password_hash, password_salt) 
    VALUES(usernameIn, 'local', emailIn, passwordHashIn, passwordSaltIn)
    RETURNING userId INTO new_id;
    
    -- Insert default notification preferences for the new user
    INSERT INTO notification_preferences (userId)
    VALUES (new_id);
    
    RETURN QUERY
    SELECT 
        u.userId, 
        u.username, 
        u.email, 
        u.phone_number,
        u.joinDate,
        'local'::VARCHAR(5) as user_type,
        CASE WHEN vu.userId IS NOT NULL THEN TRUE ELSE FALSE END AS verified,
        CASE WHEN mvu.userId IS NOT NULL THEN TRUE ELSE FALSE END AS mobile_verified
    FROM users u
    LEFT JOIN verified_users vu ON u.userId = vu.userId
    LEFT JOIN mobile_verified_users mvu ON u.userId = mvu.userId
    WHERE u.userId = new_id;
END;
$$ LANGUAGE plpgsql;

-- User authentication
CREATE OR REPLACE FUNCTION validateLocalUser(usernameIn VARCHAR(25))
RETURNS TABLE(
    userId INTEGER, 
    username VARCHAR(25),
    email VARCHAR(100),
    phone_number VARCHAR(20),
    password_hash VARCHAR(128),
    password_salt VARCHAR(32),
    joinDate TIMESTAMP,
    user_type VARCHAR(5),
    verified BOOLEAN,
    mobile_verified BOOLEAN
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        u.userId, 
        u.username, 
        u.email, 
        u.phone_number,
        u.password_hash,
        u.password_salt,
        u.joinDate,
        'local'::VARCHAR(5) as user_type,
        CASE WHEN vu.userId IS NOT NULL THEN TRUE ELSE FALSE END AS verified,
        CASE WHEN mvu.userId IS NOT NULL THEN TRUE ELSE FALSE END AS mobile_verified
    FROM users u
    LEFT JOIN verified_users vu ON u.userId = vu.userId
    LEFT JOIN mobile_verified_users mvu ON u.userId = mvu.userId
    WHERE u.username = usernameIn AND u.user_type = 'local';
END;
$$ LANGUAGE plpgsql;

-- User profile update procedures
CREATE OR REPLACE FUNCTION updateUserEmail(
    userIdIn int,
    emailIn varchar(100)
)
RETURNS TABLE(
    userId INTEGER, 
    username VARCHAR(25),
    email VARCHAR(100),
    phone_number VARCHAR(20),
    joinDate TIMESTAMP,
    user_type user_type,
    verified BOOLEAN,
    mobile_verified BOOLEAN,
    pendingVerification BOOLEAN
) AS $$
BEGIN
    -- Store new email in pending changes table instead of updating directly
    INSERT INTO pending_email_changes (userId, newEmail)
    VALUES (userIdIn, emailIn)
    ON DUPLICATE KEY UPDATE 
        newEmail = emailIn,
        createdAt = CURRENT_TIMESTAMP,
        expiresAt = (CURRENT_TIMESTAMP + INTERVAL '24 hours');
    
    -- Return user information without changing verification status
    RETURN QUERY
    SELECT 
        u.userId, 
        u.username, 
        u.email, 
        emailIn as pendingEmail,
        u.phone_number,
        u.joinDate,
        u.user_type,
        CASE WHEN vu.userId IS NOT NULL THEN TRUE ELSE FALSE END AS verified,
        CASE WHEN mvu.userId IS NOT NULL THEN TRUE ELSE FALSE END AS mobile_verified,
        TRUE as pendingVerification
    FROM users u
    LEFT JOIN verified_users vu ON u.userId = vu.userId
    LEFT JOIN mobile_verified_users mvu ON u.userId = mvu.userId
    WHERE u.userId = userIdIn;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION updateUserPhone(
    userIdIn int,
    phoneIn varchar(20)
)
RETURNS TABLE(
    userId INTEGER, 
    username VARCHAR(25),
    email VARCHAR(100),
    phone_number VARCHAR(20),
    joinDate TIMESTAMP,
    user_type user_type,
    verified BOOLEAN,
    mobile_verified BOOLEAN,
    pendingVerification BOOLEAN
) AS $$
BEGIN
    -- Store new phone in pending changes instead of updating directly
    INSERT INTO pending_phone_changes (userId, newPhone)
    VALUES (userIdIn, phoneIn)
    ON DUPLICATE KEY UPDATE 
        newPhone = phoneIn,
        createdAt = CURRENT_TIMESTAMP,
        expiresAt = (CURRENT_TIMESTAMP + INTERVAL '24 hours');
    
    -- Return user information without changing verification status
    RETURN QUERY
    SELECT 
        u.userId, 
        u.username, 
        u.email, 
        u.phone_number,
        phoneIn as pendingPhone,
        u.joinDate,
        u.user_type,
        CASE WHEN vu.userId IS NOT NULL THEN TRUE ELSE FALSE END AS verified,
        CASE WHEN mvu.userId IS NOT NULL THEN TRUE ELSE FALSE END AS mobile_verified,
        TRUE as pendingVerification
    FROM users u
    LEFT JOIN verified_users vu ON u.userId = vu.userId
    LEFT JOIN mobile_verified_users mvu ON u.userId = mvu.userId
    WHERE u.userId = userIdIn;
END;
$$ LANGUAGE plpgsql;

-- USER NOTIFICATION PREFERENCES

CREATE OR REPLACE FUNCTION getUserNotificationPreferences(userIdIn INT)
RETURNS TABLE(
    userId INTEGER,
    notifyOnBlog BOOLEAN,
    notifyOnComment BOOLEAN
) AS $$
BEGIN
    -- Insert default preferences if none exist
    INSERT INTO notification_preferences (userId)
    VALUES (userIdIn)
    ON CONFLICT (userId) DO NOTHING;
    
    RETURN QUERY
    SELECT * FROM notification_preferences
    WHERE userId = userIdIn;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION updateNotificationPreferences(
    userIdIn INT,
    notifyOnBlogIn BOOLEAN,
    notifyOnCommentIn BOOLEAN
)
RETURNS TABLE(
    userId INTEGER,
    notifyOnBlog BOOLEAN,
    notifyOnComment BOOLEAN
) AS $$
BEGIN
    INSERT INTO notification_preferences (userId, notifyOnBlog, notifyOnComment)
    VALUES (userIdIn, notifyOnBlogIn, notifyOnCommentIn)
    ON CONFLICT (userId) DO UPDATE SET
        notifyOnBlog = notifyOnBlogIn,
        notifyOnComment = notifyOnCommentIn;
        
    RETURN QUERY
    SELECT * FROM notification_preferences
    WHERE userId = userIdIn;
END;
$$ LANGUAGE plpgsql;

-- EMAIL VERIFICATION PROCEDURES

CREATE OR REPLACE FUNCTION createVerification(
    userIdIn int,
    verificationTokenIn varchar(64)
)
RETURNS VOID AS $$
BEGIN
    -- Delete any existing verification for this user
    DELETE FROM verification WHERE userId = userIdIn;
    
    -- Create new verification
    INSERT INTO verification (userId, verificationToken) 
    VALUES(userIdIn, verificationTokenIn);
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION isUserVerified(userIdIn INT)
RETURNS TABLE(verified BIGINT) AS $$
BEGIN
    RETURN QUERY
    SELECT COUNT(*) as verified 
    FROM verified_users 
    WHERE userId = userIdIn;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION verifyOTP(
    userIdIn INT,
    otpIn VARCHAR(64)
)
RETURNS TABLE(
    success BOOLEAN,
    userId INTEGER,
    updated_email VARCHAR(100)
) AS $$
DECLARE
    foundUserId INT;
    pendingEmail VARCHAR(100);
BEGIN
    -- Verify the token is valid
    SELECT v.userId INTO foundUserId
    FROM verification v
    WHERE v.userId = userIdIn
    AND v.verificationToken = otpIn
    AND v.expiresAt > NOW()
    LIMIT 1;
    
    -- If user found and token is valid
    IF foundUserId IS NOT NULL THEN
        -- Get the pending email change if any
        SELECT newEmail INTO pendingEmail
        FROM pending_email_changes
        WHERE userId = userIdIn;
        
        -- Apply the email change if there is one
        IF pendingEmail IS NOT NULL THEN
            UPDATE users
            SET email = pendingEmail
            WHERE userId = userIdIn;
            
            -- Delete the pending change
            DELETE FROM pending_email_changes
            WHERE userId = userIdIn;
        END IF;
        
        -- Add to verified users
        INSERT INTO verified_users (userId)
        VALUES (foundUserId)
        ON CONFLICT (userId) DO NOTHING;
        
        -- Remove verification record
        DELETE FROM verification 
        WHERE userId = userIdIn;
        
        RETURN QUERY
        SELECT TRUE as success, foundUserId, pendingEmail;
    ELSE
        RETURN QUERY
        SELECT FALSE as success, NULL::INTEGER as userId, NULL::VARCHAR(100) as updated_email;
    END IF;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION getPendingEmail(userIdIn INT)
RETURNS TABLE(newEmail VARCHAR(100)) AS $$
BEGIN
    RETURN QUERY
    SELECT pec.newEmail FROM pending_email_changes pec WHERE userId = userIdIn;
END;
$$ LANGUAGE plpgsql;

-- MOBILE VERIFICATION PROCEDURES

CREATE OR REPLACE FUNCTION createMobileVerification(
    userIdIn int,
    verificationTokenIn varchar(6)
)
RETURNS VOID AS $$
BEGIN
    -- Delete any existing verification for this user
    DELETE FROM mobile_verification WHERE userId = userIdIn;
    
    -- Create new verification
    INSERT INTO mobile_verification (userId, verificationToken) 
    VALUES(userIdIn, verificationTokenIn);
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION isMobileVerified(userIdIn INT)
RETURNS TABLE(verified BIGINT) AS $$
BEGIN
    RETURN QUERY
    SELECT COUNT(*) as verified 
    FROM mobile_verified_users 
    WHERE userId = userIdIn;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION verifyMobileOTP(
    userIdIn INT,
    otpIn VARCHAR(6)
)
RETURNS TABLE(
    success BOOLEAN,
    userId INTEGER,
    updated_phone VARCHAR(20)
) AS $$
DECLARE
    foundUserId INT;
    pendingPhone VARCHAR(20);
BEGIN
    -- Verify the token is valid
    SELECT v.userId INTO foundUserId
    FROM mobile_verification v
    WHERE v.userId = userIdIn
    AND v.verificationToken = otpIn
    AND v.expiresAt > NOW()
    LIMIT 1;
    
    IF foundUserId IS NOT NULL THEN
        -- Get the pending phone change
        SELECT newPhone INTO pendingPhone
        FROM pending_phone_changes
        WHERE userId = userIdIn;
        
        -- Apply the phone change if a pending phone was found
        IF pendingPhone IS NOT NULL THEN
            -- Update the user's phone number
            UPDATE users
            SET phone_number = pendingPhone
            WHERE userId = userIdIn;
            
            -- Remove the pending change
            DELETE FROM pending_phone_changes
            WHERE userId = userIdIn;
        END IF;
        
        -- Mark as verified regardless of whether there was a pending phone
        INSERT INTO mobile_verified_users (userId)
        VALUES (foundUserId)
        ON CONFLICT (userId) DO NOTHING;
        
        -- Remove verification record
        DELETE FROM mobile_verification 
        WHERE userId = userIdIn;
        
        RETURN QUERY
        SELECT TRUE as success, foundUserId as userId, pendingPhone;
    ELSE
        RETURN QUERY
        SELECT FALSE as success, NULL::INTEGER as userId, NULL::VARCHAR(20) as updated_phone;
    END IF;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION getPendingPhone(userIdIn INT)
RETURNS TABLE(newPhone VARCHAR(20)) AS $$
BEGIN
    RETURN QUERY
    SELECT ppc.newPhone FROM pending_phone_changes ppc WHERE userId = userIdIn;
END;
$$ LANGUAGE plpgsql;

-- PASSWORD RESET PROCEDURES

CREATE OR REPLACE FUNCTION createPasswordResetOTP(
    userIdIn int,
    otpIn varchar(6)
)
RETURNS TABLE(
    userId INTEGER,
    username VARCHAR(25),
    email VARCHAR(100)
) AS $$
BEGIN
    -- Delete any existing reset OTP for this user
    DELETE FROM password_reset WHERE userId = userIdIn;
    
    -- Create new reset entry with the OTP
    INSERT INTO password_reset (userId, resetOTP)
    VALUES(userIdIn, otpIn);
    
    -- Return user info
    RETURN QUERY
    SELECT u.userId, u.username, u.email
    FROM users u
    WHERE u.userId = userIdIn;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION verifyResetOTP(otpIn varchar(6))
RETURNS TABLE(
    userId INTEGER,
    username VARCHAR(25),
    email VARCHAR(100)
) AS $$
BEGIN
    RETURN QUERY
    SELECT u.userId, u.username, u.email 
    FROM password_reset pr
    JOIN users u ON pr.userId = u.userId
    WHERE pr.resetOTP = otpIn
    AND pr.expiresAt > NOW();
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION resetPasswordWithOTP(
    otpIn varchar(6),
    passwordHashIn VARCHAR(128),
    passwordSaltIn VARCHAR(32)
)
RETURNS TABLE(
    success BOOLEAN,
    userId INTEGER
) AS $$
DECLARE
    user_id INT;
BEGIN
    -- Get user ID from reset OTP
    SELECT pr.userId INTO user_id
    FROM password_reset pr
    WHERE pr.resetOTP = otpIn
    AND pr.expiresAt > NOW();
    
    -- If valid OTP found
    IF user_id IS NOT NULL THEN
        -- Update password
        UPDATE users
        SET password_hash = passwordHashIn,
            password_salt = passwordSaltIn
        WHERE userId = user_id;
        
        -- Remove reset record
        DELETE FROM password_reset WHERE userId = user_id;
        
        RETURN QUERY
        SELECT TRUE as success, user_id;
    ELSE
        RETURN QUERY
        SELECT FALSE as success, NULL::INTEGER as userId;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- BLOG MANAGEMENT PROCEDURES

CREATE OR REPLACE FUNCTION getBlogs(
    newerThanIn DATE,
    authorIn VARCHAR(25),
    limitIn INT,
    offsetIn INT
)
RETURNS TABLE(
    blogId INTEGER,
    title TEXT,
    content TEXT,
    date TIMESTAMP,
    userId INTEGER,
    author VARCHAR(25)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        b.blogId,
        b.title,
        b.content,
        b.dateCreated as date,
        b.userId,
        u.username as author
    FROM blogs b
    JOIN users u ON b.userId = u.userId
    WHERE 
        (newerThanIn IS NULL OR b.dateCreated >= newerThanIn)
        AND (authorIn IS NULL OR u.username = authorIn)
    ORDER BY b.dateCreated DESC
    LIMIT limitIn OFFSET offsetIn;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION getBlogById(blogIdIn INT)
RETURNS TABLE(
    blogId INTEGER,
    title TEXT,
    content TEXT,
    date TIMESTAMP,
    userId INTEGER,
    author VARCHAR(25)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        b.blogId,
        b.title,
        b.content,
        b.dateCreated as date,
        b.userId,
        u.username as author
    FROM blogs b
    JOIN users u ON b.userId = u.userId
    WHERE b.blogId = blogIdIn;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION getBlogsByUserId(
    userIdIn INT,
    newerThanIn DATE,
    limitIn INT,
    offsetIn INT
)
RETURNS TABLE(
    blogId INTEGER,
    title TEXT,
    content TEXT,
    date TIMESTAMP,
    userId INTEGER,
    author VARCHAR(25)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        b.blogId,
        b.title,
        b.content,
        b.dateCreated as date,
        b.userId,
        u.username as author
    FROM blogs b
    JOIN users u ON b.userId = u.userId
    WHERE 
        b.userId = userIdIn
        AND (newerThanIn IS NULL OR b.dateCreated >= newerThanIn)
    ORDER BY b.dateCreated DESC
    LIMIT limitIn OFFSET offsetIn;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION createBlog(
    titleIn TEXT,
    contentIn TEXT,
    userIdIn int
)
RETURNS TABLE(
    blogId INTEGER,
    title TEXT,
    content TEXT,
    date TIMESTAMP,
    userId INTEGER,
    author VARCHAR(25)
) AS $$
DECLARE
    new_blog_id INTEGER;
BEGIN
    INSERT INTO blogs (title, content, userId) 
    VALUES(titleIn, contentIn, userIdIn)
    RETURNING blogs.blogId INTO new_blog_id;
    
    RETURN QUERY
    SELECT 
        b.blogId,
        b.title,
        b.content,
        b.dateCreated as date,
        b.userId,
        u.username as author
    FROM blogs b
    JOIN users u ON b.userId = u.userId
    WHERE b.blogId = new_blog_id;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION updateBlog(
    blogIdIn INT,
    titleIn TEXT,
    contentIn TEXT,
    userIdIn INT
)
RETURNS TABLE(
    blogId INTEGER,
    title TEXT,
    content TEXT,
    date TIMESTAMP,
    userId INTEGER,
    author VARCHAR(25)
) AS $$
BEGIN
    UPDATE blogs 
    SET 
        title = titleIn,
        content = contentIn
    WHERE blogId = blogIdIn AND userId = userIdIn;
    
    RETURN QUERY
    SELECT 
        b.blogId,
        b.title,
        b.content,
        b.dateCreated as date,
        b.userId,
        u.username as author
    FROM blogs b
    JOIN users u ON b.userId = u.userId
    WHERE b.blogId = blogIdIn;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION deleteBlog(
    blogIdIn INT,
    userIdIn INT
)
RETURNS TABLE(affectedRows BIGINT) AS $$
DECLARE
    rows_affected INTEGER;
BEGIN
    DELETE FROM blogs WHERE blogId = blogIdIn AND userId = userIdIn;
    GET DIAGNOSTICS rows_affected = ROW_COUNT;
    
    RETURN QUERY
    SELECT rows_affected::BIGINT;
END;
$$ LANGUAGE plpgsql;

-- COMMENT MANAGEMENT PROCEDURES

CREATE OR REPLACE FUNCTION getCommentsByBlog(
    blogIdIn INT,
    newerThanIn DATE,
    limitIn INT,
    offsetIn INT
)
RETURNS TABLE(
    commentId INTEGER,
    content TEXT,
    date TIMESTAMP,
    blogId INTEGER,
    userId INTEGER,
    parentCommentId INTEGER,
    author VARCHAR(25)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        c.commentId,
        c.content,
        c.dateCreated as date,
        c.blogId,
        c.userId,
        c.parentCommentId,
        u.username as author
    FROM comments c
    JOIN users u ON c.userId = u.userId
    WHERE 
        c.blogId = blogIdIn
        AND (newerThanIn IS NULL OR c.dateCreated >= newerThanIn)
    ORDER BY 
        COALESCE(c.parentCommentId, c.commentId),
        c.dateCreated
    LIMIT limitIn OFFSET offsetIn;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION getCommentById(commentIdIn INT)
RETURNS TABLE(
    commentId INTEGER,
    content TEXT,
    date TIMESTAMP,
    blogId INTEGER,
    userId INTEGER,
    parentCommentId INTEGER,
    author VARCHAR(25)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        c.commentId,
        c.content,
        c.dateCreated as date,
        c.blogId,
        c.userId,
        c.parentCommentId,
        u.username as author
    FROM comments c
    JOIN users u ON c.userId = u.userId
    WHERE c.commentId = commentIdIn;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION getCommentReplies(commentIdIn INT)
RETURNS TABLE(
    commentId INTEGER,
    content TEXT,
    date TIMESTAMP,
    blogId INTEGER,
    userId INTEGER,
    parentCommentId INTEGER,
    author VARCHAR(25)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        c.commentId,
        c.content,
        c.dateCreated as date,
        c.blogId,
        c.userId,
        c.parentCommentId,
        u.username as author
    FROM comments c
    JOIN users u ON c.userId = u.userId
    WHERE c.parentCommentId = commentIdIn
    ORDER BY c.dateCreated;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION createComment(
    contentIn TEXT,
    userIdIn INT,
    blogIdIn INT,
    parentCommentIdIn INT
)
RETURNS TABLE(
    commentId INTEGER,
    content TEXT,
    date TIMESTAMP,
    blogId INTEGER,
    userId INTEGER,
    parentCommentId INTEGER,
    author VARCHAR(25)
) AS $$
DECLARE
    new_comment_id INTEGER;
BEGIN
    INSERT INTO comments (content, userId, blogId, parentCommentId) 
    VALUES(contentIn, userIdIn, blogIdIn, parentCommentIdIn)
    RETURNING commentId INTO new_comment_id;
    
    RETURN QUERY
    SELECT 
        c.commentId,
        c.content,
        c.dateCreated as date,
        c.blogId,
        c.userId,
        c.parentCommentId,
        u.username as author
    FROM comments c
    JOIN users u ON c.userId = u.userId
    WHERE c.commentId = new_comment_id;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION updateComment(
    commentIdIn INT,
    contentIn TEXT,
    userIdIn INT
)
RETURNS TABLE(
    commentId INTEGER,
    content TEXT,
    date TIMESTAMP,
    blogId INTEGER,
    userId INTEGER,
    parentCommentId INTEGER,
    author VARCHAR(25)
) AS $$
BEGIN
    UPDATE comments 
    SET content = contentIn
    WHERE commentId = commentIdIn AND userId = userIdIn;
    
    RETURN QUERY
    SELECT 
        c.commentId,
        c.content,
        c.dateCreated as date,
        c.blogId,
        c.userId,
        c.parentCommentId,
        u.username as author
    FROM comments c
    JOIN users u ON c.userId = u.userId
    WHERE c.commentId = commentIdIn;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION deleteComment(
    commentIdIn INT,
    userIdIn INT
)
RETURNS TABLE(affectedRows BIGINT) AS $$
DECLARE
    rows_affected INTEGER;
BEGIN
    DELETE FROM comments WHERE commentId = commentIdIn AND userId = userIdIn;
    GET DIAGNOSTICS rows_affected = ROW_COUNT;
    
    RETURN QUERY
    SELECT rows_affected::BIGINT;
END;
$$ LANGUAGE plpgsql;