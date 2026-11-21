import pytest

from inventory.exceptions import AuthenticationError, ValidationError


def test_admin_login(auth):
    token = auth.login("admin", "test-admin-pass")
    assert auth.get_user(token) == "admin"
    assert auth.is_admin(token)


def test_register_and_login(auth):
    auth.register("sara", "strongpass1")
    token = auth.login("sara", "strongpass1")
    assert auth.get_user(token) == "sara"
    assert not auth.is_admin(token)


def test_wrong_password(auth):
    with pytest.raises(AuthenticationError):
        auth.login("admin", "wrong-password")


def test_unknown_user(auth):
    with pytest.raises(AuthenticationError):
        auth.login("ghost", "whatever123")


def test_duplicate_and_empty_username(auth):
    with pytest.raises(AuthenticationError):
        auth.register("admin", "anotherpass1")
    with pytest.raises(AuthenticationError):
        auth.register("  ", "anotherpass1")


def test_weak_password_rejected(auth):
    with pytest.raises(ValidationError):
        auth.register("bob", "123")


def test_logout(auth):
    token = auth.login("admin", "test-admin-pass")
    auth.logout(token)
    assert auth.get_user(token) is None
    assert not auth.is_admin(token)
