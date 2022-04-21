import config
import neopixel

class PixelDisplayer:
	def __init__(self):
		self.pixels = neopixel.NeoPixel(config.PI_PIN, config.NUM_PIXELS, brightness=config.BRIGHTNESS_MULTIPLIER, pixel_order=config.PIXEL_DATA_ORDER, auto_write=config.AUTO_WRITE_LED)

	def display_leds(self, led_values, wheel_pos_arr):		
		self.pixels.fill((0, 0, 0))
		for i in range(0, config.NUM_PIXELS):
			scalar_factor = led_values[i]
			(r, g, b) = wheel_pos_arr[i]
			self.pixels[i] = ((int)(config.LED_PIXEL_MULTIPLIER * scalar_factor * g), (int)(config.LED_PIXEL_MULTIPLIER * scalar_factor * r), (int)(config.LED_PIXEL_MULTIPLIER * scalar_factor * b))
		self.pixels.show()
		
	def display_empty_leds(self):
		self.pixels.fill((0, 0, 0))
		self.pixels.show()
