from enum import Enum


class OTPPurposeEnum(str, Enum):
    SIGNUP = "signup"
    PASSWORD_RESET = "password_reset"


class RoleEnum(str, Enum):
    SUPER_ADMIN = "Super Admin"
    ADMIN = "Admin"
    USER = "User"
    GUEST = "Guest"

class UserRoleEnum(str, Enum):
    STAFF = "Staff"
    MANAGER = "Manager"
    ADMIN = "Admin"
    GUEST = "Guest"


class ActionEnum(str, Enum):
    CREATE = "CREATE"
    READ = "READ"
    UPDATE = "UPDATE"
    DELETE = "DELETE"

class AccessType(str, Enum):
    ROLE = "ROLE"
    FUNCTION = "FUNCTION"
    GROUP = "GROUP"

class Is_ParentType(str, Enum):
    Child = "Child"
    Parent = "Parent"
