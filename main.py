import os
import discord
import paho.mqtt.client as mqtt
from flask import Flask
from threading import Thread

# -----------------------------
# VARIABLES D'ENVIRONNEMENT
# -----------------------------
TOKEN = os.getenv("TOKEN")
MQTT_HOST = os.getenv("MQTT_HOST")
MQTT_PORT = int(os.getenv("MQTT_PORT", 8883))
MQTT_USER = os.getenv("MQTT_USER")
MQTT_PASS = os.getenv("MQTT_PASS")
TOPIC_CMD = os.getenv("TOPIC_CMD", "maison/esp1/cmd")
PORT = int(os.getenv("PORT", 8080))

# -----------------------------
# MQTT SETUP
# -----------------------------
mqtt_client = mqtt.Client(client_id="discord_bot")
mqtt_client.username_pw_set(MQTT_USER, MQTT_PASS)
mqtt_client.tls_set()  # TLS activé pour HiveMQ
mqtt_client.connect(MQTT_HOST, MQTT_PORT, 60)
mqtt_client.loop_start()

# -----------------------------
# DISCORD BOT SETUP
# -----------------------------
intents = discord.Intents.default()
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"Bot Discord connecté : {client.user}")

@client.event
async def on_message(message):
    if message.author.bot:
        return

    if message.content.lower() == "!on":
        mqtt_client.publish(TOPIC_CMD, "ON")
        await message.channel.send("LED allumée via MQTT !")

    if message.content.lower() == "!off":
        mqtt_client.publish(TOPIC_CMD, "OFF")
        await message.channel.send("LED éteinte via MQTT !")

# -----------------------------
# KEEP-ALIVE WEB SERVICE
# -----------------------------
app = Flask('')

@app.route('/')
def home():
    return "Bot Discord + MQTT actif 🚀"

def run_web():
    app.run(host='0.0.0.0', port=PORT)

Thread(target=run_web).start()

# -----------------------------
# LANCEMENT DU BOT DISCORD
# -----------------------------
client.run(TOKEN)
