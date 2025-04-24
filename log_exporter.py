import psutil
import time

class LogExporter:
    def __init__(self, controller, mqtt_client):
        self.controller = controller
        self.mqtt_client = mqtt_client
        self.sensor_status = "No sensor selected"
        self.sensor_type = "Unknown"

    def update_sensor_status(self, sensor, last_reading):
        if sensor:
            self.sensor_type = sensor.sensor_type
            value = last_reading 

            if value and isinstance(value, (list, int)) and (
                (isinstance(value, list) and len(value) > 2 and 0 < value[2] < 1024)
                or (isinstance(value, int) and value > 0)
            ):
                self.sensor_status = "working"
            else:
                self.sensor_status = "error"
        else:
            self.sensor_status = "No sensor selected"
            self.sensor_type = "Unknown"

    def export_log(self):
        data = {
            "cpu_usage": psutil.cpu_percent(),
            "sensor_status": self.sensor_status,
            "sensor_type": self.sensor_type,
            "gas_power_in": self.controller.read_gas_power_in(),
            "gas_fault": self.controller.read_gas_efuse(),
            "badge_fault": self.controller.read_badge_efuse(),
            "alarm_fault": self.controller.read_alarm_efuse(),
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
        }
        self.mqtt_client.publish_data(data)
        print(f"Published Data: {data}")  