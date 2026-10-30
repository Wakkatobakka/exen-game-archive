# Contributing to the ExEn Archive

This is an evidence-led mobile history index, not a ROM distribution repository. Please contribute corrections, original research, and verifiable file metadata without uploading game binaries.

## Corrections to a listing

Open a GitHub issue or pull request identifying the game record, exact proposed correction, source URL, and what that source establishes. Differentiate the **ExEn release** from J2ME and other versions. If sources disagree, record the conflict rather than guessing.

## Package inspection evidence

Only mark `package_inspected` as `true` after a reviewer actually handles a lawfully obtained candidate file and records, at minimum:

1. Exact original filename and any original source path.
2. File byte count (not merely a rounded download-size label).
3. SHA-256 checksum of the actual bytes examined.
4. What was inspected (archive members, headers, ExEn indicators), including how the ExEn edition was identified.
5. Evidence date, source, and reviewer notes. Mark game runtime/playability as **untested** unless a concrete test was conducted.

Do not claim a particular ExEn version, handset compatibility, or working gameplay from the existence of a third-party page alone.

## Rights and link rot

Do not submit copyrighted games, extracted artwork, proprietary manuals, or website descriptions copied from other catalogs. Use factual metadata, original text, and relevant citations. Broken links should be retained as historical references with an explicit note until a supported replacement can be established. A missing link does not mean the game never existed.

## Build and check

`python3 scripts/build.py` regenerates the static pages and machine-readable CSV from `data/catalog.json` using the Python standard library. Run the site's checks after any catalog updates and commit regenerated files together with the JSON. The original `scripts/seed_data.py` is not to be rerun.
