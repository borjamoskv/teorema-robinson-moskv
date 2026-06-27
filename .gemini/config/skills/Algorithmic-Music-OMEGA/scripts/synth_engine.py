import math
import wave
import struct
import random
import os

# █ SYS_ID: ALGORITHMIC_MUSIC_OMEGA
# █ STATE: C5-REAL | TOPOLOGY: POLYPHONIC & MULTI-OSCILLATOR

SAMPLE_RATE = 44100
AMPLITUDE_MAX = 32767.0

def generate_oscillator(freq, t, osc_type='sine'):
    """Generador base de ondas."""
    if osc_type == 'sine':
        return math.sin(2.0 * math.pi * freq * t)
    elif osc_type == 'square':
        return 1.0 if math.sin(2.0 * math.pi * freq * t) > 0 else -1.0
    elif osc_type == 'saw':
        return 2.0 * (freq * t - math.floor(0.5 + freq * t))
    elif osc_type == 'noise':
        return random.uniform(-1.0, 1.0)
    return 0.0

def generate_note_advanced(frequency, duration, volume=0.5, osc_type='sine', attack=0.05, decay=0.1, sustain=0.7, release=0.2):
    """Genera una nota con envolvente ADSR estricta y mezcla de sub-osciladores."""
    num_samples = int(SAMPLE_RATE * duration)
    samples = []
    
    attack_samples = int(SAMPLE_RATE * attack)
    decay_samples = int(SAMPLE_RATE * decay)
    release_samples = int(SAMPLE_RATE * release)
    
    for i in range(num_samples):
        t = float(i) / SAMPLE_RATE
        
        # Inyección de Envolvente Termodinámica (ADSR)
        if i < attack_samples:
            env = float(i) / (attack_samples + 1e-9)
        elif i < attack_samples + decay_samples:
            env = 1.0 - (1.0 - sustain) * (float(i - attack_samples) / (decay_samples + 1e-9))
        elif i > num_samples - release_samples:
            env = sustain * float(num_samples - i) / (release_samples + 1e-9)
        else:
            env = sustain
            
        # Fusión Isomórfica: Fundamental + Sub-octava + Detune Menor
        val1 = generate_oscillator(frequency, t, osc_type)
        val2 = generate_oscillator(frequency * 0.5, t, 'sine') * 0.3 
        val3 = generate_oscillator(frequency * 1.005, t, osc_type) * 0.2
        
        value = (val1 + val2 + val3) / 1.5 * env * volume
        samples.append(value)
        
    return samples

def synthesize_polyphony(output_file="c5_music_advanced.wav"):
    """Motor de orquestación polifónica: Bassline estructurado + Arpegio fractal."""
    scale = [110.00, 130.81, 146.83, 164.81, 196.00, 220.00, 261.63, 293.66, 329.63, 392.00, 440.00] # A Minor Range
    
    track_length_sec = 8.0
    track_length_samples = int(SAMPLE_RATE * track_length_sec)
    master_mix = [0.0] * track_length_samples
    
    random.seed(101) # Determinismo criptográfico
    
    # 1. Capa de Infraestructura (Bassline - Square)
    time_offset = 0.0
    while time_offset < track_length_sec:
        freq = random.choice([scale[0], scale[1], scale[3]]) # A2, C3, E3
        dur = 0.5 # 120 BPM Half-notes
        note_samples = generate_note_advanced(freq, dur, volume=0.4, osc_type='square', attack=0.01, release=0.1)
        
        start_idx = int(time_offset * SAMPLE_RATE)
        for i, s in enumerate(note_samples):
            if start_idx + i < track_length_samples:
                master_mix[start_idx + i] += s
        time_offset += dur

    # 2. Capa de Varianza Estocástica (Arpeggio - Sawtooth)
    time_offset = 0.0
    while time_offset < track_length_sec:
        freq = random.choice(scale[5:]) # A3 to A4
        dur = 0.125 # 120 BPM 16th-notes
        note_samples = generate_note_advanced(freq, dur, volume=0.25, osc_type='saw', attack=0.01, decay=0.05, sustain=0.2, release=0.05)
        
        start_idx = int(time_offset * SAMPLE_RATE)
        for i, s in enumerate(note_samples):
            if start_idx + i < track_length_samples:
                master_mix[start_idx + i] += s
        time_offset += dur

    # Cristalización a PCM
    with wave.open(output_file, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(SAMPLE_RATE)
        
        for sample in master_mix:
            clipped_sample = max(-32768, min(32767, int(sample * AMPLITUDE_MAX)))
            wav_file.writeframes(struct.pack('h', clipped_sample))
            
    return output_file

if __name__ == "__main__":
    bocetos_dir = "$CORTEX_ROOT/BOCETOS"
    try:
        os.makedirs(bocetos_dir, exist_ok=True)
        output_path = os.path.join(bocetos_dir, "c5_music_advanced.wav")
    except Exception:
        # Fallback to local if permission issue
        output_path = os.path.join(os.path.dirname(__file__), "c5_music_advanced.wav")
        
    print(f"Executing ALGORITHMIC_MUSIC_OMEGA (Polyphonic Delta) -> {output_path}")
    synthesize_polyphony(output_path)
    print("Polyphonic Synthesis complete. Exergy yield maximum.")

