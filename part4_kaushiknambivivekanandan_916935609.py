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
cwnd = 1
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
  print("Current Window:",list(range(packet_count + start_index - 1, packet_count + cwnd)))
  print("Sequence Number of Packet sent:", packet_count)
  print("Acknowledgement Number Received:", response, "\n")

def main():
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

  # Flag to keep account of whether the congestion window is in congestion control
  in_congestion = False
  
  # Bringing global variables into scope
  global ssthresh
  global cwnd
  global timeout_seconds
  global start_index
  
  # Variables to dynamically calculate timeout
  EstimatedRTT = 0
  DevRTT = 0
  alpha = 0.875
  alpha_1 = 0.125
  beta = 0.25
  beta_1 = 0.75
  
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
    current_cwnd = min(len(packets) - packet_count,cwnd)
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
 
        # if it is slow start
        if is_slow_start():
          # Increase window
          cwnd += 1
          in_congestion = False
        else:
          # do congestion control
          if in_congestion == False:
            cwnd += 1
            in_congestion = True

        # If the response is on the left hand side of the cwnd
        # then move the window by 1
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
        ssthresh = int(cwnd*0.8)
        cwnd = int(cwnd*0.3)
        in_congestion = False
    
    # Reset congestion flag and calculate dynamic timeout
    in_congestion = False
    SampleRTT = RTTTimes[RTTLast-1]
    EstimatedRTT = alpha_1*EstimatedRTT + alpha*(SampleRTT)
    DevRTT = beta_1*DevRTT + beta*(SampleRTT- EstimatedRTT)
    timeout_seconds = EstimatedRTT+4*DevRTT

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
  image_name = "Part4_RTT"+str(port_number)+".png"
  plt.savefig("Images/"+image_name)
  
  # Clear the plot
  plt.clf()

  # Create graph for Per packet throughput
  Throughput = sns.lineplot(x = range(0, len(PPThroughput)),y = PPThroughput)
  Throughput.set(xlabel = "Packet Number", ylabel = "Per Packet Throughput", title = "PPT for Packets on Port " + str(port_number))

  # Save the figure in the image folder 
  image_name = "Part4_PPT"+str(port_number)+".png"
  plt.savefig("Images/"+image_name)
  
# Main function
if __name__ == "__main__":
  main()