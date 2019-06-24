var app = new Vue ({
    el: '#app',
    data: {
        user: undefined,
    },
    methods: {
        getUser: function () {
            fetch('api/username', { method: 'GET', credentials: 'include' })
                .then(
                    function ( response ) {
                        return response.json();
                    }
                )
                .then(
                    function ( retJson ) {
                        var uname = retJson;
                        console.log( uname );
                        app.user = uname;
                    }
                );
        },
    }
});

var projectChooser = new Vue({
    el: '#projectChooser',
    data: {
        projects: [],
        currentProject: undefined,
    },
    methods: {
        getProjects: function () {
            // Fetch available projects from the API
            projectChooser.getActiveProject(); 
            fetch('api/projects', {method: 'GET', credentials: 'include'})
                .then(
                    function ( response ) {
                        return response.json();
                    }
                )
                .then(
                    function ( retJson ) {
                        console.log( JSON.stringify( retJson ));
                        projectChooser.projects = retJson;
                    }
                );
        },
        changeProject: function ( newProject ) {
            // Call API to rescope token for a new project
            var rescopeURL = new URL( "login/rescope", document.location );
            rescopeURL.searchParams.append( 'project', newProject );
            fetch( rescopeURL, { method: 'GET', credentials: 'include' } )
                .then(
                    function ( response ) {
                        if ( response.status == 204 ) {
                            projectChooser.currentProject = undefined;
                            projectChooser.getActiveProject();
                            if (projectChooser.currentProject == undefined) {
                                
                            }
                            s3list.getBuckets();
                        }
                        else {
                            console.log( "Failed to rescope project" );
                            console.log( "Not changing anything in the lists for now" );
                        }
                    }
                )
        },
        getActiveProject: function () {
            var getProjectURL = new URL( "api/active", document.location );
            fetch( getProjectURL, { method: 'GET', credentials: 'include' } )
                .then(
                    function ( response ) {
                        if ( response.status == 200 ) {
                            var resp = response.json();
                            console.log("active: " + JSON.stringify(resp));
                            projectChooser.currentProject = resp['name'];
                        }
                    }
                );
        },
    },
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
            fetch('api/buckets', {method: 'GET', credentials: 'include'})
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
            console.log( document.location )
            var objUrl = new URL( "api/objects", document.location )
            objUrl.searchParams.append('bucket', bucket)
            fetch(objUrl, {method: 'GET', credentials: 'include'})
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
                        for(var i = 0; i < s3list.oList.length; i++) {
                            s3list.oList[i]['url'] = '/api/dload?bucket=' + s3list.currentBucket + '&objkey=' + s3list.oList[i]['name'];
                        }
                    }
                );
        },
    }
});

app.getUser();
projectChooser.getProjects();
s3list.getBuckets();
