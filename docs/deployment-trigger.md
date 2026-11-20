# Feature-branch deployment

This file records the deployment trigger for the Cloudflare Worker migration.

A push to `cloudflare-worker-foundation` runs the Python compile and unit-test checks. When those checks pass, the workflow deploys the Worker and registers the Telegram webhook using the repository Actions secrets. The `main` branch is not changed by this commit.
