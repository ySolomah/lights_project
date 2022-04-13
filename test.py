import board
import neopixel
import time

NUM_PIXELS = 60

pixels = neopixel.NeoPixel(board.D21, NUM_PIXELS, brightness=0.5, pixel_order=neopixel.GRB)

# init
pixels.fill((0, 0, 0))

for i in range(0, NUM_PIXELS):
	pixels.fill((0, 0, 0))
	pixels[i] = (100 * (i-1) % 3, 100 * (i) % 3, 100 * (i + 1) % 3)
	time.sleep(1)
