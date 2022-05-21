import socket
import os
import sys

read_from_file_size = 949
timeout_seconds = 5
delimiter = "|"
cwnd = 1
ssthresh = 16
BufferSize = 100

def main():
  message = open("message.txt", 'r')
  file_size = os.stat("message.txt").st_size
  start_at = 0

  port_number = int(sys.argv[1])
  Server = ("127.0.0.1", port_number)
  Socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  Socket.connect(Server)
  
  message_counter = 1
  while(start_at <= file_size):
    packet = message.read(read_from_file_size)
    packet = str(message_counter) + "|" + packet
    message_counter += 1
    encoded_packet = str.encode(packet)
    Socket.send(encoded_packet)
    response = Socket.recv(BufferSize)
    print(response)


  print(file_size)
  print(start_at)


if __name__ == "__main__":
  main()