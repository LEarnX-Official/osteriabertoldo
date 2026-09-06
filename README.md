# Osteria il Bertoldo — redesign

Light, immersive redesign of [osteriabertoldo.com](https://www.osteriabertoldo.com/):
aged-paper colour grading, letterpress typography, and a CSS-driven animation
layer. **No 3D and no dependencies** — the page ships nothing but HTML, CSS and
two plain scripts.

Open `site/index.html` **through a web server** (it works from `file://` too,
but a server matches production):

```bash
cd osteriabertoldo
python3 -m http.server 8765
# → http://localhost:8765/site/index.html
```

---

## Design system — "Carta d'Epoca"

A light grade: the room's oxblood and brass printed onto aged paper rather than
sunk into candlelight. Drawn from the same dining room — the red feature wall
with the gold motif, exposed brick, timber beams, terracotta floors.

| Token | Value | Source |
|---|---|---|
| Paper | `#F5EFE2` | aged cream — the page |
| Paper 2 | `#EFE7D6` | alternating leaf, banded sections |
| Paper 3 | `#E7DCC6` | pressed panel, marquee, footer |
| Card | `#FBF7EE` | fresh leaf, raised surfaces |
| Ink | `#2A231C` | warm printing ink, headings |
| Ink soft | `#5C5044` | body copy |
| Muted | `#8B7D6B` | faded pencil |
| Ink deep | `#171310` | the dark bands: dish scenes, reviews |
| Primary | `#8B1A1A` | oxblood, the feature wall |
| Accent | `#9A7B21` | antique brass, darkened to hold on cream |

Headlines **Playfair Display** 600 (italic oxblood for the display line), body
**Source Sans 3** at 17px, 3px radii. Playfair is wider and lower-contrast than
a Didone, so it holds up over photographs and on the dark bands where hairline
serifs would break up.

---

## Files

```
home.html       the restaurant's ORIGINAL site, saved for reference only —
                © World Web Design, included to compare against, not reused
site/
  index.html    markup, Restaurant JSON-LD
  style.css     the whole design system + the vintage layer
  content.js    ALL copy, IT + EN  ← edit this to change text
  icons.js      24 hand-drawn ingredient illustrations (inline SVG)
  app.js        rendering, language switch, nav, booking form,
                and the animation layer
images/         scraped from the current live site
```

The old 3D build's `models/` and `renders/` folders have been removed. They are
preserved in `models-3d-archive.tar.gz` (2.8MB) in case the Blender sources are
ever wanted again — the site itself references nothing in them.

`images/original/` holds the untouched source photographs. It is a **local
backup and should not be deployed** — only `images/blog/` and `images/home/`
are served.

### Why the ingredient icons are drawn, not photographed

Line art in the site's brass palette carries no licensing risk, costs no extra
network requests, stays sharp at any size, and matches the engraved/vintage
grade far better than stock photography would. Each ingredient in `content.js`
names an `icon` key, and IT/EN share one drawing. To add one: draw the paths in
a `0 0 50 50` viewBox in `icons.js`, then reference its key.

### Images

Every photograph is served as **WebP with a JPEG fallback** via `<picture>`,
and the hero uses CSS `image-set()`. The originals were dramatically
over-compressed for their pixel dimensions — `home7.jpg` was 578KB for a
700x550 image — so they were re-encoded at quality 82 (JPEG) / 80 (WebP):

| | before | after |
|---|---|---|
| total | 2223KB | **380KB** (WebP) |
| home7 | 578KB | 105KB |
| blog4 | 335KB | 63KB |

That is an **83% cut** with no visible loss at the sizes they display. Every
`<img>` also carries explicit `width`/`height` so nothing shifts as it loads.

To re-run after replacing a photo:

```bash
magick images/original/NAME.jpg -strip -quality 82 -sampling-factor 4:2:0 -interlace Plane images/blog/NAME.jpg
magick images/original/NAME.jpg -strip -quality 80 -define webp:method=6 images/blog/NAME.webp
```

**Payload:** HTML + CSS + JS is ~60KB uncompressed, plus the fonts and whichever
photographs are in view. There is no library to download and nothing is fetched
at runtime beyond the images. Verified in headless Chrome — the only requests
the page makes are its own two scripts and the images.

---

## The animation layer

Everything moves in CSS; `app.js` only toggles classes and feeds a single
`requestAnimationFrame` loop, so nothing lays out on a scroll event.

1. **Loader** — an ink monogram whose brass ring and "B" draw themselves with
   `stroke-dashoffset`, then lift to reveal the page
2. **Hero** — the interior photograph sits behind a paper veil and an engraved
   plate border; it drifts slower than the page on scroll and leans toward the
   cursor. The headline rises line by line out of a mask, then the eyebrow,
   rule, subtitle and buttons follow on a stagger
3. **Marquee** — a running printed banner of the four pillars, paused on hover
4. **Dish scenes** — each of the six dishes owns a full-bleed dark band that
   alternates side to side. A blurred, darkened blow-up of the dish photo fills
   the band; the sharp photo sits inset in a framed plate with a brass ring that
   draws itself on scroll, beside an outlined numeral and a large Bodoni name.
   The plate leans toward the pointer, and each backdrop drifts against the page.
   **Clicking a plate shatters it in 3D**: the photo breaks into a 7x7 grid of
   49 shards inside a 900px perspective. Each flies outward *and toward the
   viewer* in z, tumbling on all three axes - centre shards come furthest
   forward, so the plate bursts rather than slides. Underneath, each ingredient
   flips in on its Y axis beside a drawn icon and a short nutrition note.
   Click again to reassemble. Shards are built lazily on first open and reuse
   the image already on screen, so nothing extra loads
5. **Scroll reveal** — an IntersectionObserver stages sections, pillar rules,
   and a curtain wipe across every framed photograph
6. **Reviews** — a dark stage: italic Bodoni quotes over a giant ghost quote
   mark, brass source labels, hairline rules instead of cards
7. **Menu filter** — chips filter the menu by gluten-free, fish, meat or
   vegetarian; sections with nothing left collapse, and the choice persists in
   `localStorage`. The coeliac kitchen is a genuine selling point, so it gets a
   control rather than a small tag
8. **Chrome** — a scroll-progress rail, a warm lamp pool trailing the cursor
   with inertia, buttons that lean toward the pointer and fill with an ink wipe,
   and a nav that hides going down and returns coming up

### It always degrades

Under `prefers-reduced-motion: reduce` every animation and transition is cut,
the loader is skipped, reveals are shown at rest, the marquee stops and the
cursor lamp is removed. Pointer-driven effects (lamp, tilt, magnetic buttons)
are only armed for `(hover:hover) and (pointer:fine)`, so touch devices never
pay for them.

Verified in headless Chrome: **0 console errors and no horizontal overflow** at
1440px and 390px, in both the default and reduced-motion paths.

---

## ⚠️ Before this goes live

1. **Confirm the ingredient notes.** `content.js` -> `piatti.items[].ing` in
   both `it` and `en`. These are accurate general nutrition facts, but they are
   written by us, not by the kitchen, and the ingredient lists are inferred from
   the placeholder dish names. Each panel shows a visible "sample text" notice
   until they are confirmed - remove `piatti.ingNote` once they are.
   Keep the wording nutritional ("source of iron"), not therapeutic: EU rules
   on health claims for food are strict.
2. **Replace the placeholder menu.** `content.js` → `menu.sections` in both
   `it` and `en`. Dish names and prices are plausible Veronese/seafood
   inventions, **not** the restaurant's real menu. The page shows a visible
   "sample menu" notice until they are replaced — remove `menu.note` once the
   real dishes are in.
3. **Point the booking form at a real backend.** It currently composes a
   pre-filled `mailto:` to `osteriabertoldo@gmail.com`, which matches how the
   restaurant takes bookings today (phone and email only). Swap the submit
   handler in `app.js` for a real endpoint when one exists.
4. **Reshoot the dishes.** The existing photos are 534×534 phone snaps — fine
   behind a 3D popup, thin on their own and in the gallery.
5. **Photograph the *cappuccino di polipo*.** Reviewers single it out as "a
   revelation" and there is no picture of it anywhere. It is currently in the
   menu but not in the dish cards, because there is no image for it.
6. **Confirm the English copy** with the owners before publishing.
7. **Delete `models/` and `renders/` when you are happy.** They are the
   remains of the earlier 3D build and nothing links to them any more.

## Fixed from the old site

- The **menu link that 404'd** — there is now a real menu page
- The **stale "Chiusi 24–29 Gennaio 2026" popup** that kept firing after the
  date passed — replaced by a self-expiring `NOTICE` object in `content.js`
  (`active: false`, and it hides itself past `until` regardless)
- **Italian-only** — now bilingual IT/EN, remembered per visitor
- **No online booking** — now a real form
- **No structured data** — now `Restaurant` JSON-LD, OpenGraph, Twitter cards,
  canonical, `hreflang` IT/EN alternates, `robots.txt` and `sitemap.xml`
- **2.2MB of oversized photographs** — now 380KB of WebP with JPEG fallback
- **No keyboard skip link** — now present, and translated
- **Duplicate/composite images** — `home3.jpg` (a crude two-photo composite)
  is no longer used
- **The heavy 3D layer** — Three.js and ten `.glb` models are gone; the page is
  now dependency-free and the motion is all CSS
