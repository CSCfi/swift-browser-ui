# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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

### Fixed
- Double navigation to the UploadView (GH #473)
- GH #476 CORS error headers fix
    - add CORS headers to error HTTP responses as well
    - handle test chunk uploaded request as `204` instead of `404` as recommended by https://github.com/23/resumable.js#handling-get-or-test-requests
    - remove forgotten console.logs

### Removed
- The possibility to share containers with write-only (file drop) permissions (GH #475)
- GH #493 redesign upload UI 
    - alignment in edit view of containers & objects
    - copy container view as it was driving my ocd wild as well
    - sharing view button positioning
    - fix issue with accessing ws on devserver

[Unreleased]: https://github.com/CSCfi/swift-browser-ui/compare/1.1.0b8...devel