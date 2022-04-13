import pyaudio
import numpy as np
from scipy.fft import fft, ifft, fftfreq
import matplotlib.pyplot as plt
import time

MIN_FREQ = 30
MAX_FREQ = 15000

p = pyaudio.PyAudio()
info = p.get_host_api_info_by_index(0)
num_dev = info.get('deviceCount')
for i in range(0, num_dev):
    if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
        print('Input dev id ', i, ' - ', p.get_device_info_by_host_api_device_index(0, i))


CHUNK = 4096
RATE = 44100
#stream = p.open(format=pyaudio.paInt16, channels=1, rate=RATE, input=True,
#    frames_per_buffer=CHUNK)
    
#for i in range(10):
#    data = np.fromstring(stream.read(CHUNK), dtype=np.int16)
#    print(data)

num_times = 100
done_loop = 0
while done_loop < num_times:
    done_loop = done_loop + 1
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=RATE, input=True,
    frames_per_buffer=CHUNK)
    data = np.fromstring(stream.read(CHUNK), dtype=np.int16)
    stream.stop_stream()
    stream.close()
    fft_arr = fft(data)[1:CHUNK//2]
    freq_buckets = fftfreq(CHUNK, d=1/RATE)[1:CHUNK//2]
    print(len(freq_buckets))
    print(len(fft_arr))
    min_idx = np.searchsorted(freq_buckets, MIN_FREQ, side="left")
    max_idx = np.searchsorted(freq_buckets, MAX_FREQ, side="right")
    print(min_idx, ' + ', max_idx)
    fft_arr_trim = np.log2((1.0 / CHUNK) * np.abs(fft_arr[min_idx:max_idx]))
    freq_buckets_trim = freq_buckets[min_idx:max_idx]
    plt.plot(freq_buckets_trim, fft_arr_trim)
    plt.grid()
    plt.draw()
    plt.pause(0.0005)
    plt.clf()
    


stream.stop_stream()
stream.close()
p.terminate()
