"""Generates the short codes guests type (or scan from QR code) to join a room."""

import secrets

# characters allowed in a code, leaving out ones that look similar (ex: 0/O)
ALPHABET = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"
CODE_LENGTH = 6  # matches rooms.join_code which is String(6)


def generate_join_code() -> str:
    """Generates a random code like 'KSF84W'.

    Isn't guaranteed unique; Room service handles that.
    """
    return "".join(secrets.choice(ALPHABET) for _ in range(CODE_LENGTH))
