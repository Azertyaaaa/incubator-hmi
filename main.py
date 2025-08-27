import customtkinter as ctk
import threading
import time
from typing import Dict, Any
from config.settings import Settings
from core.serial_handler import SerialHandler
from core.data_manager import DataManager
from ui.overview_page import OverviewPage
from ui.zone_detail_page import ZoneDetailPage
from ui.settings_window import SettingsWindow

class ClimateHMI:
    def __init__(self):
        self.settings = Settings()
        self.data_manager = DataManager(self.settings)
        self.serial_handlers = {}
        self.current_data = {}
        self.auto_reconnect = True
        self.reconnect_attempts = {}
        self.max_reconnect_attempts = 5
        
        for zone_id in range(1, 5):
            self.reconnect_attempts[zone_id] = 0
        
        self.setup_ui()
        self.setup_serial_connections()
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
        main_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)
        
        self.tabview = ctk.CTkTabview(main_frame, height=ui_config["height"]-100)
        self.tabview.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        self.overview_tab = self.tabview.add("Overview")
        self.zone1_tab = self.tabview.add("Zone 1")
        self.zone2_tab = self.tabview.add("Zone 2")
        self.zone3_tab = self.tabview.add("Zone 3")
        self.zone4_tab = self.tabview.add("Zone 4")
        self.settings_tab = self.tabview.add("Settings")
        
        self.setup_overview_page()
        self.setup_zone_pages()
        self.setup_settings_page()
        
        bottom_frame = ctk.CTkFrame(main_frame)
        bottom_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        bottom_frame.grid_columnconfigure((0, 1), weight=1)
        
        self.connection_status_label = ctk.CTkLabel(
            bottom_frame,
            text="Connections: Initializing...",
            font=ctk.CTkFont(size=14)
        )
        self.connection_status_label.grid(row=0, column=0, padx=10, pady=10)
        
        self.exit_button = ctk.CTkButton(
            bottom_frame,
            text="Exit Application",
            height=50,
            fg_color="red",
            command=self.on_exit
        )
        self.exit_button.grid(row=0, column=1, padx=10, pady=10)
    
    def setup_overview_page(self):
        self.overview_page = OverviewPage(self.overview_tab)
        self.overview_page.pack(fill="both", expand=True, padx=10, pady=10)
    
    def setup_zone_pages(self):
        self.zone_pages = {}
        tabs = [self.zone1_tab, self.zone2_tab, self.zone3_tab, self.zone4_tab]
        
        for i, tab in enumerate(tabs):
            zone_id = i + 1
            zone_page = ZoneDetailPage(tab, zone_id=zone_id)
            zone_page.pack(fill="both", expand=True, padx=10, pady=10)
            zone_page.set_callbacks(
                tare_callback=lambda zid=zone_id: self.on_tare(zid),
                zero_callback=lambda zid=zone_id: self.on_zero(zid)
            )
            zone_page.set_data_manager(self.data_manager)
            self.zone_pages[zone_id] = zone_page
    
    def setup_settings_page(self):
        settings_frame = ctk.CTkScrollableFrame(self.settings_tab)
        settings_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        title_label = ctk.CTkLabel(
            settings_frame,
            text="Climate Chamber Settings",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=20)
        
        self.setup_serial_settings(settings_frame)
        self.setup_calibration_settings(settings_frame)
        
    def setup_serial_settings(self, parent):
        serial_frame = ctk.CTkFrame(parent)
        serial_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            serial_frame,
            text="Serial Port Configuration",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=10)
        
        self.port_vars = {}
        self.port_dropdowns = {}
        
        import serial.tools.list_ports
        available_ports = [port.device for port in serial.tools.list_ports.comports()]
        if not available_ports:
            available_ports = ["No ports found"]
        
        for zone_id in range(1, 5):
            zone_frame = ctk.CTkFrame(serial_frame)
            zone_frame.pack(fill="x", padx=10, pady=5)
            
            ctk.CTkLabel(
                zone_frame,
                text=f"Zone {zone_id} Port:",
                font=ctk.CTkFont(size=14)
            ).pack(side="left", padx=10, pady=10)
            
            self.port_vars[zone_id] = ctk.StringVar(
                value=self.settings.get_serial_port(zone_id)
            )
            
            self.port_dropdowns[zone_id] = ctk.CTkComboBox(
                zone_frame,
                variable=self.port_vars[zone_id],
                values=available_ports,
                width=200
            )
            self.port_dropdowns[zone_id].pack(side="left", padx=10, pady=10)
            
        button_frame = ctk.CTkFrame(serial_frame)
        button_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkButton(
            button_frame,
            text="Apply Serial Settings",
            height=40,
            command=self.apply_serial_settings
        ).pack(side="left", padx=10, pady=10)
        
        ctk.CTkButton(
            button_frame,
            text="Refresh Ports",
            height=40,
            command=self.refresh_serial_ports
        ).pack(side="left", padx=10, pady=10)
    
    def setup_calibration_settings(self, parent):
        cal_frame = ctk.CTkFrame(parent)
        cal_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            cal_frame,
            text="Mass Calibration Settings",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=10)
        
        self.cal_entries = {}
        
        for zone_id in range(1, 5):
            zone_cal_frame = ctk.CTkFrame(cal_frame)
            zone_cal_frame.pack(fill="x", padx=10, pady=5)
            
            ctk.CTkLabel(
                zone_cal_frame,
                text=f"Zone {zone_id}:",
                font=ctk.CTkFont(size=14, weight="bold")
            ).pack(anchor="w", padx=10, pady=5)
            
            cal_config = self.settings.get_mass_calibration(zone_id)
            
            fields_frame = ctk.CTkFrame(zone_cal_frame)
            fields_frame.pack(fill="x", padx=10, pady=5)
            fields_frame.grid_columnconfigure((1, 3, 5), weight=1)
            
            ctk.CTkLabel(fields_frame, text="Offset:").grid(row=0, column=0, padx=5, pady=5)
            offset_entry = ctk.CTkEntry(fields_frame, width=100)
            offset_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
            offset_entry.insert(0, str(cal_config.get("mass_offset", 0)))
            
            ctk.CTkLabel(fields_frame, text="Scale:").grid(row=0, column=2, padx=5, pady=5)
            scale_entry = ctk.CTkEntry(fields_frame, width=100)
            scale_entry.grid(row=0, column=3, padx=5, pady=5, sticky="ew")
            scale_entry.insert(0, str(cal_config.get("mass_scale", 1.0)))
            
            ctk.CTkLabel(fields_frame, text="Tare:").grid(row=0, column=4, padx=5, pady=5)
            tare_entry = ctk.CTkEntry(fields_frame, width=100)
            tare_entry.grid(row=0, column=5, padx=5, pady=5, sticky="ew")
            tare_entry.insert(0, str(cal_config.get("tare", 0.0)))
            
            self.cal_entries[zone_id] = {
                "offset": offset_entry,
                "scale": scale_entry,
                "tare": tare_entry
            }
        
        ctk.CTkButton(
            cal_frame,
            text="Apply Calibration Settings",
            height=40,
            command=self.apply_calibration_settings
        ).pack(pady=10)
    
    def setup_serial_connections(self):
        for zone_id in range(1, 5):
            port = self.settings.get_serial_port(zone_id)
            serial_config = self.settings.config["serial"]
            
            handler = SerialHandler(
                port=port,
                baudrate=serial_config["baudrate"],
                timeout=serial_config["timeout"]
            )
            
            handler.set_callbacks(
                data_callback=lambda data, zid=zone_id: self.on_data_received(data, zid),
                error_callback=lambda msg, zid=zone_id: self.on_serial_error(msg, zid)
            )
            
            self.serial_handlers[zone_id] = handler
            
            if handler.start_reading():
                print(f"Zone {zone_id} connected on {port}")
            else:
                print(f"Zone {zone_id} failed to connect on {port}")
        
        self.update_connection_status()
    
    def on_data_received(self, raw_data: Dict[str, Any], zone_id: int):
        processed_data = self.data_manager.process_sensor_data(raw_data)
        self.current_data[zone_id] = processed_data
        
        self.root.after(0, lambda: self.overview_page.update_zone_data(zone_id, processed_data))
        self.root.after(0, lambda: self.zone_pages[zone_id].update_data(processed_data))
        
        self.data_manager.log_data(processed_data)
    
    def on_serial_error(self, error_msg: str, zone_id: int):
        print(f"Zone {zone_id} serial error: {error_msg}")
        
        self.root.after(0, lambda: self.overview_page.set_zone_connection_status(zone_id, False))
        self.root.after(0, lambda: self.zone_pages[zone_id].set_connection_status(False))
        
        if "connection lost" in error_msg.lower() or "clearcommerror" in error_msg.lower():
            self.reconnect_attempts[zone_id] = 0
    
    def on_tare(self, zone_id: int):
        if zone_id in self.current_data and "calibrated_mass" in self.current_data[zone_id]:
            current_mass = self.current_data[zone_id]["calibrated_mass"]
            self.data_manager.tare_mass(zone_id, current_mass)
            print(f"Tared zone {zone_id} at {current_mass:.2f}g")
    
    def on_zero(self, zone_id: int):
        if zone_id in self.current_data and "mass" in self.current_data[zone_id]:
            raw_mass = self.current_data[zone_id]["mass"]
            self.data_manager.zero_mass(zone_id, raw_mass)
            print(f"Zeroed zone {zone_id} at raw value {raw_mass}")
    
    def start_equilibrium_check(self):
        def check_equilibrium():
            while True:
                try:
                    for zone_id in range(1, 5):
                        is_equilibrated = self.data_manager.is_mass_equilibrated(zone_id)
                        self.root.after(0, lambda zid=zone_id, eq=is_equilibrated: 
                                       self.overview_page.update_zone_equilibrium(zid, eq))
                        self.root.after(0, lambda zid=zone_id, eq=is_equilibrated: 
                                       self.zone_pages[zid].update_equilibrium_status(eq))
                    time.sleep(30)
                except Exception as e:
                    print(f"Equilibrium check error: {e}")
                    time.sleep(30)
        
        eq_thread = threading.Thread(target=check_equilibrium, daemon=True)
        eq_thread.start()
    
    def start_auto_reconnect(self):
        def auto_reconnect_loop():
            while self.auto_reconnect:
                try:
                    for zone_id in range(1, 5):
                        handler = self.serial_handlers.get(zone_id)
                        if (handler and 
                            handler.get_connection_status() == "Disconnected" and
                            self.reconnect_attempts[zone_id] < self.max_reconnect_attempts):
                            
                            self.reconnect_attempts[zone_id] += 1
                            print(f"Zone {zone_id} auto-reconnect attempt {self.reconnect_attempts[zone_id]}")
                            
                            handler.disconnect()
                            time.sleep(2)
                            
                            if handler.start_reading():
                                self.reconnect_attempts[zone_id] = 0
                                print(f"Zone {zone_id} auto-reconnect successful")
                                
                                self.root.after(0, lambda zid=zone_id: 
                                               self.overview_page.set_zone_connection_status(zid, True))
                                self.root.after(0, lambda zid=zone_id: 
                                               self.zone_pages[zid].set_connection_status(True))
                    
                    self.update_connection_status()
                    time.sleep(5)
                    
                except Exception as e:
                    print(f"Auto-reconnect error: {e}")
                    time.sleep(10)
        
        reconnect_thread = threading.Thread(target=auto_reconnect_loop, daemon=True)
        reconnect_thread.start()
    
    def update_connection_status(self):
        connected_zones = []
        for zone_id in range(1, 5):
            handler = self.serial_handlers.get(zone_id)
            if handler and handler.get_connection_status() == "Connected":
                connected_zones.append(str(zone_id))
        
        if connected_zones:
            status = f"Connected Zones: {', '.join(connected_zones)}"
            color = "green"
        else:
            status = "No zones connected"
            color = "red"
            
        self.root.after(0, lambda: self.connection_status_label.configure(
            text=status, text_color=color
        ))
    
    def apply_serial_settings(self):
        for zone_id in range(1, 5):
            port = self.port_vars[zone_id].get()
            if port and port != "No ports found":
                self.settings.update_serial_port(zone_id, port)
        
        for zone_id in range(1, 5):
            if zone_id in self.serial_handlers:
                self.serial_handlers[zone_id].disconnect()
        
        self.setup_serial_connections()
        print("Serial settings applied and connections restarted")
    
    def apply_calibration_settings(self):
        try:
            for zone_id in range(1, 5):
                entries = self.cal_entries[zone_id]
                offset = float(entries["offset"].get())
                scale = float(entries["scale"].get())
                tare = float(entries["tare"].get())
                
                self.settings.update_mass_calibration(zone_id, offset=offset, scale=scale, tare=tare)
            
            print("Calibration settings applied successfully")
            
        except ValueError as e:
            print(f"Error applying calibration settings: Invalid number format")
        except Exception as e:
            print(f"Error applying calibration settings: {e}")
    
    def refresh_serial_ports(self):
        import serial.tools.list_ports
        available_ports = [port.device for port in serial.tools.list_ports.comports()]
        if not available_ports:
            available_ports = ["No ports found"]
        
        for zone_id in range(1, 5):
            self.port_dropdowns[zone_id].configure(values=available_ports)
    
    def on_exit(self):
        self.auto_reconnect = False
        for handler in self.serial_handlers.values():
            handler.disconnect()
        self.root.quit()
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = ClimateHMI()
    app.run()