/**
 * Blog Detail Component
 * 
 * Display a single blog post with content, author information,
 */

Vue.component('blog-detail', {
    props: {
        blog: {
            type: Object,
            required: true
        },
        comments: {
            type: Array,
            default: () => []
        },
        loading: {
            type: Object,
            default: () => ({
                blog: false,
                comments: false
            })
        },
        userId: {
            type: Number,
            default: null
        },
        authenticated: {
            type: Boolean,
            default: false
        },
        verified: {
            type: Boolean,
            default: false
        },
        mobileVerified: {
            type: Boolean,
            default: false
        }
    },
    data() {
        return {
            showCommentForm: false,
            newComment: {
                content: "",
                parentCommentId: null
            }
        };
    },
    computed: {
        isVerified() {
            return this.verified || this.mobileVerified;
        }
    },
    methods: {
        formatDate(dateString) {
            return window.Formatters.formatDate(dateString);
        },
        prepareEditBlog() {
            this.$emit('edit-blog', this.blog);
        },
        deleteBlog() {
            if (confirm("Are you sure you want to delete this blog?")) {
                this.$emit('delete-blog', this.blog);
            }
        },
        toggleCommentForm(parentCommentId = null) {
            this.newComment.parentCommentId = parentCommentId;
            this.showCommentForm = !this.showCommentForm;
            
            if (!this.showCommentForm) {
                this.newComment.content = '';
            }
        },
        submitComment() {
            if (!this.newComment.content.trim()) {
                return;
            }
            
            this.$emit('submit-comment', {
                content: this.newComment.content,
                parentCommentId: this.newComment.parentCommentId,
                blogId: this.blog.blogId
            });
            
            this.newComment.content = '';
            this.showCommentForm = false;
        },
        replyToComment(commentId) {
            this.$emit('reply-to-comment', commentId);
            this.newComment.parentCommentId = commentId;
            this.showCommentForm = true;
        },
        deleteComment(commentId) {
            if (confirm("Are you sure you want to delete this comment?")) {
                this.$emit('delete-comment', commentId);
            }
        }
    },
    template: `
        <div>
            <div v-if="loading.blog" class="text-center my-4">
                <div class="spinner-border text-primary" role="status">
                    <span class="sr-only">Loading...</span>
                </div>
            </div>
            
            <div v-else>
                <!-- Blog Content -->
                <div class="blog-content mb-4" v-html="blog.content">
                </div>
                
                <!-- Blog Actions -->
                <div v-if="authenticated && blog.userId === userId" class="blog-actions mb-4 text-center">
                    <button type="button" class="btn btn-outline-primary" @click="prepareEditBlog">Edit</button>
                    <button type="button" class="btn btn-outline-danger ml-2" @click="deleteBlog">Delete</button>
                </div>
                
                <!-- Comments Section -->
                <div class="comments-section">
                    <h4>Comments</h4>
                    
                    <!-- Add Comment Button -->
                    <div v-if="authenticated && isVerified" class="mb-3">
                        <button type="button" class="btn btn-outline-primary" @click="toggleCommentForm(null)">
                            {{ showCommentForm && !newComment.parentCommentId ? 'Cancel' : 'Add Comment' }}
                        </button>
                    </div>
                    
                    <!-- Comment Form -->
                    <div v-if="showCommentForm" class="comment-form mb-4">
                        <form @submit.prevent="submitComment">
                            <div class="form-group">
                                <label>
                                    {{ newComment.parentCommentId ? 'Your Reply' : 'Your Comment' }}
                                    <span v-if="newComment.parentCommentId"> (Replying to comment)</span>
                                </label>
                                <textarea class="form-control" v-model="newComment.content" rows="3" placeholder="Write your comment here...😊" required></textarea>
                            </div>
                            <div class="text-right">
                                <button type="button" class="btn btn-outline-secondary mr-2" @click="toggleCommentForm(null)">Cancel</button>
                                <button type="submit" class="btn btn-primary" :disabled="loading.comments">
                                    <span v-if="loading.comments" class="spinner-border spinner-border-sm mr-2" role="status"></span>
                                    Submit
                                </button>
                            </div>
                        </form>
                    </div>
                    
                    <!-- Loading Comments -->
                    <div v-if="loading.comments" class="text-center my-4">
                        <div class="spinner-border text-primary" role="status">
                            <span class="sr-only">Loading comments...</span>
                        </div>
                    </div>
                    
                    <!-- Comments List -->
                    <div v-else-if="comments.length" class="comments-list">
                        <div v-for="comment in comments" :key="comment.commentId" class="comment-item" :class="{ 'comment-reply': comment.parentCommentId }">
                            <div class="comment-content" v-html="comment.content">
                            </div>
                            <div class="comment-meta">
                                <span class="comment-author">{{ comment.author }}</span>
                                <span class="comment-date">{{ formatDate(comment.date) }}</span>
                            </div>
                            <div class="comment-actions">
                                <button v-if="authenticated" type="button" class="btn btn-sm btn-outline-secondary" @click="replyToComment(comment.commentId)">Reply</button>
                                <button v-if="authenticated && comment.userId === userId" type="button" class="btn btn-sm btn-outline-danger ml-2" @click="deleteComment(comment.commentId)">Delete</button>
                            </div>
                        </div>
                    </div>
                    
                    <!-- No Comments Message -->
                    <div v-else class="no-comments">
                        <p>No comments yet. Be the first to comment!</p>
                    </div>
                </div>
            </div>
        </div>
    `
});

window.BlogDetailComponent = Vue.component('blog-detail');