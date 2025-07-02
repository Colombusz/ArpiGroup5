def on_message(client, userdata, msg):
    message = msg.payload.decode()
    print(f"📨 Message from {msg.topic}: {message}")

    if msg.topic == "esp32/test/esp1":
        print("🔵 Message received from ESP1")
        response = "Hello ESP32-1"
    elif msg.topic == "esp32/test/esp2":
        print("🟢 Message received from ESP2")
        response = "Hello ESP32-2"
    else:
        print("⚠️ Message from unknown ESP")
        response = "Hello Unknown ESP32"

    client.publish("esp32/control", response)
    print(f"📤 Replied with: {response}")
