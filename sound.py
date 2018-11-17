import numpy as np
import matplotlib.pyplot as plt
import bitarray, time
from scipy import signal, integrate
from fractions import gcd
from functools import reduce
import sounddevice as sd
import math

def lcm(numbers):
        return reduce(lambda x, y: (x*y)/gcd(x,y), numbers, 1)

def afsk1200(bits, fs = 48000, fdev=500, f=1700, br=1200):
        b = np.fromstring(bits.unpack(), dtype=bool)
        c = np.array([1  if a else -1 for a in list(b)])
        upsample = lcm([br, fs])
        rep = upsample/br
        arr = []
        for bit in list(c):
            for i in range(int(rep)):
                arr += [bit]
        m = np.array(arr)
        s = np.cos(np.array([2*math.pi*f*i/upsample - 2*math.pi*fdev*y for y, i in zip(integrate.cumtrapz(m, dx=1/upsample), range(len(m)))]))
        downsample = np.array(list(s)[::round(upsample/fs)])
        return downsample

def clock(num_packets, packet_len, fs=48000, fdev=200, f=800, br=1200):
    upsample = lcm([br, fs])
    rep = upsample/br
    signalLen = rep*packet_len*num_packets

    arr = []

    ctr = 1
    i = 0
    for j in range(int(rep/2)):
        arr += [ctr]
        i+= 1

    ctr *=-1
    j = 0
    while i<signalLen:
        arr += [ctr]
        i+= 1
        j+= 1
        if j >= rep*packet_len:
            j = 0
            ctr *= -1
    m = np.array(arr)
    s = np.cos(np.array([2*math.pi*f*i/upsample - 2*math.pi*fdev*y for y, i in zip(integrate.cumtrapz(m, dx=1/upsample), range(len(m)))]))
    downsample = np.array(list(s)[::round(upsample/fs)])
    return downsample


def nc_afsk1200Demod(sig, baud = 1200, cf = 1700, fdev = 500, fs=48000.0, width=50, taps=50):
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

    an_low_envelops = signal.hilbert(lowvals)
    low_envelope = np.abs(an_low_envelops)

    an_high_envelops = signal.hilbert(highvals)
    high_envelope = np.abs(an_high_envelops)

    diff = low_envelope - high_envelope
    return np.sign(diff)

def decode(data_nrz, clock_nrz, fs=48000, baud=1200, packet_size=4):
    prev = clock_nrz[0]
    ret = []
    for i in range(len(data_nrz)):
        if prev != clock_nrz[i]:
            arr = []
            for j in range(packet_size):
                if int(i + j*fs/baud) >= len(data_nrz):
                    break;
                arr += [int(.5 + .5*data_nrz[int(i + j*fs/baud)])]
            ret += [arr]
        prev = clock_nrz[i]
    return ret

def genSignal(bits, baud, signal_cf, clock_cf, fdev, fs, packet_size):
    signal = afsk1200(bits, fs=fs, fdev=fdev, f=signal_cf, br=baud)
    clocksig = clock(len(bits)/packet_size, packet_size, fs=fs, fdev=fdev, f=clock_cf, br=baud)
    modulated = .5*signal + .5*clocksig
    return modulated

def transmit(bits, baud=1200, signal_cf=1000, clock_cf=2000, fdev=500, fs=48000, packet_size=4):
    modulated = genSignal(bits, baud, signal_cf, clock_cf, fdev, fs, packet_size)
    while True:
        sd.play(modulated, fs)
        sd.wait()

def receiveFromSignal(recording, packet_size, baud, signal_cf, clock_cf, fdev, fs, duration):
    clnrz = np.array([int((x)) for x in list(nc_afsk1200Demod(recording, fs=fs, cf=clock_cf, fdev=fdev))])
    nrz = np.array([int((x)) for x in list(nc_afsk1200Demod(recording, fs=fs, cf=signal_cf, fdev=fdev))])
    return decode(nrz, clnrz, fs=fs, baud=baud, packet_size=packet_size)

def receive(packet_size=4, baud=300, signal_cf=1000, clock_cf=2000, fdev=500, fs=48000, duration=10):
    myrecording = sd.rec(int(duration * fs), samplerate=fs, channels=1)
    sd.wait()
    recording = [x[0] for x in myrecording]
    return receiveFromSignal(recording, packet_size, baud, signal_cf, clock_cf, fdev, fs, duration)
