import socket
import os

# TCP TAHOE IMPLEMENTED AS DESCRIBED IN TEXTBOOK

read_from_file_size = 949
timeout_seconds = 5
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
  past_packets = []
  prev_response = 0
  message_counter = 1
  in_congestion = False
  response = 1
  dupAckCount = 0

  while(start_at < file_size):
    for i in range(0 ,cwnd):
      packet = message.read(read_from_file_size)
      start_at += len(packet)
      packet = str(message_counter) + "|" + packet
      message_counter += 1
      past_packets.append(packet)

      encoded_packet = str.encode(packet)

      Socket.send(encoded_packet)
      
    current_cwnd = cwnd
    recv_counter = 0
    
    while recv_counter < current_cwnd:
      Socket.settimeout(timeout_seconds)
      try:
        response = Socket.recv(BufferSize).decode()
        recv_counter += 1
        if prev_response == response:
          # do duplicate acknowledgement
          # decrease cwnd to 1
          if dupAckCount == 3:
            raise socket.timeout # If three duplicate acknowledgements were received then equivalent to timeout (from textbook)
          dupAckCount += 1
          Socket.send(str.encode(past_packets[response+1]))
          cwnd = 1
        else:
          dupAckCount = 0
          prev_response = response
          if is_slow_start():
            # do slow start
            cwnd += 1
            in_congestion = False
          else:
            # do congestion control
            if in_congestion == False:
              cwnd += 1
              in_congestion = True
        print(response)
      
      except socket.timeout:
        # timeout deal
        # decrease cwnd to 1
        ssthresh = int(cwnd/2)
        cwnd = 1
        in_congestion = False

    
    in_congestion = False

      
if __name__ == "__main__":
  main()