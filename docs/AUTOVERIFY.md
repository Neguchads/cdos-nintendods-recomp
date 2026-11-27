# AutoVerify — published release pilot

This manual, read-only workflow verifies one published release asset from this
repository. It does not rebuild, execute, unpack, modify or publish the game.
No automatic file upload to VirusTotal is supported.

## Activation

After the pull request and the pinned Core revision are independently reviewed,
merge the approved workflow. In Actions > AutoVerify published release
(manual pilot), choose Run workflow on main:

- release_tag: the exact published release tag (for example v1.3.0).
- asset_name: the exact asset filename in that release, without a directory.
- expected_sha256: an independently verified lowercase SHA-256 from a trusted
  release manifest or local build record, not an arbitrary untrusted value.
- lookup_public_noncommercial: false for the first integrity-only smoke.
  Set true only for a public, authorized, non-commercial artifact, in accordance
  with VirusTotal terms and after configuring VT_API_KEY as a repository secret.

The workflow requires the GitHub asset digest to match the expected SHA-256,
rejects draft releases and assets above 1 GiB, downloads the exact named asset,
and checks its bytes and length before any optional external lookup. Missing
digest is a failure, not a bypass. The local mode uses GitHub but does not
contact VirusTotal. The exact tested Core commit is
24d3cf694217a9fe9ebb8a65466fef423bdfb69a (PR #36); its offline CI passed.
Review that commit and any later changes before enabling external lookup.

Only integrity.json and virustotal.json are retained as Actions reports.
Zero detections do not prove safety. Unknown hashes, stale reports, errors
and detections require review; no release approval is granted. The workflow
does not replace a local antivirus, SBOM or artifact provenance check.

The public API permits non-commercial use only, not commercial products or
services or business workflows that do not contribute new files. It must not
substitute for an antivirus. Respect the account's 4 requests/minute and
500/day limits (and any monthly quota); concurrency is repository-local.
Never share private or sensitive hashes, ROMs, BIOS or unauthorized game
materials. Do not disclose the secret or create additional accounts to evade
limits. Do not enable this workflow for commercial use.

References: [VirusTotal API conditions](https://docs.virustotal.com/reference/public-vs-premium-api),
[getting started](https://docs.virustotal.com/reference/intro/getting-started),
[NAVI Core PR #36](https://github.com/Neguchads/navi-core/pull/36).

## Acceptance

Unit tests cover asset metadata validation, identity, size and digest.
The real release download and the authenticated optional lookup are separate
manual acceptance steps. A passing CI is not a successful real scan.
