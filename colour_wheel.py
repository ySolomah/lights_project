# Determine colour of LED based on number of LEDs and position of pixel
def colour_wheel(pixel_pos, num_led):
    wheel_pos = (255 / num_led) * pixel_pos
    r, g, b = (0, 0, 0)
    if (wheel_pos < 85):
        r = 0
        g = 255 - wheel_pos * 3
        b = wheel_pos * 3
    elif (wheel_pos < 170):
        wheel_pos = wheel_pos - 85
        r = wheel_pos * 3
        g = 0
        b = 255 - wheel_pos * 3
    else:
        wheel_pos = wheel_pos - 170
        r = 255 - wheel_pos * 3
        g = wheel_pos * 3
        b = 0
    return (r, g, b)
        
