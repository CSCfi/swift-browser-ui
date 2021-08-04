"""Authentication support module."""


import hmac
import time
import os


def sign_api_request(path: str) -> dict:
    """Handle authentication with a signature."""
    valid_until = str(int(time.time() + (60 * 61)))
    to_sign = (valid_until + path).encode("utf-8")

    digest = hmac.new(
        key=os.environ.get("SWIFT_UI_API_KEY", "").encode("utf-8"),
        msg=to_sign,
        digestmod="sha256",
    ).hexdigest()

    return {
        "valid": valid_until,
        "signature": digest,
    }
