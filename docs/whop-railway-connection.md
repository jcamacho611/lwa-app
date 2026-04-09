# Whop To Railway Connection Checklist

Use this when connecting the LWA Whop app to the hosted FastAPI backend instead of Whop agent token flow.

## Goal

- Run the app against your own backend
- Use the Railway deployment as the app base URL
- Keep plan access and checkout controlled in Whop
- Avoid leaving the app pointed at `agent.api.whop.com`

## Backend Values

- Base URL: `https://lwa-backend-production-c9cc.up.railway.app`
- Preferred path: `/`
- Optional custom auth header: `x-api-key`
- Optional custom auth value: your `LWA_API_KEY_SECRET`

## Dashboard Links

- Business home: `https://whop.com/dashboard/biz_5PkXdb9NPrZ6vk/`
- Products: `https://whop.com/dashboard/biz_5PkXdb9NPrZ6vk/products/`
- Checkout links: `https://whop.com/dashboard/biz_5PkXdb9NPrZ6vk/links/checkout/`
- Developer dashboard: `https://whop.com/dashboard/developer`
- Business developer view: `https://whop.com/dashboard/biz_5PkXdb9NPrZ6vk/developer/`
- Business settings: `https://whop.com/dashboard/biz_5PkXdb9NPrZ6vk/settings/`
- Promo codes: `https://whop.com/dashboard/biz_5PkXdb9NPrZ6vk/promo/`
- Team: `https://whop.com/dashboard/biz_5PkXdb9NPrZ6vk/team/`
- Payments: `https://whop.com/dashboard/biz_5PkXdb9NPrZ6vk/payments/`
- Storefront: `https://whop.com/lwa-app/lwa-ai-content-repurposer`
- Joined view: `https://whop.com/joined/lwa-app/`

## What To Set In Whop

### Developer Hosting

In the Whop developer dashboard:

1. Open the `LWA` app.
2. Find the hosting or base URL settings.
3. Set the base URL to `https://lwa-backend-production-c9cc.up.railway.app`.
4. Set the path to `/` unless your app shell needs a different path.
5. Remove any default `agent.api.whop.com` value.

### API Keys

In the Whop developer dashboard:

1. Create a company API key if you need business-level Whop API access.
2. Open the app environment variables if you need the app-level `WHOP_API_KEY`.
3. Copy the key into Railway as `WHOP_API_KEY` if the backend will call Whop APIs.

### Checkout And Plans

In Whop checkout links:

1. Create checkout links for paid plans.
2. Copy plan IDs for Free, Pro, and Scale.
3. Verify which plan is public and which plans are paid.

### Product Access

In the `LWA – AI Content Repurposer` product:

1. Verify the Free plan does not include premium app access if you do not want to give away the tool.
2. Verify Pro and Scale include the app/tool access you intend to sell.
3. Confirm the storefront visibility is correct.

## What Is Already Ready In The Repo

- Railway Release URL is wired into the iOS app
- Whop storefront URL is wired into the iOS app
- FastAPI backend can now enforce an optional custom header:
  - env var: `LWA_API_KEY_SECRET`
  - header name: `x-api-key`
- The iOS app can now send the optional API key from Settings

## What Still Requires Manual Dashboard Work

- Replacing the Whop app base URL in the developer dashboard
- Retrieving app/company Whop API keys
- Copying real plan IDs from checkout links
- Confirming Free vs Pro vs Scale app access inside the product settings

## Current Public Verification

- Backend root: `https://lwa-backend-production-c9cc.up.railway.app/`
- Backend health: `https://lwa-backend-production-c9cc.up.railway.app/health`
- Storefront: `https://whop.com/lwa-app/lwa-ai-content-repurposer`
