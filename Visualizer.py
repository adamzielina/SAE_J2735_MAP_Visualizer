# This is a Python script which listens on port 9000 to obtain SAE j2735 map messages
# sent to it via ethernet interface from Cohda MK6C device, extract the message data and visualize it

from CAVmessages import J2735_decode
import socket
import time
import folium
import json
import webbrowser
import os
from datetime import datetime

MAP_ID = '18'
ADDR = '0.0.0.0'
PORT = 9000


def J2735_extract(hex_stream):
    """
    this function takes a raw V2X protocol stack encoded data and extracts from it the entire SAE J2735 message frame.
    To do that it uses a bit pattern adhering to length field of IEEE 1609.2 standard. Acquired length field contains information about
    the length of a SAE J2735 (it's not fixed) message frame. Knowing the length and position we can obtain the correct data.

    Args:
        hex_stream (string): string representation of hexadecimal encoded encapsulated data

    return:
        (string): string representation of hexadecimal encoded SAE J2735 message frame data.
    """
    offset = 0
    length_indicator = "400380"

    while offset < len(hex_stream):
        if hex_stream[offset:offset+6] == length_indicator:
            length_field = int(hex_stream[offset+6:offset+8], 16)  # first octet of length field
            if length_field & 0x80 == 0:  # Check if the first bit is 0
                # First bit is 0, so no further bytes are present. The value is within the first byte.
                value = length_field
                print(f"SAE j2735 message length in bytes: {value}")
                return hex_stream[offset + 8:offset + 8 + 2 * value]
            else:
                # First bit is 1, indicating additional bytes are present
                length_field = length_field & 0x7f  # Extract the last 7 bits to determine number of another bytes
                value = int(hex_stream[offset+8:offset+8+2*length_field], 16)  # Convert the next 'length' bytes
                print(f"SAE j2735 message length in bytes: {value}")
                return hex_stream[offset + 8+2*length_field:offset + 8+2*length_field + 2 * value]
        offset += 2
    return -1

if __name__ == '__main__':
    date_now = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    log_path = f'C:\\python\\MapMessage\\log\\{date_now}'
    os.makedirs(log_path, exist_ok=True)
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((ADDR, PORT))
    cnt = 0
    while True:
        time.sleep(3)
        data, addr = server_socket.recvfrom(PORT)
        hex_stream = data.hex()
        hex_j2735 = J2735_extract(hex_stream)
        decode = J2735_decode(hex_j2735)
        data = json.loads(decode.json)
        #extracting field values, creating map
        if(data['MessageFrame']['messageId'] == MAP_ID):
            lat = float(data['MessageFrame']['value']['MapData']['intersections']['IntersectionGeometry']['refPoint']['lat']) / pow(10, 7)
            long = float(data['MessageFrame']['value']['MapData']['intersections']['IntersectionGeometry']['refPoint']['long']) / pow(10, 7)
            id = int(data['MessageFrame']['value']['MapData']['intersections']['IntersectionGeometry']['id']['id'])
            print(f'msg number = {cnt}, intersection id = {id}, lat = {lat}, long = {long}')
            map_object = folium.Map(location=[lat, long], zoom_start=17)
            folium.Marker([lat, long], popup=f'Intersection ID={id}').add_to(map_object)
            map_object.save(log_path + f'\\{cnt}_Intersection_id_{id}.html')
            webbrowser.open(log_path + f'\\{cnt}_Intersection_id_{id}.html')
        else:
            print("SAE J2735 other than map message")
        cnt += 1
