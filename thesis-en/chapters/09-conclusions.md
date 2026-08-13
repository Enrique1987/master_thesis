# 9. Conclusions and Future Work

The project demonstrates how several open technologies can be assembled into a Big Data pipeline and monitoring platform. Scrapy collects economic content, Kafka separates event producers from consumers, MongoDB provides primary document storage, and the Elastic Stack centralizes search, processing, visualization, and operational analysis.

The proof of concept also shows that observability must be designed as part of the architecture rather than added at the end. Logs, metrics, network events, and security signals are necessary to understand system behavior and to operate the platform reliably.

## Infrastructure improvements

### Cloud migration

The project was assembled on one computer with several virtual machines to simulate an on-premises Big Data installation. A logical next step is to move the services to a cloud environment, package them with Docker, and orchestrate them with Kubernetes.

### Job scheduling and orchestration

The prototype lacks a global scheduler that determines which jobs run, in what order, and with which dependencies. Apache Airflow or a comparable orchestrator could coordinate crawlers, transformations, data-quality checks, exports, and recovery workflows.

### Data streaming

Streaming deserves deeper investigation, especially for social-media or rapidly changing market data. Apache Flink and other stream-processing frameworks could add windowed aggregations, stateful processing, event-time semantics, and real-time enrichment.

## Data-science improvements

### Natural Language Processing

Sentiment analysis could classify whether an author discusses a company, product, or financial instrument positively, negatively, or neutrally. Entity recognition would identify the subject, and market data could measure what happened after publication.

### Avoiding historical revision and fraud

Articles can be edited after publication. A reliable analytical system should retain immutable snapshots, timestamps, source hashes, and revision histories so that later edits do not distort the evaluation of an earlier prediction.

### Model validation

Any investment-oriented model requires careful backtesting, prevention of data leakage, transparent evaluation metrics, and controls for transaction costs and risk. The data architecture is a prerequisite for that work, not evidence that a trading strategy will be profitable.

[Back to contents](../README.md#contents)
