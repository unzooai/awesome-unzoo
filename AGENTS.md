# Repository maintenance

This is a binary distribution repository, not a source mirror. Keep all application source code out. Repository maintenance scripts and their tests are allowed.

- Register real software in `software.json` before publishing. Do not create sample software entries or fake releases.
- Tag releases as `<software-id>/v<version>` and publish assets through `scripts/distribute.py`. Never replace existing published binaries or retag an old release.
- Validate package identity, version, platform and signature as applicable before publishing. Do not claim a package is signed or device-tested without evidence.
- Keep installers in ignored `inbox/` or outside the repository. Never stage binaries, credentials, signing keys or local release notes wholesale.
- README catalog markers and `catalog.json` are generated from GitHub Releases. Use `python3 scripts/distribute.py sync` to update them.
- Check `python3 -m unittest discover -s tests -v`, `python3 scripts/distribute.py check`, and `git diff --check` before committing.
- When a user requests a release with the package path and version, carry out registration, upload, publication and catalog verification within that authorization. Ask only for genuinely missing package details or required authentication.
