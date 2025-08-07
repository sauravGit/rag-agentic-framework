# Monitoring

The framework uses Prometheus and Grafana for monitoring.

## Prometheus

Prometheus is a monitoring system that collects metrics from the services. You can access the Prometheus UI at http://localhost:9090.

## Grafana

Grafana is a visualization tool that allows you to create dashboards to visualize the metrics from Prometheus. You can access the Grafana UI at http://localhost:3001.

### Default Dashboards

The framework comes with a default dashboard that shows the following metrics:

-   Request latency
-   Request count
-   Document processing time
-   Documents processed count
-   Query processing time
-   Queries processed count

### Creating Custom Dashboards

You can create your own custom dashboards in Grafana to visualize the metrics that are most important to you. For more information on how to create dashboards in Grafana, see the [Grafana documentation](https://grafana.com/docs/grafana/latest/dashboards/).
