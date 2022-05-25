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

port_number = int(input("Enter port number: "))
Server = ("", port_number)

Socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
Socket.connect(Server)

total_length = len(packets)
while(num_received < total_length):
  print("Num outbound", num_outbound, " OK SEND", ok_send)
  while(len(resend_array) > 0):
    resend = resend_array.pop(0)
    print("Resending packet num: " + str(resend.num))
    Socket.send(str.encode(resend.info))

    for packet in packet_start_times:
      if(packet.num == resend.num):
        packet.start_time = time.time()
  

  if(ok_send):
    while(window != 0):
      if(len(packets) != 0):
        packet = packets.pop(0)
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
      received_packets[int(response) - 1] = True
      print("AFTER setting receive: ", received_packets[int(response) - 1])
      print("Recieved packet num: ", response)
      num_received += 1
      print("NUM rec:", num_received)
      for packet in packet_start_times:
        if packet.num == int(response):
          packet_start_times.remove(packet)
      
      window += 1
      num_outbound -= 1

      if(int(response) == special_packet_num and num_received < total_length):
        print("Special packet found")
        special_packet_num += 1
        while(received_packets[special_packet_num - 1]):
          special_packet_num += 1
        
        print("New special packet: ", special_packet_num)
        ok_send = True
    except socket.timeout as ex:
      print("BRUH MOMENT (all packets timed out)")
      for packet in packet_start_times:
        resend_array.append(packet)
          
print("hello")


# if __name__ == "__main__":
#   message = open("message.txt", 'r')
#   file_size = os.stat("message.txt").st_size

#   port_number = int(input("Enter port number: "))
#   Server = ("", port_number)
  
#   Socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#   Socket.connect(Server)

#   cur_file_size = 0
#   packet_num = 1
# #   create_new_packet = True
#   test_packet = ""
# #   delays = []

#   packets = []
#   while(cur_file_size < file_size):
#     packets.append(str(packet_num) + "|" + message.read(read_from_file_size))
#     packet_num += 1
#     cur_file_size += 1000
  

#   while()

#   while(cur_file_size < file_size):
#     test_packet = message.read(read_from_file_size)
#     test_packet = str(packet_num) + "|" + test_packet
#     start = time.time()

#     encoded_packet = str.encode(test_packet)

#     Socket.settimeout(5)

#     try:
#       Socket.send(encoded_packet)

#       response = Socket.recv(BufferSize).decode()
#       end = time.time()
#       delays.append(end - start)

#       print()
#       print("Current Window: [" + str(packet_num) + "]")
#       print("Sequence Number of Packet Sent: " + str(packet_num))
#       print("Acknowledgement Number Received: " + str(packet_num))
#       print()

#       packet_num += 1
#       cur_file_size += 1000
#       create_new_packet = True
#     except socket.timeout as ex:
#       create_test_packet = False
  
#   delay_avg = sum(delays) / len(delays)
#   throughput_avg = cur_file_size / sum(delays)


#   print("Average Delay = <" + str(delay_avg) + ">")
#   print("Average Throughput = <" + str(throughput_avg) + ">")
#   print("Performance = <" + str(math.log(throughput_avg, 10) - math.log(delay_avg, 10)) + ">")

      
  


