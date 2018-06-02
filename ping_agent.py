import socket
import time
import argparse
import struct
import array
import select
import math

ICMP_ECHO_REQUEST = 8

def parse():
    parser = argparse.ArgumentParser()
    parser.add_argument('--sender', default=False, type=str2bool, help='the agent type')
    parser.add_argument('-p', default="123456789ABCDEF", type=str, help='ping pattern')
    parser.add_argument('--verbose', default=False, type=str2bool, help='ask you if print log out')
    parser.add_argument('--endless', default=False, type=str2bool, help='if we transfer one file and recv an EOF, we done if not endless')
    parser.add_argument('--interval', default=0, type=int, help='verbose interval time')
    parser.add_argument('--ping', default=False, type=str2bool, help='ping?')
    parser.add_argument('--input', default="file/INPUT.txt", type=str, help='the input file')
    parser.add_argument('--output', default="inter/OUTPUT.txt", type=str, help='the output file')
    parser.add_argument('--setup', default=False, type=str2bool, help='setup')
    parser.add_argument('--address', default='127.0.0.1', type=str, help='ip address')
    parser.add_argument('--port1', default=9999, type=int, help='object port')
    parser.add_argument('--port0', default=9999, type=int, help='my port')
    opt = parser.parse_args()

    sender = opt.sender
    if sender:
        print("=> I am a Tx!")
    else:
        print("=> I am a Rx!")
    if opt.p:
        print("PATTERN: %s"%(opt.p))

    if (opt.ping):
        opt.interval = 1
    return opt

def str2bool(v):
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False

def check_sum(source):
    checksum = 0
    count = (len(source) / 2) * 2
    i = 0
    while i < count:
        temp = ord(source[i + 1]) * 256 + ord(source[i]) # 256 = 2^8
        checksum = checksum + temp
        checksum = checksum & 0xffffffff # 4,294,967,296 (2^32)
        i = i + 2
    if i < len(source):
        checksum = checksum + ord(source[len(source) - 1])
        checksum = checksum & 0xffffffff
    checksum = (checksum >> 16) + (checksum & 0xffff)
    checksum = checksum + (checksum >> 16)
    answer = ~checksum
    answer = answer & 0xffff
    answer = answer >> 8 | (answer << 8 & 0xff00)
    return answer

def icmp_packet(data, icmp_seq, start_time):
    data = struct.pack("d", start_time) + data
    header = struct.pack('bbHHh', ICMP_ECHO_REQUEST, 0, 0, 0, icmp_seq)
    packet = header + data
    header = struct.pack('bbHHh', ICMP_ECHO_REQUEST, 0, socket.htons(check_sum(packet)), 0, icmp_seq) # TYPE CODE CHKSUM ID SEQ
    return header + data

def receive_ping(my_socket, ID):
    """
    receive the ping from the socket
    """
    while 1:
        try:
            rec_packet, addr = my_socket.recvfrom(1024)
            time_received = time.clock()
            icmp_header = rec_packet[20 : 28]
            ip_type, code, checksum, packet_ID, sequence = struct.unpack("bbHHh", icmp_header)
            if ip_type != 8 and packet_ID == ID: # ip_type should be 0
                byte_in_double = struct.calcsize("d")
                time_sent = struct.unpack("d", rec_packet[28 : 28 + byte_in_double])[0]
                pattern = rec_packet[28 + byte_in_double: ]
                return time_received - time_sent, pattern
        except socket.timeout:
            print "time out"
        except KeyboardInterrupt:
            print("\n-----------------------------------------" )
            exit(0)

def main():


    opts = parse()

    # ** object setting
    object_IP = opts.address
    objcet_port = opts.port1
    object_addr = (object_IP, objcet_port )
    object_addr_str = '[' + object_addr[0] + ":"+ str(object_addr[1]) + ']'
    # ** local setting


    if opts.ping :
        s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.getprotobyname("icmp"))
    else:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(1)
    my_IP = socket.gethostbyname(socket.gethostname())
    my_port = opts.port0
    my_addr = (my_IP, my_port)
    my_addr_str = '['+ str(my_IP) +':'+str(my_port)+']'

    s.bind((my_IP, my_port))
    print("set the address at" + my_addr_str)
    if (opts.setup):
        exit(0)
    ##########################################
    f = open(opts.input, 'r')
    

    total_msg = ""
    count = 0;
    last_second = time.time()
    time_out = False
    period_delay = []
    ##########################################
    while 1:
        if opts.sender :
            
            buff = opts.p if opts.ping else f.readline()
            if (buff == ""):
                s.sendto("END".encode(), object_addr)
                print("=> the send progress is end")
                break;

            start_time = time.time()
            s.sendto(icmp_packet(buff, count, start_time), object_addr) 
            try:
                rec_packet, addr = s.recvfrom(1024)
                byte_in_double = struct.calcsize("d")
                time_sent = struct.unpack("d", rec_packet[28 : 28 + byte_in_double])[0]
                period_delay.append((time.time() - time_sent))
                # print( last_second, time.time(), time.time() - last_second )
                if (time.time() - last_second > 1):
                    last_second = time.time()
                    time_diff = (sum(period_delay)/(len(period_delay)) * 1000)
                    log_str = "%d bytess"%len(rec_packet) +" from %s: "%addr[0] \
                        + "icmp_seq=%d "%count + "time=%0.3f "%(time_diff) + "ms"    
                    print log_str,
                    print "=> PATTERN is \""+rec_packet[28+byte_in_double:]+"\""
                    period_delay=[]
                else:
                    pass
                
            except socket.timeout:
                if (time.time() - last_second > 1):
                    print "time out"
                    last_second = time.time()


            # delay, data = receive_ping(s, 0)
        else:
            try:
                data, (addr, port) = s.recvfrom(1024)
                s.sendto(b'byte'*16, (addr, port))
                if (data.decode() == "END"):
                    print(other_addr + ' : EOF')
                    fout = open(opts.output, 'w')
                    fout.write(total_msg)
                    if (not opts.endless):
                        break
                payload_len = len(data)
                other_addr =  '[' + str(addr)+':'+str(port) + ']'
                if (opts.verbose):
                    print(other_addr + ' : ' + data.decode('utf-8') )
                total_msg += data.decode()
            except socket.timeout as e:
                pass
            except KeyboardInterrupt:
                print("\n-----------------------------------------" )
                exit(0)
    s.close()


if __name__ == '__main__':
    main()