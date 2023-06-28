import json

import pytest

from stactools_pipelines.pipelines import conftest
from stactools_pipelines.pipelines.sentinel1.collection import handler


@pytest.mark.parametrize("pipeline_id", ["sentinel1"])
@pytest.mark.parametrize("module", ["collection"])
def test_handler(mock_env, get_token, create_collection, requests):
    handler({}, {})
    get_token.assert_called_once()
    create_collection.assert_called_once_with(json_path="")
    requests.post.assert_called_once_with(
        url=f"{conftest.ingestor_url}/collections",
        data=json.dumps(conftest.collection),
        headers={"Authorization": f"bearer {conftest.token}"},
    )
