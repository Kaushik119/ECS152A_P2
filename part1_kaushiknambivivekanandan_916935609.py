import socket
import os
import time
import math
import seaborn as sns
import matplotlib.pyplot as plt
import sys

read_from_file_size = 1000
BufferSize = 100

if __name__ == "__main__":
  message = open("message.txt", 'r')
  file_size = os.stat("message.txt").st_size

  port_number = int(input("Enter port number: "))
  Server = ("", port_number)
  
  Socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  Socket.connect(Server)

  cur_file_size = 0
  packet_num = 1
  create_new_packet = True
  test_packet = ""
  delays = []

  while(cur_file_size < file_size):
    if(create_new_packet):
      test_packet = message.read(read_from_file_size)
      test_packet = str(packet_num) + "|" + test_packet
      start = time.time()

    encoded_packet = str.encode(test_packet)

    Socket.settimeout(5)

    try:
      Socket.send(encoded_packet)

      response = Socket.recv(BufferSize).decode()
      end = time.time()
      delays.append(end - start)

      print()
      print("Current Window: [" + str(packet_num) + "]")
      print("Sequence Number of Packet Sent: " + str(packet_num))
      print("Acknowledgement Number Received: " + str(packet_num))
      print()

      packet_num += 1
      cur_file_size += 1000
      create_new_packet = True
    except socket.timeout as ex:
      create_test_packet = False
  
  delay_avg = sum(delays) / len(delays)
  throughput_avg = cur_file_size * 8 / sum(delays)


  print("Average Delay = <" + str(delay_avg) + ">")
  print("Average Throughput = <" + str(throughput_avg) + ">")
  print("Performance = <" + str(math.log(throughput_avg, 10) - math.log(delay_avg, 10)) + ">")

  packet_size = sys.getsizeof(test_packet) * 8
  ppt = []
  for delay in delays:
    ppt.append(packet_size / delay)

  
  RTT = sns.lineplot(x = range(0, len(delays)),y = delays)
  RTT.set(xlabel = "Packet Number", ylabel = "RTT", title = "RTT for Packets on Port " + str(port_number))

  image_name = "Part1_RTT"+str(port_number)+".png"
  plt.savefig("Images/"+image_name)

  plt.clf()

  Throughput = sns.lineplot(x = range(0, len(ppt)),y = ppt)
  Throughput.set(xlabel = "Packet Number", ylabel = "Per Packet Throughput", title = "PPT for Packets on Port " + str(port_number))

  image_name = "Part1_PPT"+str(port_number)+".png"
  plt.savefig("Images/"+image_name)


      
  


