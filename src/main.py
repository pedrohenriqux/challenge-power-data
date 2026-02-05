import functions_framework

from flask import jsonify, Request

from services import swapi_data
from utils import apply_filter, process_sort, RESOURCE_CONFIG

API_KEY = "star-wars-secret-key"

def auth(request: Request):
    api_key = request.headers.get("X-API-KEY")

    if not api_key:
        return jsonify({
            "error": "Authentication required.",
            "message": "Missing X-API-KEY header"
        }), 401

    if api_key != API_KEY:
        return jsonify({
            "error": "Unauthorized access",
            "message": "Invalid API key"
        }), 403

    return None

@functions_framework.http
def star_wars_api(request: Request):
    cors_headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, X-API-KEY',
        'Access-Control-Max-Age': '3600'
    }

    if request.method == 'OPTIONS':
        return '', 204, cors_headers

    auth_error = auth(request)
    if auth_error:
        return auth_error[0], auth_error[1], cors_headers

    search_query = request.args.get('search')
    resource = request.args.get('resource', 'people')
    page = request.args.get('page', '1')

    order_by = request.args.get('order_by')
    direction = request.args.get('direction', 'asc')
    filter_key = request.args.get('filter_key')
    filter_value = request.args.get('filter_value')

    if resource not in RESOURCE_CONFIG:
        return jsonify({
            "error": "Resource invalid or not supported.",
            "available_resources": list(RESOURCE_CONFIG.keys())
        }), 400, cors_headers

    fetch_all = True if (filter_key or order_by) else False

    params = {}
    if search_query:
        params['search'] = search_query

    if page and not fetch_all:
        params['page'] = page

    data = swapi_data(resource, params = params, fetch_all = fetch_all)

    if not data:
        return jsonify({"error": "No data found or External API error"}), 502, cors_headers

    results = data.get("results", [])

    if results:
        if filter_key and filter_value:
            results = apply_filter(results, filter_key, filter_value)

        results = process_sort(results, resource, order_by, direction)

        data['results'] = results
        data['count'] = len(results)

    return jsonify(data), 200, cors_headers
