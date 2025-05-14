# -*- coding: utf-8 -*-
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow
from Server_BL import *
import sys
from PIL import Image, ImageTk
from cryptography.fernet import Fernet
import threading

BG_IMAGE = "./Images/GUI - BG.png"
BTN_IMAGE = "./Images/GUI - btn.png"


# Class GUI
class Server_GUI(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Server")
        self.setGeometry(500, 500, 900, 1000)
        self.create_ui()

    def create_ui(self):
        self.IP_label = QtWidgets.QLabel(self)
        self.IP_label.setGeometry(QtCore.QRect(120, 60, 100, 40))  # Enlarged size
        self.IP_label.setText("IP:")
        self.IP_label.setStyleSheet("font-size: 25px;")

        # Label for Port
        self.Port_label = QtWidgets.QLabel(self)
        self.Port_label.setGeometry(QtCore.QRect(105, 105, 76, 32))  # Enlarged size
        self.Port_label.setText("Port:")
        self.Port_label.setStyleSheet("font-size: 25px;")

        # IP Input field (read-only)
        self.ip_entry = QtWidgets.QLineEdit(self)
        self.ip_entry.setGeometry(QtCore.QRect(170, 60, 250, 40))  # Enlarged size
        self.ip_entry.setText('0.0.0.0')
        self.ip_entry.setEnabled(False)


        # Port Input field
        self.port_entry = QtWidgets.QLineEdit(self)
        self.port_entry.setGeometry(QtCore.QRect(170, 105, 250, 40))  # Enlarged size
        self.port_entry.setText('8822')

        # "Run" button
        self.start_button = QtWidgets.QPushButton(self)
        self.start_button.setGeometry(QtCore.QRect(555, 30, 182, 62))  # Enlarged size
        self.start_button.setText("Run")
        self.start_button.clicked.connect(self.on_click_start)

        # "Stop" button
        self.stop_button = QtWidgets.QPushButton(self) 
        self.stop_button.setGeometry(QtCore.QRect(555, 120, 182, 62))  # Enlarged size
        self.stop_button.setText("Stop")
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self.on_click_stop)

        # TextEdit to show status messages
        self.log_field = QtWidgets.QTextEdit(self)
        self.log_field.setGeometry(QtCore.QRect(135, 195, 602, 272))  # Enlarged size
        self.log_field.setReadOnly(True)  # Make this field read-only initially

        # Table to show IP and Username
        self.table = QtWidgets.QTableWidget(self)
        self.table.setGeometry(QtCore.QRect(210, 480, 480, 500))  # Increased table height
        self.table.setColumnCount(2)  # Two columns: IP and Username
        self.table.setHorizontalHeaderLabels(["IP", "Username"])

        # Insert some sample data (IP and Username) into the table
        self.table.setRowCount(50)

    def run(self):
        self.root.mainloop()

    def on_click_start(self):
        # Set status for entry fields and buttons
        self.port_entry.setEnabled(False)
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)

        # Get port
        port = int(self.port_entry.text())

        # Create object server
        self.server = Server_BL(port, self.insert_client, self.message_callback)
        # Create a thread to start server
        self.server_thread = threading.Thread(target=self.server.start_server)
        self.server_thread.start()

        self.log_field.append("Server is running...\n")

    def message_callback(self, message):
        print(message)
        self.log_field.append(message+"\n")

    def on_click_stop(self):
        self.port_entry.setEnabled(True)
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)

        # call the function quit_server
        self.server.quit_server()

    def on_click_reg(self):
        pass

    # Insert client into table
    def insert_client(self, adr):
        row_count = self.table.rowCount()
        self.table.insertRow(row_count)
        self.table.setItem(row_count, 0, QtWidgets.QTableWidgetItem('52'))
        self.table.setItem(row_count, 1, QtWidgets.QTableWidgetItem('ff'))

    # Delete client from table function
    '''def delete_client(self, adr):
        # Select all clients from the table
        all_items = self.table.get_children()
        for item in all_items:
            user_data = self.table.item(item)
            user_address = user_data['values'][1]

            if user_address == adr[1]:
                self.table.delete(item)'''


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = Server_GUI()
    window.show()
    sys.exit(app.exec_())
