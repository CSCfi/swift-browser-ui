# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- (GH #864) Vault c4ghtransit integration - Uploads object headers to Vault in addition to Object Storage
- (GH #781) Render full details of Folders you have shared and Folders shared with you
  - Show Folder status including Shared status, source project and date of sharing
  - Show tags for Folders and Objects inside them
  - Change routes from Folder view back to the equivalent Folder tab
- (GH #751) Add modal for copying folder
- (GH #746) Move container and object listings to csc-ui components
- (GH #746) Migrate buefy search to CSC styling, csc-ui component for search not an option
- (GH #714) Add modal for sharing folder with other projects
- (GH #742) Added responsive navigation
- (GH #748) Add modal for editing object's tags
- (GH #730) Add a button to copy Project Id
- (GH #674) Add modal for uploading files
- (GH #727) New upload notification
- (GH #723) Add Project information as an option under User menu
- (GH #713) Top navigation support dropdown menu, commented out old user menu items & link to browser view from app name
- (GH #645) Add menu for folder options in table view
- (GH #651) Add modal for creating folder and ability to see project members in MyCSC
- (GH #638) Added tab based folder view in browse-route
- (GH #596) Support link phrasing, icon and destination update in main navigation
- (GH #577) Updated layout for top navigation
- (GH #596) Project switcher with CSC Design system select components
- (GH #468) add support for project isolation for projects marked as restricted
  - discovery for restricted projects pending, implemented logic only for now
  - foced restricted mode can be configured on
- (GH #514) Make user roles configurable.
- (GH #546) Optional two-step login with OpenID Connect (OIDC) as the first step.
  - When OIDC is enabled, the index page is replaced with a new one, that uses CSCfi/csc-ui components.
- (GH #565) Skip second login button click when first authentication used Haka.
- (GH #599) Add support for streaming uploads allowing > 1GiB files encrypted uploads
  - Also fixes some bugs related to encrypted upload engine and repeatability
- (GH #928) Add git commit version and link to footer
- Add option to specify database port and SSL mode for request and sharing DB connections
- Add option to specify Redis Sentinel connection parameters for redis configured with Sentinel
- avoid giving over-detailed `Server` values from services
- (GH #962) Use OIDC as the default Keystone login provider for SSO
- (GH #965) Show notification when changing permission in share modal
- (GH #969) Automate building wasm with npm
- (GH #983) Make elements more semantic and improve accessibility for screen reader users
- (GH #989) Make selected Display Options consistent when browsing between pages

### Changed

- Migrate to using pyproject.toml with hatch as build tool
- Allow installing js deps with pnpm install --prod for faster and smaller install
- (GH #514) Cypress integration tests run against keystone-swift container from https://github.com/CSCfi/docker-keystone-swift.
- Improved development workflow, and added development and testing instructions.
- (GH #601) Implement new visual style using `csc-ui` in rest of the login and error pages
- (GH #601) Add a language selector to login page menu bar, using `csc-ui`
- (GH #920) Optimize docker builds, making them faster by leveraging more caching mechanisms and removing unnecessary package installation
- (GH #1007) Create new Taginput component to replace Buefy's taginput component
- (GH #1009) Replace buefy toasts with c-toasts from `csc-ui`

### Fixed

- Fix missing footer and language-selector component setup
- Use oidc login Keystone provider for automatically forwarded SSO in oidc return
- (GH #851) Kill upload sessions upon finishing uploads to allow reuploading same files in all cases
- (GH #884) Fixed multiple bugs
  - Redirected to AllFolders view whenever the selected project changes
  - Modified function and fixed notification for removing a shared permission
  - Made modal's scroll position to be always on top when opening a modal
  - Add tooltip for Copy Share ID button
  - Fine-tuned modals' font sizes and gaps between elements
- (GH #871) Fixed for data table's folders' Options, sorting functionality, and modals' widths
- (GH #858) Fixed for multiple bugs related to modals and background page's scrolling effect
- (GH #853) Fix Node 18 needing python for npm install
- (GH #827) Fixed for updating folder's items count and size when deleting objects inside it
- (GH #788) Fixed for objects of a copied folder rendering their tags correctly
- (GH #850) Call `refreshNoUpload` on file entry in upload modal
- (GH #849) Fixed upload sometimes not starting due to lazily loaded service worker
- (GH #741) Fixed incorrect API token list logic causing an incorrect 404
- (GH #780) Fixed tables' Display Options rendering the menu options correctly when data changed
- (GH #502) Items being removed from IndexedDB on network errors.
- (GH #514) Fixed container and metadata updates.
- (GH #547) Fixed upload button being enabled when there are no files to upload.
- (GH #549) Fixed changing project keeps loading previous project data.
- (GH #550) Fixed changing project shows container from previous project.
- Correctly set the global font to Museo sans
- (GL #27) Fixed the sorting of `Shared status` table column.
- Unify editing tags modal for objects and containers
- Fix 'Share ID' tooltip formatting.
- Libupload path in docker files
- Fix hiding the pagination of data tables
- Fix shared objects functionality: visibility, deleting, editing tags

### Removed

- (GL #944) Unused views and components
  - views
    - `swift_browser_ui_frontend/src/views/Dashboard.vue`
    - `swift_browser_ui_frontend/src/views/DirectRequest.vue`
    - `swift_browser_ui_frontend/src/views/DirectShare.vue`
    - `swift_browser_ui_frontend/src/views/ShareRequests.vue`
    - `swift_browser_ui_frontend/src/views/SharedFrom.vue`
    - `swift_browser_ui_frontend/src/views/SharedTo.vue`

## [v2.0.1]

### Fixed

- Deprecate `.value` from container and object db listings
  - `dexie` or `rxjs` removed this from db returns, couldn't find a change causing
    this in either project, but this is the observed behavior
- Fix routing issues from trailing slash when adding project to container ACL.
- Fix incorrect session fetch in backend when accessing objects owned by foreign projects
- Fix routing issues when accessing shared objects

## [v2.0.0]

### Added

- (GH #493) redesign upload UI
  - let users know when keys are added by default
  - compute sha256 of key instead of showing text
- add `defaultKeyMessage` to `lang.js` (GH #494)
- IndexedDB as local in-browser cache, with dexiejs as dependency.
- Cancel Upload and Clear Files added in (GH #498)

### Changed

- **BREAKING** move to aiohttp_session with Redis as session store replacing own implementation
- **BREAKING** use own client for Openstack Swift and Keystone APIs to remove synchronous parts of codebase
- **BREAKING** update API documentation updating UI API to v2.0.0
- **BREAKING** Rename code occurrences of _bucket_ to _container_ (GH #471)
- Updated dependencies in front-end as well as node.js base image to `node:14.18.3-alpine3.15`
- Redirect to front page when the session has expired. (GH #461)
- Hide most errors from the browser's console. (GH #461)
- Updated node.js base image to `node:16.14.0-alpine3.15`
- update materialdesing icon link
- update browsers list with `npx browserslist@latest --update-db`
- add margin to top footer for clearer division between content and footer
- redesign upload view as specified in issue (GH #479)
- (GH #493) redesign upload UI

  - alignment in edit view of containers & objects
  - copy container view, sharing view and token view make it consistent with other views
  - key existence should be checked with `$te` https://kazupon.github.io/vue-i18n/api/#vue-injected-methods
  - check public key exists already before adding to the table

- Drag and drop fixes (GH #497) and (GH #498)

  - stylize drag-and-drop overlay
  - use Vue store to keep public keys
  - move drag and drop files as well as files uploaded by button to store

- **BREAKING** swift-browser-ui doesn't work in Firefox's private mode, as it doesn't offer IndexedDB.
  - There is a warning message at login, and it is not possible to login in unsupported browsers.
- Improved performance by reducing number of requests after cache has been created.
  - While the cache is being created, there might be a degradation in performance for large projects.
  - Reduced number of requests for fetching object tags
- Search box in Container View now searches across all containers and objects in the project using IndexedDB.
  - Tag matches are ordered first, then containers, and then objects. In each of these 3 categories, results are ordered based on the order the matched word appears.
  - The search is different from the filtering in objects list. Query has to match beginning of tag or beginning of words extrated from the name.
  - Renamed the search box in Object list to say "Filter" instead of "Search"
  - Adding more words to the search narrows down the results. Only the first word searches the IDB, following words search in-memory.
  - A message is shown when trying to search a large project before cache is created.
  - Matching results are highlighted.
  - Results are limited to maximum 100 containers and 100 objects.

### Fixed

- Double navigation to the UploadView (GH #473)
- (GH #476) CORS error headers fix
  - add CORS headers to error HTTP responses as well
  - handle test chunk uploaded request as `204` instead of `404` as recommended by https://github.com/23/resumable.js#handling-get-or-test-requests
  - remove forgotten console.logs
- fix issue with accessing ws on devserver (GH #493)
- fix logic for disabling/enabling button for encryption, fix removal of public keys and fix upload encryption options selector positioning (GH #494)

- Drag and drop fixes (GH #497) and (GH #498)
  - avoid redundant navigation to current location for UploadView
  - clean drag-and-drop after files were added as DataTransferItemList are kept
  - fixed uploading multiple directories

### Removed

- **BREAKING** session handling without redis as session backend
- The possibility to share containers with write-only (file drop) permissions (GH #475)
- GH (GH #493) redesign upload UI
  - removed vue-material-design-icons

[unreleased]: https://github.com/CSCfi/swift-browser-ui/compare/2.0.0...devel
[v2.0.0]: https://github.com/CSCfi/swift-browser-ui/compare/1.1.0b8...2.0.0
