from asyncore import read
from re import S
import socket
import os
import sys

read_from_file_size = 949
timeout_seconds = 5
delimiter = "|"
cwnd = 1
ssthresh = 16
BufferSize = 100

def is_slow_start():
  return cwnd <= ssthresh

def main():
  message = open("message.txt", 'r')
  file_size = os.stat("message.txt").st_size
  start_at = 0

  port_number = int(input("Enter port number: "))
  Server = ("", port_number)
  
  Socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  Socket.connect(Server)
  
  packet = ""
  response = ""
  past_packets = []
  prev_response = 0
  message_counter = 1
  
  while(start_at < file_size):
    for i in range(0 ,cwnd):
      Socket.settimeout(timeout_seconds)
      
      try :
        packet = message.read(read_from_file_size)
        past_packets.append(packet)
        start_at += len(packet)
        packet = str(message_counter) + "|" + packet
        message_counter += 1
        encoded_packet = str.encode(packet)

        Socket.send(encoded_packet)
        response = Socket.recv(BufferSize)
        if prev_response == response.decode():
          # do duplicate acknowledgement
          # decrease cwnd to 1 
          pass

        print(response)
      
      except socket.timeout:
        response = response.decode()
        Socket.send(str.encode(past_packets[response-1]))
        print("timeout")
      
    if is_slow_start():
      # increase cwnd
      pass
    else :
      # congest control
      pass


if __name__ == "__main__":
  main()