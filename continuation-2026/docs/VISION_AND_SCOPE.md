# Vision and Scope

## Working name

**Market Evidence Platform**.

This name describes the purpose more accurately than “investment platform.” The system provides evidence and historical evaluation. Any investment decision remains outside the initial product.

## Initial user

An analyst or researcher who wants to answer questions such as:

- What specific claims did a source make about an asset?
- What happened 1, 5, or 20 trading sessions later?
- Did the move outperform the benchmark, or did the whole market move?
- How many observations support a source's apparent accuracy?
- Which extractor version produced each result?

## Analytical unit: the claim

The article is no longer the primary unit. One document may contain zero, one, or several claims. Each claim should include the following fields whenever the text supports them:

| Field | Purpose |
|---|---|
| `claim_id` | Stable identifier |
| `document_id` | Link to the original evidence |
| `asset_id` | Resolved entity rather than a raw name |
| `stance` | Bullish, bearish, or neutral |
| `published_at` | Earliest time at which the information was available |
| `horizon_sessions` | Explicit horizon or declared inference rule |
| `quote_start`, `quote_end` | Exact span supporting the extraction |
| `extractor_version` | Code, model, and prompt used |
| `confidence` | Extractor confidence, not expected return probability |
| `review_status` | Pending, accepted, corrected, or rejected |

## Outcome evaluation

For a claim about asset `a`, published at `t0` and evaluated at `t1`:

```text
asset_return     = adjusted_price(a, t1) / adjusted_price(a, t0) - 1
benchmark_return = adjusted_price(b, t1) / adjusted_price(b, t0) - 1
excess_return    = asset_return - benchmark_return
```

An initial binary rule may mark a bullish claim as correct when `excess_return` exceeds a threshold and a bearish claim as correct when it falls below the negative threshold. The threshold, exchange calendar, entry-price convention, and benchmark must be versioned. Results must never be recalculated silently: a methodology change creates a new evaluation version.

Absolute and relative returns are retained alongside the binary outcome so that the system does not discard useful information.

## Source and author metrics

- Number of evaluable claims and rejection rate.
- Accuracy by horizon, asset, and market regime.
- Mean excess return and result distribution.
- Confidence intervals so that 3 correct calls are not treated like 300.
- Calibration when a source expresses confidence.
- Stability and behavioral changes over time.

The platform will not publish a global ranking without a minimum sample size and visible uncertainty.

## MVP scope

Included:

- one documentary source whose use is permitted;
- one compatible market-data provider;
- ten liquid assets and one benchmark;
- idempotent daily ingestion;
- immutable evidence or fingerprints, subject to licensing;
- initial extraction using rules and/or a versioned model;
- human review;
- evaluation after five trading sessions;
- one evidence page and one source summary;
- data-quality tests, logs, and execution metrics.

Excluded:

- order execution or broker connectivity;
- personalized recommendations;
- promised profitability;
- scraping sources that prohibit it;
- scoring people without sufficient sample size and context;
- Kubernetes, low-latency streaming, or a distributed lakehouse before there is evidence that they are needed.

## Product-level risks

1. **Licensing and copyright:** retain and display only what each source permits.
2. **Content revisions:** preserve capture time, content hash, and version relationships.
3. **Identity:** avoid merging authors with the same name or ambiguous tickers.
4. **Selection bias:** record documents without claims and ingestion failures.
5. **Hindsight bias:** freeze extraction and evaluation rules before observing outcomes.
6. **Corporate actions:** use adjusted prices and correct exchange calendars.
7. **Non-deterministic LLMs:** require structured output, validation, versioning, and a human-labeled evaluation set.

## Initial definition of success

For 30 consecutive days, at least 95% of scheduled runs complete without intervention, every evaluated record retains complete provenance, and a human-reviewed sample of 100 extractions meets agreed entity and direction accuracy thresholds. Technical success does not imply that the claims predict the market.
