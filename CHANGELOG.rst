=========
Changelog
=========


0.9.1 (2026-07-30)
==================

Improved session management, UI experience, branding, and stability.

**New features**

* `SESSION_COOKIE_AGE` environment variable can now be used to specify the session lifetime.
* `SESSION_EXPIRE_AT_BROWSER_CLOSE` environment variable can now be used to specify whether a user's session should end
  when the browser closes.
* Added a global loading spinner in the sidebar to indicate when the application is loading.
* Added automatic redirection to the login page when a user's session has expired.
* Added support for the new branding, including the updated logo in the frontend, admin interface, documentation, and README files.
* Updated the manual with the new styling.

**Bug fixes**

* Fixed CSP errors by fetching selectielijstklasse resultaten through the BFF instead of directly from the service.
* Fixed an issue where the "more fields" button was shown when no additional fields were available.
* Fixed broken breadcrumbs.
* Fixed missing keys for the loading spinner.

**Project maintenance**

* Fixed various deprecation warnings.
* Updated various dependencies.


0.9.0 (2025-11-07)
==================

Initial release.
