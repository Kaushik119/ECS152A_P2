import socket
import os
import time


# TCP TAHOE IMPLEMENTED AS DESCRIBED IN TEXTBOOK

read_from_file_size = 949
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
  past_packets = []
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
  while(start_at < file_size):
    for i in range(0 ,cwnd):
      start_time = time.time()
      packet = message.read(read_from_file_size)
      start_at += len(packet)
      packet = str(message_counter) + "|" + packet
      message_counter += 1
      past_packets.append(packet)

      encoded_packet = str.encode(packet)

      Socket.send(encoded_packet)
      
    current_cwnd = cwnd
    recv_counter = 0
    
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
        Socket.send(str.encode(past_packets[response+1]))
        ssthresh = int(cwnd/2)
        cwnd = 1
        in_congestion = False

    SampleRTT = end_time - start_time
    EstimatedRTT = alpha_1*EstimatedRTT + alpha*(SampleRTT)
    DevRTT = beta_1*DevRTT + beta*(SampleRTT- EstimatedRTT)
    timeout_seconds = EstimatedRTT+4*DevRTT


if __name__ == "__main__":
  main()