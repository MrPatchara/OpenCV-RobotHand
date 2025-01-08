import cv2
from cvzone.HandTrackingModule import HandDetector
from cvzone.SerialModule import SerialObject
import tkinter as tk
from tkinter import ttk, messagebox
from threading import Thread
from PIL import Image, ImageTk
import serial.tools.list_ports

class HandTrackingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Hand Tracking with GUI")
        self.cap = None
        self.detector = HandDetector(maxHands=1, detectionCon=0.7)
        self.serial_port = None
        self.running = False

        self.create_gui()

    def create_gui(self):
        # Menu bar
        menu_bar = tk.Menu(self.root)
        settings_menu = tk.Menu(menu_bar, tearoff=0)
        settings_menu.add_command(label="Select COM Port", command=self.select_com_port)
        menu_bar.add_cascade(label="Settings", menu=settings_menu)
        self.root.config(menu=menu_bar)

        # Buttons
        self.start_button = ttk.Button(self.root, text="Start Camera", command=self.start_camera)
        self.start_button.grid(row=0, column=0, padx=10, pady=10)

        self.stop_button = ttk.Button(self.root, text="Stop Camera", command=self.stop_camera, state=tk.DISABLED)
        self.stop_button.grid(row=0, column=1, padx=10, pady=10)

        self.exit_button = ttk.Button(self.root, text="Exit", command=self.exit_app)
        self.exit_button.grid(row=0, column=2, padx=10, pady=10)

        # Layout adjustment
        self.main_frame = tk.Frame(self.root)
        self.main_frame.grid(row=1, column=0, columnspan=3, padx=10, pady=10)

        # Video frame
        self.video_frame = tk.Label(self.main_frame)
        self.video_frame.grid(row=0, column=0, padx=10, pady=10)

        # Serial output frame
        self.serial_output_frame = tk.Frame(self.main_frame)
        self.serial_output_frame.grid(row=0, column=1, padx=10, pady=10, sticky="ns")

        self.serial_output_label = tk.Label(self.serial_output_frame, text="Serial Output", font=("Arial", 14))
        self.serial_output_label.pack()

        self.serial_output_text = tk.Text(self.serial_output_frame, width=30, height=20, state="disabled")
        self.serial_output_text.pack()
        self.serial_output_frame.grid_remove()  # Initially hide the frame

    def select_com_port(self):
        def save_com_port():
            port = com_port_combo.get()
            try:
                self.serial_port = SerialObject(port, 115200, 1)
                messagebox.showinfo("Success", f"Connected to {port}")
                settings_window.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to connect to {port}: {e}")

        settings_window = tk.Toplevel(self.root)
        settings_window.title("Select COM Port")
        settings_window.geometry("300x150")

        tk.Label(settings_window, text="Select COM Port:").pack(pady=10)
        available_ports = [port.device for port in serial.tools.list_ports.comports()]
        com_port_combo = ttk.Combobox(settings_window, values=available_ports, state="readonly")
        com_port_combo.pack(pady=5)
        if available_ports:
            com_port_combo.current(0)

        save_button = ttk.Button(settings_window, text="Save", command=save_com_port)
        save_button.pack(pady=10)

    def start_camera(self):
        if self.cap is None:
            self.cap = cv2.VideoCapture(0)

        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)

        self.serial_output_frame.grid()  # Show the serial output frame

        self.running = True
        self.update_video_frame()

    def stop_camera(self):
        if self.cap:
            self.running = False
            self.cap.release()
            self.cap = None

        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

        self.serial_output_frame.grid_remove()  # Hide the serial output frame

    def update_video_frame(self):
        if self.running and self.cap:
            success, img = self.cap.read()
            if success:
                hands, img = self.detector.findHands(img)
                if hands and self.serial_port:
                    fingers = self.detector.fingersUp(hands[0])
                    self.serial_port.sendData(fingers)

                    # Update serial output
                    self.serial_output_text.config(state="normal")
                    self.serial_output_text.insert(tk.END, f"{fingers}\n")
                    self.serial_output_text.see(tk.END)
                    self.serial_output_text.config(state="disabled")

                # Convert image to PhotoImage
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(img)
                imgtk = ImageTk.PhotoImage(image=img)
                self.video_frame.imgtk = imgtk
                self.video_frame.configure(image=imgtk)

            self.root.after(10, self.update_video_frame)
        else:
            self.video_frame.config(image="")

    def exit_app(self):
        self.stop_camera()
        self.root.quit()

if __name__ == "__main__":
    root = tk.Tk()
    app = HandTrackingApp(root)
    root.mainloop()
