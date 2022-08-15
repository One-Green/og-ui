import og_client
from og_client.api import sprinkler_api, water_api
from influxdb_client import InfluxDBClient

DEBUG = True
CHART = True

# One-Green Core Api configurations
configuration = og_client.Configuration(
    host="api.dev1.og-ingest1.com",
    username='admin',
    password='admin'
)
og_api_client = og_client.ApiClient(configuration)
og_sprinkler_client = sprinkler_api.SprinklerApi(og_api_client)
og_water_client = water_api.WaterApi(og_api_client)

# Influx DB configurations
influx_db_url = "http://localhost:8086"
influxdb_bucket = "og-test-bucket"
influxdb_token = "change_this_token"
influxdb_org = "og-test"
influx_client = InfluxDBClient(url=influx_db_url, token=influxdb_token, org=influxdb_org)
