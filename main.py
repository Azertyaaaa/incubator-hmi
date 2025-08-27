import customtkinter as ctk
import threading
import time
from typing import Dict, Any
from config.settings import Settings
from core.serial_handler import SerialHandler
from core.data_manager import DataManager
from ui.zone_widget import ZoneWidget
from ui.settings_window import SettingsWindow

class ClimateHMI:
    def __init__(self):
        self.settings = Settings()
        self.data_manager = DataManager(self.settings)
        self.serial_handler = None
        self.current_data = {}
        self.auto_reconnect = True
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 5
        
        self.setup_ui()
        self.setup_serial()
        self.start_equilibrium_check()
        self.start_auto_reconnect()
        
    def setup_ui(self):
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        self.root = ctk.CTk()
        self.root.title("Climate Chamber HMI")
        
        ui_config = self.settings.config["ui"]
        if ui_config["fullscreen"]:
            self.root.attributes('-fullscreen', True)
        else:
            self.root.geometry(f"{ui_config['width']}x{ui_config['height']}")
        
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        
        main_frame = ctk.CTkFrame(self.root)
        main_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)
        
        self.zone_widget = ZoneWidget(main_frame, zone_id=1)
        self.zone_widget.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.zone_widget.set_callbacks(
            tare_callback=self.on_tare,
            zero_callback=self.on_zero
        )
        
        bottom_frame = ctk.CTkFrame(main_frame)
        bottom_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        bottom_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        self.connection_label = ctk.CTkLabel(
            bottom_frame,
            text="Connection: Disconnected",
            font=ctk.CTkFont(size=14)
        )
        self.connection_label.grid(row=0, column=0, padx=10, pady=10)
        
        self.reconnect_button = ctk.CTkButton(
            bottom_frame,
            text="Reconnect",
            height=50,
            command=self.reconnect_serial
        )
        self.reconnect_button.grid(row=0, column=1, padx=10, pady=10)
        
        self.settings_button = ctk.CTkButton(
            bottom_frame,
            text="Settings",
            height=50,
            command=self.open_settings
        )
        self.settings_button.grid(row=0, column=2, padx=10, pady=10)
        
        self.exit_button = ctk.CTkButton(
            bottom_frame,
            text="Exit",
            height=50,
            command=self.on_exit
        )
        self.exit_button.grid(row=0, column=3, padx=10, pady=10)
    
    def setup_serial(self):
        serial_config = self.settings.config["serial"]
        self.serial_handler = SerialHandler(
            port=serial_config["port"],
            baudrate=serial_config["baudrate"],
            timeout=serial_config["timeout"]
        )
        
        self.serial_handler.set_callbacks(
            data_callback=self.on_data_received,
            error_callback=self.on_serial_error
        )
        
        if self.serial_handler.start_reading():
            self.connection_label.configure(text="Connection: Connected", text_color="green")
            self.zone_widget.set_connection_status(True)
        else:
            self.connection_label.configure(text="Connection: Failed", text_color="red")
            self.zone_widget.set_connection_status(False)
    
    def on_data_received(self, raw_data: Dict[str, Any]):
        processed_data = self.data_manager.process_sensor_data(raw_data)
        self.current_data = processed_data
        
        self.root.after(0, lambda: self.zone_widget.update_data(processed_data))
        
        self.data_manager.log_data(processed_data)
    
    def on_serial_error(self, error_msg: str):
        print(f"Serial error: {error_msg}")
        self.root.after(0, lambda: self.connection_label.configure(
            text=f"Error: {error_msg[:30]}...", text_color="red"
        ))
        self.root.after(0, lambda: self.zone_widget.set_connection_status(False))
        
        if "connection lost" in error_msg.lower() or "clearcommerror" in error_msg.lower():
            self.reconnect_attempts = 0
    
    def on_tare(self, zone_id: int):
        if self.current_data and "calibrated_mass" in self.current_data:
            current_mass = self.current_data["calibrated_mass"]
            self.data_manager.tare_mass(zone_id, current_mass)
            print(f"Tared zone {zone_id} at {current_mass:.2f}g")
    
    def on_zero(self, zone_id: int):
        if self.current_data and "mass" in self.current_data:
            raw_mass = self.current_data["mass"]
            self.data_manager.zero_mass(zone_id, raw_mass)
            print(f"Zeroed zone {zone_id} at raw value {raw_mass}")
    
    def start_equilibrium_check(self):
        def check_equilibrium():
            while True:
                try:
                    is_equilibrated = self.data_manager.is_mass_equilibrated(1)
                    self.root.after(0, lambda: self.zone_widget.update_equilibrium_status(is_equilibrated))
                    time.sleep(30)
                except Exception as e:
                    print(f"Equilibrium check error: {e}")
                    time.sleep(30)
        
        eq_thread = threading.Thread(target=check_equilibrium, daemon=True)
        eq_thread.start()
    
    def reconnect_serial(self):
        if self.serial_handler:
            self.serial_handler.disconnect()
        
        self.setup_serial()
    
    def open_settings(self):
        SettingsWindow(self.root, self.settings, on_settings_changed=self.on_settings_changed)
    
    def on_settings_changed(self):
        self.settings = Settings()
        self.data_manager = DataManager(self.settings)
        self.reconnect_serial()
    
    def start_auto_reconnect(self):
        def auto_reconnect_loop():
            while self.auto_reconnect:
                try:
                    if (self.serial_handler and 
                        self.serial_handler.get_connection_status() == "Disconnected" and
                        self.reconnect_attempts < self.max_reconnect_attempts):
                        
                        self.reconnect_attempts += 1
                        print(f"Auto-reconnect attempt {self.reconnect_attempts}/{self.max_reconnect_attempts}")
                        
                        self.root.after(0, lambda: self.connection_label.configure(
                            text=f"Reconnecting... ({self.reconnect_attempts}/{self.max_reconnect_attempts})",
                            text_color="orange"
                        ))
                        
                        if self.serial_handler:
                            self.serial_handler.disconnect()
                        
                        time.sleep(2)
                        self.setup_serial()
                        
                        if self.serial_handler.get_connection_status() == "Connected":
                            self.reconnect_attempts = 0
                            print("Auto-reconnect successful")
                    
                    time.sleep(5)
                    
                except Exception as e:
                    print(f"Auto-reconnect error: {e}")
                    time.sleep(10)
        
        reconnect_thread = threading.Thread(target=auto_reconnect_loop, daemon=True)
        reconnect_thread.start()
    
    def on_exit(self):
        self.auto_reconnect = False
        if self.serial_handler:
            self.serial_handler.disconnect()
        self.root.quit()
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = ClimateHMI()
    app.run()