from tkinter import *
import tkinter
from tkinter import ttk
from Server_BL import *

from PIL import Image, ImageTk
from cryptography.fernet import Fernet

BG_IMAGE = "./Images/GUI - BG.png"
BTN_IMAGE = "./Images/GUI - btn.png"


# Class GUI
class Server_GUI():
    def __init__(self):
        self.canvas = None
        self.root = None

        self.table = None

        self.table2 = None

        self.btn_start = None
        self.btn_stop = None
        self.btn_register = None

        self.btn_send = None
        self.entry_IP = None
        self.entry_Port = None

        self.entry_Send = None
        self.entry_Received = None

        self.img_btn = None

        self.server = None
        self.btn_reg = None
        self.img_path = None

        self.img_flipped = None

        self.server_thread = None
        self.create_window()

    def create_window(self):
        # Create window
        self.root = tkinter.Tk()
        # Set title for window
        self.root.title("Assignment Client / Server GUI")

        # Load bg image
        self.img_path = PhotoImage(file=BG_IMAGE)
        img_width = self.img_path.width()
        img_height = self.img_path.height()

        # Set size of the application window = image size * 2
        self.root.geometry(f'{img_width}x{img_height * 2}')
        self.root.resizable(False, False)

        # Create a canvas to cover the entire window
        self.canvas = tkinter.Canvas(self.root, width=img_width, height=img_height * 2)
        self.canvas.pack(fill='both', expand=True)
        self.canvas.create_image(0, 0, anchor="nw", image=self.img_path)

        # Window with table
        img = Image.open(BG_IMAGE)
        img_flipped = img.transpose(Image.ROTATE_180).transpose(Image.FLIP_LEFT_RIGHT)
        self.img_flipped = ImageTk.PhotoImage(img_flipped)
        self.canvas.create_image(0, img_height, anchor="nw", image=self.img_flipped)

        self.create_ui()

    def create_ui(self):
        # Add labels, the same as add text on canvas
        self.canvas.create_text(90, 80, text='Server', font=('Calibri', 28), fill='#808080')
        self.canvas.create_text(50, 180, text='IP:', font=('Calibri', 20), fill='#000000', anchor='w')
        self.canvas.create_text(50, 230, text='Port:', font=('Calibri', 20), fill='#000000', anchor='w')
        self.canvas.create_text(50, 280, text='Received:', font=('Calibri', 20), fill='#000000', anchor='w')
        # Load button image
        self.img_btn = PhotoImage(file="./Images/GUI - btn.png")
        img_btn_w = self.img_btn.width()
        img_btn_h = self.img_btn.height()

        # Button "Start"
        self.btn_start = tkinter.Button(self.canvas, text="Start", font=("Calibri", 16), fg="#c0c0c0",
                                          compound="center",
                                          width=img_btn_w, height=img_btn_h, image=self.img_btn, bd=0,
                                          command=self.on_click_start)
        self.btn_start.place(x=650, y=50)

        # Button "Stop"
        self.btn_stop = tkinter.Button(self.canvas, text="Stop", font=("Calibri", 16), fg="#c0c0c0",
                                          compound="center",
                                          width=img_btn_w, height=img_btn_h, image=self.img_btn, bd=0,
                                          command=self.on_click_stop)

        self.btn_stop.place(x=650, y=130)
        self.btn_stop.config(state="disabled")

        self.btn_register = tkinter.Button(self.canvas, text="Register", font=("Calibri", 16), fg="#c0c0c0",
                                           compound="center",
                                           width=img_btn_w, height=img_btn_h, image=self.img_btn, bd=0,
                                           command=self.on_click_reg)

        self.btn_register.place(x=650, y=210)

        # Create Entry boxes
        # Ip
        self.entry_IP = tkinter.Entry(self.canvas, font=('Calibri', 16), fg='#808080')
        self.entry_IP.insert(0, '0.0.0.0')
        self.entry_IP.place(x=200, y=168)

        # Port
        self.entry_Port = tkinter.Entry(self.canvas, font=('Calibri', 16), fg='#808080')
        self.entry_Port.insert(0, "8822")
        self.entry_Port.place(x=200, y=218)

        # Receive
        self.entry_Received = tkinter.Text(self.canvas, width=30, height=3, font=('Calibri', 16), fg='#808080')
        self.entry_Received.insert(tkinter.END, "...")
        self.entry_Received.place(x=200, y=268)
        self.entry_Received.config(state="disabled")

        # Create Table
        self.table = tkinter.Frame(self.canvas, bg='white')
        self.table.place(x=50, y=400)

        self.table = ttk.Treeview(self.table, columns=('IP', 'Address'), show='headings', height=5)
        self.table.heading('IP', text='IP')
        self.table.heading('Address', text='Address')

        self.table.pack()

        # Second table
        self.table2 = tkinter.Frame(self.root, bg='white')
        self.table2.place(x=50, y=550)

        self.table2 = ttk.Treeview(self.table2, columns=('IP', 'Address', 'login', 'password'), show='headings',
                                   height=5)

        self.table2.heading('IP', text='IP')
        self.table2.heading('Address', text='Address')

        self.table2.column('IP', width=200)
        self.table2.column('Address', width=200)

        # Create invisible columns with login and password
        self.table2.column('login', width=0, stretch=tkinter.NO)
        self.table2.column('password', width=0, stretch=tkinter.NO)

        self.table2.pack()

    def run(self):
        self.root.mainloop()

    def on_click_start(self):
        # Set status for entry fields and buttons
        self.entry_IP.config(state="disabled")
        self.entry_Port.config(state="disabled")
        self.btn_start.config(state="disabled")
        self.btn_stop.config(state="normal")

        # Get port
        port = int(self.entry_Port.get())
        # Create object server
        self.server = Server_BL(port, self.insert_client, self.message_callback)
        # Create a thread to start server
        self.server_thread = threading.Thread(target=self.server.start_server)
        self.server_thread.start()

    def message_callback(self, message):
        self.entry_Received.config(state="normal")
        self.entry_Received.delete("1.0", tkinter.END)
        self.entry_Received.insert("1.0", message)
        self.entry_Received.config(state="disabled")

    def on_click_stop(self):
        # Set status for entry fields and buttons
        self.entry_IP.config(state="normal")
        self.entry_Port.config(state="normal")
        self.btn_start.config(state="normal")
        self.btn_stop.config(state="disabled")

        # call the function quit_server
        self.server.quit_server()

    def on_click_reg(self):
        pass

    # Insert client into table
    def insert_client(self, adr):
        self.table.insert('', 'end', values=(adr[0], adr[1]))

    # Delete client from table function
    def delete_client(self, adr):
        # Select all clients from the table
        all_items = self.table.get_children()
        for item in all_items:
            user_data = self.table.item(item)
            user_address = user_data['values'][1]

            if user_address == adr[1]:
                self.table.delete(item)

    def insert_reg(self, adr, args):
        self.table2.insert('', 'end', values=(adr[0], adr[1], args['login'], args['password']))


if __name__ == "__main__":
    client = Server_GUI()
    client.root.mainloop()
