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

        # Dark retro theme settings
        self.bg_color = "#1a1a1a"  # Dark black-gray background color
        self.fg_color = "#e6e6e6"  # Light gray for text
        self.button_bg = "#3e4a4f"  # Dark gray-blue
        self.button_fg = "#f4a300"  # Bright orange for button text
        self.highlight_color = "#ff6600"  # Retro orange for highlights
        self.root.config(bg=self.bg_color)

        self.create_gui()

    # Create GUI elements
    def create_gui(self):
        # Menu bar with dark retro theme
        menu_bar = tk.Menu(self.root, bg=self.bg_color, fg=self.fg_color)

        file_menu = tk.Menu(menu_bar, tearoff=0, bg=self.bg_color, fg=self.fg_color)
        file_menu.add_command(label="Contact Us", command=lambda: messagebox.showinfo("Contact Us", "Email:" + "\n" + "Phone:"))
        menu_bar.add_cascade(label="Help!", menu=file_menu)
        

        settings_menu = tk.Menu(menu_bar, tearoff=0, bg=self.bg_color, fg=self.fg_color)
        settings_menu.add_command(label="Select COM Port", command=self.select_com_port)
        menu_bar.add_cascade(label="Settings", menu=settings_menu)
        self.root.config(menu=menu_bar)
        
        # add developer bar
        developer_bar = tk.Label(self.root, text="Developed by: Your Name", bg=self.bg_color, fg=self.fg_color, font=("Press Start 2P", 12))
        developer_bar.grid(row=2, column=0, columnspan=3, pady
                            =10)
        
        # Buttons with dark retro styling
        self.start_button = ttk.Button(self.root, text="Start Camera", command=self.start_camera, 
                                       style="RetroButton.TButton")
        self.start_button.grid(row=0, column=0, padx=10, pady=10)

        self.stop_button = ttk.Button(self.root, text="Stop Camera", command=self.stop_camera, state=tk.DISABLED, 
                                      style="RetroButton.TButton")
        self.stop_button.grid(row=0, column=1, padx=10, pady=10)

        self.exit_button = ttk.Button(self.root, text="Exit", command=self.exit_app, 
                                      style="RetroButton.TButton")
        self.exit_button.grid(row=0, column=2, padx=10, pady=10)

        # Layout adjustment
        self.main_frame = tk.Frame(self.root, bg=self.bg_color)
        self.main_frame.grid(row=1, column=0, columnspan=3, padx=10, pady=10)

        # Video frame
        self.video_frame = tk.Label(self.main_frame, bg=self.bg_color)
        self.video_frame.grid(row=0, column=0, padx=10, pady=10)

        # Add image frame for left side when camera starts
        self.image_frame = tk.Label(self.main_frame, bg=self.bg_color)
        self.image_frame.grid(row=0, column=1, padx=10, pady=10)

        # Load an image (replace with your own image path)
        self.image = Image.open("your_image_path.png")  # Replace with your image path
        self.image = self.image.resize((350, 350))  # Resize image as needed
        self.image_tk = ImageTk.PhotoImage(self.image)
        self.image_label = tk.Label(self.image_frame, image=self.image_tk, bg=self.bg_color)

        # Serial output frame
        self.serial_output_frame = tk.Frame(self.main_frame, bg=self.bg_color)
        self.serial_output_frame.grid(row=0, column=2, padx=10, pady=10, sticky="ns")

        self.serial_output_label = tk.Label(self.serial_output_frame, text="Serial Output", font=("Press Start 2P", 14), fg=self.fg_color, bg=self.bg_color)
        self.serial_output_label.pack()

        self.serial_output_text = tk.Text(self.serial_output_frame, width=30, height=20, state="disabled", fg=self.fg_color, bg="#2d3539", font=("Courier", 12))
        self.serial_output_text.pack()
        self.serial_output_frame.grid_remove()  # Initially hide the frame

        # Set up style for buttons with dark retro look
        self.style = ttk.Style()
        self.style.configure("RetroButton.TButton", font=("Press Start 2P", 12, "bold"), padding=10, 
                             background=self.button_bg, foreground=self.button_fg, relief="flat")
        self.style.map("RetroButton.TButton", background=[('active', self.highlight_color)])  # Highlight on hover

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
        settings_window.config(bg=self.bg_color)

        tk.Label(settings_window, text="Select COM Port:", fg=self.fg_color, bg=self.bg_color, font=("Press Start 2P", 12)).pack(pady=10)
        available_ports = [port.device for port in serial.tools.list_ports.comports()]
        com_port_combo = ttk.Combobox(settings_window, values=available_ports, state="readonly", font=("Courier", 12))
        com_port_combo.pack(pady=5)
        if available_ports:
            com_port_combo.current(0)

        save_button = ttk.Button(settings_window, text="Save", command=save_com_port, style="RetroButton.TButton")
        save_button.pack(pady=10)

    def start_camera(self):
        if self.cap is None:
            self.cap = cv2.VideoCapture(0)

        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL) 

        # Show the serial output frame
        self.serial_output_frame.grid()  
        # Show image when starting camera
        self.image_label.grid(row=0, column=1, padx=10, pady=10)
       
        self.running = True 
        self.root.attributes('-fullscreen', True)  # Set fullscreen mode
        self.update_video_frame() # Start updating video frame

        #set all to center
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_columnconfigure(2, weight=1)


    def stop_camera(self):
        if self.cap:
            self.running = False
            self.cap.release()
            self.cap = None

        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

        self.serial_output_frame.grid_remove()  # Hide the serial output frame

        # Hide the image when stopping camera
        self.image_label.grid_forget()

        self.root.attributes('-fullscreen', False)  # Exit fullscreen mode

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
