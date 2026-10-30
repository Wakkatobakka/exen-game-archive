# ExEn / The Lost Catalog

**The platform faded. The catalog shouldn't.**

A searchable index of 46 ExEn game listings, with individual game pages and a source trail for every title. Part of Wakka's early mobile preservation archive, alongside [Qualcomm BREW](https://wakkatobakka.github.io/qualcomm-brew-archive/) and [Zeebo](https://wakkatobakka.github.io/zeebo-archive/).

[**Browse the archive →**](https://wakkatobakka.github.io/exen-game-archive/) · [Original ExEn listings](https://www.myabandonware.com/browse/platform/exen/) · [Sources & methods](data/SOURCES.md)

![ExEn Archive — 46 listings from early mobile history](assets/social-preview.png)

## What's here

- **46 game records**, from 2001–2006, each with its own page and original source link.
- Search by title, developer, publisher, year, or genre; filter by year and genre; sort alphabetically or chronologically.
- Featured titles, platform history, research notes, and links to the BREW and Zeebo archives.
- Downloadable [CSV](data/catalog.csv) and [JSON](data/catalog.json) catalogs.
- Static HTML that works without a framework, server, API key, or external script. All records remain visible with JavaScript disabled.
- Reproducible Python build and verification scripts using only the standard library.

The starting point is **My Abandonware's ExEn directory**, rather than a supplied collection of game packages. These are documented listings; original packages have not been inspected or tested for this index. Credits and genres are included where recorded in the supplied research, and unknown details remain open. The catalog does not claim to cover every ExEn game ever released.

## Put it on GitHub

Repository name: **`exen-game-archive`**  
Account: **`Wakkatobakka`**

1. Extract the ZIP. Open the **`exen-game-archive`** folder inside it.
2. Create a new public GitHub repository named **`exen-game-archive`**. Leave its automatic README, license, and gitignore options unchecked; this package includes them.
3. Copy the extracted folder's **contents** into the repository folder. `index.html`, `assets/`, `games/`, `about/`, `data/`, and `scripts/` should sit directly in the repository root.
4. Commit and push to **`main`**. With GitHub Desktop, open the repository folder, copy the contents into it, commit, and click **Push origin** or **Publish repository**, as appropriate.
5. On GitHub, open **Settings → Pages → Deploy from a branch → main → /(root) → Save**.

After GitHub finishes deploying, the archive address is:

**https://wakkatobakka.github.io/exen-game-archive/**

The ZIP itself is a delivery package. Extract it before adding the files to GitHub. Uploading only the ZIP does not publish the site.

To preview before publishing, open `index.html`. Links between the included pages use explicit HTML filenames so they work locally as well as on GitHub Pages. Download buttons may open their file instead of saving it in some local browsers.

## Update a record

Edit **`data/catalog.json`**, then run:

```sh
python3 scripts/build.py
python3 scripts/verify.py
```

No third-party Python packages are needed. The build regenerates the homepage, individual records, About page, CSV export, sitemap, and 404 page. The verifier checks all 46 records, CSV/JSON agreement, record-page coverage, and local links and anchors. Keep metadata changes in JSON rather than editing generated pages or CSV directly.

`source_reviewed` records the date of the underlying research. A site rebuild does not represent a fresh source review. `scripts/seed_data.py` is the historical initialization script: rerunning it overwrites the catalog, so use `build.py` for updates.

If the GitHub account or repository name changes, update `BASE` and `GITHUB` in `scripts/build.py`, rebuild, and update these instructions.

## Credits and corrections

Original listing source: [My Abandonware — ExEn](https://www.myabandonware.com/browse/platform/exen/), reviewed for the supplied research on October 29, 2026. Each game links back to its source record. Full references are in [data/SOURCES.md](data/SOURCES.md).

Found a missing credit, wrong date, or new package evidence? Open a [catalog correction](https://github.com/Wakkatobakka/exen-game-archive/issues/new?template=catalog-correction.yml) and include the title, correction, and supporting reference. See [CONTRIBUTING.md](CONTRIBUTING.md) and [data/SCHEMA.md](data/SCHEMA.md).

Independent catalog by Wakkatobakka. No affiliation with In-Fusio, My Abandonware, or original rights holders. This repository contains original site code and metadata; game files, source-site prose, and original game artwork are not bundled. The [MIT license](LICENSE) covers original site code, not third-party games or trademarks.
