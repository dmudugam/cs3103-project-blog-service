/**
 * User Blogs Component
 * 
 * Display a user's personal blog collection.
 */
Vue.component('user-blogs', {
    props: {
        blogs: {
            type: Array,
            required: true
        },
        loading: {
            type: Boolean,
            default: false
        }
    },
    methods: {
        formatDate(dateString) {
            return window.Formatters.formatDate(dateString);
        },
        viewBlog(blogId) {
            this.$emit('view-blog', blogId);
        },
        editBlog(blog) {
            this.$emit('edit-blog', blog);
        },
        deleteBlog(blog) {
            if (confirm('Are you sure you want to delete this blog?')) {
                this.$emit('delete-blog', blog);
            }
        },
        createNewBlog() {
            this.$emit('create-blog');
        }
    },
    template: `
        <div>
            <div v-if="loading" class="text-center my-4">
                <div class="spinner-border text-primary" role="status">
                    <span class="sr-only">Loading...</span>
                </div>
            </div>
            
            <div v-else-if="blogs.length" class="user-blog-list">
                <div v-for="blog in blogs" :key="blog.blogId" class="user-blog-item">
                    <div class="user-blog-header">
                        <h4>{{ blog.title }}</h4>
                        <span class="user-blog-date">{{ formatDate(blog.date) }}</span>
                    </div>
                    <div class="user-blog-actions">
                        <button type="button" class="btn btn-sm btn-outline-primary mr-2" @click="viewBlog(blog.blogId)">View</button>
                        <button type="button" class="btn btn-sm btn-outline-secondary mr-2" @click="editBlog(blog)">Edit</button>
                        <button type="button" class="btn btn-sm btn-outline-danger" @click="deleteBlog(blog)">Delete</button>
                    </div>
                </div>
            </div>
            
            <div v-else class="text-center my-4">
                <p>You haven't created any blogs yet.</p>
            </div>
            
            <div class="text-center mt-4">
                <button type="button" class="btn btn-outline-primary" @click="createNewBlog">Create New Blog</button>
            </div>
        </div>
    `
});

window.UserBlogsComponent = Vue.component('user-blogs');