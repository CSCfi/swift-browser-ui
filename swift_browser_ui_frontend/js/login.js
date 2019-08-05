var retform = new Vue ({
    el: "#retform",
    data: {
        formname: "Token id:",
    },
    methods: {
        "displayInvalid": function () {
            if (
                document.cookie.split(';')
                .filter((item) => 
                item.trim().startsWith('INVALID_TOKEN=')).length ) {
                    retform.formname = 
                    "Token id: (Invalid characters in previous token.)";
            }
        }
    }
})

retform.displayInvalid();
