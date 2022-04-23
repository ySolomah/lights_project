import config
import numpy as np

def filter_and_create_led_display_array(data_this_cycle, moving_avg_arr):
    # Normalize with moving average
    leds_to_disp = np.divide((data_this_cycle - moving_avg_arr), moving_avg_arr)
    
    # Remove negative values
    leds_to_disp = np.maximum(leds_to_disp, 0)
    
    # Remove insignificant changes
    threshold = config.THRESHOLD_FOR_LED_DISP_LOG_SCALE if config.USE_LOG_SCALE else config.THRESHOLD_FOR_LED_DISP
    leds_to_disp = np.floor(leds_to_disp, where=leds_to_disp < threshold)
    
    # Normalize with max value in array
    leds_to_disp = leds_to_disp / np.amax(leds_to_disp + config.DIVISION_ADDED_BIAS)
    
    return leds_to_disp
