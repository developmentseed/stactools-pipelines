import json
from unittest.mock import call

import pytest
from stactools.noaa_hrrr.metadata import CloudProvider, Product, Region

from stactools_pipelines.pipelines import conftest
from stactools_pipelines.pipelines.noaa_hrrr.collection import handler


@pytest.mark.parametrize("pipeline_id", ["noaa_hrrr"])
@pytest.mark.parametrize("module", ["collection"])
def test_handler(mock_env, get_token, create_collection, requests):
    handler({}, {})
    get_token.assert_called_once()

    # Prepare expected calls for create_collection
    expected_create_collection_calls = [
        call(product=product, region=region, cloud_provider=CloudProvider.aws)
        for product in Product
        for region in Region
    ]

    # Check if create_collection was called correctly for each product and region
    create_collection.assert_has_calls(expected_create_collection_calls, any_order=True)

    # Prepare expected calls for requests.post
    expected_requests_calls = [
        call(
            url=f"{conftest.ingestor_url}/collections",
            data=json.dumps(conftest.collection),
            headers={"Authorization": f"bearer {conftest.token}"},
        )
    ] * (len(Product) * len(Region))

    # Check if the post requests were called correctly
    requests.post.assert_has_calls(expected_requests_calls, any_order=True)

    # Validate total number of calls for complete accuracy
    assert create_collection.call_count == len(Product) * len(Region)
    assert requests.post.call_count == len(Product) * len(Region)
