from typing import Any, Dict, List, Optional

import requests
import logging
import time

BASE_URL: str = "https://swapi.dev/api"

_CACHE: Dict[str, Dict[str, Any]] = {}
CACHE_TTL_SECONDS = 300

def get_cache(key: str) -> Optional[Any]:
    if key in _CACHE:
        entry = _CACHE[key]
        age = time.time() - entry['timestamp']

        if age < CACHE_TTL_SECONDS:
            logging.info(f"CACHE HIT: {key}")
            return entry['data']
        else:
            logging.info(f"CACHE EXPIRED: {key}")
            del _CACHE[key]

    return None

def save_cache(key: str, data: Any):
    _CACHE[key] = {
        'data': data,
        'timestamp': time.time()
    }

def fetch_all_pages(url: str, timeout: int, params: dict) -> List[Dict[str, Any]]:
    cache_key = f"{url}?{sorted(params.items())}"

    cached_data = get_cache(cache_key)
    if cached_data:
        return cached_data

    all_results = []
    current_url = url
    local_params = params.copy()

    while current_url:
        try:
            response = requests.get(current_url, timeout = timeout, params = local_params)
            response.raise_for_status()
            data = response.json()

            all_results.extend(data.get('results', []))
            current_url = data.get('next')
            local_params = {}

        except requests.exceptions.RequestException as err:
            logging.error(f"Error fetching page {current_url}: {err}")
            break

    if all_results:
        save_cache(cache_key, all_results)

    return all_results

def swapi_data(resource: str, timeout: int = 10, fetch_all: bool = False, **kwargs: Any) -> Optional[Dict[str, Any]]:
    url: str = f"{BASE_URL}/{resource}/"
    params = kwargs.get('params', {})

    cache_key = f"{url}?fetch_all={fetch_all}&{sorted(params.items())}"

    try:
        cached_response = get_cache(cache_key)
        if cached_response:
            return cached_response

        if fetch_all:
            results = fetch_all_pages(url, timeout, params)
            final_data = {
                "count": len(results),
                "next": None,
                "previous": None,
                "results": results
            }

            save_cache(cache_key, final_data)
            return final_data

        response = requests.get(url, timeout = timeout, **kwargs)
        response.raise_for_status()
        data = response.json()

        save_cache(cache_key, data)
        return data

    except requests.exceptions.HTTPError as http_err:
        logging.error(f"HTTP error while fetching {resource}: {http_err}")

    except requests.exceptions.ConnectionError as conn_err:
        logging.error(f"Connection error: {conn_err}")

    except requests.exceptions.Timeout as timeout_err:
        logging.error(f"Request timed out: {timeout_err}")

    except requests.exceptions.RequestException as err:
        logging.error(f"Unexpected error: {err}")

    return None
