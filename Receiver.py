import numpy as np
import checksum as c

class Packet:
    def __init__(self, data, indices):
        self.data = data
        self.indices = indices

class Receiver:

    def __init__(self, chunk_size=32):
        self.received_packets = []
        self.chunk_size = chunk_size
        self.decoded_chunks = [0] * self.chunk_size
        self.found = [False for _ in range(self.chunk_size)]
        self.packet_indices=[]

    def check_packet(self, p):
        '''
        Function: Takes received packet p and determines whether it has been corrupted or not
        Input: Received packet p, taken as string of length 16+128+32
        Output: Boolean, True if packet is uncorrupted, false otherwise
        '''
        instance = Packet_2(p, sent = True)
        return instance.check_checksum()

    def receive_packet(self,p):
        """
        Take received packet and decode using LT code
        :param p: received packet
        :return: None
        """
        if p is not None:
            data,indices=self.seperate_indices_data(p)
            packet = Packet(data,indices)

            self.received_packets.append(packet)
            for chunk_idx in indices:
                if self.found[chunk_idx]:
                    packet.indices.remove(chunk_idx)
                    packet.data = np.bitwise_xor(packet.data, self.decoded_chunks[chunk_idx])
                    packet.data = bytearray(''.join(map(str,packet.data)),'utf8')
            if len(indices) == 1:
                self.peeling()

    def peeling(self):
        """
        Helper Function
        :return: None
        """
        flag = True
        idx = 0
        while flag:
            flag = False
            for packet in self.received_packets:
                if len(packet.indices) == 1:  # Found a singleton
                    flag = True
                    idx = packet.indices[0]
                    break

            # First, declare the identified chunk
            if not self.found[idx]:
                self.decoded_chunks[idx] = packet.data
                self.found[idx] = True
            # Second, peel it off from others
            for packet in self.received_packets:
                if idx in packet.indices:
                    packet.indices.remove(idx)
                    packet.data = np.bitwise_xor(packet.data, self.decoded_chunks[idx])
                    packet.data = bytearray(''.join(map(str, packet.data)), 'utf8')

    def blocks_write(self):
        """
        Convert decoded chunks into huffman code (byte str)
        :return: huffman code
        """
        huffman_code=''
        for data in self.decoded_chunks:
            huffman_code+=str(data)[str(data).find('\'')+1:-2]
        return huffman_code

    def isDone(self):
        return self.chunksDone() == self.chunk_size

    def chunksDone(self):
        return sum(self.found)

    def seperate_indices_data(self,p):
        byte2str=str(p)[str(p).find('\'')+1:-2]
        data=bytearray(byte2str[:-32],'utf8')
        indices=byte2str[-32:]
        return data,[pos for pos, char in enumerate(indices) if char == "1"]


