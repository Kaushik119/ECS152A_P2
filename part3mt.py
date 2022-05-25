# Importing libraries
from concurrent.futures import thread
import socket
import os
import time
import threading

# Global variables
read_from_file_size = 1000
timeout_seconds = 5
cwnd = 1
ssthresh = 16
BufferSize = 100

in_congestion = False
first_packet = True
start_index = 1
packets = []
Socket
packet_count = 0
BeginTime = []
RTTTimes
RTTLast = 0
current_cwnd = 0

lock = threading.Lock()

# Function that tells us if we are in slow start
def is_slow_start():
  return cwnd <= ssthresh

# Function that tells us if we received a response for the left most item in the window
def left_hand_response(response):
  return response == start_index

def send_thread():
  lock.acquire()
  global packet_count
  global Socket
  global current_cwnd

  for i in range(packet_count ,packet_count + cwnd):
    # Find the send time of the last packet in the congestion window
    encoded_packet = str.encode(packets[packet_count])
    packet_count += 1
    # Sending the packet
    Socket.send(encoded_packet)
    BeginTime.append(time.time())

  lock.release()
  current_cwnd = cwnd
  ack = threading.Thread(target= ack_thread, name = "ack")
  ack.run()

def ack_thread(current_cwd):
  lock.acquire()
  global Socket
  global timeout_seconds
  global BeginTime
  global RTTLast
  global current_cwd
  
  recv_counter = 0
  while recv_counter < current_cwd:
    Socket.settimeout(timeout_seconds)
    try:
      response = Socket.recv(BufferSize).decode()
      end_time = time.time()
      while RTTLast <= response:
        RTTTimes[RTTLast] = BeginTime[RTTLast] - end_time
        RTTLast += 1

      
    except:
      pass

  return
def main():
  # Open the message
  global Socket
  global packets
  global RTTTimes
  
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
  message_counter = 1
  
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
  
  RTTTimes = [0]* len(packets)
  send = threading.Thread(target=send_thread , name = "send")
  
  while packet_count < len(packets):
    send.start()

    send.join()