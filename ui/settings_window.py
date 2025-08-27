import customtkinter as ctk
import serial.tools.list_ports
from typing import Callable, Optional
from config.settings import Settings

class SettingsWindow:
    def __init__(self, parent, settings: Settings, on_settings_changed: Optional[Callable] = None):
        self.parent = parent
        self.settings = settings
        self.on_settings_changed = on_settings_changed
        
        self.window = ctk.CTkToplevel(parent)
        self.window.title("Settings")
        self.window.geometry("800x600")
        self.window.transient(parent)
        self.window.grab_set()
        
        self.setup_ui()
        self.load_current_settings()
    
    def setup_ui(self):
        self.window.grid_columnconfigure(0, weight=1)
        self.window.grid_rowconfigure(0, weight=1)
        
        main_frame = ctk.CTkScrollableFrame(self.window)
        main_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        main_frame.grid_columnconfigure(1, weight=1)
        
        title_label = ctk.CTkLabel(
            main_frame,
            text="Climate Chamber Settings",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=20)
        
        self.setup_serial_section(main_frame, start_row=1)
        self.setup_calibration_section(main_frame, start_row=6)
        self.setup_button_section(main_frame, start_row=12)
    
    def setup_serial_section(self, parent, start_row):
        section_label = ctk.CTkLabel(
            parent,
            text="Serial Communication",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        section_label.grid(row=start_row, column=0, columnspan=2, sticky="w", pady=(20, 10))
        
        ctk.CTkLabel(parent, text="Serial Port:", font=ctk.CTkFont(size=14)).grid(
            row=start_row+1, column=0, sticky="w", padx=(20, 10), pady=5
        )
        
        self.port_var = ctk.StringVar()
        self.port_dropdown = ctk.CTkComboBox(
            parent,
            variable=self.port_var,
            values=self.get_available_ports(),
            width=300,
            height=40,
            font=ctk.CTkFont(size=14)
        )
        self.port_dropdown.grid(row=start_row+1, column=1, sticky="w", pady=5)
        
        refresh_button = ctk.CTkButton(
            parent,
            text="Refresh Ports",
            width=120,
            height=40,
            command=self.refresh_ports
        )
        refresh_button.grid(row=start_row+1, column=2, padx=(10, 0), pady=5)
        
        ctk.CTkLabel(parent, text="Baud Rate:", font=ctk.CTkFont(size=14)).grid(
            row=start_row+2, column=0, sticky="w", padx=(20, 10), pady=5
        )
        
        self.baudrate_var = ctk.StringVar()
        self.baudrate_dropdown = ctk.CTkComboBox(
            parent,
            variable=self.baudrate_var,
            values=["9600", "19200", "38400", "57600", "115200"],
            width=300,
            height=40,
            font=ctk.CTkFont(size=14)
        )
        self.baudrate_dropdown.grid(row=start_row+2, column=1, sticky="w", pady=5)
        
        ctk.CTkLabel(parent, text="Timeout (s):", font=ctk.CTkFont(size=14)).grid(
            row=start_row+3, column=0, sticky="w", padx=(20, 10), pady=5
        )
        
        self.timeout_entry = ctk.CTkEntry(
            parent,
            width=300,
            height=40,
            font=ctk.CTkFont(size=14)
        )
        self.timeout_entry.grid(row=start_row+3, column=1, sticky="w", pady=5)
    
    def setup_calibration_section(self, parent, start_row):
        section_label = ctk.CTkLabel(
            parent,
            text="Mass Sensor Calibration - Zone 1",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        section_label.grid(row=start_row, column=0, columnspan=2, sticky="w", pady=(20, 10))
        
        ctk.CTkLabel(parent, text="Offset (raw value):", font=ctk.CTkFont(size=14)).grid(
            row=start_row+1, column=0, sticky="w", padx=(20, 10), pady=5
        )
        
        self.offset_entry = ctk.CTkEntry(
            parent,
            width=200,
            height=40,
            font=ctk.CTkFont(size=14)
        )
        self.offset_entry.grid(row=start_row+1, column=1, sticky="w", pady=5)
        
        ctk.CTkLabel(parent, text="Scale Factor:", font=ctk.CTkFont(size=14)).grid(
            row=start_row+2, column=0, sticky="w", padx=(20, 10), pady=5
        )
        
        self.scale_entry = ctk.CTkEntry(
            parent,
            width=200,
            height=40,
            font=ctk.CTkFont(size=14)
        )
        self.scale_entry.grid(row=start_row+2, column=1, sticky="w", pady=5)
        
        ctk.CTkLabel(parent, text="Tare (grams):", font=ctk.CTkFont(size=14)).grid(
            row=start_row+3, column=0, sticky="w", padx=(20, 10), pady=5
        )
        
        self.tare_entry = ctk.CTkEntry(
            parent,
            width=200,
            height=40,
            font=ctk.CTkFont(size=14)
        )
        self.tare_entry.grid(row=start_row+3, column=1, sticky="w", pady=5)
        
        info_label = ctk.CTkLabel(
            parent,
            text="Formula: actual_mass = (raw_value - offset) × scale_factor - tare",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        info_label.grid(row=start_row+4, column=0, columnspan=2, pady=10)
    
    def setup_button_section(self, parent, start_row):
        button_frame = ctk.CTkFrame(parent)
        button_frame.grid(row=start_row, column=0, columnspan=2, pady=30, sticky="ew")
        button_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        save_button = ctk.CTkButton(
            button_frame,
            text="Save Settings",
            height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            command=self.save_settings
        )
        save_button.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        test_button = ctk.CTkButton(
            button_frame,
            text="Test Connection",
            height=50,
            font=ctk.CTkFont(size=16),
            command=self.test_connection
        )
        test_button.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        
        cancel_button = ctk.CTkButton(
            button_frame,
            text="Cancel",
            height=50,
            font=ctk.CTkFont(size=16),
            fg_color="gray",
            command=self.window.destroy
        )
        cancel_button.grid(row=0, column=2, padx=10, pady=10, sticky="ew")
        
        self.status_label = ctk.CTkLabel(
            parent,
            text="",
            font=ctk.CTkFont(size=14)
        )
        self.status_label.grid(row=start_row+1, column=0, columnspan=2, pady=10)
    
    def get_available_ports(self):
        ports = serial.tools.list_ports.comports()
        return [port.device for port in ports] if ports else ["No ports found"]
    
    def refresh_ports(self):
        available_ports = self.get_available_ports()
        self.port_dropdown.configure(values=available_ports)
        if available_ports and available_ports[0] != "No ports found":
            self.port_dropdown.set(available_ports[0])
    
    def load_current_settings(self):
        serial_config = self.settings.config["serial"]
        self.port_var.set(serial_config.get("port", ""))
        self.baudrate_var.set(str(serial_config.get("baudrate", 115200)))
        self.timeout_entry.insert(0, str(serial_config.get("timeout", 1.0)))
        
        cal_config = self.settings.get_mass_calibration(1)
        self.offset_entry.insert(0, str(cal_config.get("mass_offset", 0)))
        self.scale_entry.insert(0, str(cal_config.get("mass_scale", 1.0)))
        self.tare_entry.insert(0, str(cal_config.get("tare", 0.0)))
    
    def save_settings(self):
        try:
            self.settings.config["serial"]["port"] = self.port_var.get()
            self.settings.config["serial"]["baudrate"] = int(self.baudrate_var.get())
            self.settings.config["serial"]["timeout"] = float(self.timeout_entry.get())
            
            offset = float(self.offset_entry.get())
            scale = float(self.scale_entry.get())
            tare = float(self.tare_entry.get())
            
            self.settings.update_mass_calibration(1, offset=offset, scale=scale, tare=tare)
            
            self.status_label.configure(text="Settings saved successfully!", text_color="green")
            
            if self.on_settings_changed:
                self.on_settings_changed()
                
            self.window.after(2000, self.window.destroy)
            
        except ValueError as e:
            self.status_label.configure(text=f"Error: Invalid number format", text_color="red")
        except Exception as e:
            self.status_label.configure(text=f"Error: {str(e)}", text_color="red")
    
    def test_connection(self):
        try:
            import serial
            port = self.port_var.get()
            baudrate = int(self.baudrate_var.get())
            timeout = float(self.timeout_entry.get())
            
            if not port or port == "No ports found":
                self.status_label.configure(text="Please select a valid port", text_color="red")
                return
            
            test_conn = serial.Serial(port=port, baudrate=baudrate, timeout=timeout)
            test_conn.close()
            
            self.status_label.configure(text="Connection test successful!", text_color="green")
            
        except serial.SerialException as e:
            self.status_label.configure(text=f"Connection failed: {str(e)}", text_color="red")
        except ValueError:
            self.status_label.configure(text="Invalid baudrate or timeout value", text_color="red")
        except Exception as e:
            self.status_label.configure(text=f"Test error: {str(e)}", text_color="red")