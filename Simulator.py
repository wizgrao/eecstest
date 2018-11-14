from Receiver import *
from Transmitter import *
from HuffmanCode import *
from checksum import *


#create huffman code
#huffman_compress("encode.txt","decode.txt")
a = HuffmanCode()
encode=a.compress("test.txt")

#create packet
b = Transmitter(encode)
chunks=b.chunks
packet = b.encode()


# checksum
final_packet=[]
for p in packet:
    check=Packet(p)
    final_packet.append(check.get_final_packet())



#send file
c = Receiver()
#TODO: add sound.py

while not c.isDone():
    received= "00000000000000"
    #TODO: seperate checksum form packet
    c.receive_packet(received)


de=c.decoded_chunks
huffman=c.blocks_write()

a.decompress(encode,"huffman.txt")
