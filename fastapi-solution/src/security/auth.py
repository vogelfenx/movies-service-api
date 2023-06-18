from typing import Annotated, Any

import requests
from fastapi import Depends, HTTPException, Response, status
from jose import ExpiredSignatureError, JWTError, jwt

from core.config import security_settings
from core.logger import get_logger
from security.bearers import OAuth2PasswordCookiesBearer
from security.models import UserToken

logger = get_logger(__name__)


oauth2_scheme = OAuth2PasswordCookiesBearer(
    tokenUrl=security_settings.auth_service_token_url,
)


class Auth():
    """Authentication class.

    Provide methods to handle user authentication.
    """

    def __init__(
        self,
        response: Response,
        token: Annotated[dict[str, str], Depends(oauth2_scheme)],
    ) -> None:
        self.access_token = token.get("access_token")
        self.refresh_token = token.get("refresh_token")
        self.response = response
        self._decode_token()

    def get_user_claims(self) -> UserToken:
        """Return user claims from token.

        Returns:
            UserToken: user token claims
        """
        logger.warning("The method get_user_from_token not implemented yet.")
        return UserToken()

    def _decode_token(self) -> dict[str, Any]:
        """Verifies a JWT string's signature and validates reserved claims.

        Returns:
            dict[str, Any]: jwt token dict representation.

        Raises:
            ExpiredSignatureError - if token expired
            JWTError - if token invalid
        """
        try:
            decoded_token = jwt.decode(
                token=self.access_token,
                key=security_settings.secret_key,
                algorithms=[security_settings.algorithm],
            )
        except ExpiredSignatureError:
            status = self._refresh_token()
            if not status:
                self._raise_expired_exception()
            decoded_token = self._decode_token()
        except JWTError:
            self._raise_credential_exception()

        return decoded_token

    def _refresh_token(self) -> bool:
        """Request new access & refresh tokens using the provided refresh token, if any.

        Returns:
            bool: whether the refreshing of the token was successful or not
        """
        response = requests.post(
            url=security_settings.auth_service_refresh_token_url,
            json=self.refresh_token,
        )
        if response.ok:
            tokens = response.json()

            self.response.set_cookie(
                key="access_token",
                value="Bearer {0}".format(tokens.get("access_token")),
                httponly=True,
            )
            self.response.set_cookie(
                key="refresh_token",
                value="Bearer {0}".format(tokens.get("refresh_token")),
                httponly=True,
            )
            self.access_token = tokens.get('access_token')

        return response.ok

    def _raise_expired_exception(self):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )

    def _raise_credential_exception(self):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
