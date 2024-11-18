import tkinter
import json
from tkinter import PhotoImage


BG_IMAGE = "./Images/BG.png"
Rooms_btn = "./Images/GUI - btn.png"
BTN_IMAGE = "./Images/rock-punk.png"


class Client_GUI():
    def __init__(self):
        self.canvas = None
        self.root = None

        self.btn_connect = None
        self.btn_disconnect = None

        self.btn_send = None
        self.entry_IP = None
        self.entry_Port = None

        self.entry_Send = None
        self.entry_cmd = None
        self.entry_Received = None

        self.img_btn = None

        self.client = None
        self.btn_reg = None
        self.img_path = None
        self.create_window()

    def create_window(self):
        # Create window
        self.root = tkinter.Tk()

        # Title for our window
        self.root.title("Assignment Client / Server GUI")

        # Load bg image
        self.img_path = PhotoImage(file=BG_IMAGE)
        img_width = self.root.winfo_screenwidth()
        img_height = self.root.winfo_screenheight()

        # Set size of the application window = image size
        self.root.geometry(f'{img_width}x{img_height}')
        self.root.resizable(False, False)

        # Create a canvas to cover the entire window
        self.canvas = tkinter.Canvas(self.root, width=img_width, height=img_height)
        self.canvas.pack(fill='both', expand=True)
        self.canvas.create_image(0, 0, anchor="nw", image=self.img_path)

        self.create_ui()

    def create_ui(self):
        '''# Add labels, the same as add text on canvas
        self.canvas.create_text(90, 80, text='Client', font=('Calibri', 28), fill='#808080')
        self.canvas.create_text(50, 150, text='IP:', font=('Calibri', 20), fill='#000000', anchor='w')
        self.canvas.create_text(50, 200, text='Port:', font=('Calibri', 20), fill='#000000', anchor='w')
        self.canvas.create_text(50, 250, text='Send:', font=('Calibri', 20), fill='#000000', anchor='w')
        self.canvas.create_text(50, 300, text='Received:', font=('Calibri', 20), fill='#000000', anchor='w')

        # Load button image
        self.img_btn = PhotoImage(file=BTN_IMAGE)
        img_btn_w = self.img_btn.width()
        img_btn_h = self.img_btn.height()

        # Button "Connect"
        self.btn_connect = tkinter.Button(self.canvas, text="Connect", font=("Calibri", 16), fg="#c0c0c0", compound="center",
                                      width=img_btn_w, height=img_btn_h, image=self.img_btn, bd=0,
                                      command=self.on_click_connect)

        self.btn_connect.place(x=650, y=50)

        # Button "Disconnect"
        self.btn_disconnect = tkinter.Button(self.canvas, text="Disconnect", font=("Calibri", 16), fg="#c0c0c0",
                                          compound="center",
                                          width=img_btn_w, height=img_btn_h, image=self.img_btn, bd=0,
                                          command=self.on_click_disconnect)
        self.btn_disconnect.place(x=650, y=130)
        self.btn_disconnect.config(state="disabled")
        # Button "Send Data"
        self.btn_send = tkinter.Button(self.canvas, text="Send Data", font=("Calibri", 16), fg="#c0c0c0",
                                          compound="center",
                                          width=img_btn_w, height=img_btn_h, image=self.img_btn, bd=0,
                                          command=self.on_click_send)
        self.btn_send.place(x=650, y=210)
        self.btn_send.config(state="disabled")

        self.btn_reg = tkinter.Button(self.canvas, text="Reg/Login", font=("Calibri", 16), fg="#c0c0c0",
                                       compound="center",
                                       width=img_btn_w, height=img_btn_h, image=self.img_btn, bd=0,
                                       command=self.on_click_reg)
        self.btn_reg.place(x=650, y=290)
        self.btn_reg.config(state="disabled")

        # Create Entry boxes
        # Entry box ip
        self.entry_IP = tkinter.Entry(self.canvas, font=('Calibri', 16), fg='#808080')
        self.entry_IP.insert(0, '127.0.0.1')
        self.entry_IP.place(x=165, y=138)

        # Entry box port
        self.entry_Port = tkinter.Entry(self.canvas, font=('Calibri', 16), fg='#808080')
        self.entry_Port.insert(0, "8822")
        self.entry_Port.place(x=165, y=188)

        self.entry_cmd = tkinter.Entry(self.canvas, width=15, font=('Calibri', 16), fg='#808080')
        self.entry_cmd.place(x=165, y=238)
        self.entry_cmd.insert(0, "CMD")

        self.entry_Send = tkinter.Entry(self.canvas, width=26, font=('Calibri', 16), fg='#808080')
        self.entry_Send.place(x=340, y=238)
        self.entry_Send.insert(0, "...")

        # Receive
        self.entry_Received = tkinter.Text(self.canvas, width=42, height=3, font=('Calibri', 16), fg='#808080')
        self.entry_Received.insert(tkinter.END, "...")
        self.entry_Received.place(x=165, y=282)
        self.entry_Received.config(state="disabled")

    def on_click_connect(self):
        pass
    def on_click_disconnect(self):
        pass
    def on_click_reg(self):
        pass
    def on_click_send(self):
        pass

    def run(self):
        self.root.mainloop()'''


if __name__ == "__main__":
    client = Client_GUI()
    client.root.mainloop()
