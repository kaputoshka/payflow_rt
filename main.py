import sys
from datetime import datetime
from PySide6.QtCore import QTimer,Qt
from pathlib import Path
from PySide6.QtGui import QPainter

from PySide6.QtCharts import (
    QChart,
    QChartView,
    QLineSeries,
    QValueAxis
)

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
    QTableWidgetItem,
)

from models import Payment, PaymentStatus
from engine import SimulationEngine



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

        self.status_label = QLabel("Симуляция остановлена")
        self.status_label.setObjectName("statusLabel")
        header_layout.addWidget(self.status_label)
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

        start_button.clicked.connect(self.handle_start)
        pause_button.clicked.connect(self.handle_pause)
        stop_button.clicked.connect(self.handle_stop)

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

        self.simulation_timer = QTimer(self)
        self.simulation_timer.timeout.connect(self.run_simulation_tick)
        self.simulation_timer.start(800)

        def _build_kpi_card(self, object_name: str, title: str) -> tuple[QGroupBox, QLabel, QLabel]:
            card = QGroupBox(title)
            card.setObjectName(object_name)
            card_layout = QVBoxLayout(card)

            header_row = QHBoxLayout()
            value_label = QLabel("0")
            delta_label = QLabel("")
            delta_label.setObjectName("kpiDeltaUp")
            header_row.addWidget(value_label)
            header_row.addStretch(1)
            header_row.addWidget(delta_label)

            card_layout.addLayout(header_row)
            return card, value_label, delta_label

        main_layout.addLayout(kpi_layout)

        content_layout = QHBoxLayout()
        content_layout.setSpacing(16)

        left_column = QVBoxLayout()
        left_column.setSpacing(12)

        payments_title_label = QLabel("Последние операции")
        left_column.addWidget(payments_title_label)

        self.payments_table = QTableWidget(0, 6)
        self.payments_table.setAlternatingRowColors(True)
        self.payments_table.setHorizontalHeaderLabels(
            ["ID",
             "Сумма, ₽",
             "Статус",
             "Канал",
             "Задержка, мс",
             "Время"]
        )
        left_column.addWidget(self.payments_table)

        # сюда же, если занятие №8 уже сделано, переносим charts_layout:
        # left_column.addLayout(charts_layout)

        right_column = QVBoxLayout()
        right_column.setSpacing(12)

        self.controls_placeholder = QGroupBox("Панель управления")
        right_column.addWidget(self.controls_placeholder)

        self.events_placeholder = QGroupBox("События")
        right_column.addWidget(self.events_placeholder)

        content_layout.addLayout(left_column, stretch=2)
        content_layout.addLayout(right_column, stretch=1)

        main_layout.addLayout(content_layout)



        header_layout.setSpacing(12)
        controls_layout.setSpacing(10)
        kpi_layout.setSpacing(12)

        charts_layout = QHBoxLayout()

        self.traffic_chart_view, self.traffic_series = self._build_chart(
            "Входящий поток", "оп/с"
        )
        self.latency_chart_view, self.latency_series = self._build_chart(
            "Задержка шлюза", "мс"
        )
        self.queue_chart_view, self.queue_series = self._build_chart(
            "Длина очереди", "платежей"
        )

        charts_layout.addWidget(self.traffic_chart_view)
        charts_layout.addWidget(self.latency_chart_view)
        charts_layout.addWidget(self.queue_chart_view)

        main_layout.addLayout(charts_layout)

    def update_clock(self) -> None:
        current_time = datetime.now().strftime("%H:%M:%S")
        self.clock_label.setText(current_time)

    def handle_start(self) -> None:
        self.engine.start()
        self.status_label.setText("Симуляция активна")

    def handle_pause(self) -> None:
        self.engine.pause()
        self.status_label.setText("Симуляция приостановлена")

    def handle_stop(self) -> None:
        self.engine.stop()
        self.status_label.setText("Симуляция остановлена")
        self.payments_table.setRowCount(0)

    def run_simulation_tick(self) -> None:
        changed_payments = self.engine.tick()
        for payment in changed_payments:
            self.upsert_payment_row(payment)
        self.update_kpi_cards()
        self.update_charts()

    def upsert_payment_row(self, payment: Payment) -> None:
        row = self._find_row_by_id(payment.payment_id)
        if row is None:
            row = self.payments_table.rowCount()
            self.payments_table.insertRow(row)

        values = [
            payment.payment_id,
            f"{payment.amount_rubles:,}".replace(",", " "),
            payment.status.value,
            payment.channel,
            str(payment.latency_ms),
            payment.created_at.strftime("%H:%M:%S"),
        ]

        for column, value in enumerate(values):
            item = QTableWidgetItem(value)
            self.payments_table.setItem(row, column, item)

    def _find_row_by_id(self, payment_id: str) -> int | None:
        for row in range(self.payments_table.rowCount()):
            if self.payments_table.item(row, 0).text() == payment_id:
                return row
        return None

    def update_kpi_cards(self) -> None:
        payments = self.engine.payments
        total = len(payments)

        finished = [p for p in payments if p.status in (
            PaymentStatus.APPROVED, PaymentStatus.DECLINED, PaymentStatus.ERROR
        )]
        approved = [p for p in payments if p.status == PaymentStatus.APPROVED]
        in_queue = total - len(finished)

        self.operations_value_label.setText(str(total))
        self.queue_length_value_label.setText(str(in_queue))

        if payments:
            avg_latency = sum(p.latency_ms for p in payments) / total
            self.average_latency_value_label.setText(f"{avg_latency:.0f}")
        else:
            self.average_latency_value_label.setText("0")

        if finished:
            approval_rate = len(approved) / len(finished) * 100
            self.approval_rate_value_label.setText(f"{approval_rate:.0f}")
        else:
            self.approval_rate_value_label.setText("0")

    def _build_chart(self, title: str, y_title: str) -> tuple[QChartView, QLineSeries]:
        series = QLineSeries()

        chart = QChart()
        chart.addSeries(series)
        chart.setTitle(title)
        chart.legend().hide()

        axis_x = QValueAxis()
        axis_x.setTitleText("Такт, шт.")
        axis_x.setLabelFormat("%d")
        chart.addAxis(axis_x, Qt.AlignBottom)
        series.attachAxis(axis_x)

        axis_y = QValueAxis()
        axis_y.setTitleText(y_title)
        chart.addAxis(axis_y, Qt.AlignLeft)
        series.attachAxis(axis_y)

        view = QChartView(chart)
        view.setRenderHint(QPainter.Antialiasing)
        return view, series

    def update_charts(self) -> None:
        self._fill_series(self.traffic_series, self.engine.traffic_history)
        self._fill_series(self.latency_series, self.engine.latency_history)
        self._fill_series(self.queue_series, self.engine.queue_history)

    @staticmethod
    def _fill_series(series: QLineSeries, history) -> None:
        series.clear()
        for index, value in enumerate(history):
            series.append(index, value)

        chart = series.chart()
        if history:
            chart.axes(Qt.Horizontal)[0].setRange(0, max(len(history) - 1, 1))
            chart.axes(Qt.Vertical)[0].setRange(0, max(history) * 1.2 or 1)
app = QApplication(sys.argv)
style_path = Path(__file__).with_name("styles.qss")
app.setStyleSheet(style_path.read_text(encoding="utf-8"))


window = MainWindow()
window.show()
sys.exit(app.exec())