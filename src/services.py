from typing import Any

import requests
import logging

BASE_URL: str = "https://swapi.dev/api/"

def swapi_data(resource: str, timeout: int = 10, **kwargs: Any):

    url: str = f"{BASE_URL}/{resource}/"

    try:
        response = requests.get(url, timeout = timeout, **kwargs)
        response.raise_for_status()
        return response.json()

    except requests.exceptions.HTTPError as http_err:
        logging.error(f"HTTP error while fetching {resource}: {http_err}")

    except requests.exceptions.ConnectionError as conn_err:
        logging.error(f"Connection error: {conn_err}")

    except requests.exceptions.Timeout as timeout_err:
        logging.error(f"Request timed out: {timeout_err}")

    except requests.exceptions.RequestException as err:
        logging.error(f"Unexpected error: {err}")

    return None
