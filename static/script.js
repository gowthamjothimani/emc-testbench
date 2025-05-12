var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);
       
var selectedSensor = null;
document.addEventListener("DOMContentLoaded", function () {
    const sensorDropdown = document.getElementById("sensorSelect");
    sensorDropdown.innerHTML = `
        <option value="" disabled selected>Select a Sensor</option>
        <option value="Blackline EXO">Blackline EXO</option>
        <option value="Drager X-Zone">Drager X-Zone</option>
    `;
});

// Handle sensor selection
function selectSensor() {
    let sensorDropdown = document.getElementById("sensorSelect");
    let selectedOption = sensorDropdown.value;

    if (!selectedOption) {
        alert("Please select a valid sensor.");
        return;
    }

    let confirmSelection = confirm(`Confirm selection: ${selectedOption}?`);
    if (confirmSelection) {
        selectedSensor = selectedOption;
        socket.emit('select_gas_sensor', { sensor_type: selectedSensor });
    }
}

// Listen for sensor selection confirmation from backend
socket.on('sensor_selected', function (data) {
    alert(data.message);
    if (data.sensor) {
        document.getElementById("selectedSensorText").innerText = `Selected Sensor: ${data.sensor}`;
        document.getElementById("selectedSensorText").style.color = "green";
    } else {
        document.getElementById("selectedSensorText").innerText = "No Sensor Selected";
        document.getElementById("selectedSensorText").style.color = "red";
    }
});

        function showTab(tabId) {
            const tabs = document.querySelectorAll('.tab');
            tabs.forEach(tab => tab.classList.remove('active'));
            document.getElementById(tabId).classList.add('active');
        }

        function startGasTest() {
            socket.emit('start_gas_test');
        }

        function stopGasTest() {
            socket.emit('stop_gas_test');
        }

        function startCardTest() {
            socket.emit('start_card_test');
        }

        function stopCardTest() {
            socket.emit('stop_card_test');
        }

        function controlEfuse(action) {
            fetch(`/control/${action}`)
                .then(response => response.text())
                .then(data => {
                    alert(`Action: ${action} - Response: ${data}`);
                })
                .catch(error => {
                    alert('Error controlling eFuse: ' + error);
                });
        }
            // Card test data update
            socket.on('in_data', function(data) {
                        const cardDataElement = document.getElementById('inData');
                        if (data.in_number) {
                            cardDataElement.textContent = data.in_number;
                        } else {
                            cardDataElement.textContent = '--';
                        }
                    });
                // Card test data update
                socket.on('out_data', function(data) {
                        const cardDataElement = document.getElementById('outData');
                        if (data.out_number) {
                            cardDataElement.textContent = data.out_number;
                        } else {
                            cardDataElement.textContent = '--';
                        }
                    });

        function controlLamp(action) {
            fetch(`/control/${action}`)
                .then(response => response.text())
                .then(data => {
                    alert(`Action: ${action} - Response: ${data}`);
                })
                .catch(error => {
                    alert('Error controlling Lamp: ' + error);
                });
        }

        function controlAlarm(action) {
            fetch(`/control/${action}`)
                .then(response => response.text())
                .then(data => {
                    alert(`Action: ${action} - Response: ${data}`);
                })
                .catch(error => {
                    alert('Error controlling Alarm: ' + error);
                });
        }
            socket.on('sensor_status', function(data) {
            document.getElementById("gasData").innerText = data.state;
            document.getElementById("gasData").style.backgroundColor = data.color;
        });

        socket.on('gas_fault', function(data) {
            document.getElementById("gasState").innerText = data.status;
            document.getElementById("gasState").style.backgroundColor = data.color;
        });
        socket.on('badge_fault', function(data) {
            document.getElementById("badgeState").innerText = data.status;
            document.getElementById("badgeState").style.backgroundColor = data.color;
        });
        socket.on('alarm_fault', function(data) {
            document.getElementById("alarmState").innerText = data.status;
            document.getElementById("alarmState").style.backgroundColor = data.color;
        });
        socket.on('gas_in', function(data) {
            document.getElementById("gasIn").innerText = data.status;
            document.getElementById("gasIn").style.backgroundColor = data.color;
        });

        socket.on("update_status", function (data) {
        document.getElementById("cpu_usage").innerText = data.cpu + "%";
       });

       function startTest() {
        socket.emit('start_all_tests');
    }
    
    function stopTest() {
        socket.emit('stop_all_tests');
    }

    socket.on('mqtt_status', function(data) {
        document.getElementById('networkIcon').style.color = data.color;
    });

    function openMQTTConfig() {
        document.getElementById('mqttConfigModal').style.display = "block";
    }

    function closeMQTTConfig() {
        document.getElementById('mqttConfigModal').style.display = "none";
    }

    function saveMQTTConfig() {
        let config = {
            hostname: document.getElementById('mqtt_hostname').value,
            port: parseInt(document.getElementById('mqtt_port').value),
            topic: document.getElementById('mqtt_topic').value,
            username: document.getElementById('mqtt_username').value,
            password: document.getElementById('mqtt_password').value
        };
        fetch('/update_mqtt', { method: 'POST', body: JSON.stringify(config), headers: {'Content-Type': 'application/json'}})
            .then(response => response.json())
            .then(data => console.log(data));
        closeMQTTConfig();
    }

    function exportLog() {
        socket.emit('export_log');
    }

    function updateTempHum() {
        fetch('/read_sensors')
            .then(response => response.json())
            .then(data => {
                if (data.temperature && data.humidity) {
                    document.getElementById("temp_display").textContent = data.temperature + " °C";
                    document.getElementById("hum_display").textContent = data.humidity + " %";
                } else {
                    document.getElementById("temp_display").textContent = "Err";
                    document.getElementById("hum_display").textContent = "Err";
                }
            })
            .catch(error => {
                document.getElementById("temp_display").textContent = "Fail";
                document.getElementById("hum_display").textContent = "Fail";
            });
    }
    updateTempHum();
    setInterval(updateTempHum, 10000);
    
