# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- GH #493 redesign upload UI
    - let users know when keys are added by default
    - compute sha256 of key instead of showing text
- add `defaultKeyMessage` to `lang.js` #494

### Changed
- **BREAKING** Rename code occurrences of *bucket* to *container* (GH #471)
- Updated dependencies in front-end as well as node.js base image to `node:14.18.3-alpine3.15`
- Redirect to front page when the session has expired. (GH #461)
- Hide most errors from the browser's console. (GH #461)
- Updated node.js base image to `node:16.13.2-alpine3.15`
- update materialdesing icon link
- update browsers list with `npx browserslist@latest --update-db`
- add margin to top footer for clearer division between content and footer
- redesign upload view as specified in issue #479
- GH #493 redesign upload UI 
    - alignment in edit view of containers & objects
    - copy container view, sharing view and token view make it consistent with other views
    - key existence should be checked with `$te` https://kazupon.github.io/vue-i18n/api/#vue-injected-methods
    - check public key exists already before adding to the table


### Fixed

- Double navigation to the UploadView (GH #473)
- GH #476 CORS error headers fix
    - add CORS headers to error HTTP responses as well
    - handle test chunk uploaded request as `204` instead of `404` as recommended by https://github.com/23/resumable.js#handling-get-or-test-requests
    - remove forgotten console.logs
- fix issue with accessing ws on devserver #493
- fix logic for disabling/enabling button for encryption, fix removal of public keys and fix upload encryption options selector positioning #494

### Removed

- The possibility to share containers with write-only (file drop) permissions (GH #475)
- GH #493 redesign upload UI 
    - removed vue-material-design-icons 

[Unreleased]: https://github.com/CSCfi/swift-browser-ui/compare/1.1.0b8...devel