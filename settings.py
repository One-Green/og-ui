import os
import og_client
from og_client.api import sprinkler_api, water_api
from influxdb_client import InfluxDBClient

DEBUG = bool(os.getenv("DEBUG", False))
CHART = bool(os.getenv("CHART", True))

# One-Green Core Api configurations
OG_API_HOST = os.getenv("OG_API_HOST", "api.dev1.og-ingest1.com")
OG_API_USERNAME = os.getenv("OG_API_USERNAME", "admin")
OG_API_PASSWORD = os.getenv("OG_API_PASSWORD", "admin")

# Influx DB configurations
INFLUXDB_URL = os.getenv("INFLUXDB_URL", "http://localhost:8086")
INFLUXDB_BUCKET = os.getenv("INFLUXDB_BUCKET", "og-test-bucket")
INFLUXDB_TOKEN = os.getenv("INFLUXDB_TOKEN", "change_this_token")
INFLUXDB_ORG = os.getenv("INFLUXDB_ORG", "og-test")


configuration = og_client.Configuration(
    host=OG_API_HOST,
    username=OG_API_USERNAME,
    password=OG_API_PASSWORD
)
og_api_client = og_client.ApiClient(configuration)
og_sprinkler_client = sprinkler_api.SprinklerApi(og_api_client)
og_water_client = water_api.WaterApi(og_api_client)

influx_client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
