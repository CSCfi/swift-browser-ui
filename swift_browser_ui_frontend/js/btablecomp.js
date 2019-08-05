// A vue.js component for the program breadcrumb
Vue.component('breadcrumb-list-element', {
    props: [ 'address', 'alias' ],
    template: '\
<li class=breadcrumb-element>\
    <router-link class="breadcrumb-link" v-bind:to="address">\
    {{ alias }}</router-link>\
</li>\
    ',
});
