import paho.mqtt.client as mqtt

BROKER = "localhost"
SUB_TOPIC = "esp32/test"
PUB_TOPIC = "esp32/control"
CLIENT_ID = "RaspberryPiClient"

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ Connected to MQTT broker")
        client.subscribe(SUB_TOPIC)
        print(f"📡 Subscribed to: {SUB_TOPIC}")
    else:
        print(f"❌ Failed to connect, return code {rc}")

def on_message(client, userdata, msg):
    message = msg.payload.decode()
    print(f"📨 Message from {msg.topic}: {message}")

    # Respond back to ESP32
    response = "KINGINA MO"
    client.publish(PUB_TOPIC, response)
    print(f"📤 Replied with: {'KINGINA MO'}")

client = mqtt.Client(CLIENT_ID)
client.on_connect = on_connect
client.on_message = on_message
client.connect(BROKER, 1883, 60)
client.loop_forever()
