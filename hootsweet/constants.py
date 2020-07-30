from enum import Enum

MP4 = "video/mp4"
GIF = "image/gif"
JPEG = "image/jpeg"
JPG = "image/jpg"
PNG = "image/png"

ALLOWED_MIME_TYPES = [MP4, GIF, JPEG, JPG, PNG]


class Reviewer(Enum):
    EXTERNAL = 1
    MEMBER = 2


class MessageState(Enum):
    PENDING_APPROVAL = 1
    REJECTED = 2
    SENT = 3
    SCHEDULED = 4
    SEND_FAILED_PERMANENTLY = 5
