import re


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
        #logging.warning(f"An unexpected error occurred: {e}")
        return "None", None, None

print(extractData("Time:"))