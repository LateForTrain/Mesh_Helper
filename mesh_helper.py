"""
Mesh_Helper - A Meshtastic Test Utility

Author: LateForTrain
Updated: 2025-05-23
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
import time
import meshtastic
import meshtastic.serial_interface
import re
from pubsub import pub
from datetime import datetime
from geopy.distance import geodesic


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
        global base_lat, base_long
        
        #print(packet)  # This is a dictionary 
        try:
            match packet['decoded']['portnum']:
                case "TELEMETRY_APP":
                    #Still need to understand what we will do here 
                    msg="Telemetry package..."
                case "TEXT_MESSAGE_APP":
                    logging.info(f"Text package...")
                    text = packet['decoded']['text']
                    logging.info(f"Text message: {text}")
                    mycommand, mylat, mylon = extractData(text)
                    returnMsg =""

                    if mycommand == "Distance":
                        reqDistance =calcDistance(mylat, mylon)
                        returnMsg = "Distance: " + str(round(reqDistance,0)) + " meter"
                        logging.info(f"{returnMsg}")
                        sendMessage(interface, packet['fromId'], returnMsg)
                    elif mycommand == "Signal":
                        # Extract RSSI
                        rssi = packet.get('rxRssi')
                        # Extract SNR
                        snr = packet.get('rxSnr')
                        # You can then print or use these values
                        if rssi is not None:
                            returnMsg = "Received RSSI: " + str(round(rssi,2)) + "dBm"
                        else:
                            returnMsg = "Received RSSI: --.-- dBm"

                        if snr is not None:
                            returnMsg = returnMsg + " Received SNR: " + str(round(snr,2)) + "dB"
                        else:
                            returnMsg = returnMsg + " Received SNR: --.-- dB"
                        logging.info(f"{returnMsg}")
                        sendMessage(interface, packet['fromId'], returnMsg)
                    elif mycommand == "Time":
                        current_time = datetime.now()
                        returnMsg=current_time.strftime("%Y-%m-%d %H:%M")
                        logging.info(f"{returnMsg}")
                        sendMessage(interface, packet['fromId'], returnMsg)
                    else:
                        sendMessage(interface, packet['fromId'], text)
                case "POSITION_APP":
                    #Still need to understand what we will do here 
                    msg="Position package..."
                    logging.info(msg)
                    logging.info(f"Latitude: {packet['decoded']['position']['latitude']}")
                    logging.info(f"Longitude: {packet['decoded']['position']['longitude']}")
                    logging.info(f"Altitude: {packet['decoded']['position']['altitude']}")
                    logging.info(f"Ground Speed: {packet['decoded']['position']['groundSpeed']}")
                    logging.info(f"Ground Track: {packet['decoded']['position']['groundTrack']}")
                case "NODEINFO_APP":
                    #Still need to understand what we will do here 
                    msg="NodeInfo package..."
                    logging.info(msg)
                    #logging.info(packet)
                    logging.info(f"Id: {packet['decoded']['user']['id']}")
                    logging.info(f"Long Name: {packet['decoded']['user']['longName']}") 
                    logging.info(f"Short Name: {packet['decoded']['user']['shortName']}") 
                    logging.info(f"Hardware Model: {packet['decoded']['user']['hwModel']}") 
                case "ALERT_APP":
                    #Still need to understand what we will do here 
                    msg="Alert package..."
                case _:
                    #Still need to understand what we will do here 
                    msg="Some other package..."
                    logging.info(msg)
                    #logging.info(packet)
        except Exception as e:
            logging.warning(f"Error parsing packet: {e}")

# Callback for when the connection is established
def onConnection(interface, topic=pub.AUTO_TOPIC):
    logging.info("Connected to Meshtastic device.")
    print("Connected to Meshtastic device.")
    myUser = interface.getMyUser()
    logging.info(f"Unit Long Name: {myUser['longName']}")
    print(f"Unit Long Name: {myUser['longName']}")
    logging.info("Unit Short Name: "+myUser['shortName'])
    print(f"Unit Short Name: {myUser['shortName']}")
    logging.info(f"Unit Id: {myUser['id']}")
    print(f"Unit Id: {myUser['id']}")
    logging.info(f"Model: {myUser['hwModel']}")
    print(f"Model: {myUser['hwModel']}")

# Callback for when the connection is lost
def onConnectionLost(interface):
    logging.info("Connection lost")

# Send a message to a specific node
def sendMessage(interface, toID, message):
    logging.info(f"Sending message to {toID}: {message}")
    interface.sendText(message, destinationId=toID)

# Calculate straight-line distance from received GPS coordinates to home base
def calcDistance(recvLat, recvLong):
    try:
        point1 = (base_lat, base_long)
        point2 = (recvLat, recvLong)
        return geodesic(point1, point2).meters
    except Exception as e:
        logging.error(f"Distance calculation failed: {e}")
        return None

# Extract data from a received message
def extractData(recvText):
    # Placeholder: parse message text for command, lat, long, etc.
    cmd="None"
    longitude = 0.0
    latitude = 0.0

    try:
        # Pattern 1: Matches a command with two float/integer coordinates
        pattern_coords = re.compile(r'^(\w+):\s*([-+]?\d*\.\d+|\d+),\s*([-+]?\d*\.\d+|\d+)', re.MULTILINE)
        # Pattern 2: Matches a standalone command followed by a colon
        pattern_cmd_only = re.compile(r'^(\w+):$', re.MULTILINE)

        # Try to match with coordinates first
        match_coords = pattern_coords.search(recvText)
        if match_coords:
            cmd = match_coords.group(1)
            longitude = float(match_coords.group(2))
            latitude = float(match_coords.group(3))
            return cmd, longitude, latitude
        else:
            # If no coordinates, try to match with the command only pattern
            match_cmd_only = pattern_cmd_only.search(recvText)
            if match_cmd_only:
                cmd = match_cmd_only.group(1)
                # For standalone commands, longitude and latitude remain their default values (0.0)
                return cmd, longitude, latitude
            else:
                # If neither pattern matches, return default "None" for cmd
                return "None", None, None

    except Exception as e:
        logging.warning(f"An unexpected error occurred: {e}")
        return "None", None, None

def main():
    global base_lat, base_long
    errorText = ""
    interface = None # Initialize interface to None outside the try block

    log_filename = f"logs/mesh_helper_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    logging.basicConfig(filename=log_filename, level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Load the config for the base unit.  Remember to update settings.json.
    config = loadConfig()
    base_lat = config.get("base_lat", 0.0)
    base_long = config.get("base_long", 0.0)

    try:
        logging.info("Good day to MeshBot v0.1")
        print("Good day to MeshBot v0.1")
        logging.info("Bot is now running. Press Ctrl+C to stop.")
        print("Bot is now running. Press Ctrl+C to stop.")

        # Start the Meshtastic serial interface
        # This might print "No Serial Meshtastic device detected..." if none is found
        interface = meshtastic.serial_interface.SerialInterface()
        logging.info("Meshtastic interface object created (attempting connection).")

        # Subscribe to Meshtastic events
        pub.subscribe(onReceive, "meshtastic.receive")
        pub.subscribe(onConnection, "meshtastic.connection.established")
        pub.subscribe(onConnectionLost, "meshtastic.connection.lost")

        # Give the interface a moment to connect or fail to connect
        time.sleep(3) # A short delay to allow connection attempts

        #Used to check if connected to serial device
        myLongName = interface.getLongName()

        heartbeatCounter = 0
        while True:
            time.sleep(1)
            if heartbeatCounter == 600:
                logging.info("Heartbeat: Checking connection status (if connected).")
                myLongName = interface.getLongName()
                heartbeatCounter = 0
            heartbeatCounter += 1

    except KeyboardInterrupt:
        logging.info("KeyboardInterrupt caught. Exiting...")
    except Exception as e:
        # Catch any other unexpected errors during the process
        logging.error(f"An unexpected error occurred: {e}")
        errorText = str(e)

    finally:
        # This ensures the connection is closed cleanly whether there was an error or not
        if errorText != "'SerialInterface' object has no attribute 'myInfo'": # Only try to close if the interface object was successfully created
            logging.info("Closing the Meshtastic interface...")
            interface.close()
            logging.info("Meshtastic interface closed.")
        else:
            logging.info("No Meshtastic interface object was created to close.")

if __name__ == "__main__":
    main()
