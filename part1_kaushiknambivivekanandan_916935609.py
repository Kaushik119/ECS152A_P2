import socket
import os
import time

read_from_file_size = 949

if __name__ == "__main__":
  message = open("message.txt", 'r')
  file_size = os.stat("message.txt").st_size

  port_number = int(input("Enter port number: "))
  Server = ("", port_number)
  
  Socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  Socket.connect(Server)

  test_packet = packet.read(read_from_file_size = 949)
  packet = "1|" + packet

  encoded_packet = str.encode(packet)

  Socket.send(encoded_packet)

  response = Socket.recv(BufferSize).decode()
  print(response)