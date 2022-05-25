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
  Server = ("", port_number)
  
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
  first_packet = True
  
  while start_at < file_size:
    packet = message.read(read_from_file_size)
    # Update offset
    start_at += len(packet)
    # Adding the header to the packets
    packet = str(message_counter) + "|" + packet
    message_counter += 1
    packets.append(packet)

  packet_count = 0 
  # While there is still stuff left in the file to send
  while packet_count < len(packets):
    # Send packets in the current congestion window
    for i in range(0 ,cwnd):
      # Find the send time of the last packet in the congestion window
      start_time = time.time()
      encoded_packet = str.encode(packets[packet_count])
      packet_count += 1
      # Sending the packet
      Socket.send(encoded_packet)
      
    # Storing the window size for the packets we sent
    current_cwnd = cwnd
    # Counter for how many packets we received
    recv_counter = 0

    
    # While all the packets haven't been received
    while recv_counter < current_cwnd:
      Socket.settimeout(timeout_seconds)
      try:
        response = Socket.recv(BufferSize).decode()
        end_time = time.time()
        recv_counter += 1
        if is_slow_start():
          cwnd += 1
          in_congestion = False
        else:
          # do congestion control
          if in_congestion == False:
            cwnd += 1
            in_congestion = True

      except socket.timeout:
        Socket.send(str.encode(packets[int(response)+1]))
        ssthresh = int(cwnd/2)
        cwnd = 1
        in_congestion = False

    print(timeout_seconds)
    
    SampleRTT = end_time - start_time
    
    if first_packet:
      EstimatedRTT = SampleRTT
      first_packet = False
    
    EstimatedRTT = alpha_1*EstimatedRTT + alpha*(SampleRTT)
    DevRTT = beta_1*DevRTT + beta*(SampleRTT- EstimatedRTT)
    timeout_seconds = abs(EstimatedRTT+4*DevRTT)
    print(timeout_seconds)
    print()


if __name__ == "__main__":
  main()