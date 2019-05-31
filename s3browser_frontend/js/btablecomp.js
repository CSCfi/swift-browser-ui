Vue.component('bucket-table-heading', {
    template: '<tr>\
                <th>Bucket</th>\
              </tr>'
})

Vue.component('bucket-table-row', {
    props: ['bname', 'bdate',],
    template: '<tr>\
                <td>{{ bname }}</td>\
                <button v-on:click="$emit(\'bclick\')">Get objects</button>\
               </tr>'
})

Vue.component('object-table-heading', {
    template: '<tr>\
    <td>Bucket</td>\
    <td>Name</td>\
    <td>Last modified</td>\
    <td>Size</td>\
    <button v-on:click="$emit(\'oheadingclick\')">Back</button>\
    </tr>'
})

Vue.component('object-table-row', {
    props: ['stobject', 'bucket', 'dloadlink'],
    template: '\
    <tr>\
    <td>{{ bucket }}</td>\
    <td>{{ stobject.name }}</td>\
    <td>{{ stobject.last_modified }}</td>\
    <td>{{ stobject.bytes }}</td>\
    <a :href="dloadlink">Download</a>\
    </tr>'
})
