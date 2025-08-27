import customtkinter as ctk
from typing import Dict, Any, Callable
from .zone_widget import ZoneWidget
from .chart_widget import ChartWidget

class ZoneDetailPage(ctk.CTkFrame):
    def __init__(self, parent, zone_id: int, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.zone_id = zone_id
        self.data_manager = None
        
        self.setup_ui()
        
    def setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        top_frame = ctk.CTkFrame(self)
        top_frame.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        top_frame.grid_columnconfigure(0, weight=1)
        
        self.zone_widget = ZoneWidget(top_frame, zone_id=self.zone_id)
        self.zone_widget.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        bottom_frame = ctk.CTkFrame(self)
        bottom_frame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")
        bottom_frame.grid_columnconfigure(0, weight=1)
        bottom_frame.grid_rowconfigure(0, weight=1)
        
        chart_title = ctk.CTkLabel(
            bottom_frame,
            text=f"Zone {self.zone_id} - Historical Data",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        chart_title.grid(row=0, column=0, pady=(10, 0))
        
        self.chart_widget = ChartWidget(bottom_frame, zone_id=self.zone_id)
        self.chart_widget.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        
    def set_callbacks(self, tare_callback: Callable = None, zero_callback: Callable = None):
        self.zone_widget.set_callbacks(tare_callback, zero_callback)
        
    def set_data_manager(self, data_manager):
        self.data_manager = data_manager
        self.chart_widget.set_data_manager(data_manager)
        
    def update_data(self, data: Dict[str, Any]):
        self.zone_widget.update_data(data)
        
    def update_equilibrium_status(self, is_equilibrated: bool):
        self.zone_widget.update_equilibrium_status(is_equilibrated)
        
    def set_connection_status(self, connected: bool):
        self.zone_widget.set_connection_status(connected)
        
    def refresh_chart(self):
        self.chart_widget.refresh_data()