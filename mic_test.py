import pyaudio
import numpy as np
from scipy.fft import fft, ifft, fftfreq
import matplotlib.pyplot as plt
import time
from melbank import compute_melmat


import board
import neopixel


def colour_wheel(pixel_pos, num_led):
    wheel_pos = (255 / num_led) * pixel_pos
    r, g, b = (0, 0, 0)
    if (wheel_pos < 85):
        r = 255 - wheel_pos * 3
        g = wheel_pos * 3
        b = 0
    elif (wheel_pos < 170):
        wheel_pos = wheel_pos - 85
        r = 0
        g = 255 - wheel_pos * 3
        b = wheel_pos * 3
    else:
        wheel_pos = wheel_pos - 170
        r = wheel_pos * 3
        g = 0
        b = 255 - wheel_pos * 3
    return (r, g, b)
        

MIN_FREQ = 100
MAX_FREQ = 17000

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

arr_of_vals = []
moving_avg_arr = None

wheel_pos_arr = []
for i in range(60):
    wheel_pos_arr.append(colour_wheel(i, 60))

print(wheel_pos_arr)

NUM_PIXELS = 60

pixels = neopixel.NeoPixel(board.D21, NUM_PIXELS, brightness=0.5, pixel_order=neopixel.GRB, auto_write=False)


num_times = 500
done_loop = 0
while done_loop < num_times:
    print(done_loop)
    done_loop = done_loop + 1
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=RATE, input=True,
    frames_per_buffer=CHUNK)
    data = np.fromstring(stream.read(CHUNK), dtype=np.int16)
    stream.stop_stream()
    stream.close()
    fft_arr = np.abs(fft(data)[1:CHUNK//2])
    #print(np.shape(fft_arr))
    freq_buckets = fftfreq(CHUNK, d=1/RATE)[1:CHUNK//2]
    #print(len(freq_buckets))
    #print(len(fft_arr))
    #print(np.shape(melmat))
    full_freq = np.zeros(RATE//2 + 1)
    #print(np.shape(full_freq))
    for i in range(len(freq_buckets)):
        #print(freq_buckets[i])
        left_idx = int(freq_buckets[i])
        right_idx = left_idx + 1
        full_freq[left_idx] = fft_arr[i]
        full_freq[right_idx] = fft_arr[i]
    prev_value = 0;
    # ACTUAL LINEAR INTERPOLATE 1d interpol scipy???
    for i in range(len(full_freq)):
        if (full_freq[i] > 0):
            prev_value = full_freq[i]
        if (full_freq[i] == 0):
            full_freq[i] = prev_value
    
    full_freq_to_plot = np.log(np.dot(melmat, full_freq))
    
    #print(np.shape(full_freq_to_plot))
    
    if (len(arr_of_vals) >= 10):
        remove_from_avg = arr_of_vals.pop()
        arr_of_vals.append(full_freq_to_plot)
        moving_avg_arr = moving_avg_arr - (remove_from_avg / 10) + (full_freq_to_plot / 10)
        #print(moving_avg_arr)
    else:
        arr_of_vals.append(full_freq_to_plot)
        if (moving_avg_arr is None):
            moving_avg_arr = (full_freq_to_plot / 10)
        else:
            moving_avg_arr = moving_avg_arr + (full_freq_to_plot / 10)
    
    #print(np.shape(full_freq_to_plot))
    #print(len(arr_of_vals))
    
    #if (done_loop % 2 == 0):
    #    plt.plot(freq_buckets[100:1500], np.log(fft_arr[100:1500]))
    #else:
    #    if (len(arr_of_vals) >= 10):
    #        plot_not_normalized = np.divide((full_freq_to_plot - moving_avg_arr), moving_avg_arr)
    #        plot_not_normalized = np.maximum(plot_not_normalized, 0)
    #        plt.plot(plot_not_normalized / np.amax(plot_not_normalized + 0.0001))
    #        #plt.plot(full_freq_to_plot - moving_avg_arr)
    #        print(full_freq_to_plot - moving_avg_arr)
    #    else:
    #        plt.plot(np.log(full_freq_to_plot))
        
         
    leds_to_disp = np.divide((full_freq_to_plot - moving_avg_arr), moving_avg_arr)
    leds_to_disp = np.maximum(leds_to_disp, 0)
    print("beforebefore loop ", len(leds_to_disp))
    print("before loop ", len(leds_to_disp))
    if (len(leds_to_disp) == 0):
        pixels.fill((0, 0, 0))
    else:
        print(leds_to_disp)
        print(len(leds_to_disp))
        leds_to_disp = leds_to_disp / np.amax(leds_to_disp + 0.0001)
        print(leds_to_disp)
        pixels.fill((0, 0, 0))
        for i in range(0, 30):
            pixel_pos = ((len(leds_to_disp) * 2 - 1) - i) % len(leds_to_disp)
            scalar_factor = leds_to_disp[i]
            
            (r, g, b) = wheel_pos_arr[i]
            pixels[i] = ((int)(0.50 * scalar_factor * g), (int)(0.50 * scalar_factor * r), (int)(0.50 * scalar_factor * b))
    pixels.show()
    
    #plt.grid()
    #plt.draw()
    #plt.pause(0.00001)
    #plt.clf()
    
    time.sleep(100 / 1000)
    


stream.stop_stream()
stream.close()
p.terminate()
