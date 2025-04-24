import minimalmodbus
import time

class GasSensor:
    def __init__(self, sensor_type):
        self.sensor_type = sensor_type
        self.instrument = None
        self.setup_sensor()

    def setup_sensor(self):
        if self.sensor_type == "Blackline EXO":
            self.instrument = minimalmodbus.Instrument('/dev/ttyS1', 1)  
            self.instrument.serial.baudrate = 115200
            self.instrument.serial.bytesize = 8
            self.instrument.serial.parity = 'N'
            self.instrument.serial.stopbits = 1
            self.instrument.serial.timeout = 2
        elif self.sensor_type == "Drager X-Zone":
            self.instrument = minimalmodbus.Instrument('/dev/ttyS1', 2)  
            self.instrument.serial.baudrate = 115200
            self.instrument.serial.bytesize = 8
            self.instrument.serial.parity = 'E'
            self.instrument.serial.stopbits = 1
            self.instrument.serial.timeout = 2

    def read_sensor(self):
        try:
            if self.sensor_type == "Blackline EXO":
                value = self.instrument.read_registers(0, 100, 4)  
                return value if isinstance(value, list) and len(value) > 0 else None
            elif self.sensor_type == "Drager X-Zone":
                return self.instrument.read_long(29, 3)  
        except Exception:
            return None
    
    def read_sensor_data(self):
        return self.read_sensor()
