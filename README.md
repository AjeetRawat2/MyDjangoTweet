# Chai & Chatter ☕

A Django social app for sharing quick thoughts, meeting people, and starting friendly conversations over chai.

**Live app:** [chai-chatter.ajeetrawat.me](https://chai-chatter.ajeetrawat.me)  
**Source:** [AjeetRawat2/MyDjangoTweet](https://github.com/AjeetRawat2/MyDjangoTweet)

## What you can do

### Share posts

- Publish text posts up to 240 characters.
- Attach an image or an animated GIF. GIF animation plays in browsers that support it.
- Edit or delete your own posts.
- Browse a “For you” feed or a feed of posts from people you follow.

### React and talk

- Like and unlike posts. The heart changes to red and animates; likes save without reloading the page.
- Open a post’s comments in an overlay and add a comment without reloading the feed.
- Follow and unfollow other members, and see suggested accounts.

### Find conversations

- Search posts by their text or the author’s username.
- Browse popular hashtags based on recent posts.
- See the Chai Question of the Day and take it into a conversation.
- Join Chai Tables: themed chat rooms where signed-in members can talk with other people. New messages refresh automatically.

### Make it yours

- Use the responsive layout on desktop and mobile.
- Switch between light and dark themes.
- Enjoy small motion effects on likes, comments, buttons, and newly revealed content. The interface respects the device’s reduced-motion preference.

## Install it from Chrome

Chai & Chatter is a Progressive Web App (PWA). It can be installed from the secure website and opened from your desktop or phone’s app launcher. The install option appears after the site meets Chrome’s install requirements.

### Desktop Chrome

1. Open [chai-chatter.ajeetrawat.me](https://chai-chatter.ajeetrawat.me) in Chrome.
2. Click **Install app** on the page, or use Chrome’s menu: **⋮ → Cast, save, and share → Install page as app**.
3. Confirm the installation. To make a desktop shortcut, open `chrome://apps`, right-click Chai & Chatter, choose **Create shortcut**, and select **Desktop**.

### Android Chrome

1. Open [chai-chatter.ajeetrawat.me](https://chai-chatter.ajeetrawat.me) in Chrome.
2. Tap **Install app**, or open **⋮ → Install app** (on some devices, **Add to Home screen**).
3. Confirm. The Chai & Chatter icon will appear on your home screen or in your app launcher.

### iPhone or iPad using Chrome

1. Open the site in Chrome.
2. Tap **Share → Add to Home Screen**, then confirm.

Chrome’s menu wording can vary by device and version. See Google’s [desktop](https://support.google.com/chrome/answer/9658361?co=genie.platform%3DDesktop&hl=en) and [mobile](https://support.google.com/chrome/answer/9658361?hl=en) instructions.

### Offline behavior

The app can show its offline screen when it cannot reach the server. Its service worker keeps the app’s static interface files and up to 80 images you have already viewed on that device. Signing in, loading feeds and chats, posting, liking, and commenting still need an internet connection.

## Run locally

You’ll need Python and pip installed.

```bash
git clone https://github.com/AjeetRawat2/MyDjangoTweet.git
cd MyDjangoTweet
python -m venv .venv
```

Activate the environment:

```powershell
# Windows PowerShell
.venv\Scripts\Activate.ps1
```

```bash
# macOS or Linux
source .venv/bin/activate
```

Install dependencies, apply database migrations, and start the app:

```bash
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

The project defaults to `DEBUG=False` and secure cookies. For local HTTP development, set `DEBUG=true` before starting the server.

```powershell
# Windows PowerShell
$env:DEBUG = "true"
python manage.py runserver
```

```bash
# macOS or Linux
DEBUG=true python manage.py runserver
```

## Optional account integrations

### Google sign-in

Google sign-in is shown when both environment variables are configured:

- `GOOGLE_CLIENT_ID`
- `GOOGLE_CLIENT_SECRET`

Add the app’s OAuth callback URL to the Google OAuth client’s authorized redirect URIs:

```
https://chai-chatter.ajeetrawat.me/accounts/google/login/callback/
```

For local testing, add the corresponding localhost callback URL to the OAuth client as well.

### Password reset email

Set these environment variables on the deployment to send password reset messages through SMTP:

- `EMAIL_HOST`
- `EMAIL_PORT` (defaults to `587`)
- `EMAIL_HOST_USER`
- `EMAIL_HOST_PASSWORD`
- `EMAIL_USE_TLS` (defaults to `true`)
- `DEFAULT_FROM_EMAIL`

Without an SMTP host, Django uses its console email backend, which is suitable for local development but does not deliver email to users.

## Deployment and stored files

The app uses Django, SQLite, Pillow, django-allauth, and WhiteNoise. WhiteNoise serves the app’s static files. Render deployments should use HTTPS; the configured custom domain is included in Django’s allowed hosts and CSRF trusted origins.

A Render service’s local filesystem is temporary by default. If the service is on Render Free, it can also sleep after inactivity and take around a minute to wake when the next request arrives. This can look like a brief connection failure.

Tweet uploads and the SQLite database are local files. On Render, files written to the service can be lost after a restart, sleep, or deploy unless persistent storage is configured. To keep uploaded images and app data long term, use persistent storage (where available) or move uploads to an object-storage service and the database to a managed database. The PWA’s image cache only keeps images already viewed on an individual device; it does not replace server-side storage.

The current settings file contains a hard-coded development `SECRET_KEY`. Before public production use, update settings to read a private key from the deployment environment and set that secret in Render.

### Keep follows and account data between deploys

The app uses SQLite for local development. Render's default filesystem is temporary, so a SQLite database on the web service can reset after a restart or deploy. Use Neon PostgreSQL as the persistent database:

1. Create a Neon project and database, then open **Connect** in the Neon Console.
2. Select the **pooled connection** option and copy its connection string. Neon connection strings require SSL; the app enforces SSL when `DATABASE_URL` is set.
3. In Render, open the web service's **Environment** settings and add `DATABASE_URL` with the Neon connection string as its value. Treat the string like a password; do not add it to GitHub.
4. Deploy the app, then open Render Shell and run `python manage.py migrate` to create the tables in Neon.

The app uses PostgreSQL when `DATABASE_URL` is set and keeps SQLite for local development. The Neon database starts separately from the current SQLite database, so existing accounts, follows, posts, likes, and comments do not copy over automatically. Migrate existing data separately if you need to keep it.

## Main technologies

- [Django](https://www.djangoproject.com/) for pages, authentication, data, and forms
- [django-allauth](https://docs.allauth.org/) for optional Google sign-in
- [Pillow](https://python-pillow.org/) for uploaded image validation
- [WhiteNoise](https://whitenoise.readthedocs.io/) for static files
- A web manifest and service worker for installable PWA behavior

## License

No license file is currently included in this repository.
