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

window.Modal = Vue.component('modal');