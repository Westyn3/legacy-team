#!/usr/bin/env python3
"""Build The Legacy Team site into plain static HTML.

    python build.py                 -> _site/  (production: absolute URLs, sitemap, robots)
    python build.py --preview       -> _preview/ (relative links, works from any folder or file://)
    python build.py --future        -> also publish journal posts dated in the future

Content:   content/communities/*.md, content/journal/*.md   (YAML front matter + markdown)
Settings:  site.yml
Templates: templates/*.html (Jinja2)
Needs:     pip install jinja2 pyyaml markdown
"""
import argparse
import datetime as dt
import json
import re
import shutil
from pathlib import Path

import markdown
import yaml
from jinja2 import Environment, FileSystemLoader, pass_context
from markupsafe import Markup

ROOT = Path(__file__).parent
TODAY = dt.date.today()


def read_md(path):
    raw = path.read_text(encoding="utf-8")
    _, fm, body = raw.split("---", 2)
    meta = yaml.safe_load(fm)
    meta["body_html"] = Markup(markdown.markdown(body.strip(), extensions=["smarty"]))
    return meta


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--preview", action="store_true")
    ap.add_argument("--future", action="store_true")
    args = ap.parse_args()

    site = yaml.safe_load((ROOT / "site.yml").read_text(encoding="utf-8"))
    site["url"] = site["url"].rstrip("/")
    site["year"] = TODAY.year
    site["total_reviews"] = sum(p["reviews"] for p in site["people"].values())
    out = ROOT / ("_preview" if args.preview else "_site")
    if out.exists():
        shutil.rmtree(out)
    out.mkdir()

    # ── Content ──────────────────────────────────────────────────────────
    communities = {}
    for f in sorted((ROOT / "content/communities").glob("*.md")):
        c = read_md(f)
        communities[c["slug"]] = c
    ordered = []
    for region in site["regions"]:
        region["items"] = [communities[s] for s in region["communities"]]
        for c in region["items"]:
            c["region_name"] = region["name"]
            img = site.get("community_images", {}).get(c["slug"])
            c["image"], c["image_alt"] = img if img else (region["image"], region["image_alt"])
            c["url"] = f"/{c['slug']}/"
            ordered.append(c)
    missing = set(communities) - {c["slug"] for c in ordered}
    assert not missing, f"communities not placed in a region in site.yml: {missing}"

    posts = []
    for f in sorted((ROOT / "content/journal").glob("*.md")):
        p = read_md(f)
        p["date"] = p["date"] if isinstance(p["date"], dt.date) else dt.date.fromisoformat(str(p["date"]))
        if p["date"] > TODAY and not args.future:
            continue
        p["slug"] = f.stem[11:] if f.stem[:4].isdigit() else f.stem
        p["url"] = f"/journal/{p['slug']}/"
        p["author_person"] = site["people"].get(p.get("author"))
        posts.append(p)
    posts.sort(key=lambda p: p["date"], reverse=True)

    # ── Template helpers ─────────────────────────────────────────────────
    env = Environment(loader=FileSystemLoader(ROOT / "templates"), autoescape=True, trim_blocks=True, lstrip_blocks=True)

    @pass_context
    def u(ctx, path):
        """Site-internal link. '/milton/' in production, a relative file path in preview."""
        if not args.preview:
            return path
        rel = path.strip("/")
        if "." not in rel.rsplit("/", 1)[-1]:
            rel = (rel + "/index.html").lstrip("/")
        return "../" * ctx["depth"] + rel

    @pass_context
    def a(ctx, path):
        return u(ctx, "/assets/" + path)

    def absu(path):
        return site["url"] + path

    def ld(obj):
        return Markup(json.dumps(obj, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/"))

    def longdate(d):
        return f"{d.strftime('%B')} {d.day}, {d.year}"

    env.globals.update(u=u, a=a, absu=absu, site=site, regions=site["regions"], communities=communities,
                       ordered=ordered, posts=posts, people=site["people"], preview=args.preview)
    env.filters.update(ld=ld, longdate=longdate)

    # ── Schema shared by every page ──────────────────────────────────────
    b = site["brokerage"]
    team_id = absu("/#team")

    def person(key):
        p = site["people"][key]
        return {"@type": "RealEstateAgent", "@id": absu(f"/team/#{key}"), "name": p["name"],
                "jobTitle": "Realtor", "telephone": p["tel"], "email": p["email"],
                "image": absu(f"/assets/img/{p['photo']}"), "url": absu("/team/"),
                "worksFor": {"@type": "Organization", "name": b["name"]},
                "memberOf": {"@id": team_id}, "sameAs": p["same_as"]}

    team_graph = [
        {"@type": "RealEstateAgent", "@id": team_id, "name": "The Legacy Team at Keller Williams North Atlanta",
         "alternateName": "The Legacy Team", "url": absu("/"), "image": absu("/assets/img/team.jpg"),
         "logo": absu("/assets/img/og.jpg"), "slogan": site["tagline"],
         "description": "Karen Hilliard and her daughter Britney Javens represent buyers and sellers of luxury homes, "
                        "Lake Lanier waterfront, mountain property and land from Buckhead to Blue Ridge, Georgia.",
         "telephone": site["people"]["karen"]["tel"], "email": site["people"]["karen"]["email"], "priceRange": "$$$",
         "address": {"@type": "PostalAddress", "streetAddress": b["street"], "addressLocality": b["city"],
                     "addressRegion": b["state"], "postalCode": b["zip"], "addressCountry": "US"},
         "geo": {"@type": "GeoCoordinates", "latitude": b["lat"], "longitude": b["lng"]},
         "areaServed": [{"@type": "Place", "name": f"{c['name']}, GA"} for c in ordered],
         "knowsAbout": ["Luxury real estate", "Lake Lanier waterfront homes", "North Georgia mountain homes",
                        "Equestrian estates", "Land and lot sales", "New construction", "Relocation to North Georgia"],
         "parentOrganization": {"@type": "Organization", "name": b["name"], "telephone": b["tel"]},
         "employee": [{"@id": absu("/team/#karen")}, {"@id": absu("/team/#britney")}],
         "sameAs": [site["social"]["instagram"], site["social"]["kw_team"],
                    site["people"]["karen"]["site"], site["people"]["britney"]["site"]]},
        person("karen"), person("britney"),
        {"@type": "WebSite", "@id": absu("/#website"), "name": site["name"], "url": absu("/"), "publisher": {"@id": team_id}},
    ]

    def crumbs_ld(trail):
        return {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": n, "item": absu(p)} for i, (n, p) in enumerate(trail)]}

    built = []  # (path, lastmod)

    def render(template, path, lastmod=None, noindex=False, trail=None, extra_ld=None, **ctx):
        """path is the public URL path, e.g. '/milton/'. trail = [(name, path), ...] for breadcrumbs."""
        file_rel = path.strip("/")
        file_rel = (file_rel + "/index.html").lstrip("/") if not file_rel.endswith(".html") else file_rel
        depth = file_rel.count("/")
        graph = list(team_graph)
        if trail:
            graph.append(crumbs_ld([("Home", "/")] + trail))
        graph += extra_ld or []
        html = env.get_template(template).render(
            path=path, depth=depth, canonical=absu(path), trail=trail or [], noindex=noindex,
            schema={"@context": "https://schema.org", "@graph": graph}, **ctx)
        if args.preview:  # markdown bodies carry root-relative links; make them relative too
            def fix(m):
                rel = m.group(1).strip("/")
                frag = ""
                if "#" in rel:
                    rel, frag = rel.split("#", 1)
                    frag = "#" + frag
                rel = rel.strip("/")
                if "." not in rel.rsplit("/", 1)[-1]:
                    rel = (rel + "/index.html").lstrip("/")
                return 'href="' + "../" * depth + rel + frag + '"'
            html = re.sub(r'href="(/[^"/][^"]*|/)"', fix, html)
        dest = out / file_rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(html, encoding="utf-8")
        if not noindex:
            built.append((path, lastmod or TODAY))

    # ── Pages ────────────────────────────────────────────────────────────
    render("home.html", "/")
    render("team.html", "/team/", trail=[("The team", "/team/")])
    render("buy.html", "/buy/", trail=[("Buy", "/buy/")])
    render("sell.html", "/sell/", trail=[("Sell", "/sell/")])
    render("luxury.html", "/luxury-homes/", trail=[("Luxury homes", "/luxury-homes/")])
    render("land.html", "/land-and-lots/", trail=[("Land and lots", "/land-and-lots/")])
    render("reviews.html", "/reviews/", trail=[("Reviews", "/reviews/")])
    render("contact.html", "/contact/", trail=[("Contact", "/contact/")])
    render("communities.html", "/communities/", trail=[("Communities", "/communities/")])
    render("404.html", "/404.html", noindex=True)

    for c in ordered:
        faq_ld = {"@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": q["q"], "acceptedAnswer": {"@type": "Answer", "text": q["a"]}} for q in c["faqs"]]}
        place_ld = {"@type": "Place", "name": f"{c['name']}, Georgia", "containedInPlace": {"@type": "AdministrativeArea", "name": c["county"]}}
        render("community.html", c["url"], c=c, trail=[("Communities", "/communities/"), (c["name"], c["url"])],
               extra_ld=[faq_ld, place_ld])

    render("journal.html", "/journal/", trail=[("Journal", "/journal/")])
    for p in posts:
        post_ld = {"@type": "BlogPosting", "@id": absu(p["url"]), "headline": p["title"], "description": p["description"],
                   "datePublished": p["date"].isoformat(), "dateModified": p["date"].isoformat(), "url": absu(p["url"]),
                   "image": absu("/assets/img/" + p.get("image", "og.jpg")), "mainEntityOfPage": absu(p["url"]),
                   "author": {"@id": absu(f"/team/#{p['author']}")} if p["author_person"] else {"@id": team_id},
                   "publisher": {"@id": team_id}}
        render("post.html", p["url"], p=p, lastmod=p["date"], trail=[("Journal", "/journal/"), (p["title"], p["url"])], extra_ld=[post_ld])

    # ── Static files ─────────────────────────────────────────────────────
    shutil.copytree(ROOT / "assets", out / "assets")
    (out / ".nojekyll").write_text("")
    if not args.preview:
        urls = "".join(f"  <url><loc>{absu(p)}</loc><lastmod>{d.isoformat()}</lastmod></url>\n" for p, d in built)
        (out / "sitemap.xml").write_text(
            f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}</urlset>\n')
        (out / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {absu('/sitemap.xml')}\n")
        if site.get("write_cname"):
            (out / "CNAME").write_text(site["url"].split("//", 1)[1] + "\n")

    print(f"Built {len(built)} indexable pages ({len(ordered)} communities, {len(posts)} journal posts) into {out.name}/")


if __name__ == "__main__":
    main()
