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
import moving_average
import led_filter


audio_data_processor = audio_data_processor.AudioDataProcessor()
mic_reader = mic_read.MicReader()
pixel_displayer = pixel_displayer.PixelDisplayer()
moving_average = moving_average.MovingAverage()
wheel_pos_arr = colour_wheel.create_colour_wheel()

done_loop = 0
while done_loop < config.NUM_TIMES_TO_RUN_LOOP:
    # For perf measure
    start_time = time.time()
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
    
    # Add new element to moving average
    moving_avg_arr = moving_average.update_moving_average(full_freq_processed)
                
    # Consider adding some level of bias into denominator? p50 of average array maybe?
    leds_to_disp = led_filter.filter_and_create_led_display_array(full_freq_processed, moving_avg_arr)
    
    # Display leds
    pixel_displayer.display_leds(leds_to_disp, wheel_pos_arr)
    
    # E2E time to process
    end_time = time.time()
    print('e2e time : ', end_time - start_time)
    
    # Added sleep
    time.sleep(config.ADDED_SLEEP_MS / 1000)

# Close mic
mic_reader.close_stream()
