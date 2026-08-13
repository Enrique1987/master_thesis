# 8. Machine Learning with X-Pack

The Machine Learning module examined in the thesis was a licensed Elastic feature. The chapter therefore combines a practical proof of concept with theoretical discussion rather than presenting a complete production implementation.

## 8.1 Machine Learning on server logs

Large log collections contain patterns and outliers that are difficult for a human operator to identify manually. Elastic Machine Learning can model the expected behavior of a time series and highlight observations that depart from that baseline.

The test begins by loading server-metric data into Elasticsearch.

![Uploading data to Elasticsearch](../assets/figures/source-image-067.png)

*Figure 62. Uploading the dataset to Elasticsearch.*

After creating an anomaly-detection job, the interface displays the modeled range and assigns anomaly scores to unusual points.

![Machine Learning applied to logs](../assets/figures/source-image-068.png)

*Figure 63. Applying Machine Learning to server logs.*

Zooming into a flagged interval makes it possible to examine the behavior around the anomaly and relate it to the source data.

![Detailed anomaly view](../assets/figures/source-image-069.png)

*Figure 64. Detailed view of detected anomalies.*

## 8.2 Machine Learning on user activity

The same approach can be applied to user and application activity. Advanced jobs may add influencers and partition data by fields such as host, endpoint, country, or user-agent category.

![Machine Learning on user metrics](../assets/figures/source-image-070.png)

*Figure 65. Applying Machine Learning to user-activity metrics.*

Potential applications include:

- Detecting sudden changes in request volume.
- Finding unusually high error rates.
- Identifying unexpected geographic access patterns.
- Detecting abnormal service latency.
- Highlighting behavior that may indicate an automated agent or attack.

Machine Learning complements monitoring rules but does not replace domain knowledge. Operators still need to interpret the anomaly, validate the data, and decide whether action is required.

[Back to contents](../README.md#contents)
