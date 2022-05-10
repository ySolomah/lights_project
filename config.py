import board
import neopixel

# Minimum frequency band to keep around in melmat/triangular filters
MIN_FREQ = 50

# Maximum frequency band to keep around in the melmat/triangular filters
MAX_FREQ = 12000

# Number of samples to read in single iteration from mic
CHUNK = 4096

# Sampling rate of mic
RATE = 44100

# Number of pixels on LED strip
NUM_PIXELS = 60

# Samples to store in moving average for denoising
# Loop roughly takes 0.15s, and with delay of 0.1s
# this implies 0.25s * 25 = 6.25s of moving average
MOVING_AVG_LEN = 50

# Times to run loop, set to -1 for while true
NUM_TIMES_TO_RUN_LOOP = -1

# Raspberry PI pin to push data to
PI_PIN = board.D21

# Brightness multiplier
BRIGHTNESS_MULTIPLIER = 1.0

# Pixel data order
PIXEL_DATA_ORDER = neopixel.GRB

# Autowrite LED
AUTO_WRITE_LED = False

# Relative movement threshold for minimum display
# This implies the FFT bucketized value after melmat mult must
# be at least (1 + threshold) relatively greater than the moving
# average
THRESHOLD_FOR_LED_DISP_LOG_SCALE = 0.01
THRESHOLD_FOR_LED_DISP = 0.15

# Global LED Pixel Multiplier
LED_PIXEL_MULTIPLIER = 1.0

# Bias to prevent zero division with LEDs array
DIVISION_ADDED_BIAS = 0.0001

# Added Sleep for LED display in ms
ADDED_SLEEP_MS = 50

# Moving Data Array Size
NUM_AUDIO_BLOCKS_FOR_FFT = 3

# Use normalized melbank matrix
USE_NORMAL_MELBANK = False

# Use log scale during processing
USE_LOG_SCALE = True
