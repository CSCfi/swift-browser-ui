module.exports = {
  preset: "@vue/cli-plugin-unit-jest",
  "moduleFileExtensions": [
    "js",
    "json",
    // tell Jest to handle `*.vue` files
    "vue",
  ],
  "transform": {
    // process `*.vue` files with `vue-jest`
    ".*\\.(vue)$": "vue-jest",
    // process `*.js` files with `babel-jest`
    ".*\\.(js)$": "babel-jest",
  },
};
