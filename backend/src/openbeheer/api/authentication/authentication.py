from rest_framework import authentication
from drf_spectacular.authentication import SessionScheme


class AnonCSRFSessionAuthentication(authentication.SessionAuthentication):
    """
    Enforce the CSRF checks even for non-authenticated users.

    DRF by default only enforces CSRF checks for authenticated users, assuming the
    attack vector targets logged-in sessions. However, the login endpoint also needs CSRF-protection.
    Only legitimate users who have received the CSRF-token from an endpoint are allowed to consume the API using
    session cookies.
    """

    def authenticate(self, request):
        result = super().authenticate(request)
        # this is different from core DRF
        if result is None:
            self.enforce_csrf(request)
        return result


class AnonCSRFSessionAuthScheme(SessionScheme):
    target_class = AnonCSRFSessionAuthentication
    name = "anonCSRFSession"
    # no extra requirements the csrf token is read from the Session
