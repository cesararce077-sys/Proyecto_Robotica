from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
)

from hmi.widgets.connection_panel import ConnectionPanel
from hmi.widgets.homing_panel import HomingPanel
from hmi.widgets.operation_panel import OperationPanel
from hmi.widgets.well_selector import WellSelector
from hmi.widgets.status_panel import StatusPanel


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("Robotic Pipetting HMI")
        self.setMinimumSize(1000, 650)

        self.connection_panel = ConnectionPanel()
        self.homing_panel = HomingPanel()
        self.operation_panel = OperationPanel()
        self.well_selector = WellSelector()
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

    def _on_connect_requested(self, port: str, baudrate: int) -> None:
        self.status_panel.log_message(f"Connect requested: {port} @ {baudrate}")

    def _on_disconnect_requested(self) -> None:
        self.status_panel.log_message("Disconnect requested.")

    def _on_home_requested(self) -> None:
        self.status_panel.log_message("Home requested.")

    def _on_stop_requested(self) -> None:
        self.status_panel.log_message("Stop requested.")

    def _on_estop_requested(self) -> None:
        self.status_panel.log_message("Emergency stop requested.")

    def _on_start_requested(self) -> None:
        mode = self.operation_panel.get_selected_mode()
        wells = self.well_selector.get_selected_wells()

        self.status_panel.log_message(f"Start requested. Mode: {mode}. Wells: {wells}")