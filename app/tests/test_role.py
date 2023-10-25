import pytest
from pydantic import ValidationError

from app.schema.users import RoleBase, RoleCreate


def test_create_valid_roles():
    # Test valid input
    role = RoleCreate(role_name="admin", role_desc="Role description")
    assert role.role_name == "admin"
    assert role.role_desc == "Role description"


def test_create_invalid_roles():
    # Test invalid input
    with pytest.raises(ValidationError):
        RoleCreate(role_name="a", role_desc="Role description")
    with pytest.raises(ValidationError):
        RoleCreate(role_name="admin", role_desc="")


def test_create_roles_with_long_inputs():
    # Test invalid input where role_name is more than 50 characters and role_desc is more than 200
    with pytest.raises(ValidationError):
        RoleCreate(role_name="a" * 51, role_desc="Role description")
    with pytest.raises(ValidationError):
        RoleCreate(role_name="admin", role_desc="a" * 201)


def test_create_roles_with_default_desc():
    # Test default value for role_desc
    role = RoleBase(role_name="admin")
    assert role.role_desc is None
