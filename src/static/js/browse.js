var app = new Vue ({
    el: '#app',
    data: {
        user: undefined,
    },
    methods: {

    }
});

var s3list = new Vue ({
    el: '#s3list',
    data: {
        bList: [],
        oList: [],
        buckets: true,
        objects: false,
        currentBucket: '',
    },
    methods: {
        getBuckets: function () {
            // Fetch buckets from the API for the user that's currently logged
            // in
            fetch('api/buckets')
                .then(
                    function ( response ) {
                        return response.json();
                    }
                )
                .then(
                    function ( retJson ) {
                        console.log( JSON.stringify( retJson ));
                        s3list.bList = retJson;
                        s3list.objects = false;s3list.buckets = true;
                    }
                )
        },
        bringBucketsFront: function() {
            // Bring bucket view back to the front to prevent unnecessary API
            // call for diplaying them
            s3list.objects = false;s3list.buckets = true;
        },
        getObjects: function ( bucket ) {
            // Fetch objects contained in 'bucket' from the API for the user
            // that's currently logged in.
            var objUrl = new URL( "http://127.0.0.1:8080/api/objects" )
            objUrl.searchParams.append('bucket', bucket)
            fetch(objUrl)
                .then(
                    function ( response ) {
                        return response.json();
                    }
                )
                .then(
                    function ( retJson ) {
                        console.log( JSON.stringify( retJson ));
                        s3list.oList = retJson;
                        s3list.currentBucket = bucket;
                        s3list.buckets = false;s3list.objects = true;
                        for(i = 0; i < s3list.oList.length; i++) {
                            s3list.oList[i]['url'] = '/api/dload?bucket=' + s3list.currentBucket + '&objkey=' + s3list.oList[i]['Key'];
                        }
                    } 
                )
        },
    }
});

s3list.getBuckets()
