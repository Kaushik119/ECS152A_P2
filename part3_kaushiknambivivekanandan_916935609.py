import socket
import os
import time
import statistics
import math

# TCP TAHOE IMPLEMENTED AS DESCRIBED IN TEXTBOOK

read_from_file_size = 1000
timeout_seconds = 5
cwnd = 1
ssthresh = 16
BufferSize = 100
start_index = 1

def is_slow_start():
  return cwnd <= ssthresh

def left_hand_response(response):
  return response == start_index

def printmessage(response, packet_count):
  print("Current Window:",list(range(packet_count + start_index - 1, packet_count + cwnd)))
  print("Sequence Number of Packet sent:", packet_count)
  print("Acknowledgement Number Received:", response, "\n")

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
  prev_response = 0

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
  sent_counter = 0
  ack_array = [False]*len(packets)
  response = 0

  while packet_count < len(packets):
    for i in range(sent_counter ,min(len(packets) - packet_count,cwnd)):
      Socket.send(str.encode(packets[packet_count]))
      # printmessage(response, packet_count+1)
      BeginTimes.append(time.time())
      packet_count += 1
      
    current_cwnd = min(len(packets) - packet_count,cwnd)
    recv_counter = 0
    sent_counter = 0
    while recv_counter < current_cwnd:
      Socket.settimeout(timeout_seconds)
      try:
        response = int(Socket.recv(BufferSize).decode())
        end_time = time.time()
        recv_counter += (response - prev_response)
        # printmessage(response, packet_count+1)
        prev_response = response
        Socket.settimeout(None)

        while RTTLast < response:
          RTTTimes[RTTLast] = end_time - BeginTimes[RTTLast]
          RTTLast += 1
        
        ack_array[0:response] = [True]*(response)
 
        if is_slow_start():
          cwnd += 1
          in_congestion = False
        else:
          # do congestion control
          if in_congestion == False:
            cwnd += 1
            in_congestion = True

        if left_hand_response(response):
          start_index = ack_array.index(False) + 1
          Socket.send(str.encode(packets[packet_count]))
          # printmessage(response, packet_count+1)
          sent_counter+=1
          BeginTimes.append(time.time())
          packet_count += 1


      except socket.timeout:
        Socket.send(str.encode(packets[response]))
        ssthresh = int(cwnd/2)
        cwnd = 1
        in_congestion = False
    

    in_congestion = False
    SampleRTT = RTTTimes[RTTLast-1]
    print(SampleRTT)
    EstimatedRTT = alpha_1*EstimatedRTT + alpha*(SampleRTT)
    DevRTT = beta_1*DevRTT + beta*(SampleRTT- EstimatedRTT)
    timeout_seconds = EstimatedRTT+4*DevRTT


  DelayAvg = statistics.mean(RTTTimes) * 1000
  ThroughputAvg = (file_size*8)/(sum(RTTTimes))
  Performance = math.log10(ThroughputAvg) - math.log10(DelayAvg)

  print("Average Delay =",DelayAvg )
  print("Average Througput=", ThroughputAvg)
  print("Performance =", Performance)
  
if __name__ == "__main__":
  main()