import json
import csv
import os
from datetime import datetime
from typing import Dict, Any, List
from config.settings import Settings

class DataManager:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.data_dir = "data/logs"
        self.ensure_data_directory()
        
    def ensure_data_directory(self):
        os.makedirs(self.data_dir, exist_ok=True)
    
    def calibrate_mass(self, raw_mass: float, zone: int) -> float:
        cal = self.settings.get_mass_calibration(zone)
        offset = cal.get("mass_offset", 0)
        scale = cal.get("mass_scale", 1.0)
        tare = cal.get("tare", 0.0)
        
        actual_mass = (raw_mass - offset) * scale - tare
        return max(0.0, actual_mass)
    
    def process_sensor_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        processed_data = raw_data.copy()
        processed_data["timestamp"] = datetime.now().isoformat()
        
        zone = raw_data.get("zone", 1)
        raw_mass = raw_data.get("mass", 0)
        processed_data["calibrated_mass"] = self.calibrate_mass(raw_mass, zone)
        
        return processed_data
    
    def log_data(self, data: Dict[str, Any]):
        date_str = datetime.now().strftime("%Y%m%d")
        log_file = os.path.join(self.data_dir, f"zone_{data['zone']}_{date_str}.csv")
        
        file_exists = os.path.exists(log_file)
        
        with open(log_file, 'a', newline='') as csvfile:
            fieldnames = ['timestamp', 'zone', 'temp', 'hum', 'mass', 'calibrated_mass']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            if not file_exists:
                writer.writeheader()
            
            writer.writerow(data)
    
    def get_recent_data(self, zone: int, hours: int = 1) -> List[Dict[str, Any]]:
        date_str = datetime.now().strftime("%Y%m%d")
        log_file = os.path.join(self.data_dir, f"zone_{zone}_{date_str}.csv")
        
        if not os.path.exists(log_file):
            return []
        
        recent_data = []
        cutoff_time = datetime.now().timestamp() - (hours * 3600)
        
        try:
            with open(log_file, 'r') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    timestamp = datetime.fromisoformat(row['timestamp']).timestamp()
                    if timestamp >= cutoff_time:
                        recent_data.append(row)
        except Exception as e:
            print(f"Error reading recent data: {e}")
        
        return recent_data
    
    def is_mass_equilibrated(self, zone: int, stability_threshold: float = 0.1, 
                           check_duration_minutes: int = 30) -> bool:
        recent_data = self.get_recent_data(zone, hours=1)
        
        if len(recent_data) < 3:
            return False
        
        cutoff_time = datetime.now().timestamp() - (check_duration_minutes * 60)
        stable_readings = []
        
        for reading in recent_data:
            timestamp = datetime.fromisoformat(reading['timestamp']).timestamp()
            if timestamp >= cutoff_time:
                try:
                    mass = float(reading['calibrated_mass'])
                    stable_readings.append(mass)
                except ValueError:
                    continue
        
        if len(stable_readings) < 3:
            return False
        
        mass_range = max(stable_readings) - min(stable_readings)
        return mass_range <= stability_threshold
    
    def tare_mass(self, zone: int, current_mass: float):
        self.settings.update_mass_calibration(zone, tare=current_mass)
    
    def zero_mass(self, zone: int, raw_value: float):
        self.settings.update_mass_calibration(zone, offset=raw_value)