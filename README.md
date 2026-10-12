# SimplyBin App Download Redirect

A lightweight, free, ad-free GitHub Pages site that automatically sends visitors to the correct app store for their device.

- **iPhone / iPad** → Apple App Store
- **Android** → Google Play Store
- **Desktop / other** → landing page with buttons for both stores

---

## How It Works

`index.html` uses plain JavaScript to detect the visitor's platform from `navigator.userAgent` and `navigator.platform`:

1. If the device is iOS, it immediately redirects to the configured **App Store** URL.
2. If the device is Android, it immediately redirects to the configured **Google Play** URL.
3. Otherwise, it displays a simple page with buttons for both stores.

If JavaScript is disabled, the buttons are shown by default so the page is still usable.

---

## File Structure

```
simplybin-download/
├── index.html   # Redirect page and fallback landing page
├── README.md    # This file
└── .gitignore
```

This is the minimal structure needed for GitHub Pages. You can add a `CNAME` file later if you want a custom domain.

---

## Recommended Setup

**Option used here: a dedicated repository for the download page.**

Using this `simplybin-download` repository is a good choice because:

- It is separate from the app's source code.
- It keeps the download link simple to manage.
- GitHub Pages hosts it for free.

### Cleaner URL option

The long-term cleanest URL is:

```
https://marlonssantos.github.io/simplybin/
```

To get that URL, create or rename a repository called `simplybin` and put `index.html` at its root. If you keep the current `simplybin-download` repository, the URL will be:

```
https://marlonssantos.github.io/simplybin-download/
```

Either works; choose the one that best matches your branding.

---

## Updating Store URLs

All store links live in one place at the top of `index.html`:

```javascript
const APP_STORE_URL = 'https://apps.apple.com/us/app/simplybin/idxxxxxxx';
const PLAY_STORE_URL = 'https://play.google.com/store/apps/details?id=com.simplybin.myapp&hl=en-US';
```

When your Apple App Store link is approved, replace `idxxxxxxx` with the real app ID. Only these two lines need to change.

---

## GitHub Pages Deployment Instructions

1. Push the files in this repository to the branch you want to publish (for example, `new-development` or `main`).
2. Go to the repository on GitHub.
3. Click **Settings** → **Pages**.
4. Under **Source**, select **Deploy from a branch**.
5. Choose the branch you want (for example, `new-development`) and set the folder to `/ (root)`.
6. Click **Save**.
7. Wait about 30–60 seconds, then GitHub will show the live URL at the top of the Pages settings.

---

## QR Code Generation

Once the page is live, generate a single QR code that points to the GitHub Pages URL:

1. Open <https://qrcode.de>.
2. Paste your live URL, for example:
   ```
   https://marlonssantos.github.io/simplybin-download/
   ```
3. Download the QR code image.
4. Test it with both an iPhone and an Android device to confirm the correct store opens.

---

## Success Criteria

- One QR code points to the GitHub Pages URL.
- Scanning on iOS opens the Apple App Store.
- Scanning on Android opens the Google Play Store.
- Scanning on desktop shows both download buttons.
- Hosting is free, ad-free, and fully under your control through GitHub Pages.
