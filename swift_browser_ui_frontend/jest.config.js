module.exports = {
  roots: [
    "../",
  ],
  preset: "@vue/cli-plugin-unit-jest",
  "moduleFileExtensions": [
    "js",
    "json",
    "vue",
  ],
  testMatch: [
    "**/tests/jest/**/*.spec.[jt]s?(x)",
  ],
  "transform": {
    ".*\\.(vue)$": "vue-jest",
    ".*\\.(js)$": "babel-jest",
  },
  moduleDirectories: [
    "<rootDir>/node_modules/",
  ],
};
