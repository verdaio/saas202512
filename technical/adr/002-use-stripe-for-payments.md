# ADR-002: Use Stripe for Payment Processing

**Date:** 2025-01-06
**Status:** Accepted
**Deciders:** Chris Stephens
**Technical Story:** Core MVP requirement - No-show defense requires deposits and card-on-file

---

## Context

Pet Care Scheduler needs payment processing for several critical features:

- **Deposits:** Require $20-50 deposit at booking to reduce no-shows (industry avg: 8-15%)
- **Cancellation fees:** Automatically charge fees based on cancellation timing (24hr, 2hr, etc.)
- **Final payments:** Collect remaining balance after service completion
- **Tips:** Enable owners to add gratuity after service
- **Packages:** Support pre-paid service bundles (e.g., "5 grooming sessions for $300")
- **Multi-tenant:** Each pet care business needs their own merchant account (revenue flows directly to them, not through us)

Key constraints:
- PCI DSS compliance required (handling credit cards)
- Multi-tenant architecture with subdomain-based isolation
- Solo founder building in 60-90 days (limited integration time)
- Beta launch with 20 shops (need fast merchant onboarding)
- Target ARPU: $80-120/month with 80-85% gross margin

---

## Decision

We will use **Stripe** with **Stripe Connect** for all payment processing:
- **Stripe Elements** for PCI-compliant card input (we never touch raw card data)
- **Stripe Connect** for multi-tenant merchant accounts (each shop has their own account)
- **Payment Intents API** for deposits, final payments, tips, and packages
- **Automatic fee collection** for cancellations
- **Webhooks** for payment status updates and dispute handling

---

## Consequences

### Positive Consequences
- **PCI compliance solved:** Stripe Elements handles card data, we never store or process raw card numbers (reduces compliance burden to SAQ-A)
- **Multi-tenant support:** Stripe Connect provides isolated merchant accounts per tenant with separate balances and payouts
- **Fast integration:** Excellent documentation, pre-built UI components, and Python SDK reduces integration time to ~1 week
- **Trusted brand:** Owners are familiar with Stripe checkout, increasing conversion rates
- **Comprehensive features:** Supports deposits, captures, refunds, disputes, subscriptions out of the box
- **Flexible fee structure:** Platform fee (our revenue) can be added on top or subtracted from merchant payout
- **Instant payouts:** Option to enable same-day payouts for merchants (competitive advantage)
- **Strong fraud protection:** Built-in Radar fraud detection reduces chargebacks

### Negative Consequences
- **Cost:** 2.9% + $0.30 per transaction (higher than some alternatives)
- **Additional Connect fees:** 0.25% platform fee for Connect accounts (on top of standard processing fees)
- **Payout delays:** Standard 2-day payout cycle (unless instant payouts enabled for extra fee)
- **Account holds:** Stripe may hold funds for high-risk merchants (mobile groomers may trigger this)
- **Vendor lock-in:** Switching payment processors requires significant code changes and merchant re-onboarding

### Neutral Consequences
- Requires Stripe Connect onboarding for each tenant (OAuth flow adds ~2 minutes to setup)
- Need to handle webhook signature validation for security
- Must implement idempotency for payment operations (prevent duplicate charges)
- Dashboard complexity: Merchants see payments in both Stripe dashboard and our app

---

## Alternatives Considered

### Alternative 1: Square
**Description:** Payment processor popular with small businesses, includes POS hardware

**Pros:**
- Same pricing as Stripe: 2.9% + $0.30
- Better known in brick-and-mortar small business community
- Integrated POS hardware (could support salons)
- Simpler fee structure (no separate Connect fees)

**Cons:**
- Weaker multi-tenant API (designed for single merchant, not platforms)
- Limited Connect-style functionality (harder to isolate merchant accounts)
- Less flexible webhook system
- Smaller developer ecosystem (fewer integration examples for FastAPI)
- Mobile groomer focus doesn't align with Square's POS strength

**Why rejected:** Multi-tenant architecture is critical. Square's API is optimized for single merchants, while Stripe Connect is purpose-built for platforms like ours.

---

### Alternative 2: PayPal/Braintree
**Description:** PayPal-owned payment processor with multi-tenant support

**Pros:**
- Recognizable brand (high owner trust)
- Marketplace features similar to Stripe Connect
- Competitive pricing: 2.9% + $0.30
- Good fraud protection

**Cons:**
- More complex integration (requires both PayPal and Braintree SDKs)
- Split ecosystem (PayPal vs. Braintree documentation confusion)
- Slower innovation cycle (less frequent API updates)
- Fewer developer resources and examples
- Account holds more common (anecdotal from other SaaS founders)

**Why rejected:** Developer experience matters for solo founder on tight timeline. Stripe's unified API and excellent docs reduce integration time by 30-50%.

---

### Alternative 3: Authorize.Net
**Description:** Established payment gateway with lower per-transaction fees

**Pros:**
- Lower fees: 2.9% + $0.30 base, but can negotiate volume discounts
- 20+ years in market (very stable)
- Strong enterprise adoption

**Cons:**
- No built-in multi-tenant support (would need to manage separate merchant accounts manually)
- Clunky developer experience (older API design)
- Limited webhook functionality
- Requires separate merchant account setup (more friction for beta shops)
- No modern pre-built UI components

**Why rejected:** Lack of native multi-tenant support means we'd need to build merchant account management ourselves, adding 2-3 weeks to development timeline.

---

## References

- Stripe Connect Documentation: https://stripe.com/docs/connect
- Stripe Elements: https://stripe.com/docs/payments/elements
- Stripe Python SDK: https://github.com/stripe/stripe-python
- PCI Compliance Guide: https://stripe.com/docs/security/guide
- Sprint 3 plan: `sprints/current/sprint-03-booking-payments.md`
- Multi-tenant security: `docs/SECURITY.md`

---

## Notes

**Implementation timeline:**
- Sprint 3: Basic payment integration (deposits, final payments)
- Sprint 4: Cancellation fee automation
- Sprint 3: Stripe Connect onboarding flow for tenants

**Platform fee structure (to be finalized):**
- Option A: Add platform fee on top (tenant pays processing + our fee)
- Option B: Deduct from merchant payout (we take % before payout)
- **Recommendation:** Start with Option B (simpler for merchants to understand pricing)

**Security requirements:**
- NEVER store raw card numbers (use Stripe Elements exclusively)
- Validate all webhook signatures
- Store Stripe API keys in Azure Key Vault (production)
- Use separate Stripe accounts for dev/staging/production
- Implement idempotency keys for all payment operations
- Log all payment attempts for dispute resolution

**Beta launch considerations:**
- Test mode for first 3 beta shops (validate flows before live payments)
- Stripe Connect onboarding adds ~2 minutes to 60-minute migration goal (acceptable)
- Provide support documentation for common Stripe account issues
- Monitor for account holds and have escalation path to Stripe support

**Cost mitigation:**
- Volume discounts available after $80k/month processing (negotiate when we hit scale)
- Instant payouts are optional (default to 2-day to reduce fees)
- Consider passing processing fees to owners (common in industry)

---

## Superseded By

[None]
