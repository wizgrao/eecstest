import numpy as np
import matplotlib.pyplot as plt
import bitarray, time
from scipy import signal, integrate, fftpack
from fractions import gcd
from functools import reduce
import sounddevice as sd
import math

def lcm(numbers):
        return reduce(lambda x, y: (x*y)/gcd(x,y), numbers, 1)

def afsk1200(bits, fs = 48000, fdev=500, f=1700, br=1200):
        arr = manchester(bits, fs, br)
        upsample = lcm([br, fs])
        m = np.array(arr)
        s = np.cos(np.array([2*math.pi*f*i/upsample - 2*math.pi*fdev*y for y, i in zip(integrate.cumtrapz(m, dx=1/upsample), range(len(m)))]))
        downsample = np.array(list(s)[::round(upsample/fs)])
        return downsample

def manchester(bits, fs=4800, br=200):
        b = np.fromstring(bits.unpack(), dtype=bool)
        upsample = lcm([br, fs])
        c = np.array([1  if a else -1 for a in list(b)])
        c = np.array([1,-1]*br + [1,1,1] + list(c))
        rep = upsample/br
        arr = []
        for bit in list(c):
            for i in range(int(rep)):
                if i < rep/2:
                    arr += [-bit]
                else:
                    arr += [bit]
        return arr

def decode(nrz, baud=1200, fs=48000):
    maxOff = 0
    maxOffInd = 0
    for offset in range(int(fs/baud)):
        diff = 0
        for i in range(5):
            avga = 0
            avgb = 0
            for j in range(int(fs/baud/2)):
                avga += nrz[int(offset + i*fs/baud + j)]
            for j in range(int(fs/baud/2)):
                avgb += nrz[int(offset + (i+.5)*fs/baud + j)]
            diff += abs(avga-avgb)
        if diff > maxOff:
            maxOff = diff
            maxOffInd = offset
    nrz = nrz[maxOffInd:]
    bits = []
    ind = 0
    print("offset found", maxOffInd)
    while True:
        if (ind+1)*fs/baud > len(nrz):
            break
        avga = 0
        avgb = 0
        for j in range(int(fs/baud/2)):
            avga += nrz[int(ind*fs/baud + j)]
        for j in range(int(fs/baud/2)):
            avgb += nrz[int((.5+ind)*fs/baud + j)]
        diff = avgb-avga
        bits += [int(np.sign(diff)/2+1/2)]
        ind +=1
    print("done initial decode")
    i = 0
    prev = 0
    for b in bits:
        i+=1
        if b==1:
            prev +=1
        else:
            prev = 0
        if prev >=3:
            return bits[i:]
    
def nc_afsk1200Demod(sig, baud = 1200, cf = 1700, fdev = 500, fs=48000.0, width=50, taps=50):
    plt.figure()
    plt.plot(sig[:900])
    sf = cf  - fdev
    mf = cf + fdev
    lowf1 = sf - width
    lowf2 = sf + width
    highf1 = mf - width
    highf2 = mf + width
    lowpass = signal.firwin(taps, [2*lowf1/fs, 2*lowf2/fs], pass_zero=False)
    highpass = signal.firwin(taps, [2*highf1/fs, 2*highf2/fs], pass_zero=False)

    lowvals = signal.convolve(sig, lowpass, mode='same')

    highvals = signal.convolve(sig, highpass, mode='same')
    hilbert3 = lambda x: signal.hilbert(x, fftpack.next_fast_len(len(x)))[:len(x)]
    an_low_envelops = hilbert3(lowvals)
    low_envelope = np.abs(an_low_envelops)

    an_high_envelops = hilbert3(highvals)
    high_envelope = np.abs(an_high_envelops)
    plt.plot(low_envelope[:900])
    plt.plot(high_envelope[:900])
    plt.show()
    diff = low_envelope - high_envelope
    return np.sign(diff)


def genSignal(bits, baud, signal_cf, fdev, fs):
    signal = afsk1200(bits, fs=fs, fdev=fdev, f=signal_cf, br=baud)
    return signal

def transmit(bits, baud=1200, signal_cf=1000, fdev=500, fs=48000):
    modulated = genSignal(bits, baud, signal_cf, fdev, fs)
    while True:
        sd.play(modulated, fs)
        sd.wait()

def receiveFromSignal(recording, packet_size, baud, signal_cf, fdev, fs, width, taps):
    nrz = np.array([int((x)) for x in list(nc_afsk1200Demod(recording, fs=fs, cf=signal_cf, fdev=fdev, width=width, taps=taps))])
    print("decoding")
    dec = decode(nrz, fs=fs, baud=baud)
    pack = []
    i = 0
    while (i+1)*packet_size < len(dec):
        pack += [dec[i*packet_size:(i+1)*packet_size]]
        i+=1
    return pack

def receive(packet_size=4, baud=300, signal_cf=1000, clock_cf=2000, fdev=500, fs=48000, duration=10, width=50, taps=50):
    myrecording = sd.rec(int(duration * fs), samplerate=fs, channels=1)
    sd.wait()
    recording = [x[0] for x in myrecording]
    return receiveFromSignal(recording, packet_size, baud, signal_cf, fdev, fs, width, taps)
