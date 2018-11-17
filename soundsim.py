from sound import *
from Receiver import *
from checksum import Packet as Pack
from Transmitter import *
from HuffmanCode import *
from bitarray import bitarray
import sounddevice as sd

sample = 500
a = HuffmanCode()
encode=a.compress("test.txt")

b = Transmitter(encode)
chunks=b.chunks
packet = b.encode(1)
final_packet=[]
for p in packet:
        check=Pack(p)
        final_packet.append(check.get_final_packet())
bits = ""
for p in final_packet:
        bits += p

sig = genSignal(bitarray(bits), baud=200, signal_cf=5000, clock_cf=2000, fdev=600, fs=48000, packet_size=128+16+32)
print("done creating signal")
from Receiver import *
from Transmitter import *
from HuffmanCode import *
from checksum import *
from sound import transmit, receive
from bitarray import bitarray
from checksum import Packet as Pack
a = HuffmanCode()


c = Receiver()
print("started decoding")
packets = receiveFromSignal(sig, packet_size=8+16+8, baud=200, signal_cf=5000, clock_cf=2000, fdev=600, fs=48000, duration=30, taps=50, width = 100)
print(packets)
count=0
acc = 0
print ("ended decoding")
print(c.isDone(), len(packets))
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
        acc += 1
        temp=check.get_received_packet()
        temp=bytearray(temp, 'utf8')
        print("received packet", temp)
        c.receive_packet(temp)
    else:
        print("rejected packet")
    count+=1
de=c.decoded_chunks

final = c.blocks_write()
print(final)
a.decompress(final,  "out.txt")

