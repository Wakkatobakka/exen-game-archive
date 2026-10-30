# Metadata dictionary

`catalog.json` is the source of truth. The CSV is generated from it.

| Field | Meaning |
|---|---|
| `id` | Stable URL slug; used to build `games/<id>/` |
| `title` | Title in the ExEn browse listing |
| `year` | Year displayed *for the ExEn listing* (not necessarily the page's primary edition) |
| `platform` | ExEn |
| `genre`, `publisher`, `developer` | Optional factual metadata; `null` means **not verified for this index** |
| `note` | Optional original editorial observation grounded in source metadata |
| `source_name`, `source_url`, `source_collection_url` | Linked page and collection provenance |
| `source_reviewed` | Date the indexed reference was reviewed |
| `evidence_level` | `catalog-listing` until stronger evidence has been recorded |
| `package_inspected` | Whether package bytes were actually inspected |
| `package_filename` | Exact filename from inspected package, if verified |
| `package_size_bytes` | Exact observed size in bytes, if verified |
| `sha256` | SHA-256 from inspected bytes, if verified |
| `runtime_tested`, `runtime_result` | Explicitly scoped execution test, not the presence of a file |

`null` does not mean a fact does not exist; it means it is not established in this project. **Do not invent checksum hashes, byte sizes, device support, or tested status.**

The current site generator intentionally asserts that none of the current records are package-inspected. Before introducing actual verified package records, update the generator's evidence rendering, summary statistics and assertions to handle verified and unverified entries separately. Do not merely toggle a JSON flag.
