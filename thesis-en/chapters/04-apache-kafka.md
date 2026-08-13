# 4. High-Volume Event Distribution with Apache Kafka

## 4.1 Why Kafka is introduced

The earliest ingestion design connected a source directly to a target database. That approach is simple when there is one producer and one destination, but it creates a separate integration for every source-target pair as the platform grows.

![Original point-to-point ingestion](../assets/figures/source-image-012.png)

*Figure 10. Original point-to-point ingestion.*

With several producers and consumers, the number of integrations grows quickly. Each connection requires agreement on protocols, data formats, schemas, failure handling, and security.

![Many point-to-point integrations](../assets/figures/source-image-013.png)

*Figure 11. Integration complexity in a larger Big Data system.*

Apache Kafka introduces an event backbone between source and target systems. Producers publish records to Kafka without needing to know which consumers will process them. Consumers can be added independently and can replay retained data when necessary.

![Kafka as an event backbone](../assets/figures/source-image-014.png)

*Figure 12. Kafka decoupling source and target systems.*

## 4.2 Kafka fundamentals

Kafka is a distributed event-streaming platform built around several concepts:

- **Topic:** a named logical stream of records.
- **Partition:** an ordered shard of a topic. Partitions provide parallelism and scale.
- **Offset:** the position of a record within a partition.
- **Producer:** an application that publishes records.
- **Consumer:** an application that reads records.
- **Consumer group:** a set of consumers that divides the partitions of a topic among its members.
- **Broker:** a Kafka server that stores partitions and serves clients.
- **Replication factor:** the number of broker copies maintained for each partition.
- **Leader and replicas:** one broker handles reads and writes for a partition while replicas maintain synchronized copies.
- **ZooKeeper:** the coordination component used by the Kafka generation studied in 2019.

![Kafka topic partitions](../assets/figures/source-image-015.png)

*Figure 13. Records distributed across topic partitions.*

Partitions allow a topic to grow beyond the capacity of a single machine. Replication improves availability because another broker can take over when the current leader fails.

![Kafka replication](../assets/figures/source-image-016.png)

*Figure 14. Partition replication across Kafka brokers.*

![Kafka theory summary](../assets/figures/source-image-017.png)

*Figure 15. Summary of producers, consumers, brokers, topics, and ZooKeeper.*

## 4.3 Kafka command-line interface

The Kafka CLI is used to administer topics and test message flow. The distribution examined in the thesis used ZooKeeper-based commands.

### Create and inspect a topic

```bash
bin/kafka-topics.sh \
  --create \
  --zookeeper 127.0.0.1:2181 \
  --replication-factor 1 \
  --partitions 1 \
  --topic blog_01
```

```bash
bin/kafka-topics.sh --zookeeper 127.0.0.1:2181 --list
bin/kafka-topics.sh --zookeeper 127.0.0.1:2181 --describe --topic blog_01
```

![Creating a Kafka topic](../assets/figures/source-image-018.png)

*Figure 16. Creating and listing a topic.*

### Start a producer and consumer

```bash
bin/kafka-console-producer.sh \
  --broker-list 127.0.0.1:9092 \
  --topic blog_01
```

```bash
bin/kafka-console-consumer.sh \
  --bootstrap-server 127.0.0.1:9092 \
  --topic blog_01 \
  --from-beginning
```

![Producer and consumer](../assets/figures/source-image-019.png)

*Figure 17. Sending and receiving test messages.*

## 4.4 Kafka and Java

The command-line tests prove connectivity, but the production flow must be encapsulated in applications. The Java producer serializes records and publishes them to a topic. The Java consumer subscribes to that topic, deserializes records, and forwards them to a target service.

Typical producer properties include:

```java
Properties properties = new Properties();
properties.setProperty(
    ProducerConfig.BOOTSTRAP_SERVERS_CONFIG,
    "127.0.0.1:9092"
);
properties.setProperty(
    ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG,
    StringSerializer.class.getName()
);
properties.setProperty(
    ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG,
    StringSerializer.class.getName()
);
```

![Java consumer test](../assets/figures/source-image-020.png)

*Figure 18. A Java consumer receiving records from Kafka.*

## 4.5 Kafka in the project architecture

The proof of concept also tests social-media events. A Twitter-facing producer publishes records to Kafka; a consumer reads them and writes them into Elasticsearch. The same event backbone can later serve crawled articles and additional destinations.

![Kafka in the project](../assets/figures/source-image-021.png)

*Figure 19. Twitter, producer, Kafka, consumer, and Elasticsearch.*

The producer needs the Kafka client dependency, bootstrap servers, serializers, and a topic. The consumer needs a consumer group, deserializers, topic subscription, polling logic, and a destination client. Decoupling these applications allows the storage layer to change without rewriting every source integration.

![Producer development and Twitter data](../assets/figures/source-image-022.png)

*Figure 20. Producer development and a collected Twitter event.*

The consumer can send JSON records to Elasticsearch through its REST interface or a client library.

![Consumer writing to Elasticsearch](../assets/figures/source-image-023.png)

*Additional figure. Kafka consumer writing events to Elasticsearch.*

[Back to contents](../README.md#contents)
