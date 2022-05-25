import socket
import os
import time

# TCP TAHOE IMPLEMENTED AS DESCRIBED IN TEXTBOOK

read_from_file_size = 1000
timeout_seconds = 5
cwnd = 1
ssthresh = 16
BufferSize = 100
start_index = 1

def is_slow_start():
  return cwnd <= ssthresh

def main():
  message = open("/home/osboxes/Desktop/ECS152A/ECS152A_P2/message.txt", 'r')
  file_size = os.stat("/home/osboxes/Desktop/ECS152A/ECS152A_P2/message.txt").st_size
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
  global start_index
  
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
    for i in range(sent_counter ,min(len(packets) - packet_count,cwnd)):
      Socket.send(str.encode(packets[packet_count]))
      BeginTimes.append(time.time())
      print("Packet count" ,packet_count + 1)
      packet_count += 1

    current_cwnd = min(len(packets) - packet_count,cwnd)
    recv_counter = 0

    while(recv_counter)