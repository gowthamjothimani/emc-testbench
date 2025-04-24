from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
import minimalmodbus
import threading
import time
import psutil
from emc_board import EMC_Board
from card_reader import CardReader
from mqtt_client import MQTTClient
from gas_sensor import GasSensor
from log_exporter import LogExporter  
from sensor_reader import get_temp_hum

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize components
controller = EMC_Board()
card_reader = CardReader(socketio)
mqtt_client = MQTTClient(socketio)
fuse_check_running = True
log_exporter = LogExporter(controller, mqtt_client)

# ========== GAS SENSOR CONFIGURATION ==========
gas_test_running = False
selected_sensor = None 
last_sensor_reading = None

def gas_test():
    global gas_test_running, selected_sensor
    while gas_test_running:
        if selected_sensor:
            value = selected_sensor.read_sensor()
            last_sensor_reading = value
            log_exporter.update_sensor_status(selected_sensor, last_sensor_reading) 

            if value:
                if isinstance(value, list) and len(value) > 2 and 0 < value[2] < 1024:
                    socketio.emit('sensor_status', {'state': 'working', 'color': 'lightgreen'})
                elif isinstance(value, int) and value > 0:
                    socketio.emit('sensor_status', {'state': 'working', 'color': 'lightgreen'})
                else:
                    socketio.emit('sensor_status', {'state': 'error', 'color': 'lightcoral'})
            else:
                socketio.emit('sensor_status', {'state': 'error', 'color': 'lightcoral'})
        time.sleep(1)

def monitor_fuse_and_gas_n():
    global fuse_check_running
    while fuse_check_running:
        try:
            gas_fault = controller.read_gas_efuse()
            badge_fault = controller.read_badge_efuse()
            alarm_fault = controller.read_alarm_efuse()
            gas_in = controller.read_gas_power_in()

            socketio.emit('gas_fault', {'status': gas_fault, 'color': 'lightgreen'})
            socketio.emit('badge_fault', {'status': badge_fault, 'color': 'lightgreen'})
            socketio.emit('alarm_fault', {'status': alarm_fault, 'color': 'lightgreen'})
            socketio.emit('gas_in', {'status': gas_in, 'color': 'lightgreen'})
        except Exception as e:
            print(f"Error reading values: {e}")
        time.sleep(1)

def system_status():
    while True:
        cpu_usage = psutil.cpu_percent(interval=1)
        memory_info = psutil.virtual_memory()
        socketio.emit('update_status', {'cpu': cpu_usage, 'mem': memory_info.percent})
        time.sleep(1)

# ========== TEMP & HUM SENSOR DATA =========
@app.route('/read_sensors')
def read_sensors():
    return get_temp_hum()

# ========== FLASK ROUTES ==========
@app.route('/')
def index():
    return render_template('index.html')

# ========== SENSOR SELECTION ==========
@socketio.on('select_gas_sensor')
def select_gas_sensor(data):
    global selected_sensor
    sensor_type = data.get("sensor_type")

    if sensor_type and sensor_type in ["Blackline EXO", "Drager X-Zone"]:
        selected_sensor = GasSensor(sensor_type)
        print(f"Selected Gas Sensor: {sensor_type}")
        socketio.emit('sensor_selected', {"sensor": sensor_type, "message": f"Sensor {sensor_type} selected!"})
    else:
        selected_sensor = None
        socketio.emit('sensor_selected', {"sensor": None, "message": "No sensor selected!"})


# ========== START/STOP TESTS ==========
@socketio.on('start_all_tests')
def start_all_tests():
    global gas_test_running
    if not gas_test_running:
        gas_test_running = True
        threading.Thread(target=gas_test, daemon=True).start()

    card_reader.start_card_test()

@socketio.on('stop_all_tests')
def stop_all_tests():
    """Stops all active test threads."""
    global gas_test_running
    gas_test_running = False
    card_reader.stop_card_test()

# ========== EMC BOARD CONTROL ==========
@app.route('/control/efuse_gas_on')
def efuse_gas_on():
    controller.turn_on_efuse_gas()
    return 'Gas eFuse On'

@app.route('/control/efuse_gas_off')
def efuse_gas_off():
    controller.turn_off_efuse_gas()
    return 'Gas eFuse Off'

@app.route('/control/efuse_badge_on')
def efuse_badge_on():
    controller.turn_on_efuse_badge()
    return 'Badge eFuse On'

@app.route('/control/efuse_badge_off')
def efuse_badge_off():
    controller.turn_off_efuse_badge()
    return 'Badge eFuse Off'

@app.route('/control/efuse_alarm_on')
def efuse_alarm_on():
    controller.turn_on_efuse_alarm()
    return 'Alarm eFuse On'

@app.route('/control/efuse_alarm_off')
def efuse_alarm_off():
    controller.turn_off_efuse_alarm()
    return 'Alarm eFuse Off'

@app.route('/control/lamp_badge_on')
def lamp_badge_on():
    controller.turn_on_badge_lamp()
    return 'Badge Lamp On'

@app.route('/control/lamp_badge_off')
def lamp_badge_off():
    controller.turn_off_badge_lamp()
    return 'Badge Lamp Off'

@app.route('/control/lamp_alarm_red_on')
def lamp_alarm_red_on():
    controller.turn_on_alarm_red_lamp()
    return 'Alarm Red Lamp On'

@app.route('/control/lamp_alarm_red_off')
def lamp_alarm_red_off():
    controller.turn_off_alarm_red_lamp()
    return 'Alarm Red Lamp Off'

@app.route('/control/lamp_alarm_green_on')
def lamp_alarm_green_on():
    controller.turn_on_alarm_green_lamp()
    return 'Alarm Green Lamp On'

@app.route('/control/lamp_alarm_green_off')
def lamp_alarm_green_off():
    controller.turn_off_alarm_green_lamp()
    return 'Alarm Green Lamp Off'

@app.route('/control/alarm_sound_on')
def alarm_sound_on():
    controller.turn_on_alarm_sound()
    return 'Alarm Sound On'

@app.route('/control/alarm_sound_off')
def alarm_sound_off():
    controller.turn_off_alarm_sound()
    return 'Alarm Sound Off'

# ========== MQTT CONFIGURATION ==========
@app.route('/update_mqtt', methods=['POST'])
def update_mqtt():
    config = request.json
    mqtt_client.update_config(config)
    return jsonify({"message": "MQTT configuration updated!"})

# ========== MQTT PUBLISH ==========
@socketio.on('export_log')
def export_log():
    log_exporter.export_log()


# ========== BACKGROUND THREADS ==========
def start_monitoring():
    threading.Thread(target=monitor_fuse_and_gas_n, daemon=True).start()
    threading.Thread(target=system_status, daemon=True).start()

if __name__ == '__main__':
    start_monitoring()
    mqtt_client.connect_mqtt()
    socketio.run(app, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)
