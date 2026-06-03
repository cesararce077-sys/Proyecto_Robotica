from PySide6.QtWidgets import QGroupBox, QGridLayout, QPushButton


class WellSelector(QGroupBox):
    def __init__(self) -> None:
        super().__init__("Well Selector")

        self.well_buttons = {}

        self._build_ui()

    def _build_ui(self) -> None:
        layout = QGridLayout()

        rows = ["A", "B"]
        columns = [1, 2, 3]

        for row_index, row_name in enumerate(rows):
            for column_index, column_number in enumerate(columns):
                well_name = f"{row_name}{column_number}"
                button = QPushButton(well_name)
                button.setCheckable(True)

                self.well_buttons[well_name] = button
                layout.addWidget(button, row_index, column_index)

        self.setLayout(layout)

    def get_selected_wells(self) -> list[str]:
        return [
            well_name
            for well_name, button in self.well_buttons.items()
            if button.isChecked()
        ]