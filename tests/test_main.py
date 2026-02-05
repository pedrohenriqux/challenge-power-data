import pytest
import sys
import os

from unittest.mock import patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from main import star_wars_api

MOCK_SWAPI_RESPONSE = {
    "count": 2,
    "next": None,
    "previous": None,
    "results": [
        {"name": "Luke Skywalker", "height": "172", "mass": "77", "gender": "male"},
        {"name": "C-3PO", "height": "167", "mass": "75", "gender": "n/a"}
    ]
}

AUTH_HEADERS = {'X-API-KEY': 'star-wars-secret-key'}

@pytest.fixture
def app():
    from flask import Flask
    app = Flask(__name__)
    return app

def test_auth_failure(app):
    with app.test_request_context('/?resource=people'):
        from flask import request
        response = star_wars_api(request)

        assert response[1] == 401
        assert "Authentication required" in response[0].json['error']

def test_get_people_success(app):
    with app.test_request_context('/?resource=people', headers=AUTH_HEADERS):
        with patch('main.swapi_data') as mock_service:
            mock_service.return_value = MOCK_SWAPI_RESPONSE

            from flask import request
            response = star_wars_api(request)

            assert response[1] == 200
            assert response[0].json['count'] == 2
            assert response[0].json['results'][0]['name'] == "Luke Skywalker"

def test_filter_functionality(app):
    url = '/?resource=people&filter_key=gender&filter_value=male'
    with app.test_request_context(url, headers=AUTH_HEADERS):
        with patch('main.swapi_data') as mock_service:
            mock_service.return_value = MOCK_SWAPI_RESPONSE

            from flask import request
            response = star_wars_api(request)

            data = response[0].json

            assert len(data['results']) == 1
            assert data['results'][0]['name'] == "Luke Skywalker"

def test_sort_functionality(app):
    url = '/?resource=people&order_by=mass&direction=desc'
    with app.test_request_context(url, headers=AUTH_HEADERS):
        with patch('main.swapi_data') as mock_service:
            mock_service.return_value = MOCK_SWAPI_RESPONSE

            from flask import request
            response = star_wars_api(request)

            results = response[0].json['results']
            assert results[0]['name'] == "Luke Skywalker"  # 77 > 75

def test_invalid_resource(app):
    with app.test_request_context('/?resource=batman', headers=AUTH_HEADERS):
        from flask import request
        response = star_wars_api(request)

        assert response[1] == 400
        assert "Resource invalid" in response[0].json['error']

def test_swapi_failure(app):
    with app.test_request_context('/?resource=people', headers=AUTH_HEADERS):
        with patch('main.swapi_data') as mock_service:
            mock_service.return_value = None

            from flask import request
            response = star_wars_api(request)

            assert response[1] == 502