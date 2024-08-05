import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import socket
import threading
from io import BytesIO
from PIL import Image, ImageTk, ImageFile
import datetime

server_ip = '127.0.0.1'
server_port = 8888
server_addr = (server_ip, server_port)

class TCPClient:
    def __init__(self, root) -> None:
        """
        Initialize the TCPClient class.

        Args:
            root (tk.Tk): The Tkinter root window.
        """
        self.root = root
        self.setup_ui()
        self.file_path = ''
        self.is_connecting = False

    def setup_ui(self) -> None:
        """
        Set up the user interface with canvas for image display, scrolled text for messages, and buttons for actions.
        """
        self.canvas = tk.Canvas(self.root, width=600, height=400)
        self.msg_view = scrolledtext.ScrolledText(self.root, width=100, height=30)
        self.msg_view.config(state=tk.DISABLED)
        self.file_button = tk.Button(self.root, text='이미지 선택', command=self.select_file)
        self.send_button = tk.Button(self.root, text='서버로 전송', command=self.send_data)
        self.exit_button = tk.Button(self.root, text='종료', command=self.exit_app)

        self.canvas.grid(row=0, column=0, padx=10, pady=10)
        self.msg_view.grid(row=0, column=1, padx=10, pady=10)
        self.file_button.grid(row=1, column=0, padx=10, pady=5)
        self.send_button.grid(row=1, column=1, padx=10, pady=5)
        self.exit_button.grid(row=1, column=2, padx=10, pady=5)

    def select_file(self) -> None:
        """
        Open a file dialog to select an image file for classification.
        """
        file_path = filedialog.askopenfilename(
            initialdir="/",
            title="파일 선택",
            filetypes=(("이미지 파일", "*.jpg *.jpeg"), )
        )
        if file_path:
            self.file_path = file_path 
            self.display_msg(f"선택된 파일: {file_path}", 'client')
            
            try:
                image = Image.open(file_path)
                self.display_img(image)
            except Exception as e:
                self.display_msg(f'Image Loading Error: {e}', 'error')
        
    def display_msg(self, message, type) -> None:
        """
        Display messages in the scrolled text widget.

        Args:
            message (str): The message to be displayed.
            type (str): The type of the message, either 'client', 'server', or 'error'.
        """
        def task(type) -> None:
            if type == 'client' :
                format_msg = f'Client [{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] : {message}\n\n'
            elif type == 'server' :
                format_msg = f'Server [{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] : {message}\n\n'
            elif type == 'error' :
                format_msg = f'ERROR [{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] : {message}\n\n'

            self.msg_view.config(state=tk.NORMAL)
            self.msg_view.insert(tk.END, format_msg)
            self.msg_view.yview(tk.END)
            self.msg_view.config(state=tk.DISABLED)
        self.root.after(0, task, type)

    def display_img(self, image) -> None:
        """
        Display the selected image on the canvas.

        Args:
            image: The image to be displayed.
        """
        def task() -> None:
            image.thumbnail((600,400))
            img = ImageTk.PhotoImage(image)
            self.canvas.create_image(300, 200, image = img)
            self.canvas.image = img
        self.root.after(0, task)

    def exit_app(self) -> None:
        """
        Close the application window.
        """
        if self.is_connecting:
            messagebox.showinfo("통신", "통신끝나면 다시 누르세요")
            return
        
        self.root.destroy()

    def send_data(self) -> None:
        """
        Send the selected image to the server for classification.
        """
        if not self.file_path:
            self.display_msg('파일 선택이나 하고 누르쇼', 'error')
            return
        
        try:
            self.is_connecting = True

            with open(self.file_path, 'rb') as file:
                data = file.read()
                total_size = len(data)

                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.connect((server_ip, server_port))
                    sock.sendall(total_size.to_bytes(8, 'big'))

                    chunk_size = 1024
                    for i in range(0, total_size, chunk_size):
                        chunk = data[i:i+chunk_size]
                        sock.sendall(chunk)
                    self.display_msg('Image sent successfully', 'client')

                    sock.settimeout(10)
                    response = sock.recv(1024)
                    if response:
                        self.display_msg(response.decode('utf-8'), 'server')
                    else:
                        raise Exception('No response from server')
        except Exception as e:
            self.display_msg(f'Error sending data: {e}', 'error')
        finally:
            self.is_connecting = False

if __name__ == '__main__':
    root = tk.Tk()
    root.title('Flower Classification - Client')
    root.resizable(False, False)
    app = TCPClient(root)

    root.mainloop()