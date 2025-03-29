def register_routes(api):
    # Register all API routes
    from app.routes.auth import UserRegistration, AuthLogin, AuthLogout, VerifyOTP, RequestOTP, VerifyMobileOTP, RequestMobileOTP, RequestPasswordReset, CompletePasswordReset, VerifyResetOTP
    from app.routes.blog import BlogList, BlogDetail, BlogCreate, BlogUpdate, BlogDelete
    from app.routes.comment import BlogCommentList, BlogCommentCreate, CommentDetail, CommentUpdate, CommentDelete, CommentReplyList, CommentReplyCreate 
    from app.routes.user import UserList, UserDetail, UserEmail, UserPhone, UserBlogList, UserNotificationPreferences
    from app.routes.ai import GeminiAI
    
    # Auth routes
    api.add_resource(UserRegistration, '/auth/register')
    api.add_resource(AuthLogin, '/auth/login')
    api.add_resource(AuthLogout, '/auth/logout')
    api.add_resource(VerifyOTP, '/auth/verify-otp')
    api.add_resource(RequestOTP, '/auth/request-otp')
    api.add_resource(VerifyMobileOTP, '/auth/verify-mobile-otp')
    api.add_resource(RequestMobileOTP, '/auth/request-mobile-otp')
    api.add_resource(RequestPasswordReset, '/auth/forgot-password')
    api.add_resource(VerifyResetOTP, '/auth/verify-reset-otp')
    api.add_resource(CompletePasswordReset, '/auth/reset-password')
    
    # For backwards compatibility with the original API
    api.add_resource(AuthLogin, '/user/login', endpoint='user_login')
    api.add_resource(AuthLogout, '/user/logout', endpoint='user_logout')
    
    # Blog routes
    api.add_resource(BlogList, '/blogs-api')
    api.add_resource(BlogDetail, '/blogs-api/<int:blogId>')
    api.add_resource(BlogCreate, '/blogs/create')
    api.add_resource(BlogUpdate, '/blogs/<int:blogId>/update')
    api.add_resource(BlogDelete, '/blogs/<int:blogId>/delete')
    
    # Comment routes
    api.add_resource(BlogCommentList, '/blogs-api/<int:blogId>/comments')
    api.add_resource(BlogCommentCreate, '/blogs/<int:blogId>/comments/create')
    api.add_resource(CommentDetail, '/comments/<int:commentId>')
    api.add_resource(CommentUpdate, '/comments/<int:commentId>/update')
    api.add_resource(CommentDelete, '/comments/<int:commentId>/delete')
    api.add_resource(CommentReplyList, '/comments/<int:commentId>/replies')
    api.add_resource(CommentReplyCreate, '/comments/<int:commentId>/replies/create')
    
    # User routes
    api.add_resource(UserList, '/users')
    api.add_resource(UserDetail, '/users-api/<int:userId>')
    api.add_resource(UserBlogList, '/users-api/<int:userId>/blogs')
    api.add_resource(UserEmail, '/users/email')
    api.add_resource(UserPhone, '/users/phone')
    api.add_resource(UserNotificationPreferences, '/users/notification-preferences')
    
    # AI routes
    api.add_resource(GeminiAI, '/ai/generate')