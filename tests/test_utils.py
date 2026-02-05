import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from utils import convert_numeric_value, apply_filter, process_sort

def test_convert_numeric_standard():
    assert convert_numeric_value("172") == 172.0
    assert convert_numeric_value("77.5") == 77.5

def test_convert_numeric_with_comma():
    assert convert_numeric_value("1,500") == 1500.0

def test_convert_numeric_unknown():
    assert convert_numeric_value("unknown") is None
    assert convert_numeric_value("n/a") is None
    assert convert_numeric_value(None) is None

def test_filter_exact_match():
    data = [{"color": "red"}, {"color": "blue"}, {"color": "Red"}]
    assert len(apply_filter(data, "color", "red")) == 2

def test_filter_key_not_found():
    data = [{"name": "Luke"}]
    assert len(apply_filter(data, "age", "20")) == 0

def test_sort_numeric_asc():
    data = [{"mass": "20"}, {"mass": "100"}, {"mass": "5"}]
    sorted_data = process_sort(data, "people", order_by="mass", direction="asc")
    assert sorted_data[0]['mass'] == 5.0
    assert sorted_data[2]['mass'] == 100.0

def test_sort_with_nulls_asc():
    data = [{"mass": "10"}, {"mass": None}, {"mass": "1"}]
    sorted_data = process_sort(data, "people", order_by="mass", direction="asc")
    assert sorted_data[0]['mass'] == 1.0
    assert sorted_data[1]['mass'] == 10.0
    assert sorted_data[2]['mass'] is None


def test_sort_with_nulls_desc():
    data = [{"mass": "10"}, {"mass": None}, {"mass": "1"}]
    sorted_data = process_sort(data, "people", order_by="mass", direction="desc")
    assert sorted_data[0]['mass'] == 10.0
    assert sorted_data[1]['mass'] == 1.0
    assert sorted_data[2]['mass'] is None