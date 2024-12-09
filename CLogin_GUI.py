import tkinter as tk
from tkinter import *
import subprocess

import client_gui
from client_gui import *
# Constants


# Images
BTN_IMAGE = "./Images/GUI - button small.png"
BG_IMAGE = "./Images/GUI - BG Login.png"

# Font
FONT = "Calibri"
FONT_BUTTON = (FONT, 16)


# Class CLoginGui
class CLoginGUI:

    def __init__(self):
        self.client = Client_BL(SRV_IP, SRV_PORT)
        self.login = None
        self.password = None
        self.root = None

        self.canvas = None
        self.img_bg = None
        self.img_btn = None
        self.btn_close = None

        self.entry_login = None
        self.entry_password = None

        self.btn_reg = None
        self.btn_signin = None
        self.btn_ok = None
        self.btn_cancel = None
        self.guest = None

        self.err_text = None
        self.sock = None
        self.create_ui()

    def create_ui(self):
        self.root = tk.Tk()
        self.root.title("Login")

        # BG image
        img_width = 400
        img_height = 250

        # Set window size, same size as bg image
        self.root.geometry(f'{img_width}x{img_height}')
        self.root.resizable(False, False)

        # Create canvas
        self.canvas = tk.Canvas(self.root, width=img_width, height=img_height)
        self.canvas.pack(fill='both', expand=True)
        # Load button image
        self.img_btn = PhotoImage(file=BTN_IMAGE)
        img_btn_w = self.img_btn.width()
        img_btn_h = self.img_btn.height()
        self.sock = self.client.connect()

        if (self.sock):
            print("успешно")
            # Add login and password labels
            self.canvas.create_text(50, 50, text='Login:', font=FONT_BUTTON, fill='#000000', anchor='w')
            self.canvas.create_text(50, 130, text='Password:', font=FONT_BUTTON, fill='#000000', anchor='w')

            # Button Register
            self.btn_reg = tk.Button(self.canvas, text="Register", font=FONT_BUTTON, fg="#c0c0c0", compound="center",
                                     width=img_btn_w, height=img_btn_h, image=self.img_btn, bd=0,
                                     command=self.on_click_register)
            self.btn_reg.place(x=50, y=213)

            # Button SignIn
            self.btn_signin = tk.Button(self.canvas, text="SignIn", font=FONT_BUTTON, fg="#c0c0c0", compound="center",
                                        width=img_btn_w, height=img_btn_h, image=self.img_btn, bd=0,
                                        command=self.on_click_signin)
            self.btn_signin.place(x=170, y=213)

            # Button Guest
            self.guest = tk.Button(self.canvas, text="Continue as a guest", font=FONT_BUTTON, fg="#c0c0c0", compound="center",
                                        width=img_btn_w, height=img_btn_h, image=self.img_btn, bd=0,
                                        command=self.on_click_guest)
            self.guest.place(x=290, y=213)

            # Create Entry boxes
            self.entry_login = tk.Entry(self.canvas, font=('Calibri', 16), fg='#808080')
            self.entry_login.insert(0, "")
            self.entry_login.place(x=50, y=70)

            self.entry_password = tk.Entry(self.canvas, font=('Calibri', 16), fg='#808080')
            self.entry_password.insert(0, "")
            self.entry_password.place(x=50, y=150)
        else:
            self.canvas.create_text(50, 50, text='Failed to connect to the server', font=FONT_BUTTON, fill='#FF0000', anchor='w')
            self.btn_close = tk.Button(self.canvas, text="Close", font=FONT_BUTTON, fg="#c0c0c0", compound="center",
                                        width=img_btn_w, height=img_btn_h, image=self.img_btn, bd=0,
                                        command=self.close)
            self.btn_close.place(x=170, y=200)

    def close(self):
        self.root.destroy()

    def run(self):
        self.root.mainloop()

    def on_click_guest(self):
        pass

    def on_click_register(self):
        try:
            self.canvas.delete(self.err_text)
        except:
            pass
        login = self.entry_login.get()
        password = self.entry_password.get()
        if(login == '' or password == ''):
            self.err_text = self.canvas.create_text(50, 200, text='Entry fields can`t be empty', font=FONT_BUTTON, fill='#FF0000',
                                    anchor='w')

        elif (" " in login or " " in password):
            self.err_text = self.canvas.create_text(50, 200, text='Forbidden symbols', font=FONT_BUTTON, fill='#FF0000',
                                    anchor='w')

        else:
            self.send("REG" + " " + login + " " + password)
            self.root.destroy()
            start(self.client)

    def on_click_signin(self):
        self.root.destroy()
        start(self.client)

    def send(self, msg):
        try:
            # Save message size
            self.sock.sendall(len(msg).to_bytes(4, byteorder='big'))
            # Send message
            self.sock.sendall(msg.encode(FORMAT))
            write_to_log(f"[CLIENT_BL] send {self.sock.getsockname()} {msg} ")
            return True
        except Exception as e:
            write_to_log(f"[CLIENT_BL] failed to send_data; error: {e}")
            return False


if __name__ == "__main__":
    client = CLoginGUI()
    client.root.mainloop()

