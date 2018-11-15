from Receiver import *
from Transmitter import *
from HuffmanCode import *
from sound import transmit, receive
from bitarray import bitarray
a = HuffmanCode()
encode=a.compress("test.txt")

#create packet
b = Transmitter(encode)
chunks=b.chunks
packet = b.encode()

bits = ""
for p in packet:
    bits += p.decode('utf8')


transmit(bitarray(bits), baud=200, signal_cf=800, clock_cf=1400, fdev=300, fs=11025, packet_size=128+16+32)

sd.wait()

