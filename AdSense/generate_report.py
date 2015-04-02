#!/usr/bin/python

# Original version of this file:
# https://github.com/googleads/googleads-adsense-examples/blob/master/python/v1.4/generate_report.py

"""Generate a new report"""

from datetime import datetime, timedelta
import argparse
import sys

from apiclient import sample_tools
from oauth2client import client

CLIENT_SECRETS_FILE = "../client_secrets.json"
API_SCOPES = ["https://www.googleapis.com/auth/adsense.readonly"]
API_SERVICE_NAME = "adsense"
API_VERSION = "v1.4"

def main(argv):
  now = datetime.now()
  one_day_ago = (now - timedelta(days=1)).strftime("%Y-%m-%d")
  one_week_ago = (now - timedelta(days=7)).strftime("%Y-%m-%d")
  # Declare command-line flags.
  argparser = argparse.ArgumentParser(add_help=False)
  argparser.add_argument('--account_id', help='Adsense account_id, retrieve from https://www.google.com/adsense/app (top right)',
    required=True)
  argparser.add_argument("--start-date", default=one_week_ago,
    help="Start date, in YYYY-MM-DD format")
  argparser.add_argument("--end-date", default=one_day_ago,
    help="End date, in YYYY-MM-DD format")
  argparser.add_argument('--max-results', help='Max results',
    default=50000)
  argparser.add_argument('--metrics', help='Report metrics',
    default='page_views,ad_requests,ad_requests_coverage,clicks,ad_requests_ctr')
  argparser.add_argument('--dimensions', help='Report dimensions',
    default='month,platform_type_name')

  # Authenticate and construct service.
  service, flags = sample_tools.init(
      argv, API_SERVICE_NAME, API_VERSION, __doc__, CLIENT_SECRETS_FILE, parents=[argparser],
      scope=API_SCOPES)

  try:
    # Retrieve report.
    result = service.accounts().reports().generate(
      accountId=flags.account_id, startDate=flags.start_date, endDate=flags.end_date,
      metric=flags.metrics.split(','), dimension=flags.dimensions.split(',')).execute()

    print "Data for AdSense Account ID: %s" % flags.account_id

    for column_header in result.get("headers"):
      print "%-25s" % column_header["name"],
    print

    for row in result.get("rows"):
      for value in row:
        print "%-25s" % value,
      print

  except client.AccessTokenRefreshError:
    print ('The credentials have been revoked or expired, please re-run the '
           'application to re-authorize')

if __name__ == '__main__':
  main(sys.argv)
