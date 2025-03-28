
from pythonosc import udp_client
from time import sleep, time
import random
import math

def get_message():
    return f"Message from another script! Random seed: {random.randint(0,35432)}"

ip = "127.0.0.1"    # Localhost
port = 4444     # Your desired port
osc_client = udp_client.SimpleUDPClient(ip, port)

def trigger_unreal():
    """
    This function sends an OSC message to Unreal Engine - testing
    """
    message_address = "/trigger"
    value = get_message()  # Value to be sent (you can change this as needed 
    # fetch message dynamically

    # Send the OSC message
    osc_client.send_message(message_address, value)
    print(f"Sent OSC message to {ip}:{port} with value:{value}")
    
    t = time()  # seconds since epoch

    # Frequency of the sine wave (how fast it oscillates)
    frequency = 0.5  # Hz

    # Amplitude sweep between 0 and 1
    sweep_value = (math.sin(2 * math.pi * frequency * t) + 1) / 2
    
    numbers = [
        abs(math.cos(t*frequency)),   # FLOATTTTTTT!! OTHERWISE UNREAL WONT READ THEN INDEX WILL BE 1
        
         0.0,
         0.0,]
    osc_client.send_message("/xyz", numbers)
    print(f"Sent OSC message to {ip}:{port} with value:{numbers}")


while True:
    trigger_unreal()
    sleep(1)