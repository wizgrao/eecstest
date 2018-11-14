from Receiver import *
from Transmitter import *
from HuffmanCode import *

#create huffman code
huffman_compress("encode.txt","decode.txt")
a = HuffmanCode()
encode=a.compress("test.txt")

#create packet
b = Transmitter(encode)
chunks=b.chunks
packet = b.encode()

#send file
c = Receiver()
count = 0
while not c.isDone() and count<len(packet):
    received=packet[count]
    c.receive_packet(received)
    count+=1
de=c.decoded_chunks

# #check chunks
# for i in range(len(chunks)):
#     assert len(chunks[i])==len(de[i])
#     for j in range(len(chunks[i])):
#         assert chunks[i][j]==de[i][j]

huffman=c.blocks_write()

# # check huffman code
# assert  len(huffman)==len(encode)
# for i in range(len(huffman)):
#     assert huffman[i]==encode[i]

a.decompress(huffman,"huffman.txt")
