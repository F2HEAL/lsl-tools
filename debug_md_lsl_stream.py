# debug_lsl_stream.py
from pylsl import resolve_streams, StreamInlet
import time

def debug_lsl_stream(stream_name="SynAmpsRT"):
    print(f"Looking for LSL stream: {stream_name}")
    
    # Find all streams
    streams = resolve_streams()
    print(f"Found {len(streams)} LSL stream(s):")
    
    for i, stream in enumerate(streams):
        print(f"\n[{i}] {stream.name()}")
        print(f"    Type: {stream.type()}")
        print(f"    Channels: {stream.channel_count()}")
        print(f"    Sample Rate: {stream.nominal_srate()} Hz")
        print(f"    Source ID: {stream.source_id()}")
        print(f"    Hostname: {stream.hostname()}")
        print(f"    Protocol Version: {stream.version()}")
        print(f"    Created at: {stream.created_at()}")
        print(f"    UID: {stream.uid()}")
        print(f"    Session ID: {stream.session_id()}")
    
    # Try to connect to the specific stream
    target_streams = [s for s in streams if s.name() == stream_name]
    
    if not target_streams:
        print(f"\n❌ Stream '{stream_name}' not found!")
        print("Available streams:")
        for stream in streams:
            print(f"  - {stream.name()} (type: {stream.type()})")
        return False
    
    print(f"\n✅ Found target stream: {stream_name}")
    stream = target_streams[0]
    
    # Create inlet to get FULL metadata
    try:
        inlet = StreamInlet(stream)
        print("✓ StreamInlet created successfully")
        
        # Get complete stream info
        info = inlet.info()
        print(f"\n📊 COMPLETE STREAM METADATA:")
        print(f"  Name: {info.name()}")
        print(f"  Type: {info.type()}")
        print(f"  Channel Count: {info.channel_count()}")
        print(f"  Nominal Sample Rate: {info.nominal_srate()} Hz")
        print(f"  Source ID: {info.source_id()}")
        print(f"  Hostname: {info.hostname()}")
        print(f"  Protocol Version: {info.version()}")
        print(f"  Created at: {info.created_at()}")
        print(f"  UID: {info.uid()}")
        print(f"  Session ID: {info.session_id()}")
        
        # Channel-specific information
        print(f"\n🎛️  CHANNEL INFORMATION:")
        desc = info.desc()
        channels = desc.child("channels")
        if channels.empty():
            print("  No detailed channel information available")
        else:
            channel = channels.first_child()
            ch_idx = 0
            while not channel.empty():
                print(f"  Channel {ch_idx}:")
                name = channel.child("label")
                if not name.empty():
                    print(f"    Label: {name.first_child().value()}")
                unit = channel.child("unit")
                if not unit.empty():
                    print(f"    Unit: {unit.first_child().value()}")
                type_node = channel.child("type")
                if not type_node.empty():
                    print(f"    Type: {type_node.first_child().value()}")
                channel = channel.next_sibling()
                ch_idx += 1
        
        # Stream description/metadata
        print(f"\n📋 STREAM DESCRIPTION:")
        if not desc.empty():
            # Try to get various description fields
            for field in ["manufacturer", "model", "subject", "session", "experiment"]:
                node = desc.child(field)
                if not node.empty():
                    value = node.first_child()
                    if not value.empty():
                        print(f"  {field.capitalize()}: {value.value()}")
        
        # Get channel names if available
        print(f"\n🔤 CHANNEL NAMES:")
        ch_names = []
        channels = desc.child("channels")
        if not channels.empty():
            channel = channels.first_child()
            while not channel.empty():
                name = channel.child("label")
                if not name.empty():
                    ch_name = name.first_child().value()
                    ch_names.append(ch_name)
                    print(f"  Channel {len(ch_names)-1}: {ch_name}")
                channel = channel.next_sibling()
        
        if not ch_names:
            print("  Using default channel names (no labels in stream)")
            ch_names = [f"Channel_{i}" for i in range(info.channel_count())]
        
        # Get a sample to verify data flow
        print(f"\n📥 TESTING DATA FLOW:")
        sample, timestamp = inlet.pull_sample(timeout=5.0)
        if sample:
            print(f"✓ Received sample with {len(sample)} channels")
            print(f"  First few values: {sample[:5]}")
            print(f"  Timestamp: {timestamp}")
            
            # Test multiple samples
            print(f"\n🔄 TESTING CONTINUOUS DATA:")
            samples, timestamps = inlet.pull_chunk(timeout=2.0, max_samples=10)
            if samples:
                print(f"✓ Received {len(samples)} samples in chunk")
                print(f"  Sample shape: {len(samples)}x{len(samples[0])}")
                print(f"  Timestamps range: {timestamps[0]:.3f} to {timestamps[-1]:.3f}")
            else:
                print("❌ No chunk data received")
                
            return True, info, ch_names
        else:
            print("❌ No sample received within timeout")
            return False, None, None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False, None, None

def print_stream_statistics(stream_name="SynAmpsRT", duration=10):
    """Collect and print stream statistics over time"""
    print(f"\n📈 COLLECTING STATISTICS FOR {duration} SECONDS:")
    
    target_streams = [s for s in resolve_streams() if s.name() == stream_name]
    if not target_streams:
        print(f"Stream '{stream_name}' not found for statistics")
        return
    
    inlet = StreamInlet(target_streams[0])
    start_time = time.time()
    sample_count = 0
    chunk_counts = []
    
    while time.time() - start_time < duration:
        samples, timestamps = inlet.pull_chunk(timeout=1.0)
        if samples:
            chunk_counts.append(len(samples))
            sample_count += len(samples)
    
    if chunk_counts:
        print(f"  Total samples: {sample_count}")
        print(f"  Average samples/sec: {sample_count/duration:.1f}")
        print(f"  Chunks received: {len(chunk_counts)}")
        print(f"  Average chunk size: {sum(chunk_counts)/len(chunk_counts):.1f}")
    else:
        print("  No data received during statistics collection")

if __name__ == "__main__":
    success, stream_info, channel_names = debug_lsl_stream("SynAmpsRT")
    
    if success:
        print(f"\n🎉 Stream connection successful!")
        print(f"Channel names: {channel_names}")
        
        # Optional: Collect statistics
        print_stream_statistics("SynAmpsRT", duration=5)
    else:
        print(f"\n💥 Failed to connect to stream")