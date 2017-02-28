#!/usr/bin/env

# @author Phillip Porter

import tkinter as tk
import multiprocessing

class ChatUI(tk.Frame):
    def __init__(self, user_out_queue, client_in_queue, master=None):
        tk.Frame.__init__(self, master)
        self.grid()
        self.createWidgets()

        # Queues
        # To Client
        self.UI_out_queue = user_out_queue
        # To User
        self.client_in_queue = client_in_queue

    def push_user_input_text(self):
        # Fetch string from input box and place in queue
        self.UI_out_queue.put(self.user_in.get(1.0,tk.END)[:-1])

        # Clear the box
        self.user_in.delete(1.0,tk.END)

    def append_client_output_loop(self):
        if self.client_in_queue.empty() is False:

            while self.client_in_queue.empty() is False:
                self.client_out.insert(tk.END, self.client_in_queue.get())

            # Shift down text
            self.client_out.see(tk.END)
        # Otherwise do nothing, this fixes scrolling issue

        # Schedule next update
        self.master.after(250, self.append_client_output_loop)

    def createWidgets(self):
        # Client output textbox
        self.client_out = tk.Text(self, width=80, height=20,)
        self.client_out.grid(sticky=tk.N + tk.S, row=0, column=0)

        # List of users
        self.client_users = tk.Text(self, width=20, height=20,)
        self.client_users.grid(sticky=tk.N + tk.S, row=0, column=1)

        # User input textbox
        self.user_in = tk.Text(self, width=80,height=2,)
        self.user_in.grid(sticky=tk.SW, row=1, column=0)

        # Send button
        self.send_button = tk.Button(self, text='Send',width=22,
                                     height=2, command=self.push_user_input_text)
        self.send_button.grid(sticky=tk.SE, row=1, column=1)


class Chat_UI_Process(multiprocessing.Process):
    def __init__(self):
        multiprocessing.Process.__init__(self)

        # Queues
        self.user_out_queue = multiprocessing.Queue()
        self.client_in_queue = multiprocessing.Queue()

        self.top = None
        self.app = None

    # Kills P2P client
    def kill_client(self):
        self.user_out_queue.put("e")
        self.top.destroy()

    def run(self):
        # TK loop and window setup
        self.top = tk.Tk()
        self.app = ChatUI(self.user_out_queue, self.client_in_queue,master=self.top)

        self.top.resizable(width=False, height=False)
        self.app.master.title('P2P chat client')

        # Timer to check for more client output
        self.top.after(250, self.app.append_client_output_loop())

        # Set window to kill client on close
        self.top.wm_protocol("WM_DELETE_WINDOW", self.kill_client)

        # Main loop
        self.app.mainloop()

    def get_output_string(self):
        return self.user_out_queue.get(block=True)

    def print_to_user(self, msg):
        self.client_in_queue.put(msg)

# Unit test
if __name__ == '__main__':
    app_ui = Chat_UI_Process()
    app_ui.start()
    while True:
        app_ui.print_to_user(app_ui.get_output_string())
