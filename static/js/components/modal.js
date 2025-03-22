// Defining the Modal component
Vue.component("modal", {
    template: "#modal-template",
    props: {
        animationType: {
            type: String,
            default: 'modal'
        }
    }
});

// Exporting for use in main application
window.Modal = Vue.component('modal');