import numpy as np

class Packet:
    def __init__(self, input):
        '''
        input = String input of bits, length 128 + 32 representing xor of packets
            - Last 32 bits corresponds to the metadata

        '''
        self.chunk_size = 16
        self.data = [input[16*i:16*(i+1)] for i in range(128//16)] #128 Bits
        self.meta_data = input[128:] #32 Bits
        self.total_data = list(self.data)
        total_data.append(meta_data[:16])
        total_data.append(meta_data[16:])
        self.checksum = self.get_checksum() #16 bits


    def get_complement_sum(self, one, two):
        '''
        Determines complement sum of two equal-sized binary numbers
        Helper function for get_checksum
        '''
        out = [0 for _ in range(self.chunk_size)]
        carry = 0
        one = [int(i) for i in one]
        two = [int(i) for i in two]
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
        print(out, two)
        for i in range(self.chunk_size):
            i = -(i+1)%self.chunk_size
            out[i] = (one[i] + two[i] + carry) % 2
            carry = max(0, (one[i] + two[i] + carry) - 1)
        print(out)
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
        for chunk in chunks:
            curr_checksum = self.get_complement_sum(curr_checksum, chunk)
        for i in range(len(curr_checksum)):
            curr_checksum[i] = 1 - curr_checksum[i]
        return curr_checksum

#Debugging

input = {1: '1000011001011110', 2: '1010110001100000', 3:'0111000100101010', 4:'1000000110110101'}
a = Packet(input)
print(a.checksum)
