// This file configures the VSCode Vetur extension, which adds support for Vue.js to VSCode.
module.exports = {
settings: {
  "vetur.useWorkspaceDependencies": true,
  "vetur.experimental.templateInterpolationService": true,
},
projects: [
    {
      root: './swift_browser_ui_frontend',
    },
  ],
}
