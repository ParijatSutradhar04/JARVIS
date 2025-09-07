"""
Simple PyAudio Test Script
Tests microphone input capture and audio stream functionality
"""

import pyaudio
import wave
import numpy as np
import threading
import time
import os

class AudioTester:
    """Simple audio testing class"""
    
    def __init__(self):
        self.audio = None
        self.sample_rate = 44100  # Standard sample rate
        self.chunk_size = 1024
        self.channels = 1
        self.format = pyaudio.paInt16
        
    def list_audio_devices(self):
        """List all available audio devices"""
        print("🎤 Available Audio Devices:")
        print("-" * 50)
        
        self.audio = pyaudio.PyAudio()
        
        # Get default devices
        try:
            default_input = self.audio.get_default_input_device_info()
            default_output = self.audio.get_default_output_device_info()
            print(f"🔊 DEFAULT INPUT: Device {default_input['index']} - {default_input['name']}")
            print(f"🔊 DEFAULT OUTPUT: Device {default_output['index']} - {default_output['name']}")
            print("-" * 50)
        except:
            print("⚠️ Could not get default devices")
            print("-" * 50)
        
        for i in range(self.audio.get_device_count()):
            device_info = self.audio.get_device_info_by_index(i)
            
            # Determine device capabilities
            input_channels = device_info['maxInputChannels']
            output_channels = device_info['maxOutputChannels']
            
            device_types = []
            if input_channels > 0:
                device_types.append(f"Input ({input_channels} ch)")
            if output_channels > 0:
                device_types.append(f"Output ({output_channels} ch)")
            
            device_type_str = " + ".join(device_types) if device_types else "No I/O"
            
            # Mark special devices
            markers = []
            if input_channels > 0 and i == default_input.get('index', -1):
                markers.append("🎤 DEFAULT INPUT")
            if output_channels > 0 and i == default_output.get('index', -1):
                markers.append("🔊 DEFAULT OUTPUT")
            
            marker_str = " " + " ".join(markers) if markers else ""
            
            print(f"Device {i:2d}: {device_info['name']}")
            print(f"         Type: {device_type_str}{marker_str}")
            print(f"         Rate: {device_info['defaultSampleRate']:.0f} Hz")
            print()
        
        self.audio.terminate()
        return default_input.get('index', None) if 'default_input' in locals() else None
    
    def test_microphone_capture(self, duration=5, device_id=None):
        """Test basic microphone capture"""
        device_str = f" (Device {device_id})" if device_id is not None else " (Default Device)"
        print(f"🎤 Testing microphone capture for {duration} seconds{device_str}...")
        print("📢 Start speaking now!")
        
        try:
            self.audio = pyaudio.PyAudio()
            
            # Get device info if specified
            if device_id is not None:
                try:
                    device_info = self.audio.get_device_info_by_index(device_id)
                    if device_info['maxInputChannels'] == 0:
                        print(f"❌ Device {device_id} has no input channels!")
                        return False
                    print(f"🎤 Using: {device_info['name']}")
                except:
                    print(f"❌ Invalid device ID: {device_id}")
                    return False
            else:
                try:
                    device_info = self.audio.get_default_input_device_info()
                    print(f"🎤 Using default: {device_info['name']}")
                except:
                    print("⚠️ Could not get default input device info")
            
            # Open input stream
            stream = self.audio.open(
                format=self.format,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                input_device_index=device_id,  # None means default
                frames_per_buffer=self.chunk_size
            )
            
            print("✅ Audio stream opened successfully")
            
            frames = []
            for i in range(int(self.sample_rate / self.chunk_size * duration)):
                try:
                    data = stream.read(self.chunk_size, exception_on_overflow=False)
                    frames.append(data)
                    
                    # Convert to numpy array to analyze
                    audio_data = np.frombuffer(data, dtype=np.int16)
                    
                    # Check if we have valid data
                    if len(audio_data) == 0:
                        volume = 0
                    else:
                        # Calculate volume with error handling
                        mean_square = np.mean(audio_data**2)
                        if np.isnan(mean_square) or mean_square < 0:
                            volume = 0
                        else:
                            volume = np.sqrt(mean_square)
                    
                    # Ensure volume is a valid number
                    if np.isnan(volume) or np.isinf(volume):
                        volume = 0
                    
                    # Show volume level as a simple bar
                    bar_length = int(volume / 1000) if volume > 0 else 0
                    bar = "█" * min(bar_length, 50)
                    print(f"\rVolume: {bar:<50} {volume:.0f}", end="", flush=True)
                    
                except Exception as e:
                    print(f"\n❌ Error reading audio: {e}")
                    break
            
            print(f"\n✅ Successfully captured {len(frames)} audio chunks")
            
            # Clean up
            stream.stop_stream()
            stream.close()
            self.audio.terminate()
            
            # Save to file for testing
            self.save_audio_test(frames, device_id)
            return True
            
        except Exception as e:
            print(f"❌ Microphone test failed: {e}")
            if self.audio:
                self.audio.terminate()
            return False
    
    def save_audio_test(self, frames, device_id=None):
        """Save captured audio to test file"""
        try:
            device_suffix = f"_device{device_id}" if device_id is not None else "_default"
            filename = f"audio_test{device_suffix}.wav"
            
            with wave.open(filename, 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(self.audio.get_sample_size(self.format))
                wf.setframerate(self.sample_rate)
                wf.writeframes(b''.join(frames))
            
            print(f"💾 Audio saved to {filename}")
            file_size = os.path.getsize(filename)
            print(f"📁 File size: {file_size} bytes")
            
        except Exception as e:
            print(f"❌ Failed to save audio: {e}")
    
    def test_realtime_monitoring(self, duration=10):
        """Test real-time audio level monitoring"""
        print(f"🎤 Real-time audio monitoring for {duration} seconds...")
        print("📢 Speak to see live audio levels!")
        print("Press Ctrl+C to stop early")
        
        try:
            self.audio = pyaudio.PyAudio()
            
            stream = self.audio.open(
                format=self.format,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size
            )
            
            start_time = time.time()
            max_volume = 0
            
            while time.time() - start_time < duration:
                try:
                    data = stream.read(self.chunk_size, exception_on_overflow=False)
                    audio_data = np.frombuffer(data, dtype=np.int16)
                    
                    # Calculate volume metrics with error handling
                    if len(audio_data) == 0:
                        volume_rms = 0
                        volume_peak = 0
                    else:
                        # RMS calculation with safety checks
                        try:
                            mean_square = np.mean(audio_data.astype(np.float64)**2)
                            if np.isnan(mean_square) or mean_square < 0:
                                volume_rms = 0
                            else:
                                volume_rms = np.sqrt(mean_square)
                                if np.isnan(volume_rms) or np.isinf(volume_rms):
                                    volume_rms = 0
                        except:
                            volume_rms = 0
                        
                        # Peak calculation with safety checks
                        try:
                            peak = np.max(np.abs(audio_data))
                            if np.isnan(peak) or np.isinf(peak):
                                volume_peak = 0
                            else:
                                volume_peak = float(peak)
                        except:
                            volume_peak = 0
                    
                    # Ensure values are valid numbers
                    if np.isnan(volume_rms) or np.isinf(volume_rms):
                        volume_rms = 0
                    if np.isnan(volume_peak) or np.isinf(volume_peak):
                        volume_peak = 0
                        
                    max_volume = max(max_volume, volume_rms)
                    
                    # Visual feedback with safe conversion
                    try:
                        bar_length = int(volume_rms / 500) if volume_rms > 0 and volume_rms < 1e6 else 0
                        bar = "█" * min(max(0, bar_length), 40)
                    except (ValueError, OverflowError):
                        bar = ""
                    
                    remaining = duration - (time.time() - start_time)
                    
                    print(f"\rRMS: {volume_rms:6.0f} Peak: {volume_peak:6.0f} [{bar:<40}] {remaining:.1f}s", 
                          end="", flush=True)
                    
                    time.sleep(0.01)  # Small delay
                    
                except KeyboardInterrupt:
                    print("\n⏹️ Stopped by user")
                    break
                except Exception as e:
                    print(f"\n❌ Error in monitoring: {e}")
                    break
            
            print(f"\n📊 Maximum volume recorded: {max_volume:.0f}")
            
            stream.stop_stream()
            stream.close()
            self.audio.terminate()
            
            return True
            
        except Exception as e:
            print(f"❌ Real-time monitoring failed: {e}")
            if self.audio:
                self.audio.terminate()
            return False
    
    def test_audio_format_compatibility(self):
        """Test different audio formats for compatibility"""
        print("🔧 Testing audio format compatibility...")
        
        formats_to_test = [
            (pyaudio.paInt16, "16-bit Integer"),
            (pyaudio.paInt24, "24-bit Integer"), 
            (pyaudio.paInt32, "32-bit Integer"),
            (pyaudio.paFloat32, "32-bit Float")
        ]
        
        sample_rates = [16000, 22050, 44100, 48000]
        
        self.audio = pyaudio.PyAudio()
        
        print("📋 Supported formats:")
        for fmt, name in formats_to_test:
            for rate in sample_rates:
                try:
                    # Test if format is supported
                    is_supported = self.audio.is_format_supported(
                        rate=rate,
                        input_device=None,
                        input_channels=1,
                        input_format=fmt
                    )
                    status = "✅" if is_supported else "❌"
                    print(f"  {status} {name} @ {rate}Hz")
                except:
                    print(f"  ❌ {name} @ {rate}Hz (Error)")
        
        self.audio.terminate()

def main():
    """Main test function"""
    print("🎤 PyAudio Microphone Test Suite")
    print("=" * 50)
    
    tester = AudioTester()
    
    print("Choose test to run:")
    print("1. 📋 List audio devices")
    print("2. 🎤 Test microphone capture (5 seconds)")  
    print("3. 📊 Real-time audio monitoring (10 seconds)")
    print("4. 🔧 Test format compatibility")
    print("5. 🚀 Run all tests")
    print("6. 🎯 Test specific device by ID")
    
    try:
        choice = input("\nEnter choice (1-6): ").strip()
        
        if choice == "1":
            tester.list_audio_devices()
            
        elif choice == "2":
            success = tester.test_microphone_capture()
            if success:
                print("🎉 Microphone capture test PASSED!")
            else:
                print("❌ Microphone capture test FAILED!")
                
        elif choice == "3":
            success = tester.test_realtime_monitoring()
            if success:
                print("🎉 Real-time monitoring test PASSED!")
            else:
                print("❌ Real-time monitoring test FAILED!")
                
        elif choice == "4":
            tester.test_audio_format_compatibility()
            
        elif choice == "5":
            print("🚀 Running all tests...\n")
            
            print("TEST 1/4: Audio Devices")
            tester.list_audio_devices()
            input("\nPress Enter to continue...")
            
            print("\nTEST 2/4: Microphone Capture")
            mic_success = tester.test_microphone_capture()
            input("\nPress Enter to continue...")
            
            print("\nTEST 3/4: Real-time Monitoring")  
            monitor_success = tester.test_realtime_monitoring()
            input("\nPress Enter to continue...")
            
            print("\nTEST 4/4: Format Compatibility")
            tester.test_audio_format_compatibility()
            
            print("\n" + "=" * 50)
            print("📋 TEST SUMMARY:")
            print(f"  Microphone Capture: {'✅ PASSED' if mic_success else '❌ FAILED'}")
            print(f"  Real-time Monitor: {'✅ PASSED' if monitor_success else '❌ FAILED'}")
            
            if mic_success and monitor_success:
                print("\n🎉 All critical tests PASSED!")
                print("🚀 Your audio setup is ready for JARVIS!")
            else:
                print("\n⚠️ Some tests failed. Check your microphone setup.")
        
        elif choice == "6":
            devices = tester.list_audio_devices()
            audio = pyaudio.PyAudio()
            
            try:
                device_id = input(f"\nEnter device ID to test (0-{audio.get_device_count()-1}): ").strip()
                device_id = int(device_id)
                
                if 0 <= device_id < audio.get_device_count():
                    device_info = audio.get_device_info_by_index(device_id)
                    if device_info['maxInputChannels'] > 0:
                        print(f"\n🎯 Testing specific device: {device_info['name']} and id: {device_id}")
                        success = tester.test_microphone_capture(device_id=device_id)
                        if success:
                            print(f"🎉 Device {device_id} test PASSED!")
                        else:
                            print(f"❌ Device {device_id} test FAILED!")
                    else:
                        print(f"❌ Device {device_id} ({device_info['name']}) has no input channels!")
                else:
                    print(f"❌ Invalid device ID! Must be between 0 and {audio.get_device_count()-1}")
            except ValueError:
                print("❌ Invalid input! Please enter a number.")
            finally:
                audio.terminate()
        
        else:
            print("❌ Invalid choice")
            
    except KeyboardInterrupt:
        print("\n👋 Tests interrupted")
    except Exception as e:
        print(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
