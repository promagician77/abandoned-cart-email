# Abandoned cart email - working draft

Deploy this folder to Vercel ("Other" preset, no build command). Everything on the page comes from `build/`.

## Rebuild
```
cd build
pip install django pillow
python src/make_images.py      # demo product images (writes to ../img when run from the repo root)
python src/make_naive.py       # editor-style comparison template
python src/build.py            # compile modules, render scenarios, run QA, size sweep
```
- `build/src/modules/` - 8 reusable modules (head, preheader, header, greeting, cart items, shipping note, button, footer)
- `build/dist/klaviyo_abandoned_cart.html` - the compiled, paste-ready Klaviyo template
- `build/data/scenarios.json` - test carts shaped like Klaviyo's Started Checkout event

Previews render with Django's template engine, which Klaviyo's syntax is based on. `lookup`, `unsubscribe`,
and `manage_preferences` are Klaviyo features, stubbed in `src/klaviyo_tags.py` for local previews.
Field names follow the Shopify Started Checkout event; confirm them against each store's integration.
