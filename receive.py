from Receiver import *
from Transmitter import *
from HuffmanCode import *
from checksum import *
from sound import transmit, receive
from bitarray import bitarray
from checksum import Packet as Pack
a = HuffmanCode()


c = Receiver()

packets = receive(packet_size=8+16+8, baud=50, signal_cf=800, clock_cf=1400, fdev=300, fs=48000, duration=30, taps=50, width = 100)

count=0
while not c.isDone() and count<len(packets):
    received=packets[count]
    s = ""
    for b in received:
        s+=str(b)
    if len(s) != 8+16+8:
        count+=1
        continue
    check=Pack(s, sent=True)
    if check.check_checksum():
        print("received packet")
        temp=check.get_received_packet()
        temp=bytearray(temp, 'utf8')
        c.receive_packet(temp)
    count+=1
de=c.decoded_chunks

final = c.blocks_write()
a.decompress(final,  "out.txt")
