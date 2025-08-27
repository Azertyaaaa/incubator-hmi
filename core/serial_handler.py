import serial
import json
import threading
import time
from typing import Callable, Optional, Dict, Any

class SerialHandler:
    def __init__(self, port: str, baudrate: int = 115200, timeout: float = 1.0):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial_conn: Optional[serial.Serial] = None
        self.is_running = False
        self.thread: Optional[threading.Thread] = None
        self.data_callback: Optional[Callable] = None
        self.error_callback: Optional[Callable] = None
        
    def set_callbacks(self, data_callback: Callable = None, error_callback: Callable = None):
        self.data_callback = data_callback
        self.error_callback = error_callback
    
    def connect(self) -> bool:
        try:
            self.serial_conn = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout,
                write_timeout=2.0,
                inter_byte_timeout=None,
                xonxoff=False,
                rtscts=False,
                dsrdtr=False
            )
            time.sleep(0.1)
            self.serial_conn.reset_input_buffer()
            self.serial_conn.reset_output_buffer()
            return True
        except Exception as e:
            if self.error_callback:
                self.error_callback(f"Connection failed: {e}")
            return False
    
    def disconnect(self):
        self.stop_reading()
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()
    
    def start_reading(self):
        if not self.serial_conn or not self.serial_conn.is_open:
            if not self.connect():
                return False
        
        self.is_running = True
        self.thread = threading.Thread(target=self._read_loop, daemon=True)
        self.thread.start()
        return True
    
    def stop_reading(self):
        self.is_running = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=2.0)
    
    def _read_loop(self):
        buffer = ""
        consecutive_errors = 0
        max_consecutive_errors = 5
        
        while self.is_running and self.serial_conn and self.serial_conn.is_open:
            try:
                data = self.serial_conn.read(self.serial_conn.in_waiting or 1)
                if data:
                    try:
                        decoded_data = data.decode('utf-8')
                        buffer += decoded_data
                        
                        while '\n' in buffer:
                            line, buffer = buffer.split('\n', 1)
                            line = line.strip()
                            if line:
                                self._parse_json_data(line)
                        
                        consecutive_errors = 0
                        
                    except UnicodeDecodeError:
                        buffer = ""
                        continue
                        
                else:
                    time.sleep(0.05)
                    
            except serial.SerialException as e:
                consecutive_errors += 1
                if consecutive_errors >= max_consecutive_errors:
                    if self.error_callback:
                        self.error_callback(f"Serial connection lost: {e}")
                    break
                time.sleep(0.5)
                
            except Exception as e:
                consecutive_errors += 1
                if consecutive_errors >= max_consecutive_errors:
                    if self.error_callback:
                        self.error_callback(f"Read error: {e}")
                    break
                time.sleep(0.1)
    
    def _parse_json_data(self, line: str):
        try:
            data = json.loads(line)
            required_keys = ["zone", "temp", "hum", "mass"]
            if all(key in data for key in required_keys):
                if self.data_callback:
                    self.data_callback(data)
            else:
                if self.error_callback:
                    self.error_callback(f"Missing keys in data: {line}")
        except json.JSONDecodeError as e:
            if self.error_callback:
                self.error_callback(f"JSON parse error: {e}")
    
    def get_connection_status(self) -> str:
        if self.serial_conn and self.serial_conn.is_open and self.is_running:
            return "Connected"
        elif self.serial_conn and self.serial_conn.is_open:
            return "Connected (not reading)"
        else:
            return "Disconnected"