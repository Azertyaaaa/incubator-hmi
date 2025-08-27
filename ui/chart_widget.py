import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any
import numpy as np

class ChartWidget(ctk.CTkFrame):
    def __init__(self, parent, zone_id: int, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.zone_id = zone_id
        self.data_manager = None
        
        self.setup_ui()
        self.setup_chart()
        
    def setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        control_frame = ctk.CTkFrame(self)
        control_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        control_frame.grid_columnconfigure(4, weight=1)
        
        ctk.CTkLabel(control_frame, text="Show:", font=ctk.CTkFont(size=14)).grid(
            row=0, column=0, padx=10, pady=10
        )
        
        self.temp_var = ctk.BooleanVar(value=True)
        self.temp_check = ctk.CTkCheckBox(
            control_frame,
            text="Temperature",
            variable=self.temp_var,
            command=self.update_chart,
            font=ctk.CTkFont(size=12)
        )
        self.temp_check.grid(row=0, column=1, padx=10, pady=10)
        
        self.hum_var = ctk.BooleanVar(value=True)
        self.hum_check = ctk.CTkCheckBox(
            control_frame,
            text="Humidity",
            variable=self.hum_var,
            command=self.update_chart,
            font=ctk.CTkFont(size=12)
        )
        self.hum_check.grid(row=0, column=2, padx=10, pady=10)
        
        self.mass_var = ctk.BooleanVar(value=True)
        self.mass_check = ctk.CTkCheckBox(
            control_frame,
            text="Mass",
            variable=self.mass_var,
            command=self.update_chart,
            font=ctk.CTkFont(size=12)
        )
        self.mass_check.grid(row=0, column=3, padx=10, pady=10)
        
        ctk.CTkLabel(control_frame, text="Time:", font=ctk.CTkFont(size=14)).grid(
            row=0, column=5, padx=(20, 10), pady=10
        )
        
        self.time_var = ctk.StringVar(value="1 Hour")
        self.time_dropdown = ctk.CTkComboBox(
            control_frame,
            variable=self.time_var,
            values=["30 Minutes", "1 Hour", "6 Hours", "12 Hours", "24 Hours"],
            command=self.on_time_change,
            width=120
        )
        self.time_dropdown.grid(row=0, column=6, padx=10, pady=10)
        
        refresh_button = ctk.CTkButton(
            control_frame,
            text="Refresh",
            width=80,
            height=32,
            command=self.update_chart
        )
        refresh_button.grid(row=0, column=7, padx=10, pady=10)
        
        self.chart_frame = ctk.CTkFrame(self)
        self.chart_frame.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")
        
    def setup_chart(self):
        plt.style.use('default')
        self.figure = Figure(figsize=(12, 6), dpi=80)
        self.figure.patch.set_facecolor('#212121')
        
        self.ax1 = self.figure.add_subplot(111)
        self.ax1.set_facecolor('#2b2b2b')
        self.ax1.tick_params(colors='white')
        self.ax1.spines['bottom'].set_color('white')
        self.ax1.spines['top'].set_color('white')
        self.ax1.spines['right'].set_color('white')
        self.ax1.spines['left'].set_color('white')
        
        self.ax2 = self.ax1.twinx()
        self.ax2.tick_params(colors='white')
        
        self.canvas = FigureCanvasTkAgg(self.figure, self.chart_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)
        
        self.ax1.set_xlabel('Time', color='white')
        self.ax1.set_ylabel('Temperature (°C) / Humidity (%)', color='white')
        self.ax2.set_ylabel('Mass (g)', color='white')
        
        self.ax1.grid(True, alpha=0.3, color='gray')
        self.figure.tight_layout()
        
    def set_data_manager(self, data_manager):
        self.data_manager = data_manager
        self.update_chart()
        
    def get_time_hours(self):
        time_map = {
            "30 Minutes": 0.5,
            "1 Hour": 1,
            "6 Hours": 6,
            "12 Hours": 12,
            "24 Hours": 24
        }
        return time_map.get(self.time_var.get(), 1)
        
    def on_time_change(self, value):
        self.update_chart()
        
    def update_chart(self):
        if not self.data_manager:
            return
            
        hours = self.get_time_hours()
        data = self.data_manager.get_recent_data(self.zone_id, hours)
        
        if not data:
            self.ax1.clear()
            self.ax2.clear()
            self.ax1.text(0.5, 0.5, 'No data available', 
                         horizontalalignment='center', verticalalignment='center',
                         transform=self.ax1.transAxes, color='white', fontsize=14)
            self.setup_chart_style()
            self.canvas.draw()
            return
            
        df = pd.DataFrame(data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['temp'] = pd.to_numeric(df['temp'], errors='coerce')
        df['hum'] = pd.to_numeric(df['hum'], errors='coerce')
        df['calibrated_mass'] = pd.to_numeric(df['calibrated_mass'], errors='coerce')
        
        df = df.dropna()
        
        if df.empty:
            self.ax1.clear()
            self.ax2.clear()
            self.ax1.text(0.5, 0.5, 'No valid data', 
                         horizontalalignment='center', verticalalignment='center',
                         transform=self.ax1.transAxes, color='white', fontsize=14)
            self.setup_chart_style()
            self.canvas.draw()
            return
            
        self.ax1.clear()
        self.ax2.clear()
        
        lines = []
        labels = []
        
        if self.temp_var.get():
            line1 = self.ax1.plot(df['timestamp'], df['temp'], 
                                 color='red', linewidth=2, label='Temperature (°C)')
            lines.extend(line1)
            labels.append('Temperature (°C)')
            
        if self.hum_var.get():
            line2 = self.ax1.plot(df['timestamp'], df['hum'], 
                                 color='blue', linewidth=2, label='Humidity (%)')
            lines.extend(line2)
            labels.append('Humidity (%)')
            
        if self.mass_var.get():
            line3 = self.ax2.plot(df['timestamp'], df['calibrated_mass'], 
                                 color='green', linewidth=2, label='Mass (g)')
            lines.extend(line3)
            labels.append('Mass (g)')
            
        self.setup_chart_style()
        
        if lines:
            self.ax1.legend(lines, labels, loc='upper left', 
                           facecolor='#2b2b2b', edgecolor='white', 
                           labelcolor='white')
        
        self.figure.tight_layout()
        self.canvas.draw()
        
    def setup_chart_style(self):
        self.ax1.set_facecolor('#2b2b2b')
        self.ax1.tick_params(colors='white')
        self.ax1.spines['bottom'].set_color('white')
        self.ax1.spines['top'].set_color('white')
        self.ax1.spines['right'].set_color('white')
        self.ax1.spines['left'].set_color('white')
        self.ax1.set_xlabel('Time', color='white')
        self.ax1.set_ylabel('Temperature (°C) / Humidity (%)', color='white')
        
        self.ax2.tick_params(colors='white')
        self.ax2.spines['bottom'].set_color('white')
        self.ax2.spines['top'].set_color('white') 
        self.ax2.spines['right'].set_color('white')
        self.ax2.spines['left'].set_color('white')
        self.ax2.set_ylabel('Mass (g)', color='white')
        
        self.ax1.grid(True, alpha=0.3, color='gray')
        
        import matplotlib.dates as mdates
        self.ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        self.ax1.xaxis.set_major_locator(mdates.HourLocator(interval=1))
        
        for label in self.ax1.get_xticklabels():
            label.set_rotation(45)
            
    def refresh_data(self):
        self.update_chart()