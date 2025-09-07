#!/usr/bin/env python3
"""Quick audio test to verify PyAudio NaN fix"""

import pyaudio
import numpy as np
import time

def test_audio():
    """Test audio capture with proper error handling"""
    p = pyaudio.PyAudio()
    
    try:
        # Open stream
        stream = p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=44100,
            input=True,
            frames_per_buffer=1024
        )
        
        print("🎤 Testing audio capture for 3 seconds...")
        print("Speak into your microphone!")
        
        start_time = time.time()
        while time.time() - start_time < 3:
            try:
                data = stream.read(1024, exception_on_overflow=False)
                audio_data = np.frombuffer(data, dtype=np.int16)
                
                # Safe volume calculation
                if len(audio_data) == 0:
                    volume = 0
                else:
                    try:
                        mean_square = np.mean(audio_data.astype(np.float64)**2)
                        if np.isnan(mean_square) or mean_square < 0:
                            volume = 0
                        else:
                            volume = np.sqrt(mean_square)
                            if np.isnan(volume) or np.isinf(volume):
                                volume = 0
                    except:
                        volume = 0
                
                # Safe bar creation
                try:
                    bar_length = int(volume / 500) if volume > 0 and volume < 1e6 else 0
                    bar = "█" * min(max(0, bar_length), 20)
                except (ValueError, OverflowError):
                    bar = ""
                
                remaining = 3 - (time.time() - start_time)
                print(f"\rVolume: {volume:6.0f} [{bar:<20}] {remaining:.1f}s", 
                      end="", flush=True)
                
                time.sleep(0.05)
                
            except Exception as e:
                print(f"\nError during capture: {e}")
                break
        
        print("\n✅ Audio test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    finally:
        stream.close()
        p.terminate()

if __name__ == "__main__":
    test_audio()
