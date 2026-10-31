# Preview releases

The current local package is 0.1.0-31. Commit the intended session changes only
after review; do not tag the initial repository commit as this updated package.
Use an annotated v0.1.0-31 tag on the reviewed commit. Preserve the experimental
preview designation. Existing GNOME packages and ISO settings are independent.

The preview workflow builds the panel helper first, installs it in a disposable
container and builds/tests the session. It preserves source and dependency
checks and creates a draft prerelease. A failure caused by newer rolling Arch
dependencies must be investigated rather than bypassed with --nodeps/--nocheck.

Review RELEASE-CHECKLIST.md and THIRD_PARTY.md. Graphical acceptance and artwork
provenance review remain separate from automated tests. Download the build
artifacts, verify SHA256SUMS and SOURCE-REVISION.txt, sign both packages locally
and attach them with their .sig files. Publish manually only after that review.
The preview must not be marked as the latest stable desktop release.
