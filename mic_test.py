import pyaudio
import numpy as np
from scipy.fft import fft, ifft, fftfreq
import matplotlib.pyplot as plt
import time
from melbank import compute_melmat

MIN_FREQ = 300
MAX_FREQ = 10000

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

melmat, (melfreq, _) = compute_melmat(30, MIN_FREQ, MAX_FREQ, num_fft_bands=22051, sample_rate=44100)
sum_melmat = melmat.sum(axis=1)
norm_melmat = melmat / sum_melmat[:, np.newaxis]

num_times = 100
done_loop = 0
while done_loop < num_times:
    done_loop = done_loop + 1
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=RATE, input=True,
    frames_per_buffer=CHUNK)
    data = np.fromstring(stream.read(CHUNK), dtype=np.int16)
    stream.stop_stream()
    stream.close()
    fft_arr = np.abs(fft(data)[1:CHUNK//2])
    print(np.shape(fft_arr))
    freq_buckets = fftfreq(CHUNK, d=1/RATE)[1:CHUNK//2]
    print(len(freq_buckets))
    print(len(fft_arr))
    print(np.shape(melmat))
    full_freq = np.zeros(RATE//2 + 1)
    print(np.shape(full_freq))
    for i in range(len(freq_buckets)):
        #print(freq_buckets[i])
        left_idx = int(freq_buckets[i])
        right_idx = left_idx + 1
        full_freq[left_idx] = fft_arr[i]
        full_freq[right_idx] = fft_arr[i]
    prev_value = 0;
    # Do actual linear interpolation here
    for i in range(len(full_freq)):
        if (full_freq[i] > 0):
            prev_value = full_freq[i]
        if (full_freq[i] == 0):
            full_freq[i] = prev_value
    
    full_freq_to_plot = np.dot(norm_melmat, full_freq)
        
    
    print(np.shape(full_freq_to_plot))    
    
    #if (done_loop % 2 == 0):
    #    plt.plot(freq_buckets[100:1500], np.log(fft_arr[100:1500]))
    #else:
    #    plt.plot(np.log(full_freq_to_plot))
    #plt.grid()
    #plt.draw()
    #plt.pause(0.00001)
    #plt.clf()
    time.sleep(200 / 1000)
    


stream.stop_stream()
stream.close()
p.terminate()
