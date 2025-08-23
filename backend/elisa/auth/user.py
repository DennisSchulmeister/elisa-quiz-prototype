# Elisa: AI Learning Assistant
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from __future__ import annotations

import os, requests

from jwt            import decode as jwt_decode, get_unverified_header, PyJWK
from jwt.exceptions import InvalidTokenError

class User:
    """
    Information about the currently logged-in user (if any) with authorization
    checks. An instance of this class is created by the websocket parent handler
    and passed to the down-stream handlers.
    """
    class _JWT:
        """
        Configuration values for decoding and verifying OIDC access tokens presented
        by the client.
        """
        jwks:       dict       = {}
        public_key: str        = ""
        algorithms: list[str]  = []
        require:    list[str]  = []
        audience:   str | None = None
        issuer:     str | None = None

        @classmethod
        def decode(cls, jwt: str) -> dict:
            """
            Decode access token and perform basic validation to ensure that is has
            not expired.
            """
            header     = get_unverified_header(jwt)
            public_key = cls.public_key if cls.public_key else ""
            
            for key in cls.jwks.get("keys", []):
                if key["kid"] == header["kid"]:
                    public_key = PyJWK(key)
                    break

            return jwt_decode(
                jwt        = jwt,
                key        = public_key,
                algorithms = cls.algorithms,
                audience   = cls.audience,
                issuer     = cls.issuer,
                options    = {
                    "require":    cls.require,
                    "verify_exp": True,
                },
            )
    
    class _Fallback:
        """
        Fallback user and scopes for unauthenticated requests. Note: This is only
        meant for demonstration and testing without a proper OIDC identity provider.
        """
        subject: str       = ""
        scopes:  list[str] = []

    @classmethod
    def read_config(cls):
        """
        Read configuration settings during server startup.
        """
        jwks_url = os.environ.get("ELISA_OIDC_JWKS_URL")

        if jwks_url:
            cls._JWT.jwks = requests.get(jwks_url).json()

        cls._JWT.public_key = os.environ.get("ELISA_OIDC_PUBLIC_KEY", "")
        cls._JWT.algorithms = [value.strip() for value in os.environ.get("ELISA_OIDC_ALGORITHMS", "RS256").split(",")]
        cls._JWT.require    = [value.strip() for value in os.environ.get("ELISA_OIDC_REQUIRE", "aud, exp, scope").split(",")]
        cls._JWT.audience   = os.environ.get("ELISA_OIDC_CLIENT_ID")
        cls._JWT.issuer     = os.environ.get("ELISA_OIDC_ISSUER")

        cls._Fallback.subject = os.environ.get("ELISA_AUTH_SUBJECT", "")
        cls._Fallback.scopes  = [value.strip() for value in os.environ.get("ELISA_AUTH_SCOPES", "").split(",")]

    def __init__(self, jwt: str = ""):
        """
        Initialization from a JWT token received from an OIDC identity provider.
        If no token is provided, an anonymous (logged-out) user is assumed.
        """
        self.logged_in = False
        self.subject   = self._Fallback.subject
        self.scopes    = self._Fallback.scopes

        if jwt:
            try:
                token = self._JWT.decode(jwt)

                self.subject = token["sub"]
                self.scopes  = token.get("scope", "").split()
            except InvalidTokenError:
                if not self._Fallback.subject:
                    raise
