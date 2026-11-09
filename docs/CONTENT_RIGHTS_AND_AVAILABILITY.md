# Phase 4 — Content rights and availability decisions (offline)

This is an internal **brand publishing/commerce policy**, not a legal opinion or a claim that Instagram's proprietary recommendation rules were independently verified. It deliberately fails closed for new sales/publication where owner-provided records are insufficient. No service is contacted and no actual media is downloaded.

## 1. Rights of content originating elsewhere

The campaign JSON can have `source_content` at the brief root or inside `content`, **but not both**. Each element has:

| Key | Allowed values | Requirement |
|---|---|---|
| `origin` | `owned`, `licensed`, `permission`, `third_party` | Required |
| `has_visible_watermark` | true / false | Required, real JSON boolean |
| `documented_permission` | true / false | Required, real JSON boolean; owner assertion only |
| `usage` | `publish` (default), `research` | Optional |
| `subtitles_only_repost` | true / false | Optional; true prevents publishing the clip merely with subtitles |

The gate returns a per-item audit and indexes. A third-party/permission/licensed item without documented rights, or a visible-watermark item without documented rights, is **rejected as publishable** and produces `HOLD_CREATIVE` if the brief attempts to publish it. Asset records marked `usage=research` can be used as background inspiration (topic, hook concept, narrative structure) without becoming part of the finished media. Research-only items NEVER authorize posting their audiovisual content.

`documented_permission=true` is not evidence that an externally hosted license was independently reviewed. A legally permitted licensed clip can still be non-original under Instagram's recommendation approach. Require the owner to inspect the actual terms, the right to use audio/likeness, territory and editing permission before publishing. A creator credit, new border, translation, or subtitles over somebody else's TikTok/Reel are **not** independently produced original media.

The old `content.rights_verified` / `content.claims_verified` fields remain required. Setting either to true cannot override denied individual assets. Source-origin review does not connect to the Meta API or clear legal liability.

## 2. Availability means verified ability to deliver

New `availability_type` is **optional**: missing means `physical_stock` for backwards compatibility. Unknown strings must return `DO_NOT_PROMOTE`. The old stock implementation is unchanged. All new adapters require active status, `sku`, `name`, `price`, `unit_cost` (for new sales), `currency`, fresh `last_verified`, verified checkout URL, and any configured gross-margin floor. `max_age_days` defaults to 14 days **as a business heuristic**, not an Instagram rule.

| Type | Required additional owner-asserted checks |
|---|---|
| `physical_stock` | Existing `stock_policy` tracked / supplier / verified unlimited, quantity/supplier availability, delivery, price freshness and margin |
| `digital_product` | `delivery_mode` automatic/manual/supplier; `delivery_verified=true`; `license_valid=true`; `license_valid_until` if expiry exists; automatic uses `automation_operational=true`, manual uses `manual_capacity_verified=true`, supplier uses `supplier_verified=true` and `supplier_fulfillment_verified=true`; if `requires_region_check=true` then `region_restrictions_verified=true` |
| `cohort_seats` | `seats_left` integer greater than zero; future `start_date`; `enrollment_open=true`; `cohort_confirmed=true`; optional `enrollment_deadline` must not be expired or after start |
| `consult_slots` | `open_slots` integer greater than zero; `slots_verified=true`; `response_time_hours` finite nonnegative; optional `response_sla_hours` positive and not exceeded; `service_delivery_verified=true` |

A zero-capacity service/course is blocked even if marketing copy is ready. A digital subscription with an invalid/expired license, incompatible country restrictions, or unverified automatic delivery must not be advertised as ready for immediate fulfillment.

A `PROMOTE` decision is **only** eligibility to propose a campaign, always with `requires_human_approval=true`. It does not reserve a seat, create an appointment, deliver a code or prove the supplier is live. Existing accepted/paid customer orders are obligations handled separately; this preflight must not block fulfillment of them merely to protect new-sales margins.

## 3. CLI commands

```bash
python3 -m scripts.catalog_guard examples/catalog-availability.phase4.sample.json
python3 -m scripts.campaign_decision examples/campaign-source-content.phase4.sample.json
python3 -m unittest discover -s tests -v
```

Both examples are synthetic. A real catalog belongs only in the ignored `brands/<slug>/` private workspace. No public branch should contain supplier account names, customer data or access tokens.

## 4. Unimplemented integrations and future choices

Not implemented: independent media license proof, Instagram originality status API, real-time supplier/stock availability, a live digital-code validity check, a cohort enrollment database, a calendar slot reservation API, payment, delivery or automatic publication. No universal consultation response-time SLA is assumed; it must be defined by the owner. Future live adapters must be separately authorized, tested and documented.
