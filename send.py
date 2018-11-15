from Receiver import *
from Transmitter import *
from HuffmanCode import *
from sound import transmit, receive
from bitarray import bitarray
a = HuffmanCode()
encode=a.compress("test.txt")

b = Transmitter(encode)
chunks=b.chunks
packet = b.encode()
final_packet=[]
for p in packet:
    check=Packet(p)
    # print(check.checksum)
    # print(check.total_data)

    final_packet.append(check.get_final_packet())

#
bits = ""
for p in final_packet:
    bits += p.decode('utf8')


transmit(bitarray(bits), baud=200, signal_cf=800, clock_cf=1400, fdev=300, fs=11025, packet_size=128+16+32)

sd.wait()
