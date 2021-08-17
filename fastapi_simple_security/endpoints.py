from typing import List, Optional
import os

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from email_validator import validate_email, EmailNotValidError
from fastapi_simple_security._security_secret import secret_based_security
from fastapi_simple_security.security_api_key import api_key_security
from fastapi_simple_security._sqlite_access import sqlite_access

api_key_router = APIRouter()

show_endpoints = False if "FASTAPI_SIMPLE_SECURITY_HIDE_DOCS" in os.environ else True

class NewUser(BaseModel):
    name: str
    last_name: str
    mail_address: str


@api_key_router.post("/new", include_in_schema=show_endpoints)
def get_new_api_key(new_user: NewUser, never_expires=None) -> str:
    """
    Args:
        never_expires: if set, the created API key will never be considered expired

    Returns:
        api_key: a newly generated API key
    """
    try:
        # Validate.
        valid = validate_email(new_user.mail_address)

        # Update with the normalized form.
        email = valid.email
    except EmailNotValidError as e:
    # email is not valid, exception message is human-readable
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email")
    return sqlite_access.create_key(new_user.name, new_user.last_name, email)


@api_key_router.get("/revoke", dependencies=[Depends(secret_based_security)], include_in_schema=show_endpoints)
def revoke_api_key(api_key: str):
    """
    Revokes the usage of the given API key

    Args:
        api_key: the api_key to revoke
    """
    return sqlite_access.revoke_key(api_key)


@api_key_router.get("/renew", dependencies=[Depends(api_key_security)], include_in_schema=show_endpoints)
def renew_api_key(api_key: str, expiration_date: str = None):
    """
    Renews the chosen API key, reactivating it if it was revoked.

    Args:
        api_key: the API key to renew
        expiration_date: the new expiration date in ISO format
    """
    return sqlite_access.renew_key(api_key, expiration_date)


class UsageLog(BaseModel):
    email: str
    api_key: str
    is_active: bool
    never_expire: bool
    expiration_date: str
    latest_query_date: Optional[str]
    total_queries: int


class UsageLogs(BaseModel):
    logs: List[UsageLog]


@api_key_router.get(
    "/logs", dependencies=[Depends(api_key_security)], response_model=UsageLogs, include_in_schema=show_endpoints
)
def get_api_key_usage_logs():
    """
    Returns usage information for all API keys
    """
    # TODO Add some sort of filtering on older keys/unused keys?
    print(sqlite_access.get_usage_stats())
    return UsageLogs(
        logs=[
            UsageLog(
                email=row[0],
                api_key=row[1],
                is_active=bool(row[2]),
                never_expire=bool(row[3]),
                expiration_date=row[4],
                latest_query_date=row[5],
                total_queries=int(row[6]),
            )
            for row in sqlite_access.get_usage_stats()
        ]
    )
