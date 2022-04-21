import config
import pyaudio
from collections import deque

class MicReader:
	def __init__(self):
		# Open pyaudio instance
		self.p = pyaudio.PyAudio()
		self.data = deque()
		
		# Print out the audio information currently available
		info = self.p.get_host_api_info_by_index(0)
		num_dev = info.get('deviceCount')
		for i in range(0, num_dev):
			if (self.p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
				print('Input dev id ', i, ' - ', self.p.get_device_info_by_host_api_device_index(0, i))
		
		# Create stream	
		self.stream = self.p.open(
			format=pyaudio.paInt16,
			channels=1,
			rate=config.RATE,
			input=True,
			frames_per_buffer=config.CHUNK,
			stream_callback=self.stream_callback
			)
			
		# Start stream
		self.stream.start_stream()

	# Async Mode
	def stream_callback(self, in_data, frame_count, time_info, status):
		if (len(self.data) >= config.NUM_AUDIO_BLOCKS_FOR_FFT):
			self.data.popleft()
		self.data.append(in_data)
		return (None, pyaudio.paContinue)

	# Return latest block of data
	def read_stream(self):
		data_to_return_with = self.data.copy()
		if (len(data_to_return_with) < config.NUM_AUDIO_BLOCKS_FOR_FFT):
			return None
		return_data = None
		for data in data_to_return_with:
			if return_data is None:
				return_data = data
			else:
				return_data = return_data + data
		return return_data
	
	# Close and terminate the stream
	def close_stream(self):
		self.stream.close()
		self.p.terminate()
