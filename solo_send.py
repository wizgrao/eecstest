import reedsolo as rs
from Transmitter import *
from HuffmanCode import *
from sound import transmit, receive
from bitarray import bitarray
import sounddevice as sd
import values


def solo_encode(packet,size,error=4):
    if not isinstance(packet, str):
        packet = str(packet)[str(packet).find('\'') + 1:-2]
    i = 0
    bits = ''
    solomon = rs.RSCodec(error)
    temp = bytearray()
    while i < size // 8:
        temp.append(int(packet[i * 8:(i + 1) * 8], 2))
        i += 1
    pack = solomon.encode(temp)
    for b in pack:
        bits += bin(b)[2:].rjust(8, '0')
    return bits


a = HuffmanCode()
encode=a.compress("test.txt")
b = Transmitter(encode)
chunks=b.chunks
packet = b.encode()

bits=''
packet_size=3*8

for p in packet:
    bits+=solo_encode(p, packet_size)



print("sending")
transmit(bitarray(bits), baud=values.baud, signal_cf=values.sig_cf, fdev=values.delta, fs=values.fs)

sd.wait()
