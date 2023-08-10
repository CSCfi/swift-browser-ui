const path = require('path');


module.exports = {
    context: path.resolve(__dirname, 'build'),
    mode: "development",
    devtool: "source-map",
    resolve: {
        fallback: {
            "crypto": false,
        },
    },
    output: {
        path: path.resolve(__dirname, 'build'),
    },
    entry: {
        downworker: {
            import: "./libdownload.js",
            filename: "./downworker.js",
            chunkLoading: false,
        },
        upworker: {
            import: "./libupload.js",
            filename: "./upworker.js",
            chunkLoading: false,
        },
    },
};
