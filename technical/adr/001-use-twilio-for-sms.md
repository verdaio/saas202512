# ADR-001: Use Twilio for SMS Communication

**Date:** 2025-11-02
**Status:** Accepted
**Deciders:** Chris Stephens
**Technical Story:** Core MVP requirement - SMS-first workflows are a key product differentiator

---

## Context

Pet Care Scheduler is an SMS-first platform where two-way messaging, automated reminders, and quick-action workflows are core product differentiators. The product requires:

- Two-way SMS inbox for owner-business communication
- Automated booking confirmations and reminders (24hr + 2hr before appointment)
- Quick reschedule actions ("Reply 1 for tomorrow 2pm")
- Late-running alerts sent to owners
- High deliverability for time-sensitive notifications
- Compliance with A2P/10DLC regulations for business messaging

SMS is not a secondary feature—it's the primary communication channel that enables our "60-minute migration" promise and reduces no-shows by 30%+.

---

## Decision

We will use **Twilio** as our SMS provider for all messaging functionality, including:
- Outbound transactional messages (confirmations, reminders, alerts)
- Inbound message handling via webhooks
- Two-way conversation threading
- A2P/10DLC registration for reliable business messaging

---

## Consequences

### Positive Consequences
- **High deliverability:** Twilio has industry-leading message delivery rates and carrier relationships
- **A2P/10DLC support:** Built-in compliance framework for business messaging reduces spam filtering
- **Rich webhook system:** Easy integration for inbound messages and delivery status
- **Proven at scale:** Handles high-volume messaging with 99.95% uptime SLA
- **Developer-friendly:** Excellent documentation, SDKs for Python/Node, extensive examples
- **Message templates:** Support for pre-approved templates that improve deliverability
- **Analytics:** Built-in delivery tracking, failure reasons, and conversation metrics

### Negative Consequences
- **Cost:** $0.0079/message (US) adds up at scale (100 shops × 50 appts/week = $1,580/month in SMS costs)
- **Vendor lock-in:** Switching SMS providers requires code changes and phone number migration
- **A2P/10DLC registration:** 2-3 week approval process required before production launch
- **Phone number costs:** $1.15/month per number (1 number per tenant = $1,380/month for 100 shops)

### Neutral Consequences
- Requires Twilio account setup for each beta shop (can automate via Twilio API)
- Need to implement webhook signature validation for security
- Must handle message failures gracefully (retry logic, fallback to email)

---

## Alternatives Considered

### Alternative 1: Bandwidth
**Description:** SMS API provider with competitive pricing and similar feature set

**Pros:**
- Lower cost: $0.0035/message (55% cheaper than Twilio)
- Good API documentation
- Number porting supported

**Cons:**
- Less mature A2P/10DLC compliance tools
- Smaller ecosystem and community support
- Fewer integration examples for FastAPI/Python
- Less reliable delivery rates reported by users

**Why rejected:** Deliverability is critical for our use case. The cost savings ($0.0044/message) aren't worth the risk of lower delivery rates that could hurt our 70%+ booking confirmation metric.

---

### Alternative 2: AWS SNS (Simple Notification Service)
**Description:** AWS managed messaging service supporting SMS

**Pros:**
- Integrated with AWS ecosystem (if we deploy there)
- Pay-as-you-go pricing: $0.00645/message
- No phone number required (uses AWS shared pool)
- Simpler setup (no A2P/10DLC registration)

**Cons:**
- No two-way messaging support (inbound SMS not supported)
- Lower deliverability (shared number pool = spam filters)
- No conversation threading or inbox features
- Limited to one-way notifications only

**Why rejected:** Two-way SMS inbox is a core product feature. SNS only supports outbound messages, making it unsuitable for our "Reply 1 to reschedule" workflows.

---

### Alternative 3: Build direct carrier integrations
**Description:** Integrate directly with AT&T, Verizon, T-Mobile APIs

**Pros:**
- Lowest possible cost (wholesale rates)
- Maximum control over delivery
- No middleware dependency

**Cons:**
- Requires separate integration with each carrier (3+ different APIs)
- Complex A2P/10DLC registration per carrier
- Significant engineering time (3-4 weeks minimum)
- Ongoing maintenance burden
- No unified analytics or reporting

**Why rejected:** We're a solo founder on a 60-90 day build timeline. The engineering complexity outweighs cost savings, and time-to-market is critical for beta launch.

---

## References

- Twilio Messaging API: https://www.twilio.com/docs/messaging
- A2P/10DLC Registration Guide: https://www.twilio.com/docs/messaging/guides/a2p-10dlc
- Twilio Python SDK: https://www.twilio.com/docs/libraries/python
- Pricing comparison: `product/research/sms-provider-comparison.md` (to be created during implementation)
- Sprint 5 plan: `sprints/current/sprint-05-sms-workflows.md`

---

## Notes

**Implementation timeline:**
- Sprint 3: Basic SMS sending (confirmations, reminders)
- Sprint 5: Two-way inbox and quick actions
- Before beta launch: Complete A2P/10DLC registration (2-3 weeks)

**Cost mitigation strategies:**
- Monitor per-tenant message volume and set alerts for anomalies
- Batch reminders during off-peak hours when possible
- Use email as fallback for non-critical messages
- Consider message bundling ("Your appointments for this week: ...")

**Security requirements:**
- Validate all incoming webhook signatures
- Store Twilio credentials in Azure Key Vault (production)
- Use separate Twilio accounts for dev/staging/production
- Implement rate limiting on webhook endpoints

---

## Superseded By

[None]
