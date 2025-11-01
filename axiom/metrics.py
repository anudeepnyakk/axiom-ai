from prometheus_client import Counter, Histogram

# ------------------
# Pipeline Metrics
# ------------------

# General Metrics
REQUEST_COUNT = Counter(
    'axiom_request_count',
    'Total number of requests processed by a pipeline stage.',
    ['stage']
)

ERROR_COUNT = Counter(
    'axiom_error_count',
    'Total number of errors encountered by a pipeline stage.',
    ['stage']
)

LATENCY_SECONDS = Histogram(
    'axiom_latency_seconds',
    'Latency of a pipeline stage in seconds.',
    ['stage']
)

