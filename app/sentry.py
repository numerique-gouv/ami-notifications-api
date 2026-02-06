import sentry_sdk


def add_counter(metric: str):
    sentry_sdk.metrics.incr(metric, 1)  # type: ignore
