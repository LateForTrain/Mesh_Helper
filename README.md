
# Mesh_Helper

**Mesh_Helper** is a Python application designed to help users test and validate their [Meshtastic](https://meshtastic.org/) network setup. It is intended to run on a PC or Raspberry Pi connected to a Meshtastic device via USB, acting as a fixed "home base" unit.

With a second Meshtastic device connected to a phone or portable system, users can move around and test connectivity back to the base unit in real-world conditions.

> ⚠️ This is a work in progress — features will evolve and improve over time.

## Features

- 🔁 **Message Repeater**  
  Automatically repeats any message it receives, useful for basic connectivity tests.

- 📍 **Distance Calculation** 
  If the message contains GPS coordinates (latitude and longitude), the app calculates the straight-line (great-circle) distance between the remote and base unit.
  Example (Remember the : after command, Long and let separated with , and use . for decimal): 
      Distance: 57.862083, 14,143303

- 📶 **Signal Metrics Reporting**  
  The base unit sends back the RSSI and SNR of received messages, helping users understand signal quality and propagation.
  Example (Remember the : after command): 
    Signal:

- 📝 **Event Logging**  
  All events and message data are logged to a file for later analysis.

## Typical Setup

1. A Raspberry Pi (or PC) connected to a Meshtastic device over USB.
2. A second Meshtastic device connected to a mobile device.
3. Walk around with the mobile unit to test range and signal performance with the base.

## Installation

Clone the repository and install the required dependencies:

```bash
git clone https://github.com/LateForTrain/Mesh_Helper.git
cd Mesh_Helper
pip install -r requirements.txt
```
## Setup
Edit **`settings.json`**: Navigate to the `config` directory and open the `settings.json` file. Enter your base station coordinates here. Don't worry, these coordinates are for local use only and are not loaded onto your Meshtastic device or transmitted.

## Usage

Run the main script:

```bash
python mesh_helper.py
```

Make sure your Meshtastic device is connected and visible (e.g., `/dev/ttyUSB0` on Linux or `COMx` on Windows).

The base station will only communicate over the DM link, but will receive commands in both public channel and DM.

## License

This project is licensed under the MIT License. You are free to use, modify, and distribute this code as long as the original copyright notice is preserved.

## Contributing

Contributions, suggestions, and issue reports are welcome! Feel free to submit a pull request or open an issue.

---

Made with ❤️ for the Meshtastic community.
