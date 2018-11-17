from distribution import *
import random
import numpy as np


class Transmitter:
    def __init__(self,code,chunk_size=256):
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
        a=False
        chunks = []
        data_size= 16
        assert data_size*self.chunk_size > len(huffman_code)
        huffman_code += "0"*(data_size*self.chunk_size - len(huffman_code))
        for i in range(self.chunk_size):
            data = huffman_code[i*data_size:(i+1)*data_size]
            chunks.append(bytearray(data, 'utf8'))
        # add extra padding
        return chunks

    def encode(self,repeat_num = 1):
        """
        Combine chunks into packet based on LT code
        packet structure: chunks data + indices (equals chunk_size//8 bytes)
        :param repeat_num: total number of sending packet = (repeat_num*chunk_size)
j       :return: packets
        """
        packets=[]
        for i in range(repeat_num*self.chunk_size):
            indices_str=""
            j = i%self.chunk_size
            encoded_text = self.chunks[j].copy()
            jstr = np.base_repr(j)
            jstr = ('0'*(8) + jstr)[-8:]
            encoded_text += bytearray(jstr,'utf8')
            packets.append(encoded_text)
        return packets
