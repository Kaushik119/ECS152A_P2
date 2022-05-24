import socket
import os
import time


# TCP TAHOE IMPLEMENTED AS DESCRIBED IN TEXTBOOK

read_from_file_size = 1000
timeout_seconds = 5
cwnd = 1
ssthresh = 16
BufferSize = 100

def is_slow_start():
  return cwnd <= ssthresh

def main():
  message = open("message.txt", 'r')
  file_size = os.stat("message.txt").st_size
  start_at = 0

  port_number = int(input("Enter port number: "))
  Server = ("127.0.0.1", port_number)
  
  Socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  Socket.connect(Server)
  
  packet = ""
  packets = []
  message_counter = 1
  in_congestion = False
  
  global ssthresh
  global cwnd
  global timeout_seconds
  
  EstimatedRTT = 0
  DevRTT = 0
  alpha = 0.875
  alpha_1 = 0.125
  beta = 0.25
  beta_1 = 0.75
  
  start_time = 0
  end_time = 0

  BeginTimes = []

  while start_at < file_size:
    packet = message.read(read_from_file_size)
    start_at += len(packet)
    # Adding the header to the packets
    packet = str(message_counter) + "|" + packet
    message_counter += 1
    packets.append(packet)

  packet_count = 0
  RTTTimes = [0]*len(packets)
  RTTLast = 0

  while packet_count < len(packets):
    print(cwnd)
    for i in range(0 ,min(len(packets) - packet_count,cwnd)):
      Socket.send(str.encode(packets[packet_count]))
      BeginTimes.append(time.time())
      packet_count += 1
      
    current_cwnd = min(len(packets) - packet_count,cwnd)
    recv_counter = 0
    
    while recv_counter < current_cwnd:
      Socket.settimeout(timeout_seconds)
      try:
        response = int(Socket.recv(BufferSize).decode())
        end_time = time.time()
        recv_counter += 1
        while RTTLast < response:
          RTTTimes[RTTLast] = end_time - BeginTimes[RTTLast]
          RTTLast += 1
        
        
        # Socket.send(str.encode(packets[packet_count]))
        # packet_count += 1
        
        if is_slow_start():
          cwnd += 1
          in_congestion = False
        else:
          # do congestion control
          if in_congestion == False:
            cwnd += 1
            in_congestion = True

      except socket.timeout:
        print("Timed out")
        Socket.send(str.encode(packets[response+1]))
        ssthresh = int(cwnd/2)
        cwnd = 1
        in_congestion = False

    
    in_congestion = False
    SampleRTT = RTTTimes[RTTLast-1]
    EstimatedRTT = alpha_1*EstimatedRTT + alpha*(SampleRTT)
    DevRTT = beta_1*DevRTT + beta*(SampleRTT- EstimatedRTT)
    timeout_seconds = EstimatedRTT+4*DevRTT


if __name__ == "__main__":
  main()