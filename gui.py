import sys
import socket
import serial
import can
import threading
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QTextEdit, QLineEdit, QLabel, QComboBox, QFileDialog
from PyQt5.QtCore import QTimer

class DebuggerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.tcp_socket = None
        self.udp_socket = None
        self.uart_connection = None
        self.can_bus = None
        self.logging_enabled = False

    def initUI(self):
        layout = QVBoxLayout()

        # Logging Section
        self.logFileBtn = QPushButton("Enable Logging", self)
        self.logFileBtn.clicked.connect(self.toggleLogging)
        layout.addWidget(self.logFileBtn)

        # TCP Section
        self.tcpLabel = QLabel("TCP Debugging:")
        self.tcpInput = QLineEdit(self)
        self.tcpSendBtn = QPushButton("Send TCP Message", self)
        self.tcpLog = QTextEdit(self)
        self.tcpConnectBtn = QPushButton("Connect TCP", self)
        layout.addWidget(self.tcpLabel)
        layout.addWidget(self.tcpInput)
        layout.addWidget(self.tcpSendBtn)
        layout.addWidget(self.tcpLog)
        layout.addWidget(self.tcpConnectBtn)
        self.tcpSendBtn.clicked.connect(self.sendTCP)
        self.tcpConnectBtn.clicked.connect(self.connectTCP)

        # UDP Section
        self.udpLabel = QLabel("UDP Debugging:")
        self.udpInput = QLineEdit(self)
        self.udpSendBtn = QPushButton("Send UDP Message", self)
        self.udpLog = QTextEdit(self)
        layout.addWidget(self.udpLabel)
        layout.addWidget(self.udpInput)
        layout.addWidget(self.udpSendBtn)
        layout.addWidget(self.udpLog)
        self.udpSendBtn.clicked.connect(self.sendUDP)

        # UART Section
        self.uartLabel = QLabel("UART Debugging:")
        self.uartInput = QLineEdit(self)
        self.uartSendBtn = QPushButton("Send UART Message", self)
        self.uartLog = QTextEdit(self)
        self.uartConnectBtn = QPushButton("Connect UART", self)
        self.baudRateSelect = QComboBox(self)
        self.baudRateSelect.addItems(["9600", "115200", "57600", "38400"])
        layout.addWidget(self.uartLabel)
        layout.addWidget(self.baudRateSelect)
        layout.addWidget(self.uartInput)
        layout.addWidget(self.uartSendBtn)
        layout.addWidget(self.uartLog)
        layout.addWidget(self.uartConnectBtn)
        self.uartSendBtn.clicked.connect(self.sendUART)
        self.uartConnectBtn.clicked.connect(self.connectUART)

        # CAN Section
        self.canLabel = QLabel("CAN Debugging:")
        self.canInput = QLineEdit(self)
        self.canSendBtn = QPushButton("Send CAN Message", self)
        self.canLog = QTextEdit(self)
        self.canConnectBtn = QPushButton("Connect CAN", self)
        layout.addWidget(self.canLabel)
        layout.addWidget(self.canInput)
        layout.addWidget(self.canSendBtn)
        layout.addWidget(self.canLog)
        layout.addWidget(self.canConnectBtn)
        self.canSendBtn.clicked.connect(self.sendCAN)
        self.canConnectBtn.clicked.connect(self.connectCAN)

        self.setLayout(layout)
        self.setWindowTitle('Advanced Debugger App')
        self.show()

    def logMessage(self, protocol, message):
        if self.logging_enabled:
            with open("debugger_log.txt", "a") as log_file:
                log_file.write(f"{protocol}: {message}\n")

    def toggleLogging(self):
        if not self.logging_enabled:
            self.logging_enabled = True
            self.logFileBtn.setText("Disable Logging")
            self.logMessage("INFO", "Logging enabled.")
        else:
            self.logging_enabled = False
            self.logFileBtn.setText("Enable Logging")
            self.logMessage("INFO", "Logging disabled.")

    # TCP Methods
    def connectTCP(self):
        try:
            self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.tcp_socket.connect(("127.0.0.1", 8080))
            self.tcpLog.append("Connected to TCP server.")
        except Exception as e:
            self.tcpLog.append(f"TCP Error: {e}")

    def sendTCP(self):
        try:
            message = self.tcpInput.text().encode()
            self.tcp_socket.sendall(message)
            data = self.tcp_socket.recv(1024)
            self.tcpLog.append(f"Sent: {message.decode()}, Received: {data.decode()}")
            self.logMessage("TCP", f"Sent: {message.decode()}, Received: {data.decode()}")
        except Exception as e:
            self.tcpLog.append(f"TCP Error: {e}")

    # UDP Methods
    def sendUDP(self):
        try:
            message = self.udpInput.text().encode()
            self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.udp_socket.sendto(message, ("127.0.0.1", 8080))
            data, addr = self.udp_socket.recvfrom(1024)
            self.udpLog.append(f"Sent: {message.decode()}, Received: {data.decode()}")
            self.logMessage("UDP", f"Sent: {message.decode()}, Received: {data.decode()}")
        except Exception as e:
            self.udpLog.append(f"UDP Error: {e}")

    # UART Methods
    def connectUART(self):
        try:
            baud_rate = int(self.baudRateSelect.currentText())
            self.uart_connection = serial.Serial('/dev/ttyUSB0', baud_rate)
            self.uartLog.append(f"Connected to UART with baud rate {baud_rate}.")
        except Exception as e:
            self.uartLog.append(f"UART Error: {e}")

    def sendUART(self):
        try:
            message = self.uartInput.text().encode()
            self.uart_connection.write(message)
            data = self.uart_connection.read(100)
            self.uartLog.append(f"Sent: {message.decode()}, Received: {data.decode()}")
            self.logMessage("UART", f"Sent: {message.decode()}, Received: {data.decode()}")
        except Exception as e:
            self.uartLog.append(f"UART Error: {e}")

    # CAN Methods
    def connectCAN(self):
        try:
            self.can_bus = can.interface.Bus(channel='can0', bustype='socketcan')
            self.canLog.append("Connected to CAN bus.")
        except Exception as e:
            self.canLog.append(f"CAN Error: {e}")

    def sendCAN(self):
        try:
            message = can.Message(arbitration_id=0x123, data=bytearray(self.canInput.text().encode()), is_extended_id=False)
            self.can_bus.send(message)
            self.canLog.append(f"Sent CAN message: {message}")
            self.logMessage("CAN", f"Sent CAN message: {message}")
        except Exception as e:
            self.canLog.append(f"CAN Error: {e}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = DebuggerApp()
    sys.exit(app.exec_())
