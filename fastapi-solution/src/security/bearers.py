from fastapi import HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.security.utils import get_authorization_scheme_param


class OAuth2PasswordCookiesBearer(OAuth2PasswordBearer):
    async def __call__(self, request: Request) -> dict[str, str] | None:
        bearer_acces_token = request.cookies.get("access_token")
        bearer_refresh_token = request.cookies.get("refresh_token")

        scheme, access_token = get_authorization_scheme_param(
            bearer_acces_token,
        )
        _, refresh_token = get_authorization_scheme_param(bearer_refresh_token)
        if not access_token or scheme.lower() != "bearer":
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            else:
                return None

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
        }