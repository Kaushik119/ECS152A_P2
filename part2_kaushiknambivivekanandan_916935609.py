
# Import packages
import socket
import os
import time
import sys
import seaborn as sns
import matplotlib.pyplot as plt
import math

# Global variables 
read_from_file_size = 1000
timeout_seconds = 5
cwnd = 5
ssthresh = 16
BufferSize = 100
start_index = 1

# Function that tells us if the congestion window is in slow start
def is_slow_start():
  return cwnd <= ssthresh

# Check if the response we received is on the left hand side of the window
def left_hand_response(response):
  return response == start_index

# Print the message on receive or send
def printmessage(response, packet_count):
  print("Sequence Number of Packet sent:", packet_count)
  print("Acknowledgement Number Received:", response, "\n")

def main():
  print("in main")
  # Open the file and get its size
  message = open("message.txt", 'r')
  file_size = os.stat("message.txt").st_size
  start_at = 0

  # Get port number for this instance of the program
  port_number = int(input("Enter port number: "))
  Server = ("", port_number)

  # Connect to the server
  Socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  Socket.connect(Server)
  
  # Keep track of packets
  packet = ""
  packets = []
  message_counter = 1

  
  # Bringing global variables into scope
  global ssthresh
  global cwnd
  global timeout_seconds
  global start_index
  
  
  # Other variables
  end_time = 0
  prev_response = 0

  # Array to keep track of begin times 
  BeginTimes = []

  # Create all the packets
  while start_at < file_size:
    packet = message.read(read_from_file_size)
    start_at += len(packet)
    # Adding the header to the packets
    packet = str(message_counter) + "|" + packet
    message_counter += 1
    packets.append(packet)

  print("packets created")
  # Last sent packet 
  packet_count = 0
  # Arrays to keep track of RTT
  RTTTimes = [0]*len(packets)
  # Last packet to be received
  RTTLast = 0
  # Check how many got sent in the recv side
  sent_counter = 0
  # Array to keep track of which packets got acknowledged
  ack_array = [False]*len(packets)
  # response that we received
  response = 0

  # Keep track of start time 
  total_start = time.time()
  # While there are still packets left to send
  while packet_count < len(packets):
    # Send packets in the current congestion window
    for i in range(sent_counter ,min(len(packets) - packet_count,cwnd)):
      Socket.send(str.encode(packets[packet_count]))
      printmessage(response, packet_count+1)
      BeginTimes.append(time.time())
      packet_count += 1

    # Save the current congestion window
    current_cwnd = min(len(packets) - packet_count,5)
    # Counter to see if we received everything we sent
    recv_counter = 0
    # Reset sent counter to 0
    sent_counter = 0
    # While there are still packets left to be received
    while recv_counter < current_cwnd:
      # Start timeout
      Socket.settimeout(timeout_seconds)
      try:
        # Get response
        response = int(Socket.recv(BufferSize).decode())
        # Log end time
        end_time = time.time()
        # See how many packets were received by the server (accounts for ack packets that get lost)
        recv_counter += (response - prev_response)
        printmessage(response, packet_count+1)
        prev_response = response
        Socket.settimeout(None)

        # Set the RTT times for all the unacknowledeged packets
        while RTTLast < response:
          RTTTimes[RTTLast] = end_time - BeginTimes[RTTLast]
          RTTLast += 1
        
        # Mark those packets as acknowledged
        ack_array[0:response] = [True]*(response)

        # If the response is on the left hand side of the cwnd
        # then move the window by 1
        print("Packet count: ", packet_count)
        if left_hand_response(response):
          start_index = ack_array.index(False) + 1
          Socket.send(str.encode(packets[packet_count]))
          printmessage(response, packet_count+1)
          sent_counter+=1
          BeginTimes.append(time.time())
          packet_count += 1

      # If there was a timeout 
      except socket.timeout:
        # Send the packet again and update the ssthresh and cwnd
        Socket.send(str.encode(packets[response]))
    
  # Mark end time
  total_end = time.time()
  
  # Calculate the performance metrics and show them
  DelayAvg = (total_end - total_start)/len(packets) * 1000
  ThroughputAvg = (file_size*8)/(DelayAvg)
  Performance = math.log10(ThroughputAvg) - math.log10(DelayAvg)

  print("Average Delay =",DelayAvg )
  print("Average Througput=", ThroughputAvg)
  print("Performance =", Performance)

  # Calculate the per packet througput
  PPThroughput = []
  for packet_count, times in enumerate(RTTTimes):
    if times != 0:
      PPThroughput.append((sys.getsizeof(packets[packet_count])*8)/times)
  
  # Create graph for RTT
  RTT = sns.lineplot(x = range(0, len(packets)),y = RTTTimes)
  RTT.set(xlabel = "Packet Number", ylabel = "RTT", title = "RTT for Packets on Port " + str(port_number))

  # Save the figure in the image folder 
  image_name = "Part2_RTT"+str(port_number)+".png"
  plt.savefig("Images/"+image_name)
  
  # Clear the plot
  plt.clf()

  # Create graph for Per packet throughput
  Throughput = sns.lineplot(x = range(0, len(PPThroughput)),y = PPThroughput)
  Throughput.set(xlabel = "Packet Number", ylabel = "Per Packet Throughput", title = "PPT for Packets on Port " + str(port_number))

  # Save the figure in the image folder 
  image_name = "Part2_PPT"+str(port_number)+".png"
  plt.savefig("Images/"+image_name)
  
# Main function
if __name__ == "__main__":
  main()








































# import socket
# import os
# import time
# import math

# read_from_file_size = 1000
# BufferSize = 100
# window = 5

# class Packet:
#   def __init__(self, num, info):
#     self.num = num
#     self.info = info

# class Timing:
#   def __init__(self, num, start_time):
#     self.num = num
#     self.start_time = start_time
  
#   def __eq__(self, other):
#     return self.num == other.num    

# packets = []

# message = open("message.txt", 'r')
# file_size = os.stat("message.txt").st_size

# cur_file_size = 0
# packet_num = 1
# while(cur_file_size < file_size):
#   packets.append(Packet(packet_num, str(packet_num) + "|" + message.read(read_from_file_size)))
#   packet_num += 1
#   cur_file_size += 1000

# packet_start_times = []
# special_packet_num = 1

# received_packets = [False] * len(packets)
# num_received = 0
# num_outbound = 0
# resend_array = []
# ok_send = True
# prev_response = True

# port_number = int(input("Enter port number: "))
# Server = ("", port_number)

# Socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# Socket.connect(Server)

# total_length = len(packets)
# temp_packets = packets
# while(num_received < total_length):
#   # print("Num outbound", num_outbound, " OK SEND", ok_send)
#   while(len(resend_array) > 0):
#     resend = resend_array.pop(0)
#     print("Resending packet num: " + str(packets[resend.num - 1].num))
#     Socket.send(str.encode(packets[resend.num - 1].info))

#     for packet in packet_start_times:
#       if(packet.num == resend.num):
#         packet.start_time = time.time()
  

#   if(ok_send):
#     while(window != 0):
#       if(len(temp_packets) != 0):
#         packet = temp_packets.pop(0)
#       Socket.send(str.encode(packet.info))
#       # print(packet.info)
#       print("Sending packet num: " + str(packet.num))
#       packet_start_times.append(Timing(packet.num, time.time()))
#       num_outbound += 1
#       window -= 1

#     ok_send = False
  
#   while(num_outbound > 0):
#     print("num outbound > ", num_outbound)

#     check_timeout = time.time()
#     timeout_flag = False

#     for packet in packet_start_times:
#       if(check_timeout - packet.start_time > 5):
#         print("Packet num: ", packet.num, " TIMED OUT")
#         resend_array.append(packet)
#         timeout_flag = True

#     if(timeout_flag):
#       break
    
#     Socket.settimeout(5)
#     try:
#       print("Waiting for packet")
#       response = Socket.recv(BufferSize).decode()
#       print("BEFORE setting receive: ", received_packets[int(response) - 1])
#       for i in range(special_packet_num, int(response)):
#         received_packets[i] = True
#       # for every index less than response, set received to true
#       for i in range(0, int(response)):
#         received_packets[i] = True
#       print("AFTER setting receive: ", received_packets[int(response) - 1])
#       print("Recieved packet num: ", response)
#       # num_received += 1
#       print("NUM rec:", num_received)

#       new_responses = int(response) - special_packet_num + 1
#       num_received += new_responses
      
#       index = 0
#       for packet in packet_start_times:
#         if packet.num <= int(response):
#           packet_start_times.pop(index)
#         else:
#           index += 1
      
#       print("Packet start times length", len(packet_start_times))

#       # print_start_times = []
#       # for packet in packet_start_times:
#       #   print_start_times.append(packet.num)
    
#       # print(print_start_times)
#       window += 1
#       num_outbound -= 1

#       # instead of checking special packet num == repsonse, check if received[special number - 1] == true
#       if(received_packets[special_packet_num - 1] and num_received < total_length):
#         print("Special packet found")
#         special_packet_num += 1
#         while(received_packets[special_packet_num - 1]):
#           special_packet_num += 1
        
#         print("New special packet: ", special_packet_num)
#         ok_send = True
#     except socket.timeout as ex:
#       for packet in packets:
#         if packet.num in range(special_packet_num, special_packet_num+num_outbound):
#           resend_array.append(packet)

# print("hello")
