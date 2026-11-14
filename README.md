# Zac Volheim — Portfolio v3

A static, responsive journalism/filmmaking portfolio. No traditional server is necessary.

## Preview

Open `index.html` in a browser. The three built-in latest-story cards appear even without a server. For local dynamic JSON loading, run `python -m http.server 8000` in this folder and visit `http://localhost:8000`.

## Publish with GitHub Pages (free static hosting)

1. Create a GitHub repository (e.g. `zac-volheim-portfolio`). Upload **all** the contents of this folder, including `.github/workflows` and `assets/`.
2. In GitHub: **Settings → Pages → Build and deployment → Deploy from a branch**, select `main` and `/ (root)`.
3. In **Actions**, allow workflows. Run **Refresh latest KPAX stories** manually once using **Run workflow** and inspect its logs.
4. The workflow attempts a refresh twice a day. It extracts candidate KPAX links from a public article index and verifies KPAX byline and publication date. If the source blocks access or fewer than three articles are verifiable, it **keeps the last confirmed three** instead of publishing guesses. This is a best-effort adapter, not a guaranteed live KPAX API.
5. To use `zachvolheim.com`: In GitHub **Settings → Pages → Custom domain**, enter `zachvolheim.com`; configure your registrar's DNS exactly as GitHub Pages instructs. Allow time for DNS/HTTPS provisioning. Don't change your domain's mail records.

## What's ready

- Approved dark/rose-gold homepage with the user's own photos and introduction
- Three selected KPAX stories with verified direct links
- Dynamic latest-three section (`data/latest.json`) with verified static fallback
- *Plastics Are Silly* YouTube embed and updated description
- *As the Crow Flies* crediting Zac Volheim and Evan Stephens (public video link still needed)

## Feed mechanism and limitations

GitHub Actions does the fetching (server-side), commits `data/latest.json`, and GitHub Pages serves the file. There is no need for a running server or API key. A visitor sees the last successfully fetched snapshot, not an instantaneous read of KPAX. The Muck Rack index and KPAX markup can change and may block automated requests; check Actions logs periodically, and switch to an official publication feed if one becomes available. Public indexing may lag article publication.

To add a fixed story manually, edit `data/latest.json` with exactly three items containing `title`, `date` (YYYY-MM-DD), and `url` on www.kpax.com. The next verified refresh may overwrite it.

## Article photography

The featured reporting cards use the original lead images hosted on KPAX/Scripps. The three current Latest from KPAX stories also use their article images; future feed updates attempt to read their verified `og:image` metadata. All these images load from KPAX/Scripps (rather than being repackaged) and may disappear or block hotlinking if the publisher changes access. The newsroom photo inset is recropped to center Zac.

Version 4: As the Crow Flies now embeds the supplied YouTube video (B57Sy0tMBvI), with a direct YouTube fallback link. Embedding depends on the video owner’s YouTube settings.

## Video thumbnails (V5)

Film thumbnails are local JPG stills extracted from the supplied original videos. They link directly to the public YouTube films rather than embedding YouTube players; this avoids video configuration errors when opening the site locally, and avoids depending on YouTube embedding permissions. Film playback occurs on YouTube in a separate tab.
