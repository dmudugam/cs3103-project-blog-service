/**
 * Blog List Component
 * 
 * Display a list of blog posts with title, author, and date.
 */
Vue.component('blog-list', {
    props: {
        blogs: {
            type: Array,
            required: true
        },
        loading: {
            type: Boolean,
            default: false
        },
        pagination: {
            type: Object,
            required: true
        }
    },
    methods: {
        formatDate(dateString) {
            return window.Formatters.formatDate(dateString);
        },
        viewBlog(blogId) {
            this.$emit('view-blog', blogId);
        },
        loadMore() {
            this.$emit('load-more');
        }
    },
    template: `
        <div>
            <!-- Loading Indicator -->
            <div v-if="loading" class="text-center my-4">
                <div class="spinner-border text-primary" role="status">
                    <span class="sr-only">Loading...</span>
                </div>
            </div>
            
            <!-- Blog List -->
            <div v-else-if="blogs.length" class="blog-list">
                <div v-for="blog in blogs" :key="blog.blogId" class="blog-item" @click="viewBlog(blog.blogId)">
                    <div class="blog-header">
                        <h3>{{ blog.title }}</h3>
                        <div class="blog-meta">
                            <span class="blog-author">By {{ blog.author }}</span>
                            <span class="blog-date">{{ formatDate(blog.date) }}</span>
                        </div>
                    </div>
                </div>
                
                <!-- Load More Button -->
                <div v-if="pagination.hasMore" class="text-center mt-4">
                    <button type="button" class="btn btn-outline-primary" @click="loadMore">Load More</button>
                </div>
            </div>
            
            <!-- No Blogs Message -->
            <div v-else class="text-center my-4">
                <p>No blogs found.</p>
            </div>
        </div>
    `
});

window.BlogListComponent = Vue.component('blog-list');