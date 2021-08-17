from fastapi import Security
from fastapi.security import APIKeyQuery, APIKeyHeader
from starlette.exceptions import HTTPException
from starlette.status import HTTP_403_FORBIDDEN

from fastapi_simple_security._sqlite_access import sqlite_access

API_KEY_NAME = "api_key"

# api_key_query = APIKeyQuery(name=API_KEY_NAME, scheme_name="API key query", auto_error=False)
api_key_header = APIKeyHeader(name=API_KEY_NAME, scheme_name="API key header", auto_error=False)


async def api_key_security(header_param: str = Security(api_key_header)):
    if not header_param:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="An API key must be passed in the header")

    elif header_param and sqlite_access.check_key(header_param):
        return header_param

    else:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="Wrong, revoked, or expired API key.")
