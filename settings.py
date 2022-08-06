import og_client
from og_client.api import sprinkler_api, water_api

DEBUG = True

configuration = og_client.Configuration(
    host="api.dev1.og-ingest1.com",
    username='admin',
    password='admin'
)

og_api_client = og_client.ApiClient(configuration)
og_sprinkler_client = sprinkler_api.SprinklerApi(og_api_client)
og_water_client = water_api.WaterApi(og_api_client)
