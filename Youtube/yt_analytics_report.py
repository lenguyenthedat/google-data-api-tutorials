#!/usr/bin/python

# Original version of this file:
# https://github.com/youtube/api-samples/blob/master/python/yt_analytics_report.py

from datetime import datetime, timedelta
import httplib2
import os
import sys

from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow

CLIENT_SECRETS_FILE = "../client_secrets.json"
API_SCOPES = ["https://www.googleapis.com/auth/youtube.readonly",
  "https://www.googleapis.com/auth/yt-analytics.readonly"]
API_SERVICE_NAME = "youtubeAnalytics"
API_VERSION = "v1"

def get_authenticated_services(args):
  flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE,
    scope=" ".join(API_SCOPES))

  storage = Storage("%s.dat" % API_SERVICE_NAME)
  credentials = storage.get()

  if credentials is None or credentials.invalid:
    credentials = run_flow(flow, storage, args)

  http = credentials.authorize(httplib2.Http())

  youtube_analytics = build(API_SERVICE_NAME,
    API_VERSION, http=http)

  return youtube_analytics

def run_analytics_report(youtube_analytics, options):
  # Call the Analytics API to retrieve a report. For a list of available
  # reports, see:
  # https://developers.google.com/youtube/analytics/v1/channel_reports
  analytics_query_response = youtube_analytics.reports().query(
    ids="contentOwner==%s" % options.content_owner_id,
    filters="channel==%s" % options.channel_id,
    metrics=options.metrics,
    dimensions=options.dimensions,
    start_date=options.start_date,
    end_date=options.end_date,
    max_results=options.max_results,
    sort=options.sort
  ).execute()

  print "Analytics Data for channel: %s" % options.channel_id

  for column_header in analytics_query_response.get("columnHeaders", []):
    print "%-20s" % column_header["name"],
  print

  for row in analytics_query_response.get("rows", []):
    for value in row:
      print "%-20s" % value,
    print

def main():
  now = datetime.now()
  one_day_ago = (now - timedelta(days=1)).strftime("%Y-%m-%d")
  one_week_ago = (now - timedelta(days=7)).strftime("%Y-%m-%d")

  argparser.add_argument("--channel_id", help="Channel ID",
    required=True)
  argparser.add_argument("--content_owner_id", help="Content Owner Id",
    required=True)
  argparser.add_argument("--metrics", help="Report metrics",
    default="views,comments,favoritesAdded,favoritesRemoved,likes,dislikes,shares")
  argparser.add_argument("--dimensions", help="Report dimensions",
    default="video")
  argparser.add_argument("--start-date", default=one_week_ago,
    help="Start date, in YYYY-MM-DD format")
  argparser.add_argument("--end-date", default=one_day_ago,
    help="End date, in YYYY-MM-DD format")
  argparser.add_argument("--max-results", help="Max results", default=10)
  argparser.add_argument("--sort", help="Sort order", default="-views")
  args = argparser.parse_args()

  youtube_analytics = get_authenticated_services(args)
  try:
    run_analytics_report(youtube_analytics, args)
  except HttpError, e:
    print "An HTTP error %d occurred:\n%s" % (e.resp.status, e.content)

if __name__ == '__main__':
  main()
