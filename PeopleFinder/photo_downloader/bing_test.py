import os
import requests
from dotenv import load_dotenv
from pprint import pprint

load_dotenv(override=True)

"""
This sample makes a call to the Bing Web Search API with a query and returns relevant web search.
Documentation: https://docs.microsoft.com/en-us/bing/search-apis/bing-web-search/overview
"""

# Add your Bing Search V7 subscription key and endpoint to your environment variables.
subscription_key = os.getenv("BING_SEARCH_V7_SUBSCRIPTION_KEY")
print(subscription_key)
endpoint = os.getenv("BING_SEARCH_V7_ENDPOINT")

# Ensure the endpoint does not have a trailing slash
if endpoint.endswith("/"):
    endpoint = endpoint[:-1]

# Construct the full URL
search_url = f"{endpoint}/v7.0/search"

# Query term(s) to search for.
query = "Microsoft"

# Construct a request
mkt = "en-US"
params = {"q": query, "mkt": mkt}
headers = {"Ocp-Apim-Subscription-Key": subscription_key}

# Call the API
try:
    response = requests.get(search_url, headers=headers, params=params)
    response.raise_for_status()

    print("Headers:")
    print(response.headers)

    print("JSON Response:")
    pprint(response.json())
except Exception as ex:
    raise ex
