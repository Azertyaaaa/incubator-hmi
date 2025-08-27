import customtkinter as ctk
from typing import Dict, Any, Callable

class ZoneWidget(ctk.CTkFrame):
    def __init__(self, parent, zone_id: int, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.zone_id = zone_id
        self.tare_callback: Callable = None
        self.zero_callback: Callable = None
        
        self.setup_ui()
        
    def setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(4, weight=1)
        
        title = ctk.CTkLabel(
            self, 
            text=f"Zone {self.zone_id}",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.grid(row=0, column=0, pady=10, sticky="ew")
        
        self.sensor_frame = ctk.CTkFrame(self)
        self.sensor_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        self.sensor_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        self.temp_label = ctk.CTkLabel(
            self.sensor_frame,
            text="Temperature\n--°C",
            font=ctk.CTkFont(size=18)
        )
        self.temp_label.grid(row=0, column=0, padx=10, pady=10)
        
        self.hum_label = ctk.CTkLabel(
            self.sensor_frame,
            text="Humidity\n--%",
            font=ctk.CTkFont(size=18)
        )
        self.hum_label.grid(row=0, column=1, padx=10, pady=10)
        
        self.mass_label = ctk.CTkLabel(
            self.sensor_frame,
            text="Mass\n--g",
            font=ctk.CTkFont(size=18)
        )
        self.mass_label.grid(row=0, column=2, padx=10, pady=10)
        
        self.status_frame = ctk.CTkFrame(self)
        self.status_frame.grid(row=2, column=0, padx=10, pady=5, sticky="ew")
        
        self.status_label = ctk.CTkLabel(
            self.status_frame,
            text="Status: Initializing...",
            font=ctk.CTkFont(size=16)
        )
        self.status_label.grid(row=0, column=0, padx=10, pady=10)
        
        self.equilibrium_label = ctk.CTkLabel(
            self.status_frame,
            text="Equilibrium: Unknown",
            font=ctk.CTkFont(size=16)
        )
        self.equilibrium_label.grid(row=1, column=0, padx=10, pady=5)
        
        self.button_frame = ctk.CTkFrame(self)
        self.button_frame.grid(row=3, column=0, padx=10, pady=10, sticky="ew")
        self.button_frame.grid_columnconfigure((0, 1), weight=1)
        
        self.tare_button = ctk.CTkButton(
            self.button_frame,
            text="Tare",
            height=60,
            font=ctk.CTkFont(size=16),
            command=self._on_tare
        )
        self.tare_button.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        self.zero_button = ctk.CTkButton(
            self.button_frame,
            text="Zero",
            height=60,
            font=ctk.CTkFont(size=16),
            command=self._on_zero
        )
        self.zero_button.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
    
    def set_callbacks(self, tare_callback: Callable = None, zero_callback: Callable = None):
        self.tare_callback = tare_callback
        self.zero_callback = zero_callback
    
    def update_data(self, data: Dict[str, Any]):
        temp = data.get("temp", 0)
        hum = data.get("hum", 0)
        mass = data.get("calibrated_mass", 0)
        
        self.temp_label.configure(text=f"Temperature\n{temp:.1f}°C")
        self.hum_label.configure(text=f"Humidity\n{hum:.1f}%")
        self.mass_label.configure(text=f"Mass\n{mass:.2f}g")
        
        self.status_label.configure(text="Status: Active", text_color="green")
    
    def update_equilibrium_status(self, is_equilibrated: bool):
        if is_equilibrated:
            self.equilibrium_label.configure(
                text="Equilibrium: ✓ Stable",
                text_color="green"
            )
        else:
            self.equilibrium_label.configure(
                text="Equilibrium: ⧗ Stabilizing",
                text_color="orange"
            )
    
    def set_connection_status(self, connected: bool):
        if connected:
            self.status_label.configure(text="Status: Connected", text_color="green")
        else:
            self.status_label.configure(text="Status: Disconnected", text_color="red")
    
    def _on_tare(self):
        if self.tare_callback:
            self.tare_callback(self.zone_id)
    
    def _on_zero(self):
        if self.zero_callback:
            self.zero_callback(self.zone_id)