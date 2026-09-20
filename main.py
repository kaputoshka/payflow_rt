import sys
from datetime import datetime
from PySide6.QtCore import QTimer
from pathlib import Path
from PySide6.QtWidgets import (
    QApplication,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QTableWidget,
    QVBoxLayout,
    QWidget,
)


class MainWindow(QMainWindow):
    def __init__(self) -> None:

        super().__init__()

        self.setWindowTitle("PayFlow RT Simulator")
        self.setMinimumSize(900, 600)

        title_label = QLabel("Интегрированная платёжная система")
        title_label.setObjectName("titleLabel")
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(16)

        header_layout = QHBoxLayout()
        header_layout.addWidget(title_label)
        header_layout.addStretch(1)

        status_label = QLabel("Симуляция остановлена")
        status_label.setObjectName("statusLabel")
        header_layout.addWidget(status_label)
        controls_layout = QHBoxLayout()
        operation_label = QLabel("Операционный обзор")
        controls_layout.addWidget(operation_label)

        start_button = QPushButton("Старт")
        pause_button = QPushButton("Пауза")
        stop_button = QPushButton("Стоп")
        start_button.setObjectName("startButton")
        pause_button.setObjectName("pauseButton")
        stop_button.setObjectName("stopButton")

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



        kpi_layout = QHBoxLayout()

        operations_card = QGroupBox("Операций/с")
        operations_card_layout = QVBoxLayout(operations_card)
        self.operations_value_label = QLabel("0")
        operations_card_layout.addWidget(self.operations_value_label)
        kpi_layout.addWidget(operations_card)

        latency_card = QGroupBox("Средняя задержка, мс")
        latency_card_layout = QVBoxLayout(latency_card)
        self.average_latency_value_label = QLabel("0")
        latency_card_layout.addWidget(self.average_latency_value_label)
        kpi_layout.addWidget(latency_card)

        queue_card = QGroupBox("Очередь транзакций")
        queue_card_layout = QVBoxLayout(queue_card)
        self.queue_length_value_label = QLabel("0")
        queue_card_layout.addWidget(self.queue_length_value_label)
        kpi_layout.addWidget(queue_card)

        approval_card = QGroupBox("Одобрено, %")
        approval_card_layout = QVBoxLayout(approval_card)
        self.approval_rate_value_label = QLabel("0")
        approval_card_layout.addWidget(self.approval_rate_value_label)
        kpi_layout.addWidget(approval_card)

        main_layout.addLayout(kpi_layout)


        payments_title_label = QLabel("Последние платежи")
        main_layout.addWidget(payments_title_label)
        self.payments_table = QTableWidget(0, 6)
        self.payments_table.setAlternatingRowColors(True)
        self.payments_table.setHorizontalHeaderLabels(
            [
                "ID",
                "Сумма, ₽",
                "Статус",
                "Канал",
                "Задержка, мс",
                "Время",
            ]
        )
        main_layout.addWidget(self.payments_table)

        header_layout.setSpacing(12)
        controls_layout.setSpacing(10)
        kpi_layout.setSpacing(12)

    def update_clock(self) -> None:
        current_time = datetime.now().strftime("%H:%M:%S")
        self.clock_label.setText(current_time)



app = QApplication(sys.argv)

style_path = Path(__file__).with_name("styles.qss")
app.setStyleSheet(style_path.read_text(encoding="utf-8"))


window = MainWindow()
window.show()
sys.exit(app.exec())