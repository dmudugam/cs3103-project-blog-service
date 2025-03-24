-- ===================================================================
-- DATABASE CONFIGURATION
-- ===================================================================
SET NAMES utf8mb4;
ALTER DATABASE CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci;

-- ===================================================================
-- CLEANUP (DROP EXISTING TABLES)
-- ===================================================================
DROP TABLE IF EXISTS comments;
DROP TABLE IF EXISTS blogs;
DROP TABLE IF EXISTS verification;
DROP TABLE IF EXISTS mobile_verification;
DROP TABLE IF EXISTS verified_users;
DROP TABLE IF EXISTS mobile_verified_users;
DROP TABLE IF EXISTS notification_preferences;
DROP TABLE IF EXISTS password_reset;
DROP TABLE IF EXISTS pending_email_changes;
DROP TABLE IF EXISTS pending_phone_changes;
DROP TABLE IF EXISTS users;

-- ===================================================================
-- TABLE DEFINITIONS
-- ===================================================================

-- Core user table
CREATE TABLE users(
    userId int auto_increment,
    user_type ENUM('ldap', 'local') NOT NULL DEFAULT 'ldap',
    username varchar(25) not null,
    email varchar(100) null,
    password_hash VARCHAR(128) NULL,
    password_salt VARCHAR(32) NULL,
    phone_number VARCHAR(20) NULL,
    joinDate timestamp default current_timestamp,
    primary key(userId),
    unique key(username),
    unique key(email)
);

-- Verification related tables
CREATE TABLE verified_users(
    userId int not null,
    verifiedAt timestamp default current_timestamp,
    primary key(userId),
    constraint fk_verified_user foreign key(userId) references users(userId) on delete cascade on update restrict
);

CREATE TABLE mobile_verified_users(
    userId int not null,
    verifiedAt timestamp default current_timestamp,
    primary key(userId),
    constraint fk_mobile_verified_user foreign key(userId) references users(userId) on delete cascade on update restrict
);

CREATE TABLE verification(
    userId int not null,
    verificationToken varchar(64) not null,
    createdAt timestamp default current_timestamp,
    expiresAt timestamp default (current_timestamp + interval 15 minute),
    primary key(userId),
    unique key(verificationToken),
    constraint fk_verification_user foreign key(userId) references users(userId) on delete cascade on update restrict
);

CREATE TABLE mobile_verification(
    userId int not null,
    verificationToken varchar(6) not null,
    createdAt timestamp default current_timestamp,
    expiresAt timestamp default (current_timestamp + interval 15 minute),
    primary key(userId),
    constraint fk_mobile_verification_user foreign key(userId) references users(userId) on delete cascade on update restrict
);

-- Pending verification changes
CREATE TABLE pending_email_changes (
    userId INT PRIMARY KEY,
    newEmail VARCHAR(100) NOT NULL,
    createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expiresAt TIMESTAMP DEFAULT (CURRENT_TIMESTAMP + INTERVAL 24 HOUR),
    FOREIGN KEY (userId) REFERENCES users(userId) ON DELETE CASCADE
);

CREATE TABLE pending_phone_changes (
    userId INT PRIMARY KEY,
    newPhone VARCHAR(20) NOT NULL,
    createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expiresAt TIMESTAMP DEFAULT (CURRENT_TIMESTAMP + INTERVAL 24 HOUR),
    FOREIGN KEY (userId) REFERENCES users(userId) ON DELETE CASCADE
);

-- User preferences
CREATE TABLE notification_preferences(
    userId int not null,
    notifyOnBlog boolean default true,
    notifyOnComment boolean default true,
    primary key(userId),
    constraint fk_notification_prefs foreign key(userId) references users(userId) on delete cascade on update restrict
);

-- Password reset
CREATE TABLE password_reset (
    userId int not null,
    resetOTP varchar(6) not null,
    createdAt timestamp default current_timestamp,
    expiresAt timestamp default (current_timestamp + interval 1 hour),
    primary key(userId),
    unique key(resetOTP),
    constraint fk_password_reset_user foreign key(userId) references users(userId) on delete cascade on update restrict
);

-- Content tables
CREATE TABLE blogs(
    blogId int auto_increment,
    title longtext not null,
    content longtext not null,
    dateCreated timestamp default current_timestamp,
    userId int not null,
    primary key(blogId),
    constraint fk_blog_creator foreign key(userId) references users(userId) on delete cascade on update restrict
);

CREATE TABLE comments(
    commentId int auto_increment,
    content longtext not null,
    dateCreated timestamp default current_timestamp,
    blogId int not null,
    userId int not null,
    parentCommentId int,
    primary key(commentId),
    constraint fk_comment_creator foreign key(userId) references users(userId) on delete cascade on update restrict, 
    constraint fk_blog foreign key(blogId) references blogs(blogId) on delete cascade on update restrict,
    constraint fk_parent_comment foreign key(parentCommentId) references comments(commentId) on delete cascade on update restrict
);

-- ===================================================================
-- USER MANAGEMENT PROCEDURES
-- ===================================================================

-- User retrieval procedures
DROP PROCEDURE IF EXISTS getUserById;
DELIMITER //
CREATE PROCEDURE getUserById(
    userIdIn INT
)
BEGIN
    SELECT 
        u.userId, 
        u.username, 
        u.email, 
        u.phone_number,
        u.joinDate,
        u.user_type,
        IF(vu.userId IS NOT NULL, TRUE, FALSE) AS verified,
        IF(mvu.userId IS NOT NULL, TRUE, FALSE) AS mobile_verified
    FROM users u
    LEFT JOIN verified_users vu ON u.userId = vu.userId
    LEFT JOIN mobile_verified_users mvu ON u.userId = mvu.userId
    WHERE u.userId = userIdIn;
END //
DELIMITER ;

DROP PROCEDURE IF EXISTS getUserByUsername;
DELIMITER //
CREATE PROCEDURE getUserByUsername(
    usernameIn varchar(25)
)
BEGIN
    SELECT 
        u.userId, 
        u.username, 
        u.email, 
        u.phone_number,
        u.joinDate,
        u.user_type,
        IF(vu.userId IS NOT NULL, TRUE, FALSE) AS verified,
        IF(mvu.userId IS NOT NULL, TRUE, FALSE) AS mobile_verified
    FROM users u
    LEFT JOIN verified_users vu ON u.userId = vu.userId
    LEFT JOIN mobile_verified_users mvu ON u.userId = mvu.userId
    WHERE u.username = usernameIn;
END //
DELIMITER ;

DROP PROCEDURE IF EXISTS getUserByEmail;
DELIMITER //
CREATE PROCEDURE getUserByEmail(
    emailIn varchar(100)
)
BEGIN
    SELECT 
        u.userId, 
        u.username, 
        u.email, 
        u.phone_number,
        u.joinDate,
        u.user_type,
        IF(vu.userId IS NOT NULL, TRUE, FALSE) AS verified,
        IF(mvu.userId IS NOT NULL, TRUE, FALSE) AS mobile_verified
    FROM users u
    LEFT JOIN verified_users vu ON u.userId = vu.userId
    LEFT JOIN mobile_verified_users mvu ON u.userId = mvu.userId
    WHERE u.email = emailIn;
END //
DELIMITER ;

DROP PROCEDURE IF EXISTS getUsers;
DELIMITER //
CREATE PROCEDURE getUsers(
    limitIn INT,
    offsetIn INT
)
BEGIN
    SELECT 
        u.userId, 
        u.username, 
        u.email, 
        u.phone_number,
        u.joinDate,
        u.user_type,
        IF(vu.userId IS NOT NULL, TRUE, FALSE) AS verified,
        IF(mvu.userId IS NOT NULL, TRUE, FALSE) AS mobile_verified
    FROM users u
    LEFT JOIN verified_users vu ON u.userId = vu.userId
    LEFT JOIN mobile_verified_users mvu ON u.userId = mvu.userId
    ORDER BY u.joinDate DESC
    LIMIT limitIn OFFSET offsetIn;
END //
DELIMITER ;

-- User creation procedures
DROP PROCEDURE IF EXISTS createLdapUser;
DELIMITER //
CREATE PROCEDURE createLdapUser(
    usernameIn varchar(25)
)
BEGIN
    INSERT IGNORE INTO users (username, user_type) 
    VALUES(usernameIn, 'ldap');
    
    -- Insert default notification preferences if this is a new user
    IF ROW_COUNT() > 0 THEN
        INSERT INTO notification_preferences (userId)
        VALUES (LAST_INSERT_ID());
    END IF;
    
    SELECT 
        u.userId, 
        u.username, 
        u.email, 
        u.phone_number,
        u.joinDate,
        'ldap' as user_type,
        IF(vu.userId IS NOT NULL, TRUE, FALSE) AS verified,
        IF(mvu.userId IS NOT NULL, TRUE, FALSE) AS mobile_verified
    FROM users u
    LEFT JOIN verified_users vu ON u.userId = vu.userId
    LEFT JOIN mobile_verified_users mvu ON u.userId = mvu.userId
    WHERE u.username = usernameIn;
END //
DELIMITER ;

DROP PROCEDURE IF EXISTS createLocalUser;
DELIMITER //
CREATE PROCEDURE createLocalUser(
    usernameIn VARCHAR(25),
    emailIn VARCHAR(100),
    passwordHashIn VARCHAR(128),
    passwordSaltIn VARCHAR(32)
)
BEGIN
    INSERT INTO users (username, user_type, email, password_hash, password_salt) 
    VALUES(usernameIn, 'local', emailIn, passwordHashIn, passwordSaltIn);
    
    -- Insert default notification preferences for the new user
    INSERT INTO notification_preferences (userId)
    VALUES (LAST_INSERT_ID());
    
    SELECT 
        u.userId, 
        u.username, 
        u.email, 
        u.phone_number,
        u.joinDate,
        'local' as user_type,
        IF(vu.userId IS NOT NULL, TRUE, FALSE) AS verified,
        IF(mvu.userId IS NOT NULL, TRUE, FALSE) AS mobile_verified
    FROM users u
    LEFT JOIN verified_users vu ON u.userId = vu.userId
    LEFT JOIN mobile_verified_users mvu ON u.userId = mvu.userId
    WHERE u.userId = LAST_INSERT_ID();
END //
DELIMITER ;

-- User authentication
DROP PROCEDURE IF EXISTS validateLocalUser;
DELIMITER //
CREATE PROCEDURE validateLocalUser(
    usernameIn VARCHAR(25)
)
BEGIN
    SELECT 
        u.userId, 
        u.username, 
        u.email, 
        u.phone_number,
        u.password_hash,
        u.password_salt,
        u.joinDate,
        'local' as user_type,
        IF(vu.userId IS NOT NULL, TRUE, FALSE) AS verified,
        IF(mvu.userId IS NOT NULL, TRUE, FALSE) AS mobile_verified
    FROM users u
    LEFT JOIN verified_users vu ON u.userId = vu.userId
    LEFT JOIN mobile_verified_users mvu ON u.userId = mvu.userId
    WHERE u.username = usernameIn AND u.user_type = 'local';
END //
DELIMITER ;

-- User profile update procedures
DROP PROCEDURE IF EXISTS updateUserEmail;
DELIMITER //
CREATE PROCEDURE updateUserEmail(
    userIdIn int,
    emailIn varchar(100)
)
BEGIN
    -- Store new email in pending changes table instead of updating directly
    INSERT INTO pending_email_changes (userId, newEmail)
    VALUES (userIdIn, emailIn)
    ON DUPLICATE KEY UPDATE 
        newEmail = emailIn,
        createdAt = CURRENT_TIMESTAMP,
        expiresAt = (CURRENT_TIMESTAMP + INTERVAL 24 HOUR);
    
    -- Return user information without changing verification status
    SELECT 
        u.userId, 
        u.username, 
        u.email, 
        emailIn as pendingEmail,
        u.phone_number,
        u.joinDate,
        u.user_type,
        IF(vu.userId IS NOT NULL, TRUE, FALSE) AS verified,
        IF(mvu.userId IS NOT NULL, TRUE, FALSE) AS mobile_verified,
        TRUE as pendingVerification
    FROM users u
    LEFT JOIN verified_users vu ON u.userId = vu.userId
    LEFT JOIN mobile_verified_users mvu ON u.userId = mvu.userId
    WHERE u.userId = userIdIn;
END //
DELIMITER ;

DROP PROCEDURE IF EXISTS updateUserPhone;
DELIMITER //
CREATE PROCEDURE updateUserPhone(
    userIdIn int,
    phoneIn varchar(20)
)
BEGIN
    -- Store new phone in pending changes instead of updating directly
    INSERT INTO pending_phone_changes (userId, newPhone)
    VALUES (userIdIn, phoneIn)
    ON DUPLICATE KEY UPDATE 
        newPhone = phoneIn,
        createdAt = CURRENT_TIMESTAMP,
        expiresAt = (CURRENT_TIMESTAMP + INTERVAL 24 HOUR);
    
    -- Return user information without changing verification status
    SELECT 
        u.userId, 
        u.username, 
        u.email, 
        u.phone_number,
        phoneIn as pendingPhone,
        u.joinDate,
        u.user_type,
        IF(vu.userId IS NOT NULL, TRUE, FALSE) AS verified,
        IF(mvu.userId IS NOT NULL, TRUE, FALSE) AS mobile_verified,
        TRUE as pendingVerification
    FROM users u
    LEFT JOIN verified_users vu ON u.userId = vu.userId
    LEFT JOIN mobile_verified_users mvu ON u.userId = mvu.userId
    WHERE u.userId = userIdIn;
END //
DELIMITER ;

-- ===================================================================
-- USER NOTIFICATION PREFERENCES
-- ===================================================================

DROP PROCEDURE IF EXISTS getUserNotificationPreferences;
DELIMITER //
CREATE PROCEDURE getUserNotificationPreferences(
    userIdIn INT
)
BEGIN
    -- Insert default preferences if none exist
    INSERT IGNORE INTO notification_preferences (userId)
    VALUES (userIdIn);
    
    SELECT * FROM notification_preferences
    WHERE userId = userIdIn;
END //
DELIMITER ;

DROP PROCEDURE IF EXISTS updateNotificationPreferences;
DELIMITER //
CREATE PROCEDURE updateNotificationPreferences(
    userIdIn INT,
    notifyOnBlogIn BOOLEAN,
    notifyOnCommentIn BOOLEAN
)
BEGIN
    INSERT INTO notification_preferences (userId, notifyOnBlog, notifyOnComment)
    VALUES (userIdIn, notifyOnBlogIn, notifyOnCommentIn)
    ON DUPLICATE KEY UPDATE
        notifyOnBlog = notifyOnBlogIn,
        notifyOnComment = notifyOnCommentIn;
        
    SELECT * FROM notification_preferences
    WHERE userId = userIdIn;
END //
DELIMITER ;

-- ===================================================================
-- EMAIL VERIFICATION PROCEDURES
-- ===================================================================

DROP PROCEDURE IF EXISTS createVerification;
DELIMITER //
CREATE PROCEDURE createVerification(
    userIdIn int,
    verificationTokenIn varchar(64)
)
BEGIN
    -- Delete any existing verification for this user
    DELETE FROM verification WHERE userId = userIdIn;
    
    -- Create new verification
    INSERT INTO verification (userId, verificationToken) 
    VALUES(userIdIn, verificationTokenIn);
END //
DELIMITER ;

DROP PROCEDURE IF EXISTS isUserVerified;
DELIMITER //
CREATE PROCEDURE isUserVerified(userIdIn INT)
BEGIN
    SELECT COUNT(*) as verified 
    FROM verified_users 
    WHERE userId = userIdIn;
END //
DELIMITER ;

DROP PROCEDURE IF EXISTS verifyOTP;
DELIMITER //
CREATE PROCEDURE verifyOTP(
    userIdIn INT,
    otpIn VARCHAR(64)
)
BEGIN
    DECLARE userId INT;
    DECLARE newEmail VARCHAR(100);
    
    SELECT v.userId INTO userId
    FROM verification v
    WHERE v.userId = userIdIn
    AND v.verificationToken = otpIn
    AND v.expiresAt > NOW();
    
    -- If user found and token is valid
    IF userId IS NOT NULL THEN
        -- Get the pending email change if any
        SELECT newEmail INTO newEmail
        FROM pending_email_changes
        WHERE userId = userIdIn;
        
        -- Apply the email change if there is one
        IF newEmail IS NOT NULL THEN
            UPDATE users
            SET email = newEmail
            WHERE userId = userIdIn;
            
            -- Delete the pending change
            DELETE FROM pending_email_changes
            WHERE userId = userIdIn;
        END IF;
        
        -- Add to verified users
        INSERT IGNORE INTO verified_users (userId)
        VALUES (userId);
        
        -- Remove verification record
        DELETE FROM verification 
        WHERE userId = userIdIn;
        
        SELECT TRUE as success, userId;
    ELSE
        SELECT FALSE as success, NULL as userId;
    END IF;
END //
DELIMITER ;

DROP PROCEDURE IF EXISTS getPendingEmail;
DELIMITER //
CREATE PROCEDURE getPendingEmail(
    userIdIn INT
)
BEGIN
    SELECT newEmail FROM pending_email_changes WHERE userId = userIdIn;
END //
DELIMITER ;

-- ===================================================================
-- MOBILE VERIFICATION PROCEDURES
-- ===================================================================

DROP PROCEDURE IF EXISTS createMobileVerification;
DELIMITER //
CREATE PROCEDURE createMobileVerification(
    userIdIn int,
    verificationTokenIn varchar(6)
)
BEGIN
    -- Delete any existing verification for this user
    DELETE FROM mobile_verification WHERE userId = userIdIn;
    
    -- Create new verification
    INSERT INTO mobile_verification (userId, verificationToken) 
    VALUES(userIdIn, verificationTokenIn);
END //
DELIMITER ;

DROP PROCEDURE IF EXISTS isMobileVerified;
DELIMITER //
CREATE PROCEDURE isMobileVerified(userIdIn INT)
BEGIN
    SELECT COUNT(*) as verified 
    FROM mobile_verified_users 
    WHERE userId = userIdIn;
END //
DELIMITER ;

DROP PROCEDURE IF EXISTS verifyMobileOTP;
DELIMITER //
CREATE PROCEDURE verifyMobileOTP(
    userIdIn INT,
    otpIn VARCHAR(6)
)
BEGIN
    DECLARE userId INT;
    DECLARE newPhone VARCHAR(20);
    
    SELECT v.userId INTO userId
    FROM mobile_verification v
    WHERE v.userId = userIdIn
    AND v.verificationToken = otpIn
    AND v.expiresAt > NOW();
    
    -- If user found and token is valid
    IF userId IS NOT NULL THEN
        -- Get the pending phone change if any
        SELECT newPhone INTO newPhone
        FROM pending_phone_changes
        WHERE userId = userIdIn;
        
        -- Apply the phone change if there is one
        IF newPhone IS NOT NULL THEN
            UPDATE users
            SET phone_number = newPhone
            WHERE userId = userIdIn;
            
            -- Delete the pending change
            DELETE FROM pending_phone_changes
            WHERE userId = userIdIn;
        END IF;
        
        -- Add to mobile verified users
        INSERT IGNORE INTO mobile_verified_users (userId)
        VALUES (userId);
        
        -- Remove verification record
        DELETE FROM mobile_verification 
        WHERE userId = userIdIn;
        
        SELECT TRUE as success, userId;
    ELSE
        SELECT FALSE as success, NULL as userId;
    END IF;
END //
DELIMITER ;

DROP PROCEDURE IF EXISTS getPendingPhone;
DELIMITER //
CREATE PROCEDURE getPendingPhone(
    userIdIn INT
)
BEGIN
    SELECT newPhone as phone FROM pending_phone_changes WHERE userId = userIdIn;
END //
DELIMITER ;

-- ===================================================================
-- PASSWORD RESET PROCEDURES
-- ===================================================================

DROP PROCEDURE IF EXISTS createPasswordResetOTP;
DELIMITER //
CREATE PROCEDURE createPasswordResetOTP(
    userIdIn int,
    otpIn varchar(6)
)
BEGIN
    -- Delete any existing reset OTP for this user
    DELETE FROM password_reset WHERE userId = userIdIn;
    
    -- Create new reset entry with the OTP
    INSERT INTO password_reset (userId, resetOTP)
    VALUES(userIdIn, otpIn);
    
    -- Return user info
    SELECT u.userId, u.username, u.email
    FROM users u
    WHERE u.userId = userIdIn;
END //
DELIMITER ;

DROP PROCEDURE IF EXISTS verifyResetOTP;
DELIMITER //
CREATE PROCEDURE verifyResetOTP(
    otpIn varchar(6)
)
BEGIN
    SELECT u.userId, u.username, u.email 
    FROM password_reset pr
    JOIN users u ON pr.userId = u.userId
    WHERE pr.resetOTP = otpIn
    AND pr.expiresAt > NOW();
END //
DELIMITER ;

DROP PROCEDURE IF EXISTS resetPasswordWithOTP;
DELIMITER //
CREATE PROCEDURE resetPasswordWithOTP(
    otpIn varchar(6),
    passwordHashIn VARCHAR(128),
    passwordSaltIn VARCHAR(32)
)
BEGIN
    DECLARE userId INT;
    
    -- Get user ID from reset OTP
    SELECT pr.userId INTO userId
    FROM password_reset pr
    WHERE pr.resetOTP = otpIn
    AND pr.expiresAt > NOW();
    
    -- If valid OTP found
    IF userId IS NOT NULL THEN
        -- Update password
        UPDATE users
        SET password_hash = passwordHashIn,
            password_salt = passwordSaltIn
        WHERE userId = userId;
        
        -- Remove reset record
        DELETE FROM password_reset WHERE userId = userId;
        
        SELECT TRUE as success, userId;
    ELSE
        SELECT FALSE as success, NULL as userId;
    END IF;
END //
DELIMITER ;

-- ===================================================================
-- BLOG MANAGEMENT PROCEDURES
-- ===================================================================

DROP PROCEDURE IF EXISTS getBlogs;
DELIMITER //
CREATE PROCEDURE getBlogs(
    newerThanIn DATE,
    authorIn VARCHAR(25),
    limitIn INT,
    offsetIn INT
)
BEGIN
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
END //
DELIMITER ;

DROP PROCEDURE IF EXISTS getBlogById;
DELIMITER //
CREATE PROCEDURE getBlogById(
    blogIdIn INT
)
BEGIN
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
END //
DELIMITER ;

DROP PROCEDURE IF EXISTS getBlogsByUserId;
DELIMITER //
CREATE PROCEDURE getBlogsByUserId(
    userIdIn INT,
    newerThanIn DATE,
    limitIn INT,
    offsetIn INT
)
BEGIN
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
END //
DELIMITER ;

DROP PROCEDURE IF EXISTS createBlog;
DELIMITER //
CREATE PROCEDURE createBlog(
    titleIn VARCHAR(50),
    contentIn longtext,
    userIdIn int
)
BEGIN
    INSERT INTO blogs (title, content, userId) 
    VALUES(titleIn, contentIn, userIdIn);
    
    SELECT 
        b.blogId,
        b.title,
        b.content,
        b.dateCreated as date,
        b.userId,
        u.username as author
    FROM blogs b
    JOIN users u ON b.userId = u.userId
    WHERE b.blogId = LAST_INSERT_ID();
END //
DELIMITER ;

DROP PROCEDURE IF EXISTS updateBlog;
DELIMITER //
CREATE PROCEDURE updateBlog(
    blogIdIn INT,
    titleIn VARCHAR(50),
    contentIn longtext,
    userIdIn INT
)
BEGIN
    UPDATE blogs 
    SET 
        title = titleIn,
        content = contentIn
    WHERE blogId = blogIdIn AND userId = userIdIn;
    
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
END //
DELIMITER ;

DROP PROCEDURE IF EXISTS deleteBlog;
DELIMITER //
CREATE PROCEDURE deleteBlog(
    blogIdIn INT,
    userIdIn INT
)
BEGIN
    DELETE FROM blogs WHERE blogId = blogIdIn AND userId = userIdIn;
    
    SELECT ROW_COUNT() as affectedRows;
END //
DELIMITER ;

-- ===================================================================
-- COMMENT MANAGEMENT PROCEDURES
-- ===================================================================

DROP PROCEDURE IF EXISTS getCommentsByBlog;
DELIMITER //
CREATE PROCEDURE getCommentsByBlog(
    blogIdIn INT,
    newerThanIn DATE,
    limitIn INT,
    offsetIn INT
)
BEGIN
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
END //
DELIMITER ;

DROP PROCEDURE IF EXISTS getCommentById;
DELIMITER //
CREATE PROCEDURE getCommentById(
    commentIdIn INT
)
BEGIN
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
END //
DELIMITER ;

DROP PROCEDURE IF EXISTS getCommentReplies;
DELIMITER //
CREATE PROCEDURE getCommentReplies(
    commentIdIn INT
)
BEGIN
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
END //
DELIMITER ;

DROP PROCEDURE IF EXISTS createComment;
DELIMITER //
CREATE PROCEDURE createComment(
    contentIn longtext,
    userIdIn int,
    blogIdIn int,
    parentCommentIdIn int
)
BEGIN
    INSERT INTO comments (content, userId, blogId, parentCommentId) 
    VALUES(contentIn, userIdIn, blogIdIn, parentCommentIdIn);
    
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
    WHERE c.commentId = LAST_INSERT_ID();
END //
DELIMITER ;

DROP PROCEDURE IF EXISTS updateComment;
DELIMITER //
CREATE PROCEDURE updateComment(
    commentIdIn INT,
    contentIn longtext,
    userIdIn INT
)
BEGIN
    UPDATE comments 
    SET content = contentIn
    WHERE commentId = commentIdIn AND userId = userIdIn;
    
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
END //
DELIMITER ;

DROP PROCEDURE IF EXISTS deleteComment;
DELIMITER //
CREATE PROCEDURE deleteComment(
    commentIdIn INT,
    userIdIn INT
)
BEGIN
    DELETE FROM comments WHERE commentId = commentIdIn AND userId = userIdIn;
    
    SELECT ROW_COUNT() as affectedRows;
END //
DELIMITER ;

-- ===================================================================
-- MAINTENANCE PROCEDURES
-- ===================================================================

DROP PROCEDURE IF EXISTS cleanupExpiredVerifications;
DELIMITER //
CREATE PROCEDURE cleanupExpiredVerifications()
BEGIN
    -- Delete expired verification tokens
    DELETE FROM verification WHERE expiresAt < NOW();
    DELETE FROM mobile_verification WHERE expiresAt < NOW();
    
    -- Delete expired pending changes
    DELETE FROM pending_email_changes WHERE expiresAt < NOW();
    DELETE FROM pending_phone_changes WHERE expiresAt < NOW();
END //
DELIMITER ;