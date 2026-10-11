# Community page spec (The Legacy Team site)

Each community is one file: content/communities/<slug>.md — YAML front matter, then a markdown body.

```
---
name: Milton                      # display name
slug: milton
region: north-atlanta             # north-atlanta | lake-lanier | mountains
lead: both                        # britney | karen | both  (who leads this market)
county: Fulton County
seo_title: "Milton GA Luxury Homes & Estates | The Legacy Team"   # <= 60 chars, must end "| The Legacy Team"
description: "..."                # meta description, 130-155 chars, mentions The Legacy Team
headline: "..."                   # H1, 4-9 words, includes the place name and "Georgia" or "GA"
lede: "..."                       # 1-2 sentences, max 45 words
price_note: "..."                 # one short sentence on price range, ONLY from source facts
known_for: ["...", "...", "..."]  # exactly 3 short phrases (2-5 words each)
neighborhoods:                    # 4-6 items
  - name: "..."
    text: "..."                   # 1-2 sentences
faqs:                             # 4-5 items
  - q: "..."
    a: "..."                      # 2-4 sentences
nearby: [alpharetta, roswell]     # 3-4 slugs from the allowed list
---
Three paragraphs of body copy in markdown (roughly 70-110 words each). No headings in the body.
```

Allowed slugs: buckhead, brookhaven, chamblee, sandy-springs, norcross, duluth, roswell, johns-creek,
alpharetta, milton, cumming, buford, flowery-branch, gainesville, lake-lanier, dawsonville, dahlonega, blue-ridge

## Rules
1. FACTS: every factual claim (prices, schools, neighborhood names, distances, history, amenities, regulations)
   must come from the source HTML page(s) for that community. Do not add facts from your own knowledge. If the
   source doesn't say it, leave it out.
2. ORIGINAL WORDING: this is a third website; Google must not see it as a copy. Do not reuse any sentence from the
   sources. Restructure, reorder, and rewrite everything in fresh language. Different FAQ question wording too.
3. VOICE: first person plural ("we") — The Legacy Team, a mother-daughter team: Karen Hilliard (luxury, Lake Lanier,
   mountains, land; construction-management background; 12+ years living on Lake Lanier) and her daughter Britney
   Javens (North Atlanta and intown; home flipping/renovation background). Both are Realtors with Keller Williams
   North Atlanta. Name whichever agent leads the market where natural ("Britney leads our Buckhead work").
   Tone: quiet confidence, specific, plain verbs. Luxury through restraint — no hype words ("stunning", "dream
   home", "nestled", "boasts", "unparalleled"), no exclamation marks, no ALL CAPS, no em-dash-heavy sentences.
4. Angle: emphasise the upper end of each market and the advantage of two agents covering the whole corridor from
   Buckhead to Blue Ridge, where it fits naturally. Don't force it into every paragraph.
5. YAML must be valid: wrap every string value in double quotes; escape inner double quotes or use single
   apostrophes; no tabs.
6. No phone numbers, emails, or URLs in the content (the template adds them).
