import customtkinter as ctk
from typing import Dict, Any, Callable

class ZoneCard(ctk.CTkFrame):
    def __init__(self, parent, zone_id: int, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.zone_id = zone_id
        self.setup_ui()
        
    def setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        
        title_label = ctk.CTkLabel(
            self,
            text=f"Zone {self.zone_id}",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.grid(row=0, column=0, pady=(10, 5), sticky="ew")
        
        values_frame = ctk.CTkFrame(self)
        values_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        values_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        self.temp_label = ctk.CTkLabel(
            values_frame,
            text="--°C",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.temp_label.grid(row=0, column=0, padx=5, pady=5)
        
        ctk.CTkLabel(
            values_frame,
            text="Temperature",
            font=ctk.CTkFont(size=10)
        ).grid(row=1, column=0, padx=5, pady=(0, 5))
        
        self.hum_label = ctk.CTkLabel(
            values_frame,
            text="--%",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.hum_label.grid(row=0, column=1, padx=5, pady=5)
        
        ctk.CTkLabel(
            values_frame,
            text="Humidity",
            font=ctk.CTkFont(size=10)
        ).grid(row=1, column=1, padx=5, pady=(0, 5))
        
        self.mass_label = ctk.CTkLabel(
            values_frame,
            text="--g",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.mass_label.grid(row=0, column=2, padx=5, pady=5)
        
        ctk.CTkLabel(
            values_frame,
            text="Mass",
            font=ctk.CTkFont(size=10)
        ).grid(row=1, column=2, padx=5, pady=(0, 5))
        
        self.status_label = ctk.CTkLabel(
            self,
            text="Status: Disconnected",
            font=ctk.CTkFont(size=12)
        )
        self.status_label.grid(row=2, column=0, pady=5)
        
        self.equilibrium_label = ctk.CTkLabel(
            self,
            text="Equilibrium: Unknown",
            font=ctk.CTkFont(size=12)
        )
        self.equilibrium_label.grid(row=3, column=0, pady=(0, 10))
        
    def update_data(self, data: Dict[str, Any]):
        temp = data.get("temp", 0)
        hum = data.get("hum", 0)
        mass = data.get("calibrated_mass", 0)
        
        self.temp_label.configure(text=f"{temp:.1f}°C")
        self.hum_label.configure(text=f"{hum:.1f}%")
        self.mass_label.configure(text=f"{mass:.2f}g")
        
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

class OverviewPage(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.zone_cards = {}
        self.setup_ui()
        
    def setup_ui(self):
        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure((0, 1), weight=1)
        
        title_frame = ctk.CTkFrame(self)
        title_frame.grid(row=0, column=0, columnspan=2, padx=20, pady=20, sticky="ew")
        
        title_label = ctk.CTkLabel(
            title_frame,
            text="Climate Chamber Overview",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title_label.pack(pady=20)
        
        for zone_id in range(1, 5):
            row = 1 + (zone_id - 1) // 2
            col = (zone_id - 1) % 2
            
            zone_card = ZoneCard(self, zone_id=zone_id)
            zone_card.grid(row=row, column=col, padx=20, pady=20, sticky="nsew")
            
            self.zone_cards[zone_id] = zone_card
            
    def update_zone_data(self, zone_id: int, data: Dict[str, Any]):
        if zone_id in self.zone_cards:
            self.zone_cards[zone_id].update_data(data)
            
    def update_zone_equilibrium(self, zone_id: int, is_equilibrated: bool):
        if zone_id in self.zone_cards:
            self.zone_cards[zone_id].update_equilibrium_status(is_equilibrated)
            
    def set_zone_connection_status(self, zone_id: int, connected: bool):
        if zone_id in self.zone_cards:
            self.zone_cards[zone_id].set_connection_status(connected)