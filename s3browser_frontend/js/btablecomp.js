// There is some trickery with tricks with links instead of text, to
// enable alt focusing to relevant parts of the screen (e.g. back-button,
// changing to bucket). The reason this is done with links is to prevent
// having to use a library to implement this basic functionality, there's
// already vue.js and it can be used to implement link behaviour overriding.
// Anything on top of that would be unnecessary bloat leading to increased
// load times.

// A vue.js component for the bucket table headings. The only column currently
// is the bucket/container name, so not much needs to be displayed
Vue.component('bucket-table-heading', {
    template: '<tr>\
                <th>Bucket</th>\
              </tr>'
});

// A vue.js component for the bucket table rows. The bucket/container name will
// emit a bclick event when clicked, and thus will lead to the clicked bucket
// being opened
Vue.component('bucket-table-row', {
    props: ['bname', 'bdate',],
    template: '<tr>\
                <td id="bucketname" v-on:click="$emit(\'bclick\')">{{ bname }}</td>\
               </tr>'
});

// A vue.js component for the object table headings. The columns are the Back
// -column (used to provide a visible back button), Bucket-column (used to
// display the bucket the objects belong to), Name-column (used to display
// the name of the objetc on the row), Last modified -column (used to
// display the date the object was last modified), Size-column (used to display
// the size of the object) and the Download-column, containing download links
// for each object (though the link will be only actually generated upon action
// on the server side)
Vue.component('object-table-heading', {
    template: '<tr>\
    <th id="backheading" v-on:click="$emit(\'oheadingclick\')"><a v-on:click.prevent="$emit(\'oheadingclick\')">Back</a></th>\
    <th>Bucket</th>\
    <th>Name</th>\
    <th>Last modified</th>\
    <th>Size</th>\
    <th>Download</th>\
    </tr>'
});

// A vue.js component for the object table rows. The columns are as specified
// before. The column with the ID backcolumn will emit an 'oheadingclick' event
// upon clicking, so the spa knows to go back to displaying buckets.
Vue.component('object-table-row', {
    props: ['stobject', 'bucket', 'dloadlink'],
    template: '\
    <tr>\
    <td id="backcolumn" v-on:click="$emit(\'oheadingclick\')"><-</td>\
    <td>{{ bucket }}</td>\
    <td>{{ stobject.name }}</td>\
    <td>{{ stobject.last_modified }}</td>\
    <td>{{ stobject.bytes }}</td>\
    <td id="tableaddrrow"><a id="tableaddr" :href="dloadlink">Link</a></td>\
    </tr>'
});

// A vue.js component for listing all the projects which are available for the
// user that's currently logged in
Vue.component('project-list-element', {
    props: ['project'],
    template: '\
    <li>\
    {{ project }}\
    </li>'
});
