import customtkinter as ctk
import pyvisa
from tkinter import messagebox
import threading

# --- Constants ---
# Set a default IP here if you frequently connect to the same one.
DEFAULT_IP = "169.254.41.244" 

class RTB2004GUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Rohde & Schwarz RTB2004 - Control Panel")
        self.geometry("800x550") # Adjusted size for the new layout
        ctk.set_appearance_mode("dark") # Dark mode is common for ATE
        ctk.set_default_color_theme("blue")

        self.rm = None
        self.scope = None

        # --- Configure root grid ---
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0) # Connection frame
        self.grid_rowconfigure(1, weight=0) # Status frame
        self.grid_rowconfigure(2, weight=1) # Main controls frame

        # --- Create Widgets ---
        self.create_connection_widgets()
        self.create_status_widgets()
        self.create_control_widgets()

    def create_connection_widgets(self):
        """Creates the top bar for device discovery and connection."""
        frame_conn = ctk.CTkFrame(self, corner_radius=0)
        frame_conn.grid(row=0, column=0, sticky="ew", padx=10, pady=(10,5))
        frame_conn.grid_columnconfigure(2, weight=1) # Allow IP entry to expand

        self.btn_scan = ctk.CTkButton(frame_conn, text="Scan Devices", width=120, command=self.scan_devices)
        self.btn_scan.grid(row=0, column=0, padx=5, pady=5)

        self.combo_devices = ctk.CTkComboBox(frame_conn, values=["No Devices Found"], width=200)
        self.combo_devices.grid(row=0, column=1, padx=5, pady=5)

        self.entry_ip = ctk.CTkEntry(frame_conn, placeholder_text="Enter IP for LAN (e.g. 169.254.41.244)")
        self.entry_ip.insert(0, DEFAULT_IP)
        self.entry_ip.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

        self.btn_connect = ctk.CTkButton(frame_conn, text="Connect", width=100, command=self.connect_scope, fg_color="green")
        self.btn_connect.grid(row=0, column=3, padx=5, pady=5)

        self.btn_disconnect = ctk.CTkButton(frame_conn, text="Disconnect", width=100, command=self.disconnect_scope, state="disabled", fg_color="red")
        self.btn_disconnect.grid(row=0, column=4, padx=(5,10), pady=5)

    def create_status_widgets(self):
        """Creates the status bar below the connection bar."""
        frame_status = ctk.CTkFrame(self)
        frame_status.grid(row=1, column=0, sticky="ew", padx=10, pady=0)
        frame_status.grid_columnconfigure(1, weight=1)

        self.label_status = ctk.CTkLabel(frame_status, text="Status: Disconnected", text_color="red", font=("", 14, "bold"))
        self.label_status.grid(row=0, column=0, padx=10, pady=5)
        
        self.label_id = ctk.CTkLabel(frame_status, text="Instrument ID: ---", font=("", 12), anchor="w")
        self.label_id.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

    def create_control_widgets(self):
        """Creates the main control area with logical columns."""
        frame_main = ctk.CTkFrame(self)
        frame_main.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)
        frame_main.grid_columnconfigure((0, 1), weight=1)
        frame_main.grid_rowconfigure(0, weight=1)

        # --- Left Column (Channels) ---
        frame_ch = ctk.CTkFrame(frame_main)
        frame_ch.grid(row=0, column=0, padx=(10,5), pady=10, sticky="nsew")
        
        ctk.CTkLabel(frame_ch, text="Channel Controls", font=("", 16, "bold")).pack(pady=10)

        self.channel_select = ctk.CTkComboBox(frame_ch, values=["CH1", "CH2", "CH3", "CH4"], width=120)
        self.channel_select.set("CH1")
        self.channel_select.pack(pady=10)

        self.entry_vscale = self._entry_with_label(frame_ch, "Vertical Scale (V/div):", "0.5")
        self.entry_voffset = self._entry_with_label(frame_ch, "Vertical Offset (V):", "0.0")
        self.combo_coupling = self._combo_with_label(frame_ch, "Coupling:", ["DC", "AC", "GND"])
        self.combo_probe = self._combo_with_label(frame_ch, "Probe Attenuation:", ["1", "10", "100"])

        # --- Right Column (Timebase & Trigger) ---
        frame_right = ctk.CTkFrame(frame_main, fg_color="transparent")
        frame_right.grid(row=0, column=1, padx=(5,10), pady=0, sticky="nsew")
        frame_right.grid_rowconfigure(0, weight=1)
        frame_right.grid_rowconfigure(1, weight=1)
        frame_right.grid_columnconfigure(0, weight=1)

        # Timebase Frame (Top Right)
        frame_time = ctk.CTkFrame(frame_right)
        frame_time.grid(row=0, column=0, pady=(10,5), sticky="nsew")
        ctk.CTkLabel(frame_time, text="Timebase Controls", font=("", 16, "bold")).pack(pady=10)

        self.entry_tscale = self._entry_with_label(frame_time, "Timebase Scale (s/div):", "0.001")
        self.entry_tpos = self._entry_with_label(frame_time, "Timebase Position (s):", "0")

        # Trigger Frame (Bottom Right)
        frame_trig = ctk.CTkFrame(frame_right)
        frame_trig.grid(row=1, column=0, pady=(5,10), sticky="nsew")
        ctk.CTkLabel(frame_trig, text="Trigger Controls", font=("", 16, "bold")).pack(pady=10)

        self.combo_trig_source = self._combo_with_label(frame_trig, "Source:", ["CH1", "CH2", "CH3", "CH4", "EXT"])
        self.combo_trig_mode = self._combo_with_label(frame_trig, "Mode:", ["AUTO", "NORMAL", "SINGLE"])
        self.entry_trig_level = self._entry_with_label(frame_trig, "Level (V):", "0.0")

        # --- Bottom Action Buttons ---
        frame_actions = ctk.CTkFrame(self)
        frame_actions.grid(row=3, column=0, sticky="ew", padx=10, pady=(0,10))
        frame_actions.grid_columnconfigure((0,1,2,3), weight=1) # Distribute buttons evenly

        self.btn_apply_all = ctk.CTkButton(frame_actions, text="Apply All Settings", height=40, command=self.apply_all_settings)
        self.btn_apply_all.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        
        self.btn_run = ctk.CTkButton(frame_actions, text="RUN", height=40, command=lambda: self.send_cmd("RUN"))
        self.btn_run.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        self.btn_stop = ctk.CTkButton(frame_actions, text="STOP", height=40, command=lambda: self.send_cmd("STOP"))
        self.btn_stop.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

        self.btn_autoset = ctk.CTkButton(frame_actions, text="AutoSet", height=40, command=lambda: self.send_cmd("AUT"))
        self.btn_autoset.grid(row=0, column=3, padx=5, pady=5, sticky="ew")

    # ---------- Helper Widgets (using .grid()) ----------
    def _entry_with_label(self, parent, text, default):
        """Creates a labeled entry widget using .grid()"""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", pady=4, padx=20)
        frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(frame, text=text, width=150, anchor="w").grid(row=0, column=0, padx=5)
        entry = ctk.CTkEntry(frame)
        entry.insert(0, default)
        entry.grid(row=0, column=1, padx=5, sticky="ew")
        return entry

    def _combo_with_label(self, parent, text, values):
        """Creates a labeled combobox widget using .grid()"""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", pady=4, padx=20)
        frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(frame, text=text, width=150, anchor="w").grid(row=0, column=0, padx=5)
        combo = ctk.CTkComboBox(frame, values=values)
        combo.set(values[0])
        combo.grid(row=0, column=1, padx=5, sticky="ew")
        return combo

    # ---------- Core Functions (No changes to logic) ----------
    
    def scan_devices(self):
        try:
            self.rm = pyvisa.ResourceManager()
            resources = self.rm.list_resources()

            if not resources:
                self.combo_devices.configure(values=["No Devices Found"])
                self.combo_devices.set("No Devices Found")
                messagebox.showwarning("Scan", "No VISA instruments detected.")
                return

            self.combo_devices.configure(values=list(resources))
            self.combo_devices.set(resources[0])
            messagebox.showinfo("Scan Complete", f"Found {len(resources)} device(s).")

        except Exception as e:
            messagebox.showerror("Error", f"VISA scan failed:\n{e}")

    def connect_scope(self):
        try:
            self.rm = pyvisa.ResourceManager()

            ip = self.entry_ip.get().strip()
            if ip:
                visa_str = f"TCPIP::{ip}::INSTR"
            else:
                visa_str = self.combo_devices.get()
            
            if visa_str == "No Devices Found":
                raise Exception("No device selected or found.")

            self.scope = self.rm.open_resource(visa_str)
            self.scope.timeout = 5000 # 5 second timeout
            idn = self.scope.query("*IDN?")

            self.label_id.configure(text=f"ID: {idn.strip()}")
            self.label_status.configure(text="Status: Connected", text_color="#00FF00") # Bright Green
            self.btn_connect.configure(state="disabled")
            self.btn_disconnect.configure(state="normal")
            
            messagebox.showinfo("Connection", f"Connected successfully:\n{visa_str}")

        except Exception as e:
            messagebox.showerror("Connection Error", f"Could not connect:\n{e}")

    def disconnect_scope(self):
        if self.scope:
            try:
                self.scope.close()
            except Exception as e:
                print(f"Error during disconnect: {e}") # Log to console
            self.scope = None

        self.label_status.configure(text="Status: Disconnected", text_color="red")
        self.label_id.configure(text="Instrument ID: ---")
        self.btn_connect.configure(state="normal")
        self.btn_disconnect.configure(state="disabled")

    def send_cmd(self, cmd):
        if not self.scope:
            messagebox.showwarning("Warning", "Connect to scope first.")
            return
        
        # Use a thread to send command to avoid freezing GUI if scope is slow
        threading.Thread(target=self._send_cmd_thread, args=(cmd,), daemon=True).start()

    def _send_cmd_thread(self, cmd):
        try:
            self.scope.write(cmd)
            print(f"Sent command: {cmd}") # Log to console
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Command Error", str(e)))

    def apply_all_settings(self):
        """Consolidated function to apply all settings from the GUI."""
        if not self.scope:
            messagebox.showwarning("Warning", "Connect to scope first.")
            return
        
        # Run settings application in a thread
        threading.Thread(target=self._apply_all_thread, daemon=True).start()

    def _apply_all_thread(self):
        """Threaded function to apply all settings."""
        try:
            self.set_channel_params(show_success=False)
            self.set_timebase_params(show_success=False)
            self.set_trigger_params(show_success=False)
            # Notify user on the main thread
            self.after(0, lambda: messagebox.showinfo("Success", "All settings applied successfully."))
        except Exception as e:
            # Notify user of error on the main thread
            self.after(0, lambda: messagebox.showerror("Error", str(e)))

    def set_channel_params(self, show_success=True):
        if not self.scope:
            if show_success: messagebox.showwarning("Warning", "Connect to scope first.")
            return
        ch = self.channel_select.get()
        vscale = self.entry_vscale.get()
        voffset = self.entry_voffset.get()
        coupling = self.combo_coupling.get()
        probe = self.combo_probe.get()
        
        # Send commands as a batch
        self.scope.write(f"{ch}:SCAL {vscale}")
        self.scope.write(f"{ch}:OFFS {voffset}")
        self.scope.write(f"{ch}:COUP {coupling}")
        self.scope.write(f"{ch}:PROB {probe}")
        
        if show_success:
            self.after(0, lambda: messagebox.showinfo("Channel", f"{ch} configured successfully."))

    def set_timebase_params(self, show_success=True):
        if not self.scope:
            if show_success: messagebox.showwarning("Warning", "Connect to scope first.")
            return
        scale = self.entry_tscale.get()
        pos = self.entry_tpos.get()
        
        self.scope.write(f"TIM:SCAL {scale}")
        self.scope.write(f"TIM:POS {pos}")
        
        if show_success:
            self.after(0, lambda: messagebox.showinfo("Timebase", "Timebase configured successfully."))

    def set_trigger_params(self, show_success=True):
        if not self.scope:
            if show_success: messagebox.showwarning("Warning", "Connect to scope first.")
            return
        src = self.combo_trig_source.get()
        mode = self.combo_trig_mode.get()
        level = self.entry_trig_level.get()

        self.scope.write(f"TRIG:A:SOUR {src}")
        self.scope.write(f"TRIG:A:MODE {mode}")
        self.scope.write(f"TRIG:A:LEV {level}")
        
        if show_success:
            self.after(0, lambda: messagebox.showinfo("Trigger", "Trigger configured successfully."))


# ---------- MAIN ----------
if __name__ == "__main__":
    # Add a safety check for pyvisa
    if pyvisa is None:
        messagebox.showerror("Fatal Error", "PyVISA library not found!\nPlease install it by running:\npip install pyvisa")
        sys.exit()

    app = RTB2004GUI()
    app.mainloop()