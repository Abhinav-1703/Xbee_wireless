import serial
import sys
import random
import pyqtgraph as pg
import threading
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QTextEdit, QLabel, QHBoxLayout
from PyQt5.QtCore import QTimer

class SerialGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

        # Serial port setup (modify for your actual port)
        try:
            self.ser = serial.Serial('COM11', 9600, timeout=1)
        except serial.SerialException:
            self.ser = None
            print("Failed to open serial port!")
        
        # Data storage for plotting
        self.time_x = []
        self.speed_y = []
        self.battery_y = []
        self.is_running = False  # Track power state

        # Timer for updating the plot
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(2000)

        # Start a thread for reading serial data
        self.serial_thread = threading.Thread(target=self.receive_data, daemon=True)
        self.serial_thread.start()

    def initUI(self):
        layout = QVBoxLayout()

        # Separate sections for plot data and command replies
        text_layout = QHBoxLayout()
        
        self.plot_data_display = QTextEdit()
        self.plot_data_display.setReadOnly(True)
        self.plot_data_display.setPlaceholderText("Received Plot Data")
        text_layout.addWidget(self.plot_data_display)

        self.command_reply_display = QTextEdit()
        self.command_reply_display.setReadOnly(True)
        self.command_reply_display.setPlaceholderText("Command Replies / Log Data")
        text_layout.addWidget(self.command_reply_display)

        layout.addLayout(text_layout)

        self.plot = pg.PlotWidget()
        layout.addWidget(self.plot)
        self.plot.setTitle("Speed and Battery Voltage Over Time")
        self.plot.setLabel('left', 'Speed (%) / Battery Voltage (V)')
        self.plot.setLabel('bottom', 'Time (s)')
        self.speed_curve = self.plot.plot(pen='r', name="Speed (%)")
        self.battery_curve = self.plot.plot(pen='b', name="Battery (V)")

        self.btn_on = QPushButton('Power ON')
        self.btn_on.clicked.connect(lambda: self.toggle_power(True))
        layout.addWidget(self.btn_on)

        self.btn_off = QPushButton('Power OFF')
        self.btn_off.clicked.connect(lambda: self.toggle_power(False))
        layout.addWidget(self.btn_off)

        self.btn_log = QPushButton('Request Log')
        self.btn_log.clicked.connect(lambda: self.send_command("R"))
        layout.addWidget(self.btn_log)

        self.setLayout(layout)
        self.setWindowTitle("ESP Debugging GUI")
        self.setGeometry(100, 100, 600, 400)

    def toggle_power(self, state):
        self.is_running = state
        self.send_command("1" if state else "0")

    def send_command(self, msg):
        if self.ser:
            self.ser.write((msg + '\n').encode())
            self.command_reply_display.append(f"Sent: {msg}")

    def receive_data(self):
        while True:
            if self.ser and self.ser.in_waiting > 0:
                data = self.ser.readline().decode('utf-8').strip()
                if data:
                    if "PLOT DATA" in data and self.is_running:
                        self.process_plot_data(data)
                    else:
                        self.command_reply_display.append(f"Received: {data}")

    def process_plot_data(self, msg):
        self.plot_data_display.append(f"Received: {msg}")
        try:
            parts = msg.split(", ")
            speed_str = [p for p in parts if "Speed=" in p][0]
            battery_str = [p for p in parts if "Battery=" in p][0]
            speed_value = int(speed_str.split("=")[1].replace("%", ""))
            battery_value = float(battery_str.split("=")[1].replace("V", ""))
            
            self.time_x.append(len(self.time_x))
            self.speed_y.append(speed_value)
            self.battery_y.append(battery_value)
            
            self.speed_curve.setData(self.time_x, self.speed_y)
            self.battery_curve.setData(self.time_x, self.battery_y)
        except Exception as e:
            print(f"Error parsing PLOT DATA: {e}")

    def update_plot(self):
        if not self.is_running or not self.time_x:
            return
        self.speed_curve.setData(self.time_x, self.speed_y)
        self.battery_curve.setData(self.time_x, self.battery_y)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = SerialGUI()
    gui.show()
    sys.exit(app.exec())
