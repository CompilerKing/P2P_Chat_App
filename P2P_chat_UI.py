#!/usr/bin/env

# @author Phillip Porter

import tkinter as tk


class Chat_UI(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.grid()
        self.createWidgets()

    def createWidgets(self):
        # Quit command button
        self.quitButton = tk.Button(self, text='Quit',
                                    command=self.quit)
        self.quitButton.grid(sticky=tk.NW, row=0, column=0)

        # Client output textbox
        self.client_out = tk.Text(self, width=80, height=20)
        self.client_out.grid(sticky=tk.N + tk.S, row=1, column=0)

        # List of users
        self.client_users = tk.Text(self, width=20, height=20)
        self.client_users.grid(sticky=tk.N + tk.S, row=1, column=1)

        # User input textbox
        self.user_in = tk.Text(self, width=80, height=2)
        self.user_in.grid(sticky=tk.SW, row=2, column=0)

        # Send button
        self.send_button = tk.Button(self, text='Send',
                                     width=22, height=2, command=self.quit)
        self.send_button.grid(sticky=tk.SE, row=2, column=1)


top = tk.Tk()
app = Chat_UI(master=top)
top.resizable(width=False, height=False)
app.master.title('P2P chat client')
app.mainloop()
