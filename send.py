from Receiver import *
from checksum import Packet as Pack
from Transmitter import *
from HuffmanCode import *
from sound import transmit, receive
from bitarray import bitarray
import sounddevice as sd

a = HuffmanCode()
encode=a.compress("test.txt")

b = Transmitter(encode)
chunks=b.chunks
packet = b.encode()
final_packet=[]
for p in packet:
    check=Pack(p)
    # print(check.checksum)
    # print(check.total_data)

    final_packet.append(check.get_final_packet())

#
bits = ""
for p in final_packet:
    print(p)
    bits += p

print("sending")
transmit(bitarray(bits), baud=50, signal_cf=800, clock_cf=1400, fdev=300, fs=48000, packet_size=32)

sd.wait()
