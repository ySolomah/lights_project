import pyaudio
import numpy as np
from scipy.fft import fft, ifft, fftfreq
import matplotlib.pyplot as plt
import time
from melbank import compute_melmat
from scipy import interpolate


import board
import neopixel

import config


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
        

p = pyaudio.PyAudio()
info = p.get_host_api_info_by_index(0)
num_dev = info.get('deviceCount')
for i in range(0, num_dev):
    if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
        print('Input dev id ', i, ' - ', p.get_device_info_by_host_api_device_index(0, i))


melmat, (melfreq, _) = compute_melmat(config.NUM_PIXELS, config.MIN_FREQ, config.MAX_FREQ, num_fft_bands=(config.RATE // 2) + 1, sample_rate=config.RATE)
sum_melmat = melmat.sum(axis=1)
norm_melmat = melmat / sum_melmat[:, np.newaxis]

arr_of_vals = []
moving_avg_arr = None

wheel_pos_arr = []
for i in range(config.NUM_PIXELS):
    wheel_pos_arr.append(colour_wheel(i, config.NUM_PIXELS))

print(wheel_pos_arr)

pixels = neopixel.NeoPixel(config.PI_PIN, config.NUM_PIXELS, brightness=config.BRIGHTNESS_MULTIPLIER, pixel_order=config.PIXEL_DATA_ORDER, auto_write=config.AUTO_WRITE_LED)

done_loop = 0
while done_loop < config.NUM_TIMES_TO_RUN_LOOP:
    time_0 = time.time()
    print(done_loop)
    done_loop = done_loop + 1
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=config.RATE, input=True, frames_per_buffer=config.CHUNK)
    data = np.fromstring(stream.read(config.CHUNK), dtype=np.int16)
    stream.stop_stream()
    stream.close()
    fft_arr = np.abs(fft(data)[1:config.CHUNK // 2])
    freq_buckets = fftfreq(config.CHUNK, d=1 / config.RATE)[1:config.CHUNK // 2]
    full_freq = np.zeros((config.RATE // 2) + 1)
    #print(np.shape(full_freq))
    time_1 = time.time()
    
    f_scipy_interpol = interpolate.interp1d(freq_buckets, fft_arr, fill_value="extrapolate")
    
    print('time of stream open and fft and freq bucket : ', time_1 - time_0)
    time_3 = time.time()
    
    fft_freqs_new_bucket = np.arange(0, (config.RATE // 2) + 1, 1)
    new_full_freq_to_plot = f_scipy_interpol(fft_freqs_new_bucket)

    full_freq_to_plot = np.log(melmat.dot(new_full_freq_to_plot))
    
    #full_freq_to_plot = np.log(np.dot(melmat, full_freq))
    
    time_4 = time.time()
    print('time of np log and matrix mul : ', time_4 - time_3)

    
    #print(np.shape(full_freq_to_plot))
    
    if (len(arr_of_vals) >= config.MOVING_AVG_LEN):
        remove_from_avg = arr_of_vals.pop()
        arr_of_vals.append(full_freq_to_plot)
        moving_avg_arr = moving_avg_arr - (remove_from_avg / config.MOVING_AVG_LEN) + (full_freq_to_plot / config.MOVING_AVG_LEN)
        #print(moving_avg_arr)
    else:
        arr_of_vals.append(full_freq_to_plot)
        if (moving_avg_arr is None):
            moving_avg_arr = (full_freq_to_plot / config.MOVING_AVG_LEN)
        else:
            moving_avg_arr = moving_avg_arr + (full_freq_to_plot / config.MOVING_AVG_LEN)
            
    time_5 = time.time()
    print('time of moving avg : ', time_5 - time_4)

    
        
         
    leds_to_disp = np.divide((full_freq_to_plot - moving_avg_arr), moving_avg_arr)
    leds_to_disp = np.maximum(leds_to_disp, 0)
    leds_to_disp = np.floor(leds_to_disp, where=leds_to_disp < config.THRESHOLD_FOR_LED_DISP)
    if (len(leds_to_disp) == 0):
        pixels.fill((0, 0, 0))
    else:
        #print(leds_to_disp)
        #print(len(leds_to_disp))
        leds_to_disp = leds_to_disp / np.amax(leds_to_disp + config.DIVISION_ADDED_BIAS)
        #print(leds_to_disp)
        pixels.fill((0, 0, 0))
        for i in range(0, 60):
            pixel_pos = ((len(leds_to_disp) * 2 - 1) - i) % len(leds_to_disp)
            scalar_factor = leds_to_disp[i]
            
            (r, g, b) = wheel_pos_arr[i]
            pixels[i] = ((int)(config.LED_PIXEL_MULTIPLIER * scalar_factor * g), (int)(config.LED_PIXEL_MULTIPLIER * scalar_factor * r), (int)(config.LED_PIXEL_MULTIPLIER * scalar_factor * b))
    pixels.show()
    
    time_6 = time.time()
    
    print('time of led disp : ', time_6 - time_5)

    print('e2e time : ', time_6 - time_0)
    
    
    time.sleep(config.ADDED_SLEEP_MS / 1000)
    


stream.stop_stream()
stream.close()
p.terminate()
