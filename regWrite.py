import sys,socket,struct

sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
TCP_IP = 'localhost'
TCP_PORT = 1234
sock.connect((TCP_IP,TCP_PORT))

msg1 = "abcd1234"
msg2 = "FE170002"
msg3 = "00000005"
msg4 = "00000000"
msg = [socket.htonl(int(msg1,16)),socket.htonl(int(msg2,16)),socket.htonl(int(msg3,16)),socket.htonl(int(msg4,16))]
msg = struct.pack("<4I",*msg)
print repr(msg)
sock.sendall(msg)
sock.close()
