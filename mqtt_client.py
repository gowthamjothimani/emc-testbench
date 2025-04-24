import paho.mqtt.client as mqtt
import json
import time

class MQTTClient:
    def __init__(self, socketio):
        self.client = None
        self.socketio = socketio
        self.connected = False

        # MQTT settings
        self.mqtt_config = {
            "hostname": "10.30.250.241",
            "port": 1883,
            "topic": "emc_test",
            "username": "",
            "password": ""
        }

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.connected = True
            print("Connected to MQTT Broker")
        else:
            self.connected = False
            print("Failed to connect")
        self.update_status()

    def on_disconnect(self, client, userdata, rc):
        self.connected = False
        self.update_status()
        print("Disconnected from MQTT Broker")

    def update_status(self):
        color = "lightgreen" if self.connected else "lightcoral"
        self.socketio.emit('mqtt_status', {"color": color})

    def connect_mqtt(self):
        if self.client:
            self.client.disconnect()

        self.client = mqtt.Client()
        
        if self.mqtt_config["username"]:
            self.client.username_pw_set(self.mqtt_config["username"], self.mqtt_config["password"])

        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect

        try:
            self.client.connect(self.mqtt_config["hostname"], self.mqtt_config["port"], 60)
            self.client.loop_start()
        except Exception as e:
            print(f"MQTT Connection Error: {e}")
            self.connected = False
            self.update_status()

    def update_config(self, config):
        self.mqtt_config.update(config)
        self.connect_mqtt()

    def publish_data(self, data):
        if self.connected:
            payload = json.dumps(data)
            self.client.publish(self.mqtt_config["topic"], payload)
            print("Published Data:", payload)
