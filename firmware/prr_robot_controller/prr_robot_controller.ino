#include "communication/command_parser/command_parser.h"
#include "communication/serial_protocol/serial_protocol.h"
#include "controller_state_machine/robot_state_machine/robot_state_machine.h"
#include "state_actions/state_actions.h"

void setup() {
  initializeSerialProtocol();
  initializeStateMachine();

  sendStatus("IDLE", "ESP32-C6 state machine firmware ready");
}

void loop() {
  String line;

  if (readSerialLine(line)) {
    processJsonLine(line);
  }

  updateStateActions();
}