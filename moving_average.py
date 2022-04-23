import numpy
import config
from collections import deque

class MovingAverage:
	def __init__(self):
		self.arr_of_vals = deque()
		self.moving_average = None


	def update_moving_average(self, new_data):
		if (len(self.arr_of_vals) >= config.MOVING_AVG_LEN):
			# Remove first element, add in new element
			remove_from_avg = self.arr_of_vals.popleft()
			self.arr_of_vals.append(new_data)
			self.moving_average = self.moving_average - (remove_from_avg / config.MOVING_AVG_LEN) + (new_data / config.MOVING_AVG_LEN)
		else:
			# Not enough data yet
			self.arr_of_vals.append(new_data)
			if (self.moving_average is None):
				self.moving_average = (new_data / config.MOVING_AVG_LEN)
			else:
				self.moving_average = self.moving_average + (new_data / config.MOVING_AVG_LEN)
				
		return self.moving_average
		
