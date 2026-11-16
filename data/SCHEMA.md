# ExEn archive data dictionary

## catalog.json / catalog.csv

The original 46 ExEn catalog records retain their ids, title, source-listed year, platform, genre, publisher, developer, note, source name and URLs. `source_reviewed` records the research date. `evidence_level`, `package_inspected`, `package_filename`, `package_size_bytes`, `sha256`, `runtime_tested` and `runtime_result` describe the original-file record. These do not imply that a game has been tested.

`year` is the catalogued ExEn date. A documented earlier release can be displayed by an editorial record without overwriting the source’s bibliographic value. Crash uses its 2002 French release on the website and retains the later US 2005 listing here.

## research.json

- `version`: current editorial format, 3.0.
- `reviewed`: research review date.
- `premise`: the archive’s purpose.
- `sources`: reference objects, keyed by stable source id.
- `games`: records keyed by existing catalog id.
- `platform`: sourced sections for platform history.

Each source has `title`, `url`, `kind`, `published` (date or null), `reviewed` and `note`. Its URL should lead to the actual reference, not a search query. Source ids are used for numbered citations and backlinks.

Each game retains `summary`, `summary_sources`, `reviewed`, `sections`, `credits`, `studio_roles`, `questions` and `status` for existing consumers. `sections` mirrors the current public summaries; it is not a separate historical narrative. `questions` may be empty. `status` is a legacy research category, not a playability label.

### entry

- `deck`: short factual description used as the page introduction and catalog-card text.
- `overview`, `development`, `release`, `notes`: ordered paragraph arrays. Each item has `text` and a nonempty array of source ids in `sources`. An optional `after_quote: true` places a reception paragraph after the quotation. Empty arrays are valid.
- `quotes`: exact excerpts with `text`, `speaker`, `attribution`, `translation` (label or null), `section` (`development` or `reception`) and `source`. A translated quotation identifies its translator or reproduction source.
- Optional `hero_facts`: explicit label/value pairs where original and adaptation studios need to be distinguished.
- Optional `display_year`: a source-specific date label.
- Optional `sort_year`: the documented year used by catalog cards, filters and sorting. Defaults to the original catalog year.

Use a direct quotation only after checking the wording. Keep paraphrases outside quotation marks. Do not infer a toolchain, engine or development schedule from a credit roll.

### credits and studio_roles

Personal credits have `name`, `role`, `team`, `source` and `scope`. Preserve the relevant edition or interview scope. Several roles can belong to one person. The website combines those roles for display while retaining all records in `credits.csv`.

Studio roles have `name`, `role` and `source`. Original development, ExEn adaptation, licensing, publishing, artwork and distribution may refer to different companies. The creator index and related-game links are calculated from these records.

### media

Optional image records contain repository-relative `path`, `alt`, `caption`, `credit`, `source`, `original_url`, `kind`, `width`, `height` and `placement` (`game`, `development` or `gallery`). Screenshot records retain `platform` and `platform_evidence` where available.

Images must have source-page evidence tying them to the correct platform. Do not use a J2ME, BREW or console screenshot to stand in for an ExEn capture. Historical artwork and photographs are identified by publication rather than assigned an unverified artist or subject identity.

## Generated outputs

Run `python3 scripts/build.py` after edits. It generates all 52 HTML pages, `catalog.csv`, `credits.csv` and `sitemap.xml`. Run `python3 scripts/verify.py` to check data references, media, exports, routes and local anchors.
