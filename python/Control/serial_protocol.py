"""
Serial JSON protocol definitions for the PRR robotic pipetting project.

This file centralizes command names, message types, statuses, and communication
settings used by the Python control layer and HMI.

Protocol version: 0.1
"""

from enum import StrEnum


# ------------------------------------------------------------
# Serial communication settings
# ------------------------------------------------------------

BAUD_RATE = 115200
ENCODING = "utf-8"
LINE_ENDING = "\n"
READ_TIMEOUT_S = 0.1


# ------------------------------------------------------------
# Commands sent from Python/HMI to firmware
# ------------------------------------------------------------

class Command(StrEnum):
    PING = "PING"
    HOME = "HOME"
    STOP = "STOP"


# ------------------------------------------------------------
# Message types sent from firmware to Python/HMI
# ------------------------------------------------------------

class MessageType(StrEnum):
    ACK = "ack"
    STATUS = "status"
    ERROR = "error"


# ------------------------------------------------------------
# Firmware/robot statuses
# ------------------------------------------------------------

class RobotStatus(StrEnum):
    READY = "READY"
    IDLE = "IDLE"
    HOMING = "HOMING"
    HOMED = "HOMED"
    STOPPED = "STOPPED"
    ERROR = "ERROR"


# ------------------------------------------------------------
# JSON field names
# ------------------------------------------------------------

FIELD_COMMAND = "cmd"
FIELD_TYPE = "type"
FIELD_STATUS = "status"
FIELD_OK = "ok"
FIELD_MESSAGE = "message"


# ------------------------------------------------------------
# Helper functions for outgoing Python messages
# ------------------------------------------------------------

def make_command(command: Command) -> dict:
    """
    Build a command message to send to the firmware.

    Example:
        make_command(Command.HOME)
        -> {"cmd": "HOME"}
    """
    return {
        FIELD_COMMAND: command.value
    }


def make_ping_command() -> dict:
    return make_command(Command.PING)


def make_home_command() -> dict:
    return make_command(Command.HOME)


def make_stop_command() -> dict:
    return make_command(Command.STOP)


# ------------------------------------------------------------
# Helper functions for received firmware messages
# ------------------------------------------------------------

def is_ack_message(message: dict) -> bool:
    return message.get(FIELD_TYPE) == MessageType.ACK.value


def is_status_message(message: dict) -> bool:
    return message.get(FIELD_TYPE) == MessageType.STATUS.value


def is_error_message(message: dict) -> bool:
    return message.get(FIELD_TYPE) == MessageType.ERROR.value


def get_message_text(message: dict) -> str:
    """
    Return a readable message for the HMI status label.
    """
    status = message.get(FIELD_STATUS)
    text = message.get(FIELD_MESSAGE)

    if status and text:
        return f"{status}: {text}"

    if text:
        return text

    return str(message)