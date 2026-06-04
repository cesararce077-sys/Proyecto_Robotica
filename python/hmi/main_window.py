from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
)

from tools.config_loader import load_yaml_config
from hmi.widgets.connection_panel import ConnectionPanel
from hmi.widgets.homing_panel import HomingPanel
from hmi.widgets.operation_panel import OperationPanel
from hmi.widgets.well_selector import WellSelector
from hmi.widgets.status_panel import StatusPanel
from hmi.serial_qt_bridge import SerialQtBridge

class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("Robotic Pipetting HMI")
        self.setMinimumSize(1000, 650)

        serial_config_file = load_yaml_config("serial_config.yaml")
        serial_config = serial_config_file.get("serial", {})

        plate_config_file = load_yaml_config("plate_config.yaml")
        plate_config = plate_config_file.get("plate", {})


        self.serial_bridge: SerialQtBridge | None = None

        self.connection_panel = ConnectionPanel(serial_config=serial_config)
        self.homing_panel = HomingPanel()
        self.operation_panel = OperationPanel()
        self.well_selector = WellSelector(plate_config=plate_config)
        self.status_panel = StatusPanel()

        self._build_ui()
        self._connect_signals()

    def _build_ui(self) -> None:
        central_widget = QWidget()
        main_layout = QVBoxLayout()

        title = QLabel("Robotic Pipetting HMI")
        title.setObjectName("titleLabel")

        top_layout = QHBoxLayout()
        top_layout.addWidget(self.connection_panel)
        top_layout.addWidget(self.homing_panel)

        middle_layout = QHBoxLayout()
        middle_layout.addWidget(self.operation_panel)
        middle_layout.addWidget(self.well_selector)

        main_layout.addWidget(title)
        main_layout.addLayout(top_layout)
        main_layout.addLayout(middle_layout)
        main_layout.addWidget(self.status_panel)

        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def _connect_signals(self) -> None:
        self.connection_panel.connect_requested.connect(self._on_connect_requested)
        self.connection_panel.disconnect_requested.connect(self._on_disconnect_requested)

        self.homing_panel.home_requested.connect(self._on_home_requested)
        self.homing_panel.stop_requested.connect(self._on_stop_requested)
        self.homing_panel.estop_requested.connect(self._on_estop_requested)

        self.operation_panel.start_requested.connect(self._on_start_requested)
        self.well_selector.well_selection_changed.connect(self._on_well_selection_changed)

    def _on_connect_requested(self, port: str, baudrate: int) -> None:
        self.status_panel.log_message(f"Connecting to {port} @ {baudrate}...")

        if self.serial_bridge is not None and self.serial_bridge.is_connected:
            self.status_panel.log_message("Already connected.")
            return

        self.serial_bridge = SerialQtBridge(port=port, baud_rate=baudrate)

        self.serial_bridge.status_text_received.connect(self._on_serial_status_text)
        self.serial_bridge.error_received.connect(self._on_serial_error)
        self.serial_bridge.connection_changed.connect(self._on_serial_connection_changed)

        self.serial_bridge.connect_serial()

    def _on_disconnect_requested(self) -> None:
        if self.serial_bridge is None:
            self.status_panel.log_message("Disconnect requested, but no serial bridge exists.")
            return

        self.serial_bridge.disconnect_serial()
        self.status_panel.log_message("Disconnect requested.")

    def _on_home_requested(self) -> None:
        self.status_panel.log_message("Home requested.")

        if self.serial_bridge is None or not self.serial_bridge.is_connected:
            self.status_panel.log_message("Error: Serial controller is not connected.")
            return

        self.serial_bridge.home()

    def _on_stop_requested(self) -> None:
        self.status_panel.log_message("Stop requested.")

        if self.serial_bridge is None or not self.serial_bridge.is_connected:
            self.status_panel.log_message("Error: Serial controller is not connected.")
            return

        self.serial_bridge.stop()

    def _on_estop_requested(self) -> None:
        self.status_panel.log_message("Emergency stop requested.")

        if self.serial_bridge is None or not self.serial_bridge.is_connected:
            self.status_panel.log_message("Error: Serial controller is not connected.")
            return

        self.serial_bridge.stop()

    def _on_start_requested(self) -> None:
        mode = self.operation_panel.get_selected_mode()

        if mode == "all":
            wells = self.well_selector.get_all_wells()
        elif mode == "selected":
            wells = self.well_selector.get_selected_wells()
        elif mode == "route":
            wells = self.well_selector.get_route_wells()
        else:
            self.status_panel.log_message(f"Error: Unknown operation mode: {mode}")
            return

        self.status_panel.log_message(f"Start requested. Mode: {mode}. Wells: {wells}")

        for well in wells:
            try:
                coordinates = self.well_selector.get_well_coordinates(well)
                self.status_panel.log_message(f"{well}: {coordinates}")
            except ValueError as error:
                self.status_panel.log_message(f"Error: {error}")

    def _on_well_selection_changed(self, wells: list[str]) -> None:
        mode = self.operation_panel.get_selected_mode()

        if mode == "route":
            self.status_panel.log_message(f"Route order: {wells}")
        else:
            selected_wells = self.well_selector.get_selected_wells()
            self.status_panel.log_message(f"Selected wells: {selected_wells}")

    def _on_serial_status_text(self, text: str) -> None:
        self.status_panel.log_message(f"Firmware: {text}")

    def _on_serial_error(self, error: str) -> None:
        self.status_panel.log_message(f"Serial error: {error}")

    def _on_serial_connection_changed(self, connected: bool) -> None:
        if connected:
            self.connection_panel.status_label.setText("Status: Connected")
            self.status_panel.log_message("Serial connection established.")
        else:
            self.connection_panel.status_label.setText("Status: Disconnected")
            self.status_panel.log_message("Serial connection closed.")