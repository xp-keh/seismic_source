from prometheus_client import Counter, Histogram, start_http_server

# Define Prometheus metrics
EXECUTION_TIME = Histogram('producer_execution_time', 'Execution time in seconds from streaming start to Kafka publish')
THROUGHPUT = Counter('producer_throughput', 'Number of messages published to Kafka')

def start_prometheus_server(port=8001):
    start_http_server(port)