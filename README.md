# The Legacy Team website

Team site for Karen Hilliard and Britney Javens (Keller Williams North Atlanta).
Static HTML, built by one Python script and deployed to GitHub Pages by GitHub Actions.

## Build

    pip install -r requirements.txt
    python build.py              # production build into _site/
    python build.py --preview    # relative links, opens from any folder: _preview/index.html
    python build.py --future     # include journal posts dated in the future

## Where things live

| What | Where |
|---|---|
| Domain, phones, emails, IDX links, form endpoints, GA4 ID, community order | `site.yml` |
| Community pages (18) | `content/communities/<slug>.md` |
| Journal posts | `content/journal/YYYY-MM-DD-slug.md` |
| Page layouts and fixed-page copy | `templates/` |
| Styles, script, fonts, photos, video | `assets/` |

Add a community: create the `.md` file (spec in `content/COMMUNITY-SPEC.md`) and add its slug to a region in `site.yml`.

Schedule a journal post: give it a future `date`. The daily Action publishes it once that date arrives.

## Launch checklist

1. In `site.yml`: set `url` to the real domain, `base_path: ""` and `write_cname: true`. (Until then the site is a noindexed staging copy at westyn3.github.io/legacy-team/.)
2. Repo Settings > Pages > Source: GitHub Actions. Point DNS at GitHub Pages.
3. Add a GA4 ID to `site.yml`.
4. In Formspree, allow the new domain on both forms (Karen `mvkokeva`, Britney `xjglzlno`), or create a team form and swap the IDs in `site.yml`.
5. In Elfsight, allow the new domain on both review widgets.
6. Add the property to Search Console and submit `/sitemap.xml`.
7. Link to this site from both agent sites, both Google Business Profiles and legacyteam.kw.com.

## Lead routing

The contact form sends to Britney's Formspree form for North Atlanta and intown enquiries and to Karen's for
everything else. The mapping is the `data-agent` attribute on each option in `templates/_contact.html`.
