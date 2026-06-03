from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QGroupBox,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QPushButton,
)


class ConnectionPanel(QGroupBox):
    connect_requested = Signal(str, int)
    disconnect_requested = Signal()

    def __init__(self) -> None:
        super().__init__("Connection")

        self.port_combo = QComboBox()
        self.port_combo.addItems(["COM3", "COM4", "/dev/ttyUSB0", "/dev/ttyACM0"])

        self.baudrate_combo = QComboBox()
        self.baudrate_combo.addItems([
            "9600",
            "19200",
            "38400",
            "57600",
            "115200",
            "230400",
            "460800",
            "921600",
        ])
        self.baudrate_combo.setCurrentText("115200")

        self.connect_button = QPushButton("Connect")
        self.disconnect_button = QPushButton("Disconnect")

        self.status_label = QLabel("Status: Disconnected")

        self._build_ui()
        self._connect_signals()

    def _build_ui(self) -> None:
        layout = QVBoxLayout()

        port_layout = QHBoxLayout()
        port_layout.addWidget(QLabel("Port:"))
        port_layout.addWidget(self.port_combo)

        baud_layout = QHBoxLayout()
        baud_layout.addWidget(QLabel("Baudrate:"))
        baud_layout.addWidget(self.baudrate_combo)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.connect_button)
        button_layout.addWidget(self.disconnect_button)

        layout.addLayout(port_layout)
        layout.addLayout(baud_layout)
        layout.addLayout(button_layout)
        layout.addWidget(self.status_label)

        self.setLayout(layout)

    def _connect_signals(self) -> None:
        self.connect_button.clicked.connect(self._emit_connect)
        self.disconnect_button.clicked.connect(self.disconnect_requested.emit)

    def _emit_connect(self) -> None:
        port = self.port_combo.currentText()
        baudrate = int(self.baudrate_combo.currentText())
        self.connect_requested.emit(port, baudrate)