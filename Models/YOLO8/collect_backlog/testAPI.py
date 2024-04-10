# WebCOOS API Python Request
from io import BytesIO
import requests
import json
# import os
from datetime import datetime, timedelta

# 2024-04-07T07:00:00Z


def get_inventory(start_time):
    # Define API token.
    api_token = 'c5b771f56d81cbfbcb3644eb7ec19fc707e36f6a'
    headers = {'Authorization': f'Token {
        api_token}', 'Accept': 'application/json'}

    # Define API endpoints.

    endpoint_url = 'https://app.webcoos.org/webcoos/api/v1/elements/'

    # Get list of specific camera's statistical inventory of dates that data is available.
    # Order is earliest to latest date of coverage. "NaT" means no data available.
    # INPUT: station = 'Common Slug'
    station = 'masonboro_inlet'
    inventory_url = f'https://app.webcoos.org/webcoos/api/v1/services/{
        station}-one-minute-stills-s3/inventory/'

    # Parse the starting_after time
    starting_after = datetime.strptime(
        start_time, '%Y-%m-%dT%H:%M:%SZ')

    # Add 15 minutes
    starting_before = starting_after + timedelta(minutes=30)

    # Convert back to string
    starting_after = starting_after.strftime('%Y-%m-%dT%H:%M:%SZ')
    starting_before = starting_before.strftime('%Y-%m-%dT%H:%M:%SZ')

    # Set parameters for element request.
    params = {
        'service': station + '-one-minute-stills-s3',
        'starting_after': starting_after,
        'starting_before': starting_before
    }
    element_response = requests.get(
        endpoint_url, headers=headers, params=params)
    elements_data = element_response.json()

    # PRINT ALL.
    # for element in elements_data['results']: uuid, slug, url, size, temporal_min = element['uuid'], element['data']['common']['slug'], element['data']['properties']['url'], element['data']['properties']['size'], element['data']['extents']['temporal']['min']; print(f"UUID: {uuid}\nSlug: {slug}\nURL: {url}\nSize: {size} bytes\nTemporal Min: {temporal_min}\n{'-' * 40}")

    # PRINT URL and TEMPORAL MIN only.
    for element in elements_data['results']:
        url = element['data']['properties']['url']
        temporal_min = element['data']['extents']['temporal']['min']
    return elements_data['results']
