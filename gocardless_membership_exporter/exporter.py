import logging
import os
import sys
import time
from collections import Counter
from typing import Literal

from prometheus_client import Info, Summary, start_http_server
from prometheus_client.core import REGISTRY, GaugeMetricFamily
from prometheus_client.registry import Collector
import gocardless_pro

from gocardless_membership_exporter import VERSION

from .config import settings


class GoCardlessMembershipCollector(Collector):
    scrape_time = Summary(
        "gocardless_scrape_time", "Timings for calls to the GoCardless API"
    )
    exporter_version = Info(
        "gocardless_exporter_version", "Version of the GoCardless exporter"
    )

    def __init__(self, environment: Literal["live", "sanbox"], token: str):
        self._token = token
        self._environment = environment

        self.exporter_version.info({"version": VERSION})

    @scrape_time.time()
    def collect(self):
        members = GaugeMetricFamily(
            "gocardless_members_count", "Number of active members in GoCardless"
        )
        subscriptions_total = GaugeMetricFamily(
            "gocardless_subscriptions_total_count",
            "Number of active subscriptions in GoCardless",
        )
        subscriptions = GaugeMetricFamily(
            "gocardless_subscriptions_count",
            "Number of active subscriptions by name in GoCardless",
            labels=["name"],
        )

        # Init the GoCardless client
        client = gocardless_pro.Client(
            access_token=self._token, environment=self._environment
        )

        subscription_data = list(
            client.subscriptions.all(
                {
                    "limit": "500",
                    "status": "active",
                }
            )
        )

        # Total subscriptions
        subscriptions_total.add_metric([], len(subscription_data))

        # Per subscription totals
        for key, value in Counter(x.name for x in subscription_data).items():
            subscriptions.add_metric([key], value)

        # Create a list of associated mandate IDs for the subscriptions
        mandates_ids = [x.links.mandate for x in subscription_data]

        # Call the mandates API endpoint, subscriptions don't provide the
        # customer ref so we call the mandates endpoint to work out the
        # unique customer IDs, which would represent members.
        mandates_data = client.mandates.all(
            {
                "limit": "500",
                "status": "active",
            }
        )

        # Get unique customer IDs
        members_count = len(set([mandate.links.customer for mandate in mandates_data if mandate.id in mandates_ids]))

        # Total members
        members.add_metric([], members_count)

        # Yield out the results to Prometheus Client
        yield members
        yield subscriptions_total
        yield subscriptions


def main():
    logging.basicConfig(level=logging.DEBUG)

    collector = GoCardlessMembershipCollector(
        settings.gocardless_environment, settings.gocardless_token
    )
    REGISTRY.register(collector)

    start_http_server(5002)

    try:
        while True:
            time.sleep(100)
    except KeyboardInterrupt:
        pass

    sys.exit(os.EX_OK)


if __name__ == "__main__":
    main()
