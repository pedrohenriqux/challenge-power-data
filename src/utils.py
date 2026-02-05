from typing import Any, List, Dict, Optional

RESOURCE_CONFIG = {
    "people": ["height", "mass"],
    "planets": ["diameter", "rotation_period", "orbital_period", "population", "surface_water"],
    "starships": ["cost_in_credits", "length", "crew", "passengers", "cargo_capacity", "max_atmosphering_speed", "hyperdrive_rating", "MGLT"],
    "species": ["average_height", "average_lifespan"],
    "vehicles": ["cost_in_credits", "length", "crew", "passengers", "cargo_capacity", "max_atmosphering_speed"],
    "films": ["episode_id"]
}

def convert_numeric_value(value: Any) -> Optional[float]:
    if value is None:
        return None

    str_value = str(value).replace(',', '').strip().lower()

    if str_value in ['unknown', 'n/a', 'none']:
        return None

    try:
        return float(str_value)
    except ValueError:
        return None

def apply_filter(results: List[Dict], filter_key: str, filter_value: str) -> List[Dict]:
    if not filter_key or not filter_value:
        return results

    return [
        item for item in results
        if filter_key in item and str(item[filter_key]).lower() == str(filter_value).lower()
    ]

def process_sort(results: List[Dict], resource: str, order_by: str = None, direction: str = 'asc') -> List[Dict]:
    clear_fields = RESOURCE_CONFIG.get(resource, [])

    for item in results:
        for field in clear_fields:
            if field in item:
                item[field] = convert_numeric_value(item.get(field))

    if order_by and results:
        valid_items = []
        null_items = []

        for item in results:
            val = item.get(order_by)

            if val is None:
                null_items.append(item)
            else:
                valid_items.append(item)

        reverse = (direction.lower() == 'desc')

        try:
            valid_items.sort(key = lambda x: x.get(order_by), reverse = reverse)
        except TypeError:
            valid_items.sort(key = lambda x: str(x.get(order_by)), reverse = reverse)

        results = valid_items + null_items

    return results
