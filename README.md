# Gojo Fortnite Shop SMS Checker

This project runs once per day on Render and sends an SMS if a Gojo Satoru-related item appears in the Fortnite item shop.

## What this implementation does

1. Runs `check_shop.py` on a daily Render cron schedule.
2. Calls `https://fortnite-api.com/v2/shop/br`.
3. Searches entries for `gojo satoru` / `gojo` (or your custom terms).
4. Sends an SMS with Twilio only if there is at least one match.

## Environment variables

### Required

- `TWILIO_ACCOUNT_SID` - from Twilio Console.
- `TWILIO_AUTH_TOKEN` - from Twilio Console.
- `TWILIO_FROM_PHONE` - your Twilio sender number (E.164 format, e.g. `+15551234567`).
- `TARGET_PHONE` - your private destination number (E.164 format, e.g. `+15557654321`).

### Optional

- `SEARCH_TERMS` - comma-separated list, e.g. `gojo satoru,gojo`.
- `LOG_LEVEL` - e.g. `INFO`, `DEBUG`.

## Render setup (fixes your current error)

Your screenshot error `ModuleNotFoundError: No module named 'requests'` means dependencies were not installed for the running service.

Use a **Cron Job** (or Blueprint-generated cron), not a Web Service.

### Correct values

- **Build Command:** `pip install -r requirements.txt`
- **Pre-Deploy Command:** *(leave blank)*
- **Start Command:** `python3 check_shop.py` (or `python check_shop.py`)

### If it still fails

1. Confirm service type is **Cron Job**.
2. Click **Manual Deploy** -> **Clear build cache & deploy**.
3. Check deploy logs and make sure `pip install -r requirements.txt` ran successfully.
4. Re-run the job.

## Using Blueprint (recommended)

If you deploy with Blueprint, Render reads `render.yaml` and sets the cron/build/start commands automatically.

## Local run

```bash
pip install -r requirements.txt
cp .env.example .env
python check_shop.py
```

## Twilio notes

- Trial Twilio accounts can only send SMS to verified recipient numbers.
- Ensure your Twilio number supports SMS for your destination region.
