import json, re, sys, html as H
from pathlib import Path
sys.path.insert(0, "src")
import django
from django.conf import settings
settings.configure(TEMPLATES=[], USE_TZ=False)
django.setup()
from django.template import Engine, Context

ROOT = Path("."); MOD = ROOT / "src/modules"
LIMIT = 102 * 1024                                     # Gmail clips HTML above ~102 KB

def compile_template(placeholder):
    src = (ROOT / "src/email.html").read_text()
    src = re.sub(r"<!--@include (\w+)-->", lambda m: (MOD / f"{m.group(1)}.html").read_text().strip(), src)
    return src.replace("__PLACEHOLDER__", placeholder)

engine = Engine(builtins=["klaviyo_tags"])
dist = compile_template("https://cdn.example.com/fernhill/placeholder.jpg")
Path("dist").mkdir(exist_ok=True); (ROOT / "dist/klaviyo_abandoned_cart.html").write_text(dist)
built_t = engine.from_string(compile_template("/img/placeholder.jpg"))
naive_t = engine.from_string((ROOT / "src/naive_email.html").read_text())
scen = json.loads((ROOT / "data/scenarios.json").read_text())

def qa(out, s):
    items = s["event"]["extra"]["line_items"]; n = len(items)
    imgs = re.findall(r"<img\b[^>]*>", out)
    hrefs = re.findall(r'href="([^"]*)"', out)
    styles = " ".join(re.findall(r'style="([^"]*)"', out)).replace(" ", "")
    pre = re.search(r'mso-hide:all">(.*?)</div>', out)
    pre_txt = re.sub(r"&#?\w+;", "", pre.group(1)).strip() if pre else ""
    shown = out.count('class="thumb"')
    more = re.search(r"\+ (\d+) more item", out)
    sub = re.search(r"Subtotal&nbsp; <b>\$([\d.]+)</b>", out)
    size = len(out.encode())
    return [
        ("Under Gmail's 102 KB clip", f"{size / 1024:.1f} KB", size < LIMIT),
        ("Every template tag rendered", "no {{ or {% left" if "{{" not in out and "{%" not in out else "unrendered tags found", "{{" not in out and "{%" not in out),
        ("Greeting never blank", re.search(r"Hi [^,<]*,", out).group(0), not re.search(r"Hi\s*,", out)),
        ("No Shopify 'Default Title'", "hidden" if "Default Title" not in out else "shown to customer", "Default Title" not in out),
        ("Products capped at 3", f"{shown} shown" + (f", '+{more.group(1)} more' row" if more else ""), shown == min(n, 3) and (bool(more) == (n > 3)) and (not more or int(more.group(1)) == n - 3)),
        ("Missing image falls back", "placeholder used" if "placeholder.jpg" in out else "all images present", all(re.search(r'src="[^"]+"', i) for i in imgs)),
        ("Subtotal matches the cart", f"${sub.group(1)} vs ${sum(i['line_price'] for i in items):.2f}" if sub else "missing", bool(sub) and abs(float(sub.group(1)) - sum(i["line_price"] for i in items)) < 0.005),
        ("Images have alt and width", f"{len(imgs)} images", all(" alt=" in i and " width=" in i for i in imgs)),
        ("Links are https", f"{len(hrefs)} links", all(h.startswith("https://") for h in hrefs)),
        ("Outlook-safe CSS", "no flex, grid, or positioning", not re.search(r"display:(flex|grid)|position:(absolute|fixed)", styles)),
        ("Outlook button (VML)", "present" if "v:roundrect" in out else "missing", "v:roundrect" in out),
        ("Preheader 40-130 chars", f"{len(pre_txt)} chars", 40 <= len(pre_txt) <= 130),
        ("Dark mode support", "color-scheme meta + styles" if 'name="color-scheme"' in out and "prefers-color-scheme" in out else "missing", 'name="color-scheme"' in out and "prefers-color-scheme" in out),
    ]

report = {"limit_kb": LIMIT / 1024, "scenarios": {}}
for key, s in scen.items():
    ctx = Context({"person": s["person"], "event": s["event"]})
    out = built_t.render(ctx); naive = naive_t.render(ctx)
    (ROOT / f"site/render/{key}.html").write_text(out)
    (ROOT / f"site/render/{key}_naive.html").write_text(naive)
    checks = qa(out, s)
    report["scenarios"][key] = {
        "label": s["label"], "items": len(s["event"]["extra"]["line_items"]),
        "built_kb": round(len(out.encode()) / 1024, 1), "naive_kb": round(len(naive.encode()) / 1024, 1),
        "naive_issues": [t for t, bad in (("blank greeting", bool(re.search(r"Hi\s*,", naive))), ("'Default Title' shown", "Default Title" in naive), ("broken image", 'src=""' in naive or "src=''" in naive), ("clipped by Gmail", len(naive.encode()) >= LIMIT)) if bad],
        "checks": [{"check": c, "detail": d, "pass": bool(p)} for c, d, p in checks],
    }
    fails = [c for c, _, p in checks if not p]
    print(f"{key:13} built {report['scenarios'][key]['built_kb']:6.1f} KB  naive {report['scenarios'][key]['naive_kb']:6.1f} KB  "
          f"checks {len(checks) - len(fails)}/{len(checks)}  naive issues: {report['scenarios'][key]['naive_issues']}" + (f"  FAILS: {fails}" if fails else ""))
def triggers(s):
    p, ev = s["person"], s["event"]; items = ev["extra"]["line_items"]; t = []
    if not p.get("first_name"): t.append(["No first name on the profile", "Greets 'Hi there' instead of 'Hi ,'"])
    if any((i["product"].get("variant") or {}).get("title") == "Default Title" for i in items): t.append(["Shopify 'Default Title' variant", "Hidden, so customers never see it"])
    if len(items) > 3: t.append([f"{len(items)} items in the cart", f"Shows 3, folds the rest into '+{len(items) - 3} more'"])
    if any(not i["product"].get("images") for i in items): t.append(["Product with no image", "A placeholder keeps the layout intact"])
    if any(len(i["product"]["title"]) > 48 for i in items): t.append(["Very long product name", "Shortened so it can't break the row"])
    t.append(["Cart over $75", "Free-shipping line switches on"] if ev["$value"] >= 75 else ["Cart under $75", "Shows the free-shipping threshold instead"])
    return t
for key, s in scen.items(): report["scenarios"][key]["triggers"] = triggers(s)
report["all_pass"] = all(c["pass"] for s in report["scenarios"].values() for c in s["checks"])
(ROOT / "site/report.json").write_text(json.dumps(report, indent=1))
(ROOT / "site/klaviyo_abandoned_cart.html.txt").write_text(dist)
print("ALL PASS" if report["all_pass"] else "SOME CHECKS FAILED")

# size sweep: how each template grows with the cart
import copy
base = scen["nine_items"]; pool = base["event"]["extra"]["line_items"]
sweep = []
for n in range(1, 21):
    ev = copy.deepcopy(base["event"]); ev["extra"]["line_items"] = [copy.deepcopy(pool[i % len(pool)]) for i in range(n)]
    ev["$value"] = sum(i["line_price"] for i in ev["extra"]["line_items"])
    ctx = Context({"person": {"first_name": "Ana"}, "event": ev})
    sweep.append({"items": n, "built_kb": round(len(built_t.render(ctx).encode()) / 1024, 1), "naive_kb": round(len(naive_t.render(ctx).encode()) / 1024, 1)})
cross = next((r["items"] for r in sweep if r["naive_kb"] * 1024 >= LIMIT), None)
report["sweep"] = sweep; report["naive_clips_at_items"] = cross
report["naive_kb_per_item"] = round((sweep[-1]["naive_kb"] - sweep[0]["naive_kb"]) / 19, 1)
(ROOT / "site/report.json").write_text(json.dumps(report, indent=1))
print("editor-style template clips at", cross, "items;", report["naive_kb_per_item"], "KB per extra item; built at 20 items:", sweep[-1]["built_kb"], "KB")
