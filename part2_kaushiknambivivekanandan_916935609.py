import socket
import os
import time
import math

read_from_file_size = 1000
BufferSize = 100
window = 5

class Packet:
  def __init__(self, num, info):
    self.num = num
    self.info = info

class Timing:
  def __init__(self, num, start_time):
    self.num = num
    self.start_time = start_time
  
  def __eq__(self, other):
    return self.num == other.num    

packets = []

message = open("message.txt", 'r')
file_size = os.stat("message.txt").st_size

cur_file_size = 0
packet_num = 1
while(cur_file_size < file_size):
  packets.append(Packet(packet_num, str(packet_num) + "|" + message.read(read_from_file_size)))
  packet_num += 1
  cur_file_size += 1000

packet_start_times = []
special_packet_num = 1

received_packets = [False] * len(packets)
num_received = 0
num_outbound = 0
resend_array = []
ok_send = True
prev_response = True

port_number = int(input("Enter port number: "))
Server = ("", port_number)

Socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
Socket.connect(Server)

total_length = len(packets)
temp_packets = packets
while(num_received < total_length):
  # print("Num outbound", num_outbound, " OK SEND", ok_send)
  while(len(resend_array) > 0):
    resend = resend_array.pop(0)
    print("Resending packet num: " + str(packets[resend.num - 1].num))
    Socket.send(str.encode(packets[resend.num - 1].info))

    for packet in packet_start_times:
      if(packet.num == resend.num):
        packet.start_time = time.time()
  

  if(ok_send):
    while(window != 0):
      if(len(temp_packets) != 0):
        packet = temp_packets.pop(0)
      Socket.send(str.encode(packet.info))
      # print(packet.info)
      print("Sending packet num: " + str(packet.num))
      packet_start_times.append(Timing(packet.num, time.time()))
      num_outbound += 1
      window -= 1

    ok_send = False
  
  while(num_outbound > 0):
    print("num outbound > ", num_outbound)

    check_timeout = time.time()
    timeout_flag = False

    for packet in packet_start_times:
      if(check_timeout - packet.start_time > 5):
        print("Packet num: ", packet.num, " TIMED OUT")
        resend_array.append(packet)
        timeout_flag = True

    if(timeout_flag):
      break
    
    Socket.settimeout(5)
    try:
      print("Waiting for packet")
      response = Socket.recv(BufferSize).decode()
      print("BEFORE setting receive: ", received_packets[int(response) - 1])
      for i in range(special_packet_num, int(response)):
        received_packets[i] = True
      # for every index less than response, set received to true
      for i in range(0, int(response)):
        received_packets[i] = True
      print("AFTER setting receive: ", received_packets[int(response) - 1])
      print("Recieved packet num: ", response)
      # num_received += 1
      print("NUM rec:", num_received)

      new_responses = int(response) - special_packet_num + 1
      num_received += new_responses
      
      index = 0
      for packet in packet_start_times:
        if packet.num <= int(response):
          packet_start_times.pop(index)
        else:
          index += 1
      
      print("Packet start times length", len(packet_start_times))

      # print_start_times = []
      # for packet in packet_start_times:
      #   print_start_times.append(packet.num)
    
      # print(print_start_times)
      window += 1
      num_outbound -= 1

      # instead of checking special packet num == repsonse, check if received[special number - 1] == true
      if(received_packets[special_packet_num - 1] and num_received < total_length):
        print("Special packet found")
        special_packet_num += 1
        while(received_packets[special_packet_num - 1]):
          special_packet_num += 1
        
        print("New special packet: ", special_packet_num)
        ok_send = True
    except socket.timeout as ex:
      for packet in packets:
        if packet.num in range(special_packet_num, special_packet_num+num_outbound):
          resend_array.append(packet)

print("hello")
