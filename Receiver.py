import numpy as np


class Packet:
    def __init__(self, data, indices):
        self.data = data
        self.indices = indices

class Receiver:

    def __init__(self, chunk_size=32):
        self.received_packets = []
        self.chunk_size = chunk_size
        self.decoded_chunks = [0] * self.chunk_size
        self.found = [ False for _ in range(self.chunk_size)]
        self.packet_indices=[]

    def receive_packet(self,p):
        """
        Take received packet and decode using LT code
        :param p: received packet
        :return: None
        """
        if p is not None:
            indices = self.get_indices(p)
            data=p[:-self.chunk_size//8]
            packet = Packet(np.frombuffer(data,np.uint8),indices)

            self.received_packets.append(packet)
            for chunk_idx in indices:
                if self.found[chunk_idx]:
                    packet.indices.remove(chunk_idx)
                    packet.data = np.bitwise_xor(packet.data, self.decoded_chunks[chunk_idx])
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

    def blocks_write(self):
        """
        Convert decoded chunks into huffman code (byte str)
        :return: huffman code
        """
        self.uint8_to_byte()
        huffman_code=bytearray()
        for data in self.decoded_chunks:
            pad_info = data[-1]
            huffman_code+=data[:-pad_info]

        return bytes(huffman_code)

    def isDone(self):
        return self.chunksDone() == self.chunk_size

    def chunksDone(self):
        return sum(self.found)

    def uint8_to_byte(self):
        for i in range(len(self.decoded_chunks)):
            self.decoded_chunks[i]=bytearray(self.decoded_chunks[i])

    def get_indices(self,packet):
        """
        Get indices array from decode packet
        :param packet: packet
        :return: indices array
        """
        bits=""
        for i in range(self.chunk_size//8):
            bits+=bin(packet[(-self.chunk_size // 8)+i])[2:].rjust(8, '0')
        return [pos for pos, char in enumerate(bits) if char == "1"]
