import reedsolo as rs
from Receiver import *
from HuffmanCode import *
from sound import transmit, receive

import values

a = HuffmanCode()
c = Receiver()

def solo_decode(packet,size,error=4):
    i = 0
    bits = ''
    solomon = rs.RSCodec(error)
    temp = bytearray()
    while i < size // 8:
        temp.append(int(packet[i * 8:(i + 1) * 8], 2))
        i += 1
    try:
        pack = solomon.decode(temp)
        for b in pack:
            bits += bin(b)[2:].rjust(8, '0')
        return bits
    except rs.ReedSolomonError:
        print("Fail")
        return -1


packets = receive(packet_size=7*8, baud=values.baud, signal_cf=values.sig_cf, fdev=values.delta, fs=values.fs, duration=120, taps=values.taps, width = 100)

count=0
while not c.isDone() and count<len(packets):
    received=packets[count]
    s = ""
    for b in received:
        s+=str(b)
    if len(s) != 7*8:
        print('wrong number of bits')
        count+=1
        continue
    temp=solo_decode(s,7*8)
    if temp != -1:
        temp = bytearray(temp, 'utf8')
        print("received", temp)
        c.receive_packet(temp)
    count+=1

de=c.decoded_chunks
final = c.blocks_write()
a.decompress(final,  "out.txt")
