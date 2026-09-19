import sys
from datetime import datetime
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class MainWindow(QMainWindow):
    def __init__(self) -> None:

        super().__init__()

        self.setWindowTitle("PayFlow RT Simulator")
        self.setMinimumSize(900, 600)

        title_label = QLabel("Интегрированная платёжная система")
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)

        header_layout = QHBoxLayout()
        header_layout.addWidget(title_label)

        status_label = QLabel("Симуляция остановлена")
        header_layout.addWidget(status_label)
        controls_layout = QHBoxLayout()
        operation_label = QLabel("Операционный обзор")
        controls_layout.addWidget(operation_label)

        start_button = QPushButton("Старт")
        pause_button = QPushButton("Пауза")
        stop_button = QPushButton("Стоп")
        controls_layout.addStretch(stretch=100)
        start_button.clicked.connect(lambda: status_label.setText("Симуляция активна"))
        pause_button.clicked.connect(lambda: status_label.setText("Симуляция приостановлена"))
        stop_button.clicked.connect(lambda: status_label.setText("Симуляция остановлена"))

        controls_layout.addWidget(start_button)

        controls_layout.addWidget(pause_button)
        controls_layout.addWidget(stop_button)

        main_layout.addLayout(header_layout)
        main_layout.addLayout(controls_layout)

        self.setCentralWidget(central_widget)
        self.clock_label = QLabel()
        header_layout.addWidget(self.clock_label)

        self.clock_timer = QTimer(self)
        self.clock_timer.timeout.connect(self.update_clock)
        self.clock_timer.start(1000)

        self.update_clock()
        def update_clock(self) -> None:
                current_time = datetime.now().strftime("%H:%M:%S")
                self.clock_label.setText(current_time)


app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec())