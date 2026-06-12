#include "command_parser.h"

#include <ArduinoJson.h>

#include "robot_state_machine.h"
#include "serial_protocol.h"

static void handlePing() {
  sendAck("PING", true, "ESP32-C6 alive");
}

static void handleHome() {
  if (!canStartHoming()) {
    sendCommandError("HOME", "Homing can only start from IDLE or STOPPED");
    return;
  }

  setIsHomed(false);

  sendAck("HOME", true, "HOME command received");

  enterState(STATE_HOMING);
  sendStatus("HOMING", "Homing started");
}

static void handleStop() {
  if (getCurrentState() == STATE_ESTOPPED) {
    sendCommandError("STOP", "Cannot stop because robot is already in ESTOPPED state");
    return;
  }

  sendAck("STOP", true, "STOP command received");

  enterState(STATE_STOPPED);
  sendStatus("STOPPED", "Robot stopped by command");
}

static void handleEmergencyStop() {
  setIsHomed(false);

  sendAck("ESTOP", true, "Emergency stop command received");

  enterState(STATE_ESTOPPED);
  sendStatus("ESTOPPED", "Emergency stop active");
}

static void handleMoveDummy() {
  if (!canStartMotion()) {
    sendCommandError("MOVE_DUMMY", "Motion requires IDLE state and completed homing");
    return;
  }

  sendAck("MOVE_DUMMY", true, "Dummy move command received");

  enterState(STATE_MOVING);
  sendStatus("MOVING", "Dummy movement started");
}

void processJsonLine(String line) {
  line.trim();

  if (line.length() == 0) {
    return;
  }

  StaticJsonDocument<256> doc;
  DeserializationError error = deserializeJson(doc, line);

  if (error) {
    sendError("Invalid JSON");
    return;
  }

  if (!doc.containsKey("cmd")) {
    sendError("Missing cmd field");
    return;
  }

  const char* cmd = doc["cmd"];

  // High-priority software commands first.
  if (strcmp(cmd, "ESTOP") == 0) {
    handleEmergencyStop();
    return;
  }

  if (strcmp(cmd, "STOP") == 0) {
    handleStop();
    return;
  }

  // Normal commands.
  if (strcmp(cmd, "PING") == 0) {
    handlePing();
  } else if (strcmp(cmd, "HOME") == 0) {
    handleHome();
  } else if (strcmp(cmd, "MOVE_DUMMY") == 0) {
    handleMoveDummy();
  } else {
    sendCommandError(cmd, "Unknown command");
  }
}