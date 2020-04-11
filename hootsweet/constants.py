from enum import Enum


class Reviewer(Enum):
    EXTERNAL = 1
    MEMBER = 2


class MessageState(Enum):
    PENDING_APPROVAL = 1
    REJECTED = 2
    SENT = 3
    SCHEDULED = 4
    SEND_FAILED_PERMANENTLY = 5
