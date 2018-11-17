from Receiver import *
from Transmitter import *
from HuffmanCode import *
from checksum import *
from sound import transmit, receive
#create huffman code
#huffman_compress("encode.txt","decode.txt")
a = HuffmanCode()
encode=a.compress("test.txt")

#create packet
b = Transmitter(encode)
chunks=b.chunks
packet = b.encode()
final_packet=[]
for p in packet:
    check=Packet(p)
    # print(check.checksum)
    # print(check.total_data)

    final_packet.append(check.get_final_packet())

#send file
c = Receiver()
count = 0
packet == packet[::-1]
while not c.isDone() and count<len(packet):
    received=final_packet[count]
    print(received)
    check=Packet(received, sent = True)
    print(check.check_checksum())
    if check.check_checksum():

        temp=check.get_received_packet()
        temp=bytearray(temp,'utf8')
        c.receive_packet(temp)
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
