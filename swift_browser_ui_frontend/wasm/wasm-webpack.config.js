const path = require('path');


module.exports = {
    context: path.resolve(__dirname, ''),
    mode: "development",
    devtool: "source-map",
    output: {
        path: path.resolve(__dirname, ''),
    },
    entry: {
        downworker: {
            import: "./js/crypt-post-downworker.js",
            filename: "./build/downworker-post.js",
            chunkLoading: false,
        },
        upworker: {
            import: "./js/crypt-post-upworker.js",
            filename: "./build/upworker-post.js",
            chunkLoading: false,
        },
    },
};
