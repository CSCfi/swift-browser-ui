Vue.component('bucket-table-heading', {
    template: '<tr>\
                <th>Bucket</th>\
                <th>Creation date</th>\
              </tr>'
})

Vue.component('bucket-table-row', {
    props: ['bname', 'bdate',],
    template: '<tr>\
                <td>{{ bname }}</td>\
                <td>{{ bdate }}</td>\
                <button v-on:click="$emit(\'bclick\')">Get objects</button>\
               </tr>'
})

Vue.component('object-table-heading', {
    template: '<tr>\
    <td>Bucket</td>\
    <td>Key</td>\
    <td>Last modified</td>\
    <td>Size</td>\
    <td>Owner</td>\
    <button v-on:click="$emit(\'oheadingclick\')">Back</button>\
    </tr>'
})

Vue.component('object-table-row', {
    props: ['stobject', 'bucket', 'dloadlink'],
    template: '\
    <tr>\
    <td>{{ bucket }}</td>\
    <td>{{ stobject.Key }}</td>\
    <td>{{ stobject.LastModified }}</td>\
    <td>{{ stobject.Size }}</td>\
    <td>{{ stobject.Owner.DisplayName }}</td>\
    <a :href="dloadlink">Download</a>\
    </tr>'
})
