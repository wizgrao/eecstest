import numpy as np

class Packet:
    def __init__(self, input, sent = False):
        '''
        input = String input of bits, length 128 + 32 representing xor of packets
            - Last 32 bits corresponds to the metadata
        '''
        self.sent=sent
        if not isinstance(input, str):
            self.input = byte2str = str(input)[str(input).find('\'') + 1:-2]
        else:
            self.input = input
        if not sent:
            self.packet_size = 16
            self.chunk_size = 8
            self.data = [self.input[self.chunk_size*i:self.chunk_size*(i+1)] for i in range(self.packet_size//self.chunk_size)] #128 Bits
            self.meta_data = self.input[self.packet_size:] #32 Bits
            self.total_data = list(self.data)
            self.total_data.append(self.meta_data[:self.chunk_size])
            #self.total_data.append(self.meta_data[self.chunk_size:])
            self.checksum = self.get_checksum() #16 bits
        else:
            self.packet_size = 16
            self.chunk_size = 8
            self.sent = True
            self.checksum = self.input[:self.chunk_size]
            self.data = [self.input[self.chunk_size*(i+1): self.chunk_size*(i+2)] for i in range(self.packet_size//self.chunk_size)]
            self.total_data = list(self.data)
            self.total_data.append(self.checksum)
            self.meta_data = self.input[self.packet_size + self.chunk_size:]
            self.total_data.append(self.meta_data)

    def get_final_packet(self):
        return ''.join(map(str, self.checksum)) + self.input
    def get_received_packet(self):
        packet= self.input
        return packet[self.chunk_size:]

    def get_complement_sum(self, one, two):
        '''
        Determines complement sum of two equal-sized binary numbers
        Helper function for get_checksum
        '''
        out = [0 for _ in range(self.chunk_size)]
        carry = 0
        #print(one, two)
        one = [int(i) for i in one]
        x = list(two)
        two = [int(i) for i in two[0]]
        #Regular bitwise addition
        for i in range(self.chunk_size):
            i = -(i+1) % self.chunk_size
            out[i] = (one[i] + two[i] + carry) % 2
            carry = max(0, (one[i] + two[i] + carry)//2)

        #Preprocessing for carryover
        one = list(out)
        two = bin(carry)[2:]
        new_two = ''
        for i in range(len(two)):
            if i == len(two) - 1:
                new_two += two[i]
            else:
                new_two += (two[i] + ' ')
        two = new_two.split()
        two = [int(i) for i in two]
        #Carryover addition
        carry = 0
        x = [0 for _ in range(self.chunk_size - len(two))]
        x.extend(two)
        two = x
        #print(out, two)
        for i in range(self.chunk_size):
            i = -(i+1)%self.chunk_size
            out[i] = (one[i] + two[i] + carry) % 2
            carry = max(0, (one[i] + two[i] + carry) - 1)
        #print(out)
        return np.array(out)

    def get_checksum(self):
        '''
        Input: Chunks xor'd together, broken into 16-bit length strings
        Output: Internet checksum of these chunks
        '''
        curr_checksum = np.zeros(self.chunk_size)
        chunks = self.total_data
        # for i in range(len(self.data)//self.chunk_size):
        #     chunks.append(self.data[self.chunk_size*i:self.chunk_size*(i+1)])
        # Converts string to bit array
        for i in range(len(chunks)):
            new_chunk = ''
            chunk = chunks[i]
            for j in range(len(chunk)):
                new_chunk += (chunk[j] + ' ')
            chunks[i] = new_chunk
        chunks = [np.array([chunk.split()]) for chunk in chunks]
        #print(len(chunks))
        #print(chunks.pop())
        #print(chunks.pop())
        #print(len(chunks))
        #print(chunks)
        for chunk in chunks:
            curr_checksum = self.get_complement_sum(curr_checksum, chunk)
        for i in range(len(curr_checksum)):
            curr_checksum[i] = 1 - curr_checksum[i]
        return curr_checksum

    def check_checksum(self):
        '''
        Checks to see if packet was corrupted in transmission
        '''
        if not self.sent:
            return None
        chunks = list(self.total_data)
        for i in range(len(chunks)):
            new_chunk = ''
            chunk = chunks[i]
            for j in range(len(chunk)):
                new_chunk += (chunk[j] + ' ')
            chunks[i] = new_chunk
        chunks = [np.array([chunk.split()]) for chunk in chunks]
        h = np.zeros(self.chunk_size)
        for chunk in chunks:
            h = self.get_complement_sum(h,chunk)
        #print(h)
        #print(h)
        return all(h == np.ones(self.chunk_size))
#Debugging
#
#
# input = '10000110010111101010110001100000011100010010101010000001101101011000011001011110101011000110000001110001001010101000000110110101'
# a = Packet(input)
# c = '1011010011000001'
#
# b = Packet(c+input, sent = True)
# print(b.check_checksum())
