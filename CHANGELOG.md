# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- IndexedDB as local in-browser cache, with dexiejs as dependency.

### Changed
- **BREAKING** Rename code occurrences of *bucket* to *container* (GH #471)
- Updated dependencies in front-end as well as node.js base image to `node:14.18.3-alpine3.15`
- **BREAKING** swift-browser-ui doesn't work in Firefox's private mode, as it doesn't offer IndexedDB.
    - There is a warning message at login, and it is not possible to login in unsupported browsers.
- Improved performance by reducing number of requests after cache has been created.
    - While the cache is being created, there might be a degradation in performance for large projects.
    - Reduced number of requests for fetching object tags
- Search box in Container View now searches across all containers and objects in the project using IndexedDB.
    - There is no ranking. Containers are returned before objects in the order they are in the IDB.
    - The search is different from the filtering in objects list. Query has to match beginning of tag or beginning of words extrated from the name.
    - Adding more words to the search narrows down the results.
    - A message is shown when trying to search a large project before cache is created.

### Fixed
- Double navigation to the UploadView (GH #473)
- GH #476 CORS error headers fix
    - add CORS headers to error HTTP responses as well
    - handle test chunk uploaded request as `204` instead of `404` as recommended by https://github.com/23/resumable.js#handling-get-or-test-requests
    - remove forgotten console.logs


[Unreleased]: https://github.com/CSCfi/swift-browser-ui/compare/1.1.0b8...devel
