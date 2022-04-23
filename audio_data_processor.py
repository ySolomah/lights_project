import config
from melbank import compute_melmat
from scipy import interpolate
import numpy as np
from scipy.fft import fft, ifft, fftfreq


class AudioDataProcessor:
    def __init__(self):
        # Create malbank matrix to bias displayed data to low freq
        melbank_matrix, (melfreq, _) = compute_melmat(config.NUM_PIXELS,
                                                        config.MIN_FREQ,
                                                        config.MAX_FREQ,
                                                        num_fft_bands=(config.RATE // 2) + 1,
                                                        sample_rate=config.RATE)
        # Sum over each row to normalize melbank matrix
        sum_melbank_matrix = melbank_matrix.sum(axis=1)
        # Copy over melbank matrix to variable, and create normalized melbank matrix
        self.melbank_matrix = melbank_matrix
        self.normalized_melbank_matrix = melbank_matrix / \
            sum_melbank_matrix[:, np.newaxis]

    def process_raw_audio_data(self, mic_data):
        # Process the raw string from the mic
        data = np.fromstring(mic_data, dtype=np.int16)

        # Create FFT Array and Frequency buckets
        fft_arr = np.abs(
            fft(data)[1:config.CHUNK * config.NUM_AUDIO_BLOCKS_FOR_FFT // 2])
        freq_buckets = fftfreq(config.CHUNK * config.NUM_AUDIO_BLOCKS_FOR_FFT,
                               d=1 / config.RATE)[1:config.CHUNK * config.NUM_AUDIO_BLOCKS_FOR_FFT // 2]

        # Interpolate values between given FFT values for Triangular Filter
        f_scipy_interpol = interpolate.interp1d(
            freq_buckets, fft_arr, fill_value="extrapolate")

        # Create full interpolated and extrapolated spectrum
        fft_freqs_new_bucket = np.arange(0, (config.RATE // 2) + 1, 1)
        full_freq = f_scipy_interpol(fft_freqs_new_bucket)

        # Do multiplication with melbank matrix
        if config.USE_NORMAL_MELBANK:
            melbank_result = self.normalized_melbank_matrix.dot(full_freq)
        else:
            melbank_result = self.melbank_matrix.dot(full_freq)
            
        # Final return result
        if config.USE_LOG_SCALE:
            final_result = np.log(melbank_result)
        else:
            final_result = melbank_result
            
        return final_result
