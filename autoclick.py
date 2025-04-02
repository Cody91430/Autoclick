import tkinter as tk
import threading
from pynput.mouse import Controller, Button
import keyboard
import time

MAX_CPS = 1000

class AutoClicker:
    def __init__(self):
        self.clicking = False
        self.click_count = 0
        self.mouse_controller = Controller()
        self.start_time = time.time()
        self.total_clicks_in_last_second = 0

        # Create main window
        self.root = tk.Tk()
        self.root.title("Auto Clicker")
        self.root.geometry("240x150")  # Slightly larger window for better readability
        self.root.resizable(False, False)
        self.root.attributes("-topmost", True)

        # Same font size for all text
        font_style = ("Arial", 10)

        # Status label
        self.status = tk.Label(self.root, text="Stopped", fg="red", font=font_style)
        self.status.pack(pady=5)

        # Frame for input fields
        frame = tk.Frame(self.root)
        frame.pack(pady=5)

        # Label for CPS input
        tk.Label(frame, text=f"CPS (Max {MAX_CPS}):", font=font_style).grid(row=0, column=0, padx=5)

        # Entry box for CPS input
        self.cps_entry = tk.Entry(frame, width=5, font=font_style, justify="center")
        self.cps_entry.insert(0, "10")
        self.cps_entry.grid(row=0, column=1, padx=5)
        self.cps_entry.bind("<KeyRelease>", self.validate_input)

        # Label for the current CPS rate
        self.rate = tk.Label(self.root, text="Current: 0 CPS", font=font_style)
        self.rate.pack(pady=5)

        # Instructions for hotkey
        tk.Label(self.root, text="Press F2 to toggle", font=font_style).pack(pady=5)

        # Start listening for hotkey in a separate thread
        threading.Thread(target=self.listen_hotkey, daemon=True).start()

        # Update rate every 100ms
        self.root.after(100, self.update_rate)

        self.root.mainloop()

    def validate_input(self, event):
        # Ensure input is a valid integer, and if not, reset to 10
        try:
            int_value = int(self.cps_entry.get())
            if int_value < 0:
                self.cps_entry.delete(0, tk.END)
                self.cps_entry.insert(0, "10")
        except ValueError:
            self.cps_entry.delete(0, tk.END)
            self.cps_entry.insert(0, "10")

    def listen_hotkey(self):
        try:
            keyboard.add_hotkey('F2', self.toggle)
            keyboard.wait()
        except Exception as e:
            print(f"Error listening for hotkeys: {e}")

    def toggle(self):
        if not self.clicking:
            try:
                cps = min(int(self.cps_entry.get()), MAX_CPS)
            except:
                cps = 10
            interval = 1 / cps if cps > 0 else 0.01
            self.status.config(text="Clicking", fg="green")
            self.clicking = True
            threading.Thread(target=self.click_loop, args=(interval,), daemon=True).start()
        else:
            self.clicking = False
            self.status.config(text="Stopped", fg="red")

    def click_loop(self, interval):
        last_click_time = time.time()
        while self.clicking:
            current_time = time.time()
            if current_time - last_click_time >= interval:
                self.mouse_controller.click(Button.left)
                self.click_count += 1
                last_click_time = current_time

    def update_rate(self):
        current_time = time.time()
        elapsed_time = current_time - self.start_time

        if elapsed_time >= 1:
            self.total_clicks_in_last_second = self.click_count
            self.click_count = 0
            self.start_time = current_time

        # Display the current CPS as an integer
        self.rate.config(text=f"Current: {self.total_clicks_in_last_second} CPS")

        self.root.after(100, self.update_rate)

if __name__ == "__main__":
    try:
        AutoClicker()
    except Exception as e:
        print(f"Error starting AutoClicker: {e}")
