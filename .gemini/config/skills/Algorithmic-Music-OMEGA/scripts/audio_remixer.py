import wave
import struct
import math
import os
import sys

# █ SYS_ID: ALGORITHMIC_MUSIC_OMEGA (VECTOR: REMIX)
# █ STATE: C5-REAL | TARGET: WEIRDCORE_AUDIO_MUTATION

def apply_remix(input_file, output_file):
    with wave.open(input_file, 'r') as wav_in:
        n_channels = wav_in.getnchannels()
        sampwidth = wav_in.getsampwidth()
        framerate = wav_in.getframerate()
        n_frames = wav_in.getnframes()
        
        raw_data = wav_in.readframes(n_frames)
        samples = struct.unpack(f"{n_frames * n_channels}h", raw_data)
        
    remixed_samples = []
    
    # Delay parameters (Echo)
    delay_ms = 350
    delay_samples = int((delay_ms / 1000.0) * framerate) * n_channels
    decay = 0.6
    delay_buffer = [0] * delay_samples
    buffer_idx = 0
    
    # Bitcrush parameters (Quantize to 4-bit for harsh industrial texture)
    bit_depth = 4
    step = 2**(16 - bit_depth)
    
    for s in samples:
        # 1. Bitcrush (Degradación de señal)
        crushed = (s // step) * step
        
        # 2. Delay (Inyección de memoria termodinámica)
        delayed = delay_buffer[buffer_idx]
        mixed = crushed + (delayed * decay)
        
        # 3. Buffer Update
        delay_buffer[buffer_idx] = mixed
        buffer_idx = (buffer_idx + 1) % delay_samples
        
        # 4. Soft Clipping (Prevenir Overflow)
        final_sample = max(-32768, min(32767, int(mixed)))
        remixed_samples.append(final_sample)
        
    with wave.open(output_file, 'w') as wav_out:
        wav_out.setnchannels(n_channels)
        wav_out.setsampwidth(sampwidth)
        wav_out.setframerate(framerate)
        
        packed_data = struct.pack(f"{len(remixed_samples)}h", *remixed_samples)
        wav_out.writeframes(packed_data)
        
    return output_file

if __name__ == "__main__":
    if len(sys.argv) > 2:
        in_file = sys.argv[1]
        out_file = sys.argv[2]
    else:
        base_dir = os.path.dirname(__file__)
        in_file = os.path.join(base_dir, "c5_music_advanced.wav")
        out_file = os.path.join(base_dir, "c5_music_remix.wav")
        
    print(f"Executing C5-REAL Audio Remix...\nInput: {in_file}\nTarget: {out_file}")
    apply_remix(in_file, out_file)
    print("Remix complete. Industrial Lo-Fi aesthetics enforced.")
