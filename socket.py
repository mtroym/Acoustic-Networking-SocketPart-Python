import socket
import time
sender = True
# ** object setting
object_IP = '10.20.196.117'
objcet_port = 1234
object_addr = (object_IP, objcet_port )
object_addr_str = '[' + object_addr[0] + ":"+ str(object_addr[1]) + ']'
# ** local setting
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
my_IP = socket.gethostbyname(socket.gethostname())
my_port = 1234
my_add = (my_IP, my_port)
my_addr_str = '['+ str(my_IP) +':'+str(my_port)+']'

s.bind((my_IP, my_port))
print("set the address at" + my_addr)
##########################################
payload = "1234567890" * 10
start_time = time.time()
count = 0;
##########################################
while 1:
    if sender :
        time_diff = time.time() - start_time
        if (count >= 10.0):
            break;
        if (time_diff > 1 and int(time_diff * 1000) % 1000 == 0):
            s.sendto(payload, object_addr)
            start_time += 1
            count += 1
#             data, (addr, port) = s.recvfrom(1024)
#             msg = data.decode('utf-8')
#             print( my_addr + '->'+object_addr_str+' : ' + msg)
    else:
        data, (addr, port) = s.recvfrom(1024)
        payload_len = len(data)*8
        info = 'payload:' + str(payload_len) +' Bytes'
        other_addr =  '[' + str(addr)+':'+str(port) + ']'
        print(my_addr + '->' + other_addr + ' : ' + info ) 
        s.sendto(b'got one!', (addr, port))
s.close()