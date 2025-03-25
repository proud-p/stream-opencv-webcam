from pythonosc import dispatcher, osc_server

def handle_answer(address, *args):
    print(f" Received on {address}: {args}")

def start_osc_receiver(ip="0.0.0.0", port=1234):
    disp = dispatcher.Dispatcher()
    disp.map("/trigger", handle_answer)  # Listen for messages sent to /answer

    server = osc_server.ThreadingOSCUDPServer((ip, port), disp)
    print(f"✅ OSC server listening on {ip}:{port} (Ctrl+C to stop)")
    server.serve_forever()


if __name__ == "__main__":
    ip = "127.0.0.1"        
    port = 4444   # Your desired port
    
    start_osc_receiver(ip,port)
