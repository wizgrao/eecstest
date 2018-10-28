from collections import Counter
from heapq import heappush, heappop


def HuffEncode(freq_dict):
    freq = []
    huffman = {}
    for key in freq_dict:
        heappush(freq, ((freq_dict[key]), [key]))
        huffman[key]= ""
    while len(freq) > 1:
        char_1 = heappop(freq)
        char_2 = heappop(freq)
        combined = (char_1[0] + char_2[0], char_1[1] + char_2[1])
        for symbol in char_1[1]:
            huffman[symbol] = "0" + huffman[symbol]
        for symbol in char_2[1]:
            huffman[symbol] = "1" + huffman[symbol]
        heappush(freq, combined)
    return huffman,{v: k for k, v in huffman.items()}


def huffman_compress(sourcefile, incodePath, decodePath):
    """
    Create text files to store huffman tree
    :param sourcefile: source file to create huffman tree
    :param incodePath: text file to store dictionary from char -> bits
    :param decodePath: text file to store dictionary from bits -> char
    :return: None
    """
    with open(sourcefile, 'r+') as file:
        text = file.read()
        text = text.rstrip()
    codes, reverse_mapping = HuffEncode(Counter(text))
    with open(incodePath, 'w') as encode,open(decodePath, 'w') as decode:
        for k, v in codes.items():
            if k=='\n': k='\\n'
            encode.write(str(k) + ' ' + str(v) + '\n')
        for k, v in reverse_mapping.items():
            if v=='\n': v='\\n'
            decode.write(str(k) + ' ' + str(v) + '\n')


def text_huffman(path,reverse=False):
    """
    Read text file containing huffman tree.
    Warning: Manually adding char for "\n" and " "
    :param path: text file
    :param reverse: True is reading dict bits -> char
    :return:
    """

    huffman_tree = {}
    with open(path) as f:
        for line in f:
            (key, val) = line.split()
            huffman_tree[key] = val
    if reverse:
        huffman_tree["10000"] = "\n"
        huffman_tree["01"] = " "
    else:
        huffman_tree["\n"]="10000"
        huffman_tree[" "]="01"
    return huffman_tree


def text_to_bytes(text):
    """
    Convert bits to bytes (include extra padding)
    :param text: bit string
    :return: byte string
    """
    b = bytearray()
    extra_pad = 8 - len(text) % 8
    pad_info = "{0:08b}".format(extra_pad)
    padded_text = pad_info + text + ''.join(["0"] * extra_pad)
    for i in range(0, len(padded_text), 8):
        byte = padded_text[i:i + 8]
        b.append(int(byte, 2))
    return b


def bytes_to_text(bytes):
    """
    Convert bytes to bits (remove any extra padding)
    :param bytes: byte string
    :return: bit string
    """
    padded_info = bytes[:8]
    extra_padding = int(padded_info, 2)
    padded_encoded_text = bytes[8:]
    encoded_text = padded_encoded_text[:-1 * extra_padding]
    return encoded_text


class HuffmanCode:

    def compress(self,path):
        """
        Compress text file in byte string
        :param path: text name
        :return: byte str
        """
        with open(path, 'r+') as file:
            text = file.read()
            text = text.rstrip()
            huffman_tree = text_huffman("encode.txt")
            encoded =bytes(text_to_bytes(''.join([huffman_tree[c] for c in text])))
        return encoded

    def decompress(self, text,file):
        """
        Decompre byte string into text and store into text file
        :param text: encoded byte str
        :param file: saved file
        :return: None
        """
        with open(file, 'w') as output:
            huffman_tree= text_huffman("decode.txt",True)
            bit_str = ""
            huffman_char = ""
            decoded = ""
            for byte in text:
                bit_str +=bin(byte)[2:].rjust(8, '0')
            bit_str = bytes_to_text(bit_str)
            for bits in bit_str:
                huffman_char += bits
                if huffman_char in huffman_tree:
                    decoded += huffman_tree[huffman_char]
                    huffman_char = ""
            output.write(decoded)
