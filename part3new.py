# Importing libraries
import socket
import os
import time

# Global variables
read_from_file_size = 1000
timeout_seconds = 5
cwnd = 1
ssthresh = 16
BufferSize = 100
start_index = 1

# Function that tells us if we are in slow start
def is_slow_start():
  return cwnd <= ssthresh

# Function that tells us if we received a response for the left most item in the window
def left_hand_response(response):
  return response == start_index

def main():
  # Open the message
  message = open("message.txt", 'r')
  file_size = os.stat("message.txt").st_size
  start_at = 0

  # Connect to the socket
  port_number = int(input("Enter port number: "))
  Server = ("", port_number)
  
  Socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  Socket.connect(Server)
  
  # Variables to keep track of packet and packet count 
  packet = ""
  packets = []
  message_counter = 1
  in_congestion = False
  
  # Bringing global variables in scope
  global ssthresh
  global cwnd
  global timeout_seconds
  global start_index
  
  # Constants for calculating RTT based timeout
  EstimatedRTT = 0
  DevRTT = 0
  alpha = 0.875
  alpha_1 = 0.125
  beta = 0.25
  beta_1 = 0.75

  # Flag for first packet timeout calculations
  first_packet = True
  
  # Creating all the packets to send
  while start_at < file_size:
    packet = message.read(read_from_file_size)
    start_at += len(packet)
    # Adding the header to the packets
    packet = str(message_counter) + "|" + packet
    message_counter += 1
    packets.append(packet)

  # Counter to keep track of counter
  packet_count = 0
  # Time at which we send the packet
  BeginTimes = []
  # Round Trip Times for each packet
  RTTTimes = [0] * len(packets)
  # Last packet that we set the RTT for
  RTTLast = 0

  # Send the first packet
  Socket.send(str.encode(packets[packet_count]))
  BeginTimes.append(time.time)
  packet_count+=1

  # While packets still left to send
  while packet_count < len(packets):
    # Start timeout
    Socket.settimeout(timeout_seconds)
    try:
      # receive response
      response = Socket.recv(BufferSize).decode()
      # Check end time
      end_time = time.time()
      
      # set RTTs for all the packets sent until the one we got the response for
      while RTTLast <= response:
        RTTTimes[RTTLast] = BeginTimes[RTTLast] - end_time
        RTTLast += 1

      # If slow start
      if is_slow_start():
        # Increase it per receive
        cwnd += 1

        # If the response was for a left most packet in the window
        if left_hand_response(response):
          start_index += 1
          # We can slide the window by 1 and send the packets in the new congestion window
          for i in range(packet_count, packet_count+cwnd):
            Socket.send(str.encode(packets[i]))
            BeginTimes.append(time.time)
            packet_count += 1
        # we are in slow start so congestion false
        in_congestion = False
      
      # If not slow start
      else:
        # do congestion control
        # We only want to do it once per RTT
        if in_congestion == False:
          cwnd += 1
          start_index += 1
          in_congestion = True

        if left_hand_response(response):
          start_index += 1
          for i in range(packet_count, packet_count+cwnd):
            Socket.send(str.encode(packets[i]))
            packet_count += 1

    
    except socket.timeout:
      Socket.send(str.encode(packets[int(response)+1]))
      ssthresh = int(cwnd/2)
      cwnd = 1
      in_congestion = False

    in_congestion = False

    SampleRTT = RTTTimes[RTTLast]

    if first_packet:
      EstimatedRTT = SampleRTT
      first_packet = False
    
    EstimatedRTT = alpha_1*EstimatedRTT + alpha*(SampleRTT)
    DevRTT = beta_1*DevRTT + beta*(SampleRTT- EstimatedRTT)
    timeout_seconds = abs(EstimatedRTT+4*DevRTT)