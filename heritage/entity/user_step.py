from enum import Enum


class UserStep(str, Enum):
    START = "Start"
    HELP = "Get help"
    GET = "Get photos"
    GET_MORE = "Get more photos"
