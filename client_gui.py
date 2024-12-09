import tkinter

from Client_BL import *
from tkinter import scrolledtext

BTN_IMAGE = "./Images/GUI - btn.png"
SRV_IP = "127.0.0.1"
SRV_PORT = "8822"


class Client_GUI():
    def __init__(self, client_bl):
        self.canvas = None
        self.root = None
        self.client = client_bl

        self.Room1 = None
        self.Room2 = None

        self.btn_connect = None
        self.img_btn = None

        self.text1 = None
        self.entry = None
        self.Room1_id = None
        self.chat_window = None
        self.create_window()

    def create_window(self):

        # Create window
        self.root = tkinter.Tk()

        # Title for our window
        self.root.title("Assignment Client / Server GUI")

        # Load bg image
        self.root.geometry("1920x1080")

        # Создаем Canvas с белым фоном
        self.canvas = tkinter.Canvas(self.root, width=1920, height=1080, bg="white")
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.canvas.pack(fill="both", expand=True)
        self.create_ui()

    def create_ui(self):


        # Create separate line
        self.canvas.create_line(400, 0, 400, 1080, fill="black", width=2)
        # Create buttons
        self.img_btn = tkinter.PhotoImage(file=BTN_IMAGE)
        img_btn_w = self.img_btn.width()
        img_btn_h = self.img_btn.height()
        self.Room1 = tkinter.Button(self.canvas, text="ROOM1", font=("Calibri", 16), fg="#c0c0c0",compound='center',
                                          width=img_btn_w, height=img_btn_h, image=self.img_btn, bd=0, command=self.on_click_room1)
        self.Room1.place(x=150, y=100)


    def on_click_room1(self):
        #print("ni0gga")
        self.text1 = self.canvas.create_text(900, 100, text='Connect to the room?', font=('Calibri', 40), fill='#808080')
        self.Room1 = tkinter.Button(self.canvas, text="Yes", font=("Calibri", 16), fg="#c0c0c0", compound='center',
                                    width=self.img_btn.width(), height=self.img_btn.height(), image=self.img_btn, bd=0,
                                    command=self.on_click_connect1)
        self.Room1_id = self.canvas.create_window(870, 130, window=self.Room1)
        self.Room1.place(x=870, y=130)

    def on_click_connect1(self):

        if True:
            # Chat window
            self.chat_window = scrolledtext.ScrolledText(self.root, wrap=tkinter.WORD, font=("Arial", 14),
                                                         state=tkinter.DISABLED)
            self.chat_window.place(x=400, y=0, width=1030, height=1000)

            self.entry = tkinter.Entry(self.root, font=("Arial", 14), bg="#87CEEB", fg="black", bd=0, highlightthickness=2,
                             highlightbackground="#000000")
            self.entry.place(x=600, y=760, width=500, height=30)

            send_button = tkinter.Button(self.root, text="Send", command=self.send_message)
            send_button.place(x=1100, y=760, width=80, height=30)

    def send_message(self):
        message = self.entry.get()
        if message:
            result = self.client.send("MSG " + message)
            self.chat_window.config(state=tkinter.NORMAL)  # Разблокируем для редактирования
            self.chat_window.insert(tkinter.END, f"You: {message}\n")  # Добавляем сообщение в конец
            self.chat_window.see(tkinter.END)  # Прокручиваем к последнему сообщению
            self.chat_window.config(state=tkinter.DISABLED)  # Блокируем для редактирования
            self.entry.delete(0, tkinter.END)


def start(client):
    client = Client_GUI(client)
    client.root.mainloop()


