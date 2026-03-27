# Gojo Fortnite Shop SMS Checker

This project runs once per day on Render and sends an SMS if a Gojo Satoru-related item appears in the Fortnite item shop.

## What this implementation does

1. Runs `check_shop.py` on a daily Render cron schedule.
2. Calls `https://fortnite-api.com/v2/shop/br`.
3. Searches entries for `gojo satoru` / `gojo` (or your custom terms).
4. Sends an SMS with Twilio **only** if there is at least one match.
5. Uses your requested target number by default: **`****`**.

## Environment variables

### Required

- `TWILIO_ACCOUNT_SID` - from Twilio Console.
- `TWILIO_AUTH_TOKEN` - from Twilio Console.
- `TWILIO_FROM_PHONE` - your Twilio phone number (E.164 format, e.g. `+15551234567`).

### Optional

- `TARGET_PHONE` - destination number. Defaults to `+16032052315` if omitted.
- `SEARCH_TERMS` - comma-separated list, e.g. `gojo satoru,gojo`.
- `LOG_LEVEL` - e.g. `INFO`, `DEBUG`.

## Deploy on Render (free) - step by step

### 1) Push this repo to GitHub

```bash
git init
git add .
git commit -m "Initial Gojo shop checker"
git branch -M main
git remote add origin git@github.com:<your-user>/<your-repo>.git
git push -u origin main
```

### 2) Connect GitHub to Render

- In Render dashboard, click **New +** -> **Blueprint**.
- Connect your GitHub account if you have not already.
- Choose this repository.
- Render will detect `render.yaml` and create a cron service.

### 3) Set environment variables in Render

In Render service -> **Environment**, add:

- `TWILIO_ACCOUNT_SID`
- `TWILIO_AUTH_TOKEN`
- `TWILIO_FROM_PHONE`
- Optional: `TARGET_PHONE` (only if you want to override `****`)
- Optional: `SEARCH_TERMS`
- Optional: `LOG_LEVEL`

### 4) Save, deploy, and test once manually

- Click **Manual Deploy** / **Run now** once.
- Check logs in Render to confirm:
  - Shop fetch succeeded
  - Match/no-match behavior
  - SMS sent (if matched)

## Git + SSH keys (if you want key-based auth)

Render itself pulls from GitHub using the GitHub integration, so you usually do **not** need deploy keys manually. For your own local Git access:

### Create an SSH key locally

```bash
ssh-keygen -t ed25519 -C "you@example.com"
```

### Add public key to GitHub

```bash
cat ~/.ssh/id_ed25519.pub
```

- Copy output.
- GitHub -> **Settings** -> **SSH and GPG keys** -> **New SSH key**.

### Verify SSH

```bash
ssh -T git@github.com
```

If successful, use SSH remote format:

```bash
git remote set-url origin git@github.com:<your-user>/<your-repo>.git
```

## Schedule

`render.yaml` currently uses:

- `0 15 * * *` -> once daily at 15:00 UTC.

Change this cron expression in `render.yaml` if you want a different time.

## Local run

```bash
pip install -r requirements.txt
cp .env.example .env
python check_shop.py
```

## Twilio notes

- Trial Twilio accounts can only send SMS to verified recipient numbers.
- Make sure your `TWILIO_FROM_PHONE` supports SMS in your target region.
