from enum import Enum


class UserRole(Enum):
    MANAGER = "manager"
    QA = "qa"
    DEVELOPER = "developer"

    @classmethod
    def choices(cls):
        return [(role.value, role.name.capitalize()) for role in cls]


class TaskStatus(Enum):
    OPEN = "open"
    REVIEW = "review"
    WORKING = "working"
    AWAITING_RELEASE = "awaiting_release"
    WAITING_QA = "waiting_qa"

    @classmethod
    def choices(cls):
        return [
            (status.value, status.name.replace("_", " ").capitalize()) for status in cls
        ]
