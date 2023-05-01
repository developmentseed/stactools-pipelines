import os

import requests


def get_token() -> str:
    domain = os.environ["DOMAIN"]
    client_secret = os.environ["CLIENT_SECRET"]
    client_id = os.environ["CLIENT_ID"]
    scope = os.environ["SCOPE"]
    response = requests.post(
        f"{domain}/oauth2/token",
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
        },
        auth=(client_id, client_secret),
        data={
            "grant_type": "client_credentials",
            # A space-separated list of scopes to request for the generated access token.
            "scope": scope,
        },
    )
    try:
        response.raise_for_status()
    except Exception:
        print(response.text)
        raise

    return response.json()["access_token"]
