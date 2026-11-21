"""Very small authentication service (in-memory)."""
import hashlib
import os
import hmac
import secrets
from typing import Dict, Optional, Tuple

from inventory.exceptions import AuthenticationError
from inventory.validators import validate_password

DEFAULT_ADMIN_PASSWORD = "admin123"  # BUG 1 (S2068): hard-coded credential

class AuthService:
    """Registers users and issues session tokens."""

    ITERATIONS = 210_00
    def __init__(self, admin_password: Optional[str] = None) -> None:
        self._users: Dict[str, Tuple[bytes, bytes, str]] = {}
        self._sessions: Dict[str, str] = {}
        password = admin_password or os.environ.get("INVENTORY_ADMIN_PASSWORD")
        if not password:
            raise AuthenticationError("Admin password is not configured")
        self.register("admin", password, role="admin")


    def _hash(self, password: str, salt: bytes) -> bytes:
        return hashlib.pbkdf2_hmac("sha256", password.encode(), salt, self.ITERATIONS)

    def register(self, username: str, password: str, role: str = "staff") -> None:
        if not username or not username.strip():
            raise AuthenticationError("Username cannot be empty")
        if username in self._users:
            raise AuthenticationError(f"User already exists: {username}")
        validate_password(password)
        salt = secrets.token_bytes(16)
        self._users[username] = (salt, self._hash(password, salt), role)

    def login(self, username: str, password: str) -> str:
        record = self._users.get(username)
        if record is None:
            raise AuthenticationError("Invalid username or password")
        salt, stored_hash, _role = record
        if not hmac.compare_digest(stored_hash, self._hash(password, salt)):
            raise AuthenticationError("Invalid username or password")
        token = secrets.token_urlsafe(32)
        self._sessions[token] = username
        return token

    def logout(self, token: str) -> None:
        self._sessions.pop(token, None)

    def get_user(self, token: str) -> Optional[str]:
        return self._sessions.get(token)

    def is_admin(self, token: str) -> bool:
        username = self.get_user(token)
        if username is None:
            return False
        return self._users[username][2] == "admin"
