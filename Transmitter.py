from distribution import *
import random
import numpy as np


class Transmitter:
    def __init__(self,code,chunk_size=32):
        self.code=code
        self.chunk_size=chunk_size
        self.chunks = self.blocks_read(self.code)

    def blocks_read(self,huffman_code):
        """
        Read huffman code( byte str) and divide into chunks.
        Default chunks size in 32 (4 bytes)
        chunk structure: data (+ extra pad )+padding info (1 byte)
        :param huffman_code: byte string
        :return: chunks
        """
        chunks = []
        data_size= 128
        huffman_code += str(bytearray(data_size*self.chunk_size - len(huffman_code)))
        for i in range(self.chunk_size):
            data = huffman_code[i*data_size:(i+1)*data_size]
            chunks.append(data)
        # add extra padding
        return chunks

    def encode(self,repeat_num=10):
        """
        Combine chunks into packet based on LT code
        packet structure: chunks data + indices (equals chunk_size//8 bytes)
        :param repeat_num: total number of sending packet = (repeat_num*chunk_size)
j       :return: packets
        """
        packets=[]
        degree = robust_distribution(self.chunk_size,repeat_num)
        for i in range(repeat_num*self.chunk_size):
            chunk_indices = random.sample(range(self.chunk_size),degree[i])
            encoded_text = self.chunks[chunk_indices[0]]
            for j in range(1, degree[i]):
                encoded_text = np.bitwise_xor(encoded_text, self.chunks[chunk_indices[j]])
            #  adding indices
            indices=[0]*self.chunk_size
            indices_str=""
            for n in range(degree[i]): indices[chunk_indices[n]]= 1
            for k in range(self.chunk_size):indices_str+="1" if indices[k]==1 else "0"
            encoded_text=bytearray(encoded_text, 'utf8')
            temp=bytearray()
            for i in range(0,self.chunk_size//8):
                temp.append(int(indices_str[i*8:(i+1)*8],2))
            encoded_text+=temp
            packets.append(encoded_text)
        return packets
