# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- (GH #746) Move container and object listings to csc-ui components
- (GH #746) Migrate buefy search to CSC styling, csc-ui component for search not an option
- (GH #714) Add modal for sharing folder with other projects
- (GH #730) Add a button to copy Project Id
- (GH #674) Add modal for uploading files
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

### Changed

- (GH #514) Cypress integration tests run against keystone-swift container from https://github.com/CSCfi/docker-keystone-swift.
- Improved development workflow, and added development and testing instructions.
- (GH #601) Implement new visual style using `csc-ui` in rest of the login and error pages
- (GH #601) Add a language selector to login page menu bar, using `csc-ui`

### Fixed

- (GH #780) Fixed tables' Display Options rendering the menu options correctly when data changed
- (GH #502) Items being removed from IndexedDB on network errors.
- (GH #514) Fixed container and metadata updates.
- (GH #547) Fixed upload button being enabled when there are no files to upload.
- (GH #549) Fixed changing project keeps loading previous project data.
- (GH #550) Fixed changing project shows container from previous project.

## [v2.0.1]

### Fixed

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
