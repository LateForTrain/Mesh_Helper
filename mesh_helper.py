"""
Mesh_Helper - A Meshtastic Test Utility

Author: LateForTrain
License: MIT
Repository: https://github.com/LateForTrain/Mesh_Helper

Description:
This script helps test Meshtastic mesh network setups by acting as a home base node.
It listens for messages, repeats them, calculates distance from GPS coordinates,
logs signal metrics, and supports simple configuration.

Run this on a PC or Raspberry Pi connected to a Meshtastic device over USB.

Requirements:
- meshtastic
- pyserial
- geopy

"""

import json
import logging
from geopy.distance import geodesic
import meshtastic
import meshtastic.serial_interface
import meshtastic.util
from meshtastic import pub

# Load configuration
def loadConfig(path='config/settings.json'):
    try:
        with open(path, 'r') as f:
            config = json.load(f)
            return config
    except Exception as e:
        logging.error(f"Failed to load config: {e}")
        return {}

# Callback for when a packet is received
def onReceive(packet, interface):
    logging.info(f"Received packet: {packet}")
    # TODO: Parse packet, extract info, act accordingly

# Callback for when the connection is established
def onConnection(interface, topic=pub.AUTO_TOPIC):
    logging.info("Connected to Meshtastic device.")
    interface.pubsub.subscribe(topic)
    interface.addReceiveHandler(lambda p: onReceive(p, interface))

# Send a message to a specific node
def sendMessage(interface, toID, message):
    logging.info(f"Sending message to {toID}: {message}")
    interface.sendText(message, destinationId=toID)

# Calculate straight-line distance from received GPS coordinates to home base
def calcDistance(recvLat, recvLong, baseLat, baseLong):
    try:
        point1 = (baseLat, baseLong)
        point2 = (recvLat, recvLong)
        return geodesic(point1, point2).meters
    except Exception as e:
        logging.error(f"Distance calculation failed: {e}")
        return None

# Extract data from a received message
def extractData(recvText):
    # Placeholder: parse message text for lat, long, etc.
    try:
        data = json.loads(recvText)
        return data.get('lat'), data.get('lon'), data.get('message')
    except json.JSONDecodeError:
        logging.warning("Failed to decode message as JSON.")
        return None, None, recvText

def main():
    logging.basicConfig(filename='logs/mesh_helper.log', level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')

    config = loadConfig()
    base_id = config.get("base_id", "UNKNOWN")
    base_lat = config.get("base_lat", 0.0)
    base_long = config.get("base_long", 0.0)

    interface = meshtastic.serial_interface.SerialInterface()
    onConnection(interface)

if __name__ == "__main__":
    main()
