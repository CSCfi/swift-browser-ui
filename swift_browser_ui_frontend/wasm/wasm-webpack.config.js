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
        s3upworker: {
            import: "./js/crypt-post-s3upload.js",
            filename: "./build/crypt-post-s3upload.js",
            chunkLoading: false,
        },
        s3downworker: {
            import: "./js/crypt-post-s3download.js",
            filename: "./build/crypt-post-s3download.js",
            chunkLoading: false,
        },
        s3headerworker: {
            import: "./js/crypt-post-headers.js",
            filename: "./build/crypt-post-headers.js",
            chunkLoading: false,
        },
    },
};
