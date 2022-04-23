import pyaudio
import numpy as np
import matplotlib.pyplot as plt
import time


import board
import neopixel

import config
import mic_read
import pixel_displayer

import colour_wheel
import audio_data_processor



arr_of_vals = []
moving_avg_arr = None

mic_reader = mic_read.MicReader()
pixel_displayer = pixel_displayer.PixelDisplayer()

wheel_pos_arr = []
for i in range(config.NUM_PIXELS):
    wheel_pos_arr.append(colour_wheel.colour_wheel(i, config.NUM_PIXELS))

print(wheel_pos_arr)


audio_data_processor = audio_data_processor.AudioDataProcessor()

done_loop = 0
while done_loop < config.NUM_TIMES_TO_RUN_LOOP:
    # For perf measure
    time_0 = time.time()
    print(done_loop)
    
    # Iterate loop, to be removed
    done_loop = done_loop + 1
    
    # Read in mic data
    mic_data = mic_reader.read_stream()
    if mic_data is None:
        # We missed audio data, let's just wait a second for it
        time.sleep(1)
        continue
    
    # Process data
    full_freq_processed = audio_data_processor.process_raw_audio_data(mic_data)
    

    
    
    if (len(arr_of_vals) >= config.MOVING_AVG_LEN):
        remove_from_avg = arr_of_vals.pop()
        arr_of_vals.append(full_freq_processed)
        moving_avg_arr = moving_avg_arr - (remove_from_avg / config.MOVING_AVG_LEN) + (full_freq_processed / config.MOVING_AVG_LEN)
        #print(moving_avg_arr)
    else:
        arr_of_vals.append(full_freq_processed)
        if (moving_avg_arr is None):
            moving_avg_arr = (full_freq_processed / config.MOVING_AVG_LEN)
        else:
            moving_avg_arr = moving_avg_arr + (full_freq_processed / config.MOVING_AVG_LEN)
            

    
        
         
    leds_to_disp = np.divide((full_freq_processed - moving_avg_arr), moving_avg_arr)
    leds_to_disp = np.maximum(leds_to_disp, 0)
    threshold = config.THRESHOLD_FOR_LED_DISP_LOG_SCALE if config.USE_LOG_SCALE else config.THRESHOLD_FOR_LED_DISP
    leds_to_disp = np.floor(leds_to_disp, where=leds_to_disp < threshold)
    leds_to_disp = leds_to_disp / np.amax(leds_to_disp + config.DIVISION_ADDED_BIAS)
    
    pixel_displayer.display_leds(leds_to_disp, wheel_pos_arr)

    
    time_6 = time.time()
    

    print('e2e time : ', time_6 - time_0)
    
    
    time.sleep(config.ADDED_SLEEP_MS / 1000)
    


mic_reader.close_stream()
