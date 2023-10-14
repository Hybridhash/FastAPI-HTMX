import uuid
from typing import Optional

from fastapi import Depends, Request
from fastapi_users import BaseUserManager, FastAPIUsers, UUIDIDMixin
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    CookieTransport,
    JWTStrategy,
)
from fastapi_users.db import SQLAlchemyUserDatabase
from fastapi_users.jwt import decode_jwt
from jwt.exceptions import InvalidTokenError
from loguru import logger

from app.database.db import User, get_user_db

SECRET = "SECRET"


class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        print(f"User {user.id} has registered.")

    async def on_after_forgot_password(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        print(f"User {user.id} has forgot their password. Reset token: {token}")

    async def on_after_request_verify(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        print(f"Verification requested for user {user.id}. Verification token: {token}")

    # Decoding the JWT token using the inheritance of the BaseUserManager
    async def on_decode_jwt(self, jwt_token: str):
        """
        Decodes a JWT token using the verification token secret and audience.

        Args:
            jwt_token (str): The JWT token to decode.

        Returns:
            dict: The decoded JWT token.
        """
        return decode_jwt(
            jwt_token,
            self.verification_token_secret,
            [self.verification_token_audience],
        )

async def get_user_manager(user_db: SQLAlchemyUserDatabase = Depends(get_user_db)):
    yield UserManager(user_db)

cookie_transport = CookieTransport(cookie_max_age=3600)
bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET, lifetime_seconds=300)


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=cookie_transport,
    get_strategy=get_jwt_strategy,
)


async def verify_jwt(jwt_token: str, user_db: SQLAlchemyUserDatabase = Depends(get_user_db)) -> bool:
    """
    Verifies the given JWT token by decoding it and checking its validity.

    Args:
        jwt_token (str): The JWT token to be verified.
        user_db (SQLAlchemyUserDatabase, optional): The user database to use for verification. 
                                                    Defaults to Depends(get_user_db).

    Returns:
        bool: True if the token is valid, False otherwise.
    """
    isTokenValid: bool = False
    try:
        async for user_manager in get_user_manager(user_db=user_db):
            payload = user_manager.on_decode_jwt(jwt_token)
            logger.debug(payload)
            # Add your verification logic here
            if payload:
                isTokenValid = True
    except InvalidTokenError:
        logger.debug(None)
    return isTokenValid


fastapi_users = FastAPIUsers[User, uuid.UUID](get_user_manager, [auth_backend])

logger.info(fastapi_users)

current_active_user = fastapi_users.current_user(active=True)