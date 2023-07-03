import sys
import os
import time
import logging
import requests
from collections import Counter
from urllib.parse import urljoin
from typing import Literal, Optional, Dict
from prometheus_client import Summary, start_http_server
from prometheus_client.core import REGISTRY, GaugeMetricFamily
from prometheus_client.registry import Collector
from .config import settings


class GoCardlessMembershipCollector(Collector):
    scrape_time = Summary(
        "gocardless_scrape_time", "Timings for calls to the GoCardless API"
    )

    def __init__(self, environment: Literal["live", "sanbox"], token: str):
        self._token = token
        self._environment = environment

        # Prep the session
        self.session = requests.session()
        self.session.headers = {
            "Authorization": "Bearer {0}".format(self._token),
            "GoCardless-Version": "2015-07-06",
            "Accept": "application/json",
        }

    def call_gocardless(
        self, environment: str, endpoint: str, params: Dict = {}
    ) -> Optional[Dict]:
        if environment == "sandbox":
            base_url = "https://api-sandbox.gocardless.com"
        else:
            base_url = "https://api.gocardless.com"

        resp = self.session.get(
            urljoin(base_url, endpoint),
            params=params,
        )

        if resp.ok:
            return resp.json()

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

        # Call Subscriptions endpoint
        resp_data = self.call_gocardless(
            self._environment,
            "/subscriptions",
            params={
                "limit": "500",
                "status": "active",
            },
        )

        # Did we get a valid response?
        if resp_data and "error" not in resp_data:
            # We don't paginate - but we should in the future, warn about it!
            if resp_data["meta"]["limit"] == (resp_data["subscriptions"]):
                logging.warning("API call hit the pagnation limit - time to implement!")

            # Total subscriptions
            subscriptions_total.add_metric([], len(resp_data["subscriptions"]))

            # Per subscription totals
            for key, value in Counter(
                x["name"] for x in resp_data["subscriptions"]
            ).items():
                subscriptions.add_metric([key], value)

        # Call the mandates API endpoint, subscriptions don't provide the
        # customer ref so we call the mandates endpoint to work out the
        # unique customer IDs, which would represent members.
        resp_data = self.call_gocardless(
            self._environment,
            "/mandates",
            params={
                "limit": "500",
                "status": "active",
            },
        )

        # Did we get a valid response?
        if resp_data and "error" not in resp_data:
            # Get unique customer IDs
            members_count = len(
                set([mandate["links"]["customer"] for mandate in resp_data["mandates"]])
            )

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
