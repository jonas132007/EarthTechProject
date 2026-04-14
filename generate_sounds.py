import wave, struct, math

def generate_tone(filename, freq_start, freq_end, duration, volume=0.3):
    sample_rate = 44100
    n_samples = int(sample_rate * duration)
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        for i in range(n_samples):
            t = float(i) / sample_rate
            current_freq = freq_start + (freq_end - freq_start) * (t / duration)
            
            # Simple envelope to remove clicks
            env = 1.0
            if t < 0.05: env = t / 0.05
            if t > duration - 0.05: env = (duration - t) / 0.05
                
            value = int(volume * env * 32767.0 * math.sin(2.0 * math.pi * current_freq * t))
            data = struct.pack('<h', value)
            wav_file.writeframesraw(data)

# Score/Success (High happy ping)
generate_tone("score.wav", 600, 1200, 0.2, 0.3)

# Throw (Whoosh up)
generate_tone("throw.wav", 200, 400, 0.15, 0.2)

# Error / Hit obstacle (Low descending)
generate_tone("error.wav", 300, 150, 0.3, 0.3)

print("Generated 3 sound files.")
