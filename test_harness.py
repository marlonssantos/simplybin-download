import json, re, subprocess, sys, tempfile, os, html as htmllib

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
SRC = open("index.html", encoding="utf-8").read()

# Injected just before </body> — reports state as JSON
REPORTER = """\
<script>
  (function() {
    var el = document.createElement('pre');
    el.id = '__result';
    el.textContent = JSON.stringify({
      redirect: window.__redirect || null,
      comingSoonShown: !document.getElementById('comingSoon').hidden,
      messageHidden: document.getElementById('message').hidden,
      messageText: document.getElementById('message').textContent,
      buttonsDisplay: document.getElementById('buttons').style.display,
      appleHref: document.getElementById('appleBtn').getAttribute('href'),
      appleText: document.getElementById('appleBtn').textContent,
      appleDisabled: document.getElementById('appleBtn').classList.contains('disabled'),
      googleHref: document.getElementById('googleBtn').getAttribute('href')
    });
    document.body.appendChild(el);
  })();
</script>
</body>"""


def render(label, ua, platform, touch, live=False, appstore_url=""):
    html = SRC
    # Stub out UA, platform, maxTouchPoints so the script sees our test values
    html = html.replace("navigator.userAgent || ''", json.dumps(ua))
    html = html.replace("navigator.platform || ''", json.dumps(platform))
    html = html.replace("navigator.maxTouchPoints || 0", str(touch))
    # Stub redirect so Chrome doesn't actually navigate away
    html = html.replace("window.location.href =", "window.__redirect =")
    if live:
        html = html.replace("const APP_STORE_LIVE = false;", "const APP_STORE_LIVE = true;")
        html = html.replace("const APP_STORE_URL = '';", "const APP_STORE_URL = %s;" % json.dumps(appstore_url))
    html = html.replace("</body>", REPORTER)
    f = tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8")
    f.write(html)
    f.close()
    out = subprocess.run(
        [CHROME, "--headless=new", "--disable-gpu", "--dump-dom", f.name],
        capture_output=True, timeout=60)
    os.unlink(f.name)
    stdout = out.stdout.decode("utf-8", errors="replace")
    m = re.search(r'<pre id="__result">(.*?)</pre>', stdout, re.S)
    if not m:
        return {"error": "no __result element", "dom": stdout[-1000:]}
    # Chrome's --dump-dom re-encodes text content as HTML, so unescape before
    # JSON-parsing (e.g. & -> &amp; in URLs, en-dash -> &ndash; etc.)
    return json.loads(htmllib.unescape(m.group(1)))


PLAY = "https://play.google.com/store/apps/details?id=com.simplybin.myapp&hl=en-US"
IPHONE_UA = "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
IPAD_UA = "Mozilla/5.0 (iPad; CPU OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
IPADOS_DESKTOP_UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15"
ANDROID_UA = "Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36"
WIN_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
MAC_UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
TEST_APP_URL = "https://apps.apple.com/us/app/simplybin/id1234567890"

results = []

def check(name, cond, detail):
    status = "PASS" if cond else "FAIL"
    results.append((status, name))
    print(status, "-", name)
    if not cond:
        print("   ", json.dumps(detail, indent=2)[:400])
    return cond

# --- iPhone (APP_STORE_LIVE=false) ---
r = render("iPhone", IPHONE_UA, "iPhone", 5)
check("iPhone: no redirect", r.get("redirect") is None, r)
check("iPhone: coming-soon shown", r.get("comingSoonShown"), r)
check("iPhone: detecting message hidden", r.get("messageHidden"), r)

# --- iPad ---
r = render("iPad", IPAD_UA, "iPad", 5)
check("iPad: coming-soon shown, no redirect", r.get("comingSoonShown") and r.get("redirect") is None, r)

# --- iPadOS 13+ desktop mode: Macintosh UA + touch points ---
r = render("iPadOS desktop", IPADOS_DESKTOP_UA, "MacIntel", 5)
check("iPadOS desktop (Mac UA + touch): coming-soon shown", r.get("comingSoonShown") and r.get("redirect") is None, r)

# --- Android ---
r = render("Android", ANDROID_UA, "Linux armv8l", 5)
check("Android: redirects to Google Play", r.get("redirect") == PLAY, r)
check("Android: coming-soon NOT shown", not r.get("comingSoonShown"), r)

# --- Desktop Windows ---
r = render("Desktop Win", WIN_UA, "Win32", 0)
check("Desktop Win: buttons shown", r.get("buttonsDisplay") == "flex", r)
check("Desktop Win: App Store button disabled", r.get("appleDisabled"), r)
check("Desktop Win: App Store button has no href", r.get("appleHref") is None, r)
check("Desktop Win: App Store badge text", r.get("appleText") == "App Store \u2013 Coming Nov 10, 2026", r)
check("Desktop Win: Play link correct", r.get("googleHref") == PLAY, r)

# --- Desktop Mac (real, no touch) must NOT be treated as iOS ---
r = render("Desktop Mac", MAC_UA, "MacIntel", 0)
check("Desktop Mac (no touch): NOT treated as iOS", r.get("buttonsDisplay") == "flex" and not r.get("comingSoonShown"), r)

# --- Flip test: APP_STORE_LIVE=true ---
r = render("Flip iPhone", IPHONE_UA, "iPhone", 5, live=True, appstore_url=TEST_APP_URL)
check("FLIP: iPhone redirects to App Store URL", r.get("redirect") == TEST_APP_URL, r)

r = render("Flip Android", ANDROID_UA, "Linux armv8l", 5, live=True, appstore_url=TEST_APP_URL)
check("FLIP: Android still redirects to Google Play", r.get("redirect") == PLAY, r)

r = render("Flip Desktop", WIN_UA, "Win32", 0, live=True, appstore_url=TEST_APP_URL)
check("FLIP: desktop App Store button becomes live link", r.get("appleHref") == TEST_APP_URL, r)
check("FLIP: desktop App Store button enabled", not r.get("appleDisabled"), r)
check("FLIP: desktop App Store button text", r.get("appleText") == "Download on the App Store", r)

# --- Edge case: live=true but URL is empty -> coming soon, no loop ---
r = render("Edge live+empty", IPHONE_UA, "iPhone", 5, live=True, appstore_url="")
check("EDGE: live=true + empty URL -> coming-soon (no redirect loop)", r.get("comingSoonShown") and r.get("redirect") is None, r)

print()
passed = sum(1 for s, _ in results if s == "PASS")
failed = sum(1 for s, _ in results if s == "FAIL")
print(f"Results: {passed} passed, {failed} failed")
sys.exit(0 if failed == 0 else 1)
