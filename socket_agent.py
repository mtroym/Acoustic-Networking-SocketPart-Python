import socket
import time
import argparse


def parse():
    parser = argparse.ArgumentParser()
    parser.add_argument('--sender', default=False, type=str2bool, help='the agent type')
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

    if (opt.ping):
        opt.interval = 1
    return opt

def str2bool(v):
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False


def main():


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
    ##########################################
    while 1:
        if sender :
            
            buff = "0" if opts.ping else f.readline()
            if (buff == ""):
                s.sendto("END".encode(), object_addr)
                print("=> the send progress is end")
                break;

            start_time = time.time()
            s.sendto(buff.encode(), object_addr) 
            try:
                data, (addr, port) = s.recvfrom(1024)
            except Exception as e:
                log_str = "Request timeout for icmp_seq %d"%count
                time_out = True
            recent_time = time.time()
            time_diff = recent_time - start_time
            time_line = recent_time - last_second
            if (time_line > opts.interval):
                if (not time_out):
                    log_str = "%d bytess"%len(data.decode()) +" from %s: %d "%(addr,port) \
                        + "icmp_seq=%d "%count + "time=%0.4f"%(time_diff * 1000) + "ms"                
                print(log_str)
                last_second = recent_time
                time_out = False
                count += 1
            # print("object said:" + data.decode('utf-8'))
    #             print( my_addr_str + ' : ' + msg)
        else:
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
            print(other_addr + ' : ' + data.decode('utf-8') )
            total_msg += data.decode()
    s.close()


if __name__ == '__main__':
    main()