import socket
import time
import argparse


def parse():
    parser = argparse.ArgumentParser()
    parser.add_argument('--sender', default=False, type=str2bool, help='the agent type')
    parser.add_argument('--setup', default=False, type=str2bool, help='setup')
    parser.add_argument('--address', default='127.0.0.1', type=str, help='ip address')
    parser.add_argument('--port1', default=9999, type=int, help='object port')
    parser.add_argument('--port0', default=9999, type=int, help='my port')
    opt = parser.parse_args()
    return opt

def str2bool(v):
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False

opts = parse()

sender = opts.sender
if sender:
    print("=> I am a Tx!")
else:
    print("=> I am a Rx!")
# ** object setting
object_IP = opts.address
objcet_port = opts.port1
object_addr = (object_IP, objcet_port )
object_addr_str = '[' + object_addr[0] + ":"+ str(object_addr[1]) + ']'
# ** local setting
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
my_IP = socket.gethostbyname(socket.gethostname())
my_port = opts.port0
my_addr = (my_IP, my_port)
my_addr_str = '['+ str(my_IP) +':'+str(my_port)+']'

s.bind((my_IP, my_port))
print("set the address at" + my_addr_str)
if (opts.setup):
    exit(0)
##########################################
payload = "1234567890" * 10
start_time = time.time()
count = 0;
##########################################
while 1:
    if sender :
        time_diff = time.time() - start_time
        if (count >= 10.0):
            s.sendto("END", object_addr)
            print("=> the send progress is end")
            break;
        if (time_diff > 1 and int(time_diff * 1000) % 1000 == 0):
            s.sendto(payload, object_addr)
            start_time += 1
            count += 1
#             data, (addr, port) = s.recvfrom(1024)
#             msg = data.decode('utf-8')
#             print( my_addr_str + ' : ' + msg)
    else:
        data, (addr, port) = s.recvfrom(1024)
        if (data == "END"):
            print(other_addr + ' : EOF')
            break;
        payload_len = len(data)*8
        info = 'payload:' + str(payload_len) +' Bytes'
        other_addr =  '[' + str(addr)+':'+str(port) + ']'
        print(other_addr + ' : ' + info ) 
        # s.sendto(b'got one!', (addr, port))
s.close()