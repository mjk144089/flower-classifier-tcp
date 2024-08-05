import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import socket
import threading
import tensorflow as tf
import numpy as np
import pandas as pd
from io import BytesIO
from PIL import Image, ImageTk, ImageFile
import datetime

# Load pre-trained flower classification model and labels
model = tf.saved_model.load('./model')
label = './flower_classification_labels.xlsx'
df = pd.read_excel(label)
print(list(model.signatures.keys()))

# Server configuration
server_ip = '127.0.0.1'
server_port = 8888
server_addr = (server_ip, server_port)

class TCPServer:

    def __init__(self, root) -> None:
        """
        Initialize the TCPServer class.

        Args:
            root (tk.Tk): The Tkinter root window.
        """
        self.root = root
        self.setup_ui()

        self.running = True
        self.client_threads = []
        self.server_socket = None
        self.local = threading.local()

        # Get the inference function from the model
        self.infer = model.signatures['serving_default']

    def setup_ui(self) -> None:
        """
        Set up the user interface with scrolled text for messages and an exit button.
        """
        self.msg_view = scrolledtext.ScrolledText(self.root, width=100, height=50)
        self.msg_view.config(state=tk.DISABLED)
        self.exit_button = tk.Button(self.root, text='서버 종료', command=self.stop_server)

        self.msg_view.grid(row=0, column=0, padx=10, pady=10)
        self.exit_button.grid(row=1, column=0, padx=10, pady=5)

    def display_msg(self, message, type) -> None:
        """
        Display messages in the scrolled text widget.

        Args:
            message (str): The message to be displayed.
            type (str): The type of the message, either 'msg' or 'error'.
        """
        def task() -> None:
            if type == 'msg':
                format_msg = f'Message [{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] {message}\n\n'
            elif type == 'error':
                format_msg = f'Error [{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] {message}\n\n'
            
            self.msg_view.config(state=tk.NORMAL)
            self.msg_view.insert(tk.END, format_msg)
            self.msg_view.yview(tk.END)
            self.msg_view.config(state=tk.DISABLED)
        self.msg_view.after(0, task)

    def stop_server(self) -> None:
        """
        Stop the server and close all client connections.
        """
        self.running = False
        self.display_msg("Stopping server...", 'msg')

        for thread in self.client_threads:
            if thread.is_alive():
                thread.client_socket.close()

        if self.server_socket:
            self.server_socket.close()

        for thread in self.client_threads:
            thread.join()

        self.root.destroy()
        self.display_msg("Server stopped", 'msg')

    def preprocess_image(self, image) -> np.ndarray:
        """
        Preprocess the input image for model prediction.

        Args:
            image: The input image.

        Returns:
            np.ndarray: The preprocessed image as a NumPy array.
        """
        if image.mode == 'RGBA':
            image = image.convert('RGB')
        
        image = image.resize((299, 299))
        arr = np.array(image)
        arr = arr / 255.0
        arr = np.expand_dims(arr, axis=0)
        
        return arr

    def classify_image(self, image) -> np.ndarray:
        """
        Classify the input image using the pre-trained model.

        Args:
            image: The input image.

        Returns:
            np.ndarray: The prediction array from the model.
        """
        preprocessed_image = self.preprocess_image(image)
        # Get the input tensor from the preprocessed image
        input_tensor = tf.convert_to_tensor(preprocessed_image, dtype=tf.float32)
        # Perform inference
        prediction = self.infer(input_tensor)
        # Extract the output tensor
        output_key = list(self.infer.structured_outputs.keys())[0]  # Extract output key
        return prediction[output_key].numpy()

    def get_flower_names_by_index(self, index):
        """
        Get flower names (English and Korean) based on the provided index.

        Args:
            index: The index corresponding to the flower.

        Returns:
            tuple: Tuple containing English and Korean flower names.
        """
        return (df.iloc[index]['en_class'], df.iloc[index]['ko_class'])
    
    def listen_for_client(self) -> None:
        """
        Listen for incoming client connections and handle them in separate threads.
        """
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # IPv4
        self.server_socket.bind(server_addr)
        self.server_socket.listen(socket.SOMAXCONN)

        self.display_msg(f'Server listening on {server_ip}:{server_port}', 'msg')

        while self.running:
            try:
                if not self.running:
                    break

                client_sock, addr = self.server_socket.accept()
                self.display_msg(f'Connection from {addr} established', 'msg')

                client_thread = threading.Thread(target=self.handle_client, args=(client_sock, addr))
                self.client_threads.append(client_thread)
                client_thread.start()
                
            except Exception as e:
                if not self.running: 
                    self.display_msg('Server running plague is False', 'msg')
                else: 
                    self.display_msg(f'Error during client connection', 'error')

    def handle_client(self, client_sock, addr) -> None:
        """
        Handle client data, receive images, and send classification results.

        Args:
            client_sock: The client socket.
            addr: The address of the client.
        """
        self.local.prediction_completed = False

        try:
            img_size_data = client_sock.recv(8)
            if not img_size_data:
                raise Exception("Failed receive img_size_data")
        
            total_size = int.from_bytes(img_size_data, 'big')
            received_size = 0
            image_data = bytearray()

            while received_size < total_size:
                chunk = client_sock.recv(1024)
                if not chunk:
                    raise Exception("Connection lost while receiving data")
                image_data.extend(chunk)
                received_size += len(chunk)

            image = Image.open(BytesIO(image_data))
            self.display_msg('Image loaded successfully', 'msg')

            prediction = self.classify_image(image)
            predicted_class_idx = np.argmax(prediction[0])
            self.display_msg(f'{prediction}', 'msg')
            self.display_msg(f'Index = {predicted_class_idx}', 'msg')

            en_label, ko_label = self.get_flower_names_by_index(predicted_class_idx)
            result = f'Flower classification : {ko_label}({en_label})'

            self.display_msg(result, 'msg')

            self.local.prediction_completed = True

            client_sock.sendall(result.encode('utf-8'))

        except Exception as e:
            self.display_msg(f'Error handling client data', 'error')
        
            
if __name__ == '__main__':
    root = tk.Tk()
    root.title('Flower Classification - Server')
    root.resizable(False, False)
    app = TCPServer(root)

    server_thread = threading.Thread(target=app.listen_for_client)
    server_thread.start()

    root.mainloop()
