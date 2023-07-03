# GoCardless Membership Exporter

A simple Prometheus exporter that queries GoCardless and pulls back subscription statistics. This has been developed to export membership figures for [Leigh Hackspace](https://leighhack.org).

## Configuration

Configuration is handled by environment variables.

| Value                    | Default | Description                                    |
| ------------------------ | ------- | ---------------------------------------------- |
| `GOCARDLESS_TOKEN`       |         | API Token for the GoCardless account           |
| `GOCARDLESS_ENVIRONMENT` | `live`  | Environment to use, either `live` or `sandbox` |

## Example Output

```
# HELP gocardless_scrape_time Timings for calls to the GoCardless API
# TYPE gocardless_scrape_time summary
gocardless_scrape_time_count 4.0
gocardless_scrape_time_sum 9.999028407037258e-06
# HELP gocardless_scrape_time_created Timings for calls to the GoCardless API
# TYPE gocardless_scrape_time_created gauge
gocardless_scrape_time_created 1.68838067418901e+09
# HELP gocardless_members_count Number of active members in GoCardless
# TYPE gocardless_members_count gauge
gocardless_members_count 1.0
# HELP gocardless_subscriptions_total_count Number of active subscriptions in GoCardless
# TYPE gocardless_subscriptions_total_count gauge
gocardless_subscriptions_total_count 1.0
# HELP gocardless_subscriptions_count Number of active subscriptions by name in GoCardless
# TYPE gocardless_subscriptions_count gauge
gocardless_subscriptions_count{name="Membership"} 1.0
```