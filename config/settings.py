import json
import os

class Settings:
    def __init__(self):
        self.config_file = "config/hmi_config.json"
        self.default_config = {
            "serial": {
                "ports": {
                    "zone_1": "COM3",
                    "zone_2": "COM4", 
                    "zone_3": "COM5",
                    "zone_4": "COM6"
                },
                "baudrate": 115200,
                "timeout": 1.0
            },
            "calibration": {
                "zone_1": {
                    "mass_offset": 0,
                    "mass_scale": 1.0,
                    "tare": 0.0
                },
                "zone_2": {
                    "mass_offset": 0,
                    "mass_scale": 1.0,
                    "tare": 0.0
                },
                "zone_3": {
                    "mass_offset": 0,
                    "mass_scale": 1.0,
                    "tare": 0.0
                },
                "zone_4": {
                    "mass_offset": 0,
                    "mass_scale": 1.0,
                    "tare": 0.0
                }
            },
            "ui": {
                "fullscreen": True,
                "width": 1280,
                "height": 720,
                "touch_button_height": 80
            },
            "logging": {
                "interval_seconds": 10,
                "max_log_days": 30
            }
        }
        self.config = self.load_config()
    
    def load_config(self):
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
                # Ensure all 4 zones have calibration data
                for zone_id in range(1, 5):
                    zone_key = f"zone_{zone_id}"
                    if zone_key not in config.get("calibration", {}):
                        if "calibration" not in config:
                            config["calibration"] = {}
                        config["calibration"][zone_key] = {
                            "mass_offset": 0,
                            "mass_scale": 1.0,
                            "tare": 0.0
                        }
                return config
        except FileNotFoundError:
            self.save_config(self.default_config)
            return self.default_config
    
    def save_config(self, config=None):
        if config is None:
            config = self.config
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=4)
    
    def get_mass_calibration(self, zone):
        return self.config["calibration"].get(f"zone_{zone}", {
            "mass_offset": 0,
            "mass_scale": 1.0,
            "tare": 0.0
        })
    
    def update_mass_calibration(self, zone, offset=None, scale=None, tare=None):
        zone_key = f"zone_{zone}"
        if zone_key not in self.config["calibration"]:
            self.config["calibration"][zone_key] = {"mass_offset": 0, "mass_scale": 1.0, "tare": 0.0}
        
        if offset is not None:
            self.config["calibration"][zone_key]["mass_offset"] = offset
        if scale is not None:
            self.config["calibration"][zone_key]["mass_scale"] = scale
        if tare is not None:
            self.config["calibration"][zone_key]["tare"] = tare
        
        self.save_config()
    
    def get_serial_port(self, zone):
        zone_key = f"zone_{zone}"
        
        # Handle old config format (single port) vs new format (multiple ports)
        if "ports" in self.config["serial"]:
            return self.config["serial"]["ports"].get(zone_key, f"COM{zone+2}")
        else:
            # Old format - use the single port for zone 1, generate others
            if zone == 1 and "port" in self.config["serial"]:
                return self.config["serial"]["port"]
            else:
                return f"COM{zone+2}"
    
    def update_serial_port(self, zone, port):
        zone_key = f"zone_{zone}"
        if "ports" not in self.config["serial"]:
            # Migrate from old format to new format
            old_port = self.config["serial"].get("port", "COM3")
            self.config["serial"]["ports"] = {
                "zone_1": old_port,
                "zone_2": "COM4",
                "zone_3": "COM5", 
                "zone_4": "COM6"
            }
            # Remove old port key if it exists
            if "port" in self.config["serial"]:
                del self.config["serial"]["port"]
        
        self.config["serial"]["ports"][zone_key] = port
        self.save_config()