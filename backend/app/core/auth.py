from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader, HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from jose.constants import ALGORITHMS

from app.core.config import settings

bearer_scheme = HTTPBearer()
api_key_header = APIKeyHeader(name="X-API-Key")

# ── Supabase JWKS cache ─────────────────────────────────────────────────────
_jwks_client = None
_jwks = None


async def _get_jwks():
    """Lazy-load and cache Supabase JWKS for token validation."""
    global _jwks, _jwks_client
    if _jwks is not None:
        return _jwks
    if not settings.supabase_url:
        # Fallback: decode with local secret (dev mode without Supabase)
        return None

    try:
        import httpx
        url = f"{settings.supabase_url.rstrip('/')}/auth/v1/.well-known/jwks.json"
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, timeout=10)
            resp.raise_for_status()
            data = resp.json()
        from jose import jwk
        _jwks = [jwk.construct(k) for k in data.get("keys", [])]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load JWKS: {e}")
    return _jwks


# ── Dependencies ─────────────────────────────────────────────────────────────


async def verify_jwt(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)) -> dict:
    """Validate JWT against Supabase JWKS (or local secret fallback)."""
    token = credentials.credentials
    try:
        keys = await _get_jwks()
        payload = None

        if keys:
            for key in keys:
                try:
                    payload = jwt.decode(token, key, algorithms=[ALGORITHMS.RS256], audience="authenticated")
                    break
                except JWTError:
                    continue
        else:
            # Dev fallback: local HS256
            payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])

        if payload is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token: no matching JWKS key")

        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token: missing sub")
        return {"user_id": user_id}

    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")


async def verify_m2m(api_key: str = Security(api_key_header)) -> dict:
    """Static API-Key auth for Hermes M2M router."""
    if api_key != settings.hermes_api_key:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid M2M API key")
    return {"service": "hermes"}
