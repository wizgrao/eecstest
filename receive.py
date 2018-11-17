from Receiver import *
from Transmitter import *
from HuffmanCode import *
from checksum import *
from sound import transmit, receive
from bitarray import bitarray
from checksum import Packet as Pack
import values
a = HuffmanCode()


c = Receiver()

packets = receive(packet_size=8+16+8, baud=values.baud, signal_cf=values.sig_cf, clock_cf=values.clock_cf, fdev=values.delta, fs=values.fs, duration=30, taps=50, width = 200)

count=0
while not c.isDone() and count<len(packets):
    received=packets[count]
    s = ""
    for b in received:
        s+=str(b)
    if len(s) != 8+16+8:
        print('wrong number of bits')
        count+=1
        continue
    check=Pack(s, sent=True)
    if check.check_checksum():
        temp=check.get_received_packet()
        temp=bytearray(temp, 'utf8')
        print("received", temp)
        c.receive_packet(temp)
    else:
        print('corrupted')
    count+=1
de=c.decoded_chunks

final = c.blocks_write()
a.decompress(final,  "out.txt")
