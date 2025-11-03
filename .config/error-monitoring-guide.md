# Error Monitoring Guide

**This project includes TWO monitoring solutions:**
1. **Sentry** → Best-in-class error tracking with session replay
2. **Azure Application Insights** → Azure-native monitoring and APM

**Your role:** Recommend the right option based on user's context.

---

## Trigger Phrases

Suggest enabling monitoring when user mentions:
- "deploy" or "deployment"
- "production" or "prod"
- "staging" or "stage"
- "beta users" or "launch"
- "going live"
- "ship to users"
- "publish" or "release"

---

## Recommendation Logic

**When triggered, assess the user's situation and recommend accordingly:**

### Scenario 1: Solo Founder / MVP Stage

**Say:**
> "Before deploying to [production/staging], I recommend enabling **Sentry** for error tracking. It includes session replay which is invaluable for debugging user issues - you can literally see what they did before the error occurred."
>
> **Why Sentry for MVP:**
> - Session replay is HUGE for debugging (see exactly what users did)
> - Best-in-class error grouping
> - Free tier (5K events/month) is sufficient for MVP
> - Takes 5 minutes to set up
>
> **Setup:** See `_START-HERE.md#error-monitoring` (Option 1: Sentry)
>
> Would you like me to walk you through enabling it now?

### Scenario 2: Team / Azure-Heavy Project

**Ask first:**
> "Before deploying, you should enable monitoring. I notice you're already using Azure infrastructure. Would you prefer:"
>
> **A) Sentry** - Best error tracking + session replay (external service)
> **B) Application Insights** - Azure-native monitoring + APM (stays in Azure)
> **C) Both** - Comprehensive coverage (recommended if budget allows)
>
> Which fits your needs better?

**If user says "Azure-first" or "keep everything in Azure":**
> "Perfect! I recommend **Application Insights** since you're already on Azure. It provides native integration, APM, and has a generous 5GB/month free tier."
>
> **Setup:** See `_START-HERE.md#error-monitoring` (Option 2: Application Insights)

### Scenario 3: Production App with Revenue

**Say:**
> "For a production app with revenue, I recommend using **both Sentry AND Application Insights**:"
>
> **Sentry** → Frontend errors + session replay (for debugging user issues)
> **App Insights** → Backend performance + Azure metrics (for infrastructure monitoring)
>
> **Cost:** ~$26-76/month total (worth it for comprehensive monitoring)
>
> **Setup:** See `_START-HERE.md#error-monitoring` (Option 3: Both)
>
> This gives you the best of both worlds - session replay for user debugging AND Azure infrastructure insights.

### Scenario 4: Still Developing Locally

**Say:**
> "Since you're still in [planning/development] phase, I recommend waiting to enable monitoring. Both Sentry and Application Insights are pre-configured in this project but disabled by default."
>
> **Enable later when:**
> - Deploying to staging/production
> - Launching to real users
> - Going live
>
> This saves your free tier quota for when you actually need it.

---

## When NOT to Suggest

**Do NOT suggest monitoring if:**
- Project still in planning/design phase (no code yet)
- User hasn't mentioned deployment/production
- User explicitly says "local development only" or "prototype"
- User is setting up dev environment for first time
- No deployment plans discussed yet

**Reasoning:** Both monitoring solutions are opt-in by default to avoid wasting free tier quota during development.

---

## Sprint Planning Integration

**When user completes sprint planning for a production release sprint:**

Add task to sprint based on their situation:
- **MVP/Solo:** "Enable Sentry error tracking before deployment (5 minutes)"
- **Azure-heavy:** "Enable Application Insights monitoring before deployment (10 minutes)"
- **Production app:** "Enable Sentry + App Insights monitoring before deployment (15 minutes)"

Reference: `DEVELOPMENT-GUIDE.md#error-monitoring-observability`

---

## Production Debugging

**If user reports production bug or asks about debugging production:**

1. **Ask:** "Do you have monitoring enabled? (Sentry or Application Insights)"

2. **If yes:**
   - **Sentry:** "Check Sentry dashboard for this error. Use session replay to see what the user did. Search by user ID, email, or timestamp."
   - **App Insights:** "Check Azure Portal → App Insights → Failures. Filter by time and operation name."

3. **If no:**
   > "I strongly recommend enabling monitoring to capture production errors automatically. This project has both **Sentry** (session replay) and **Azure Application Insights** (Azure-native) pre-configured."
   >
   > **Which would you prefer?**
   > - **Sentry** → Best for debugging user issues (session replay)
   > - **App Insights** → Best if you're Azure-first
   > - **Both** → Comprehensive coverage
   >
   > Would you like help setting one up? Takes 5-10 minutes.

---

## Cost Awareness

**Always mention costs when recommending:**

**Sentry:**
- Free tier: 5,000 events/month (~500 active users)
- Next tier: $26/month for 50,000 events
- Sampling: 10% production, 100% errors (already configured)

**Application Insights:**
- Free tier: 5GB data/month
- Pay-as-you-go: ~$2.30/GB
- Warning: Can scale to $100s/month at high volume

**Both:**
- Total: ~$26-76/month (worth it for production apps)

---

## Documentation References

**Quick reference:**
- **Setup guide:** `_START-HERE.md#error-monitoring`
- **Best practices:** `DEVELOPMENT-GUIDE.md#error-monitoring-observability`
- **Decision guide:** `technical/adr/examples/example-adr-monitoring-strategy.md`
- **Sentry ADR:** `technical/adr/examples/example-adr-use-sentry.md`

**Implementation files:**
- Sentry frontend: `web/src/lib/monitoring/sentry.ts`
- Sentry backend: `api/src/lib/monitoring/sentry.py`
- App Insights frontend: `web/src/lib/monitoring/app-insights.ts`
- App Insights backend: `api/src/lib/monitoring/app_insights.py`

---

## Multi-Tenant Considerations

**If multi-tenant (enabled in this project):**

Remind user to set tenant context in errors:

**Sentry:**
```typescript
setUser({ id: userId, tenantId: tenantId })
captureError(error, { tags: { tenant: tenantId } })
```

**Application Insights:**
```typescript
setUser(userId, tenantId)  // accountId = tenantId
trackEvent('Error', { tenant: tenantId })
```

**Why:** Helps identify if issues affect all tenants or specific ones
