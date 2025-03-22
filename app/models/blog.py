from datetime import datetime

class Blog:
    """
    Blog model - represents a blog post
    """
    def __init__(self, blog_id=None, title=None, content=None, user_id=None, created_at=None, updated_at=None):
        self.blog_id = blog_id
        self.title = title
        self.content = content
        self.user_id = user_id
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()

class Comment:
    """
    Comment model - represents a comment on a blog post or a reply to another comment
    """
    def __init__(self, comment_id=None, content=None, user_id=None, blog_id=None, parent_comment_id=None, created_at=None, updated_at=None):
        self.comment_id = comment_id
        self.content = content
        self.user_id = user_id
        self.blog_id = blog_id
        self.parent_comment_id = parent_comment_id
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()