# Planted issues and fixes

## Issue 1 – Hard-coded credential (Vulnerability, rule `python:S2068`)
File: `inventory/auth.py`

Before:
```python
DEFAULT_ADMIN_PASSWORD = "admin123"

class AuthService:
    def __init__(self) -> None:
        ...
        self.register("admin", DEFAULT_ADMIN_PASSWORD, role="admin")
```

After:
```python
import os
from typing import Dict, Optional, Tuple

class AuthService:
    ITERATIONS = 210_000

    def __init__(self, admin_password: Optional[str] = None) -> None:
        self._users: Dict[str, Tuple[bytes, bytes, str]] = {}
        self._sessions: Dict[str, str] = {}
        password = admin_password or os.environ.get("INVENTORY_ADMIN_PASSWORD")
        if not password:
            raise AuthenticationError("Admin password is not configured")
        self.register("admin", password, role="admin")
```
(Delete the `DEFAULT_ADMIN_PASSWORD` constant.)

Update `tests/conftest.py` and `tests/test_auth.py`:
```python
# conftest.py
return AuthService(admin_password="test-admin-pass")

# test_auth.py: replace "admin123" with "test-admin-pass"
```

## Issue 2 – Duplicate `elif` condition (Bug, rule `python:S1862`)
File: `inventory/services.py` – the third branch can never run, so a
higher tier is never applied.

Before:
```python
if tier == "gold":
    rate = 0.15
elif tier == "silver":
    rate = 0.10
elif tier == "gold":
    rate = 0.20
```

After:
```python
def discount_rate(self, tier: str) -> float:
    rates = {"standard": 0.0, "silver": 0.10, "gold": 0.15, "platinum": 0.20}
    return rates.get(tier, 0.0)
```

Add a test:
```python
def test_platinum_discount(service):
    assert service.discount_rate("platinum") == 0.20
```
