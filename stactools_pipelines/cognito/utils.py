import os
import time
import requests
from typing import Optional

import boto3


class JwtCache:
    """
    A DynamoDB cache for JWT tokens. Used to avoid high fees for M2M authentication in
    Cognito.
    """

    def __init__(self, table_name: str):
        self.dynamodb = boto3.resource("dynamodb")
        self.table = self.dynamodb.Table(table_name)

    def get_token(self, client_id: str) -> Optional[str]:
        response = self.table.get_item(Key={"client_id": client_id})
        item = response.get("Item")
        if not item:
            return None

        now = int(time.time())
        if item.get("expires_at", 0) > now:
            return item.get("jwt")
        return None

    def set_token(self, client_id: str, jwt: str, expires_at: int):
        self.table.put_item(
            Item={
                "client_id": client_id,
                "jwt": jwt,
                "expires_at": expires_at,
                "created_at": int(time.time()),
            }
        )


def get_token() -> str:
    domain = os.environ["DOMAIN"]
    client_secret = os.environ["CLIENT_SECRET"]
    client_id = os.environ["CLIENT_ID"]
    scope = os.environ["SCOPE"]

    # Try to get a non-expired JWT from the cache
    cache = JwtCache(os.environ["JWT_CACHE_TABLE_NAME"])
    jwt = cache.get_token(client_id)
    if jwt:
        return jwt

    # No valid JWT found, get a new one from Cognito
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

    data = response.json()
    jwt = data["access_token"]

    # Store the new JWT in the cache
    cache.set_token(
        client_id,
        jwt=jwt,
        expires_at=data["exp"] - (60 * 1000),  # expire 1 min early for safety
    )

    return jwt
