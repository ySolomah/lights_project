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
import mic_read
import pixel_displayer

import colour_wheel





melmat, (melfreq, _) = compute_melmat(config.NUM_PIXELS, config.MIN_FREQ, config.MAX_FREQ, num_fft_bands=(config.RATE // 2) + 1, sample_rate=config.RATE)
sum_melmat = melmat.sum(axis=1)
norm_melmat = melmat / sum_melmat[:, np.newaxis]

arr_of_vals = []
moving_avg_arr = None

mic_reader = mic_read.MicReader()
pixel_displayer = pixel_displayer.PixelDisplayer()

wheel_pos_arr = []
for i in range(config.NUM_PIXELS):
    wheel_pos_arr.append(colour_wheel.colour_wheel(i, config.NUM_PIXELS))

print(wheel_pos_arr)


done_loop = 0
while done_loop < config.NUM_TIMES_TO_RUN_LOOP:
    time_0 = time.time()
    print(done_loop)
    done_loop = done_loop + 1
    mic_data = mic_reader.read_stream()
    if mic_data is None:
        # We missed audio data, let's just wait a second for it
        time.sleep(1)
        continue
    data = np.fromstring(mic_data, dtype=np.int16)
    fft_arr = np.abs(fft(data)[1:config.CHUNK * config.NUM_AUDIO_BLOCKS_FOR_FFT // 2])
    freq_buckets = fftfreq(config.CHUNK * config.NUM_AUDIO_BLOCKS_FOR_FFT, d=1 / config.RATE)[1:config.CHUNK * config.NUM_AUDIO_BLOCKS_FOR_FFT // 2]
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
    leds_to_disp = leds_to_disp / np.amax(leds_to_disp + config.DIVISION_ADDED_BIAS)
    
    pixel_displayer.display_leds(leds_to_disp, wheel_pos_arr)

    
    time_6 = time.time()
    
    print('time of led disp : ', time_6 - time_5)

    print('e2e time : ', time_6 - time_0)
    
    
    time.sleep(config.ADDED_SLEEP_MS / 1000)
    


mic_reader.close_stream()
