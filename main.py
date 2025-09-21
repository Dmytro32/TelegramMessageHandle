import tkinter as tk
from tkinter import simpledialog
from telegram import MyRequests
from tkcalendar import DateEntry


from tkinter.filedialog import askopenfilename
class DateDialog(simpledialog.Dialog):
    def __init__(self,parent,title):
        self.chosendate=None
        super().__init__(parent, title)
    def body(self,frame):
        label=tk.Label(frame,text="Choose data where gt from")
        self.data=DateEntry(frame)
        label.pack()
        self.data.pack()
    def ok_pressed(self):
        self.chosendate =self.data.get_date()
        self.destroy()
    def cancel_pressed(self):
        # print("cancel")
        self.destroy()
    def buttonbox(self):
        self.ok_button = tk.Button(self, text='OK', width=5, command=self.ok_pressed)
        self.ok_button.pack(side="left")
        cancel_button = tk.Button(self, text='Cancel', width=5, command=self.cancel_pressed)
        cancel_button.pack(side="right")
        self.bind("<Return>", lambda event: self.ok_pressed())
        self.bind("<Escape>", lambda event: self.cancel_pressed())

def show_message(message_text):
    file=askopenfilename(filetypes=[("CSV file","*.csv")])
    myReq.display_messages(message_text,file)
def mydialog(app):
    dialog = DateDialog(title="Date choose", parent=app)
    print(dialog.chosendate)
    if dialog.chosendate:
        myReq.loop_get_messages(dialog.chosendate)
root = tk.Tk()
root.title("Telegram Channel Monitor")

api_id_label = tk.Label(root, text="API ID:")
api_id_label.grid(row=0, column=0, sticky="w")
api_id_entry = tk.Entry(root)
api_id_entry.grid(row=0, column=1)

api_hash_label = tk.Label(root, text="API Hash:")
api_hash_label.grid(row=1, column=0, sticky="w")
api_hash_entry = tk.Entry(root)
api_hash_entry.grid(row=1, column=1)
myReq=MyRequests()

channel_url_label = tk.Label(root, text="Channel URL:")
channel_url_label.grid(row=2, column=0, sticky="w")
channel_url_entry = tk.Entry(root)
channel_url_entry.grid(row=2, column=1)

start_button = tk.Button(root, text="Start", command=lambda:myReq.create_credentiol(api_id_entry,api_hash_entry,channel_url_entry))
start_button.grid(row=3, column=0, columnspan=1, pady=10)

read_button = tk.Button(root, text="Read", command=lambda:mydialog(root))
read_button.grid(row=3, column=1, columnspan=3, pady=10)


message_text = tk.Text(root, height=10, width=50)
message_text.grid(row=4, column=0, columnspan=2)

display_button = tk.Button(root, text="Display Messages", command=lambda:show_message(message_text))
display_button.grid(row=5, column=0, columnspan=2, pady=10)

root.mainloop()

