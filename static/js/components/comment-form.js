/**
 * Comment Form Component
 */
Vue.component('comment-form', {
    props: {
        parentCommentId: {
            type: Number,
            default: null
        },
        loading: {
            type: Boolean,
            default: false
        }
    },
    
    data() {
        return {
            content: ''
        };
    },
    
    computed: {
        isReply() {
            return this.parentCommentId !== null;
        },
        
        submitLabel() {
            return this.isReply ? 'Reply' : 'Comment';
        }
    },
    
    methods: {
        submitComment() {
            // Prevent empty submissions
            if (!this.content.trim()) {
                return;
            }
            
            this.$emit('submit', {
                content: this.content,
                parentCommentId: this.parentCommentId
            });
            
            this.content = '';
        },
        
        // Handle cancellation
        cancel() {
            this.$emit('cancel');
        }
    },
    
    template: `
        <div class="comment-form">
            <form @submit.prevent="submitComment">
                <div class="form-group">
                    <label>
                        {{ isReply ? 'Your Reply' : 'Your Comment' }}
                        <span v-if="isReply"> (Replying to comment)</span>
                    </label>
                    <textarea class="form-control" v-model="content" rows="3" placeholder="Write your comment here...😊" required></textarea>
                </div>
                <div class="text-right">
                    <button type="button" class="btn btn-outline-secondary mr-2" @click="cancel">Cancel</button>
                    <button type="submit" class="btn btn-primary" :disabled="loading">
                        <span v-if="loading" class="spinner-border spinner-border-sm mr-2" role="status"></span>
                        {{ submitLabel }}
                    </button>
                </div>
            </form>
        </div>
    `
});

window.CommentFormComponent = Vue.component('comment-form');