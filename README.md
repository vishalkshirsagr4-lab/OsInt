# OsInt

## Cloudflare migration

The `cloudflare-worker-foundation` branch contains a Cloudflare Python Worker,
a Telegram webhook endpoint, D1 health binding, and deployment instructions.

**This is not yet a feature-complete replacement for the legacy bot.** The
original `osintfinl.py` is retained unchanged for reference and is not imported
by the Worker. Its polling loop, local server startup, local SQLite persistence,
and private-personal-data lookup integrations are not part of this migration.

### Quick start

1. Switch to the `cloudflare-worker-foundation` branch.
2. Follow [CLOUDFLARE_DEPLOYMENT.md](CLOUDFLARE_DEPLOYMENT.md).
3. Create a Cloudflare D1 database and set its ID in `wrangler.jsonc`.
4. Add `BOT_TOKEN` and `TELEGRAM_WEBHOOK_SECRET` as Worker secrets.
5. Deploy and register the Telegram webhook.

### Currently migrated

- `/start`
- `/menu`
- `/help`
- Protected webhook validation and basic health checks.

Ordinary non-command messages are ignored. The Worker does not persist Telegram
profiles, message bodies, or lookup queries. Other legitimate legacy features
must be ported and tested incrementally before production cutover.
