# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- (GL #1205) Add a route back to front page from top toolbar
- (GL #1126) Added download progress bar for direct downloads (Chrome)
- (GL #1166) Added clarifying text about folder extension during download
- (GL #1168) Added notifications for failed downloads
- Update Finnish version for Accessibility statement
- (GL #1180) Add enforcing token lifetimes to signature authentication middleware

### Changed
- Refactor to remove eslint supression
  - for sharing and sharing tooltip including language changes
  - for share modal to comply Vue style guide
  - no-prototype-builtins and camel case
  - Cypress test related
- Refactor entries' files, IndexPage and IndexOIDCPage
- (GL #1200) New terms for sharing permissions

### Removed
- (GL #1204) Remove old upload code from frontend

### Fixed
- (GL #1222) Fix `view destination folder` link not working with shared containers

## [2024.02.0]

### Added
- (GL #1203) Add a warning when deleting files from a shared folder
- (GL #1185) Add Accessibility page (English version)
- (GL #1174) Download files that cannot be decrypted directly as is
- (GL #1207) Make vault service id configurable via environment variable

### Changed
- (GL #1202) Change the status text of unshared folder
- Package dependency updates

### Fixed
- (GL #1187) Trim whitespace from container names before creation
- (GL #1182) Prevent folder icons in table from shrinking
- (GL #1198) Faulty subfolders in route should lead to status 404

## [2024.01.0]

### Added
- (GL #1192) Add link to privacy policy in footer

### Changed
- Package dependency updates

### Fixed
- (GL #1183) Downloaded containers having wrong sizes
- (GL #1194) Fix upload functionality after cancelling large uploads
- (GL #1196) Fix service worker stopping downloads for large containers and files
- (GL #1176) Prevent incorrect 2-step login order causing session fixation

## [2023.12.0]

### Added
- (GH #642) Add support for decrypting downloaded files
- Automate building wasm with npm
  - use `CSCfi/docker-emscripten-crypt4gh` image `1.2.0`
- Show notification when changing permission in share modal
- Use OIDC as the default Keystone login provider for SSO
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
- (GH #944) Create new Taginput component to replace Buefy's taginput component
- (GL #944) Replace buefy upload button with a new component: `CUploadButton`
- (GL #940) Added TokenModal to replace token page
- (GL #936) Add missing icon for subfolders
- (GL #985) Add breadcrumb component
- (GL #1050) Add generic error handling for request, sharing, and upload backend components
- (GL #1051) Filter projects based on response from OIDC provider
  - introduced `SDCONNECT_ENABLED` environment variable so that we can force the check for `sdConnectProjects` claim when deployed to production
  - check `oidc_enabled` in middleware in order to invalidate session that don't contain oidc
- (GL #1043) Add folder name length validation when creating a folder, copying, uploading to a new one
- (GL #970) Cancel fetch requests when navigating away from page
- (GL #1013) Restrict users from creating folders with ending `_segments`
- (GL #923) Add `Last modified` column for Container Table
- (GL #999) Add three level sharing with view option
- (GL #947) Added cypress tests for login, adding and showing containers, uploading files
- (GL #1047) Added redis and vault monitoring to `/health` endpoint
- (GL #947) Added cypress tests for sharing folders
- (GL #987) Added keyboard navigation for all modals in the UI
- (GL #931) Added proper parallel upload and download support
  - Move tar archiving to frontend
  - Add frontend support for downloading arbitrary files as an archive
  - Use msgpack for parsing websocket data
  - Separate upload and download workers
  - Use direct file system writes if available on system
  - Move upload, download fetch calls to workers to reduce messaging overhead
- (GL #1145) Added new api for modifying write access from container's access control list
- (GL #1151) New folder moved to the top of the table for a while when created via Upload modal or Create Folder modal
- (GL #1147) Add a toast when user cannot download archive due to ustar limits on file path
- (GL #1152) Added ConfirmRouteModal to confirm navigating away from project with ongoing upload
- Add unit tests for WebAssembly C code
- (GL #1170) Added alerts to require user confirmation to change or delete sharing permissions
- Support tokens for authentication on the upload runner API
- (GL #1138) Make it possible to cancel an upload without error and a new upload can start successfully

### Changed

- (GH #779) Remove `/data` `/.segments` split in container, revert to `_segments` container for segments
- Migrate to using pyproject.toml with hatch as build tool
- Allow installing js deps with pnpm install --prod for faster and smaller install
- (GH #514) Cypress integration tests run against keystone-swift container from https://github.com/CSCfi/docker-keystone-swift.
- Improved development workflow, and added development and testing instructions.
- (GH #601) Implement new visual style using `csc-ui` in rest of the login and error pages
- (GH #601) Add a language selector to login page menu bar, using `csc-ui`
- (GH #920) Optimize docker builds, making them faster by leveraging more caching mechanisms and removing unnecessary package installation
- (GH #1009) Replace buefy toasts with c-toasts from `csc-ui`
- (GH #1014) Replace buefy snackbars with custom c-toasts from `csc-ui`
- (GL #944) Replace buefy b-input with c-text-field from `csc-ui`
- (GL #944) Replace buefy b-button with c-button from `csc-ui`
- (GL #944) Replace buefy b-select with c-select from `csc-ui`
- (GL #944) Replace buefy b-loading with c-loader from `csc-ui` and remove unused b-loading
- (GL #944) Replace buefy b-table with c-data-table from `csc-ui`
- (GH #1028) Switch from `aioredis` to `redis` library due to deprecation
- (GH #1025) add timeout to `requests` as recommended by `bandit`
- (GL #944) Replace buefy dialogs with c-modal from `csc-ui`
- (GL #944) Replace buefy notifications with c-toasts from `csc-ui`
- (GL #944) Replace buefy Autocomplete component with c-autocomplete from `csc-ui`
- (GH #982) Migrate from vue-cli to vite
- (GH #1034) Migrate to vue3
- (GL #1032) `_segments` folders no longer have tokens
- (GL #1027) Update advanced encryption options, remove private key option
- (GL #1072) Relative time (from now) made default display option for last_modified dates
- (GL #1083) Disabled `create folder` when inside containers to avoid user confusion that they can create subfolders
- (GL #1069) Forbid special characters in container names
- (GL #1074) Updated `/api/{project}` endpoint to check for `last_modified` values before returning the container list
- (GL #1105) Upload modal restricted to uploading to current container, or creating a new one in main container view
- (GL #1028) Disallow uploading files with size 0
- Use common base class for database connections
- (GL #1153) Display decimals with single digit file sizes
- (GL #1184) Move `create folder` button out of secondary nav bar into containers' view

### Fixed

- (GH #704) Fix lost folder structure in shared mode uploads
- (GH #705) Fix logic for creating folders on upload and uploading into pseudofolders
- (GH #819) Fix upload modal not pre-filling current folder name
- (GH #869) Fix pseudofolder rendering
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
- URL does not strip the path, when that is present. Also small fixes to make it deployable under the same URL.
- (GL #933) Fix for selecting and mass deleting subfolders and files
- (GL #992) Fix for uploading folder with special chars resulted in multiple copied folders
- (GL #993) Fix for showing correct folder name when refreshing Upload view
- (GL #979) Fix for creating and uploading to a folder works at the same time
- (GL #989 #990) Fix sorting in datatable
- (GL #925) Files can be deleted when shown as paths
- (GL #965) Only files with unique paths are added for upload
- (GL #1008) Stop adding files for upload when cancel is pressed
- (GL #988) Fix for missing translation in some parts of UI
- (GL #971) Fix broken UI when session doesn't exist in the backend by setting more strict session checks in the backend
- (GL #993 #981) Fix upload not starting
- (GL #978) Fix for folder, subfolder and file's size being zero, hide segment folder from view but get it shared properly
- (GL #1010) Fix for what actions a shared folder could have with different permissions (Copy, Download & Copy, Download, Upload)
- (GL #969) Fix not validating ShareID format
- (GL #1032) Fix `_segments` folder sharing by creating a `_segments` folder when a new folder is created
- (GL #1011) Fix for preventing user from uploading to shared containers without rights
- (GL #1040) Fix for editing tags functionality for subfolder and files
- (GL #1015 #1018) Fix issues for large files upload
  - Encode comma ´,´ character in object names to avoid backend returns 500
  - Update logic for IndexedDB to handle large upload of >50 files properly
  - Add check for null session in wasm when canceling large upload of >50 files
- (GL #1034) Fix search not including shared folders or files, and search result routing
- (GL #1049) Fix for missing banner image from build version
- (GL #1044) Fix search not including subfolders into results
- (GL #1050) Fix unified token DB causing HTTP409
  - fixed `REQUEST_DB_PORT` instead of `SHARING_DB_PORT` in sharing db
  - fixed typing for python code in db so that ports are int instead of string - required for deployment
- (GL #1056) Fix creating a pseudo-container (forward slash) returning 403 and logging user out
- (GL #1050) fixed missing paths in backend: `unauth`, `forbid`, `uidown`, `badrequest`, `notfound` and front-end api responses
- (GL #1074) Fix for error when last_modified date is null/undefined
- (GL #1068) Fix copy request failing silently if container name is already in use
- (GL #1059) Fixed item deletion bug in which deleting last item on a page left open an empty page
- (GL #1081) Fix for objects' tag editings and deletion being disabled in a normal container
- (GL #1092) Fix display options' persistence for individual containers and container table
- (GL #1080 #1086) Fix subfolders changing last_modified dates when sorting and sorting by size
- (GL #1084) Disable download option for empty container and empty object
- (GL #1058) Fix shown size of copied container when source container has a lot of objects
- (GL #972) Fix for missing required param `"user"` and no match location for path `"/browse"`
- (GL #1111) Fix for Share button not always working
- (GL #1066) Fix for sharing/permissions not removed correctly
- (GL #1078) Fix overwriting existing files with upload
- (GL #1108) Fix deleting large amount of objects (~100 items) with long names
- (GL #1140) Fix Sharing permissions swapping between options after sharing
- (GL #1125) Remove shared containers if the owner container is deleted
- (GL #966) Fix upload cancel/finish breaking upload and download functions due to `ServiceWorker` issues
- (GL #1137) Fix upload repeatability and worker lifecycle issues leading to upload unavailability
- (GL #1127) Fix `ServiceWorker` issues affecting Firefox downloads
- (GL #1091) Fix subfolder download button downloading only one file
- (GL #1129) Fix shared folder uploads and downloads in the new upload implementation (follow-up)
- Fix possible prototype pollution vector in upload/download workers
- (GL #1149) Fix headers no getting copied when replicating a container
- (GL #1154) Fix session cookie not getting properly clear on invalidation
- (GL #1160) Fix large uploaded file (> 5 GiB) showing wrong size in the UI
- (GL #1165) Fix download function not working reliably in Firefox
- (GL #1173) Fix new upload regressions in congested conditions

### Removed

- (GL #944) Unused views and components
  - views
    - `swift_browser_ui_frontend/src/views/Dashboard.vue`
    - `swift_browser_ui_frontend/src/views/DirectRequest.vue`
    - `swift_browser_ui_frontend/src/views/DirectShare.vue`
    - `swift_browser_ui_frontend/src/views/ShareRequests.vue`
    - `swift_browser_ui_frontend/src/views/SharedFrom.vue`
    - `swift_browser_ui_frontend/src/views/SharedTo.vue`
- (GL #944) Buefy dependency

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

[unreleased]: https://gitlab.ci.csc.fi/sds-dev/sd-connect/swift-browser-ui/-/compare/2024.01.0...main
[2024.02.0]: https://gitlab.ci.csc.fi/sds-dev/sd-connect/swift-browser-ui/-/compare/2024.01.0...2024.02.0
[2024.01.0]: https://gitlab.ci.csc.fi/sds-dev/sd-connect/swift-browser-ui/-/compare/3.0.0...2024.01.0
[2023.12.0]: https://gitlab.ci.csc.fi/sds-dev/sd-connect/swift-browser-ui/-/compare/v2.0.0...3.0.0
