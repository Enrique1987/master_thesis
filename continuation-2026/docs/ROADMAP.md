# Roadmap

Phases are defined by verifiable outcomes rather than installed tools.

## Phase 0 — Decisions and first data contract

**Objective:** remove ambiguities that could invalidate the experiment.

Deliverables:

- a list of ten assets and one benchmark;
- one authorized documentary source and one market-data provider;
- retention policies by source;
- versioned schemas for `document`, `claim`, `asset`, `price`, and `evaluation`;
- manually annotated examples, including documents that contain no claim;
- a mathematical definition of a correct five-session claim.

**Exit criterion:** five real documents can be represented without losing provenance or leaving known ambiguities unresolved.

## Phase 1 — First vertical slice

**Objective:** process one real case from end to end.

Deliverables:

- Python project with configuration, linting, and tests;
- containers for PostgreSQL and Dagster;
- idempotent document connector;
- idempotent price connector;
- raw storage with content hashes and capture metadata;
- initial asset and direction extraction;
- reproducible five-session outcome calculation;
- a simple page showing the source, evidence, extraction, and result.

**Exit criterion:** one claim can be reproduced from capture through evaluation with one command and one automated integration test.

## Phase 2 — Reliability over 30 days

**Objective:** move from a demonstration to an operable product.

Deliverables:

- scheduled daily runs and backfills;
- retries, quarantine, and alerts;
- contract, quality, and regression tests;
- human review queue;
- golden dataset of at least 100 examples;
- freshness, coverage, and failure dashboard;
- recovery runbook.

**Exit criterion:** at least 95% successful runs over 30 days, with no silent data loss and complete provenance.

## Phase 3 — Analytical evaluation

**Objective:** determine whether a signal exists without hindsight bias.

Deliverables:

- 1, 5, and 20-session horizons;
- adjusted and benchmark-relative returns with confidence intervals;
- temporal training, validation, and test splits;
- metrics by source, author, asset, and market regime;
- versioned rules, datasets, prompts, and models;
- error analysis for entity, direction, and horizon extraction.

**Exit criterion:** a reproducible report explains whether a signal exists, how uncertain it is, and where the system fails. “No signal” is a valid result.

## Phase 4 — Justified scale

**Objective:** introduce distributed components only where a measured limitation exists.

Possible deliverables:

- Kafka or Redpanda for multiple consumers and replay;
- Iceberg for snapshots, concurrency, and table evolution;
- a distributed engine for volumes beyond DuckDB's practical range;
- specialized search;
- infrastructure as code and cloud deployment;
- complete OpenTelemetry observability.

**Exit criterion:** every new component has a before-and-after metric, an operational owner, and a removal plan.

## First executable backlog

1. Record the seven pending architecture decisions.
2. Define the five core schemas and their invariants.
3. Create ten manually annotated examples.
4. Implement the document connector.
5. Implement the price connector.
6. Persist raw and normalized data idempotently.
7. Extract the first structured claim.
8. Evaluate it after the fifth trading session.
9. Display one evidence page.
10. Automate the complete path as an integration test.

## Rule for choosing the next tool

Before adding a technology, write a short decision that answers:

1. What measured problem does it solve?
2. Why is the current solution no longer sufficient?
3. What development and operational cost does it add?
4. How will success be measured?
5. How can it be removed without losing data?
