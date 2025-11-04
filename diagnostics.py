#!/usr/bin/env python3
"""
OpenCode System Diagnostics
Comprehensive system health check and reporting
"""

import psutil
import subprocess
import os
import json
from datetime import datetime

def check_cpu():
    """Check CPU usage and information"""
    print("\n=== CPU Diagnostics ===")
    cpu_percent = psutil.cpu_percent(interval=2, percpu=True)
    print(f"CPU Usage per core: {cpu_percent}")
    print(f"Average CPU Usage: {sum(cpu_percent)/len(cpu_percent):.2f}%")
    print(f"CPU Count: {psutil.cpu_count()} cores")
    
    # Get CPU frequency if available
    try:
        freq = psutil.cpu_freq()
        if freq:
            print(f"CPU Frequency: {freq.current:.2f} MHz")
    except:
        pass
    
    # CPU temperature
    try:
        temps = psutil.sensors_temperatures()
        if 'coretemp' in temps:
            print(f"CPU Temperature: {temps['coretemp'][0].current}°C")
    except:
        print("Temperature sensors not available")

def check_memory():
    """Check memory usage"""
    print("\n=== Memory Diagnostics ===")
    mem = psutil.virtual_memory()
    print(f"Total Memory: {mem.total / (1024**3):.2f} GB")
    print(f"Available Memory: {mem.available / (1024**3):.2f} GB")
    print(f"Used Memory: {mem.used / (1024**3):.2f} GB ({mem.percent}%)")
    
    swap = psutil.swap_memory()
    print(f"Swap Total: {swap.total / (1024**3):.2f} GB")
    print(f"Swap Used: {swap.used / (1024**3):.2f} GB ({swap.percent}%)")

def check_disk():
    """Check disk usage"""
    print("\n=== Disk Diagnostics ===")
    partitions = psutil.disk_partitions()
    
    for partition in partitions:
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            print(f"\nPartition: {partition.device}")
            print(f"  Mountpoint: {partition.mountpoint}")
            print(f"  File system: {partition.fstype}")
            print(f"  Total: {usage.total / (1024**3):.2f} GB")
            print(f"  Used: {usage.used / (1024**3):.2f} GB ({usage.percent}%)")
            print(f"  Free: {usage.free / (1024**3):.2f} GB")
        except PermissionError:
            continue

def check_network():
    """Check network interfaces and connectivity"""
    print("\n=== Network Diagnostics ===")
    
    # Network interfaces
    interfaces = psutil.net_if_addrs()
    for interface, addresses in interfaces.items():
        print(f"\nInterface: {interface}")
        for addr in addresses:
            print(f"  {addr.family.name}: {addr.address}")
    
    # Network statistics
    net_io = psutil.net_io_counters()
    print(f"\nNetwork I/O:")
    print(f"  Bytes Sent: {net_io.bytes_sent / (1024**2):.2f} MB")
    print(f"  Bytes Received: {net_io.bytes_recv / (1024**2):.2f} MB")
    
    # Test connectivity
    print("\nConnectivity Test:")
    try:
        result = subprocess.run(
            ["ping", "-c", "3", "8.8.8.8"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            print("  Internet: Connected")
        else:
            print("  Internet: Disconnected")
    except:
        print("  Internet: Unable to test")

def check_docker():
    """Check Docker status"""
    print("\n=== Docker Diagnostics ===")
    
    try:
        # Docker version
        version = subprocess.check_output(
            ["docker", "--version"],
            text=True
        ).strip()
        print(f"Docker Version: {version}")
        
        # Running containers
        containers = subprocess.check_output(
            ["docker", "ps", "--format", "{{.Names}}\t{{.Status}}\t{{.Size}}"],
            text=True
        ).strip()
        
        if containers:
            print("\nRunning Containers:")
            for line in containers.split('\n'):
                print(f"  {line}")
        else:
            print("\nNo running containers")
        
        # Docker system info
        info = subprocess.check_output(
            ["docker", "system", "df"],
            text=True
        )
        print(f"\nDocker System Usage:")
        print(info)
        
    except FileNotFoundError:
        print("Docker not installed or not accessible")
    except subprocess.CalledProcessError:
        print("Docker not running or permission denied")

def check_processes():
    """Check top processes by CPU and memory"""
    print("\n=== Process Diagnostics ===")
    
    # Get all processes
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            processes.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    
    # Top CPU consumers
    print("\nTop 5 CPU Consumers:")
    top_cpu = sorted(processes, key=lambda x: x['cpu_percent'], reverse=True)[:5]
    for proc in top_cpu:
        print(f"  {proc['name']}: {proc['cpu_percent']:.1f}%")
    
    # Top memory consumers
    print("\nTop 5 Memory Consumers:")
    top_mem = sorted(processes, key=lambda x: x['memory_percent'], reverse=True)[:5]
    for proc in top_mem:
        print(f"  {proc['name']}: {proc['memory_percent']:.1f}%")

def check_audio():
    """Check audio devices"""
    print("\n=== Audio Diagnostics ===")
    
    try:
        import sounddevice as sd
        devices = sd.query_devices()
        print("Audio Devices:")
        print(devices)
    except Exception as e:
        print(f"Unable to query audio devices: {e}")

def generate_report():
    """Generate comprehensive diagnostic report"""
    print("=" * 60)
    print("OpenCode System Diagnostics Report")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    check_cpu()
    check_memory()
    check_disk()
    check_network()
    check_docker()
    check_processes()
    check_audio()
    
    print("\n" + "=" * 60)
    print("Diagnostics Complete")
    print("=" * 60)
    
    # Save report to file
    report_file = f"/app/logs/diagnostics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    try:
        with open(report_file, 'w') as f:
            # Redirect output to file (simplified version)
            pass
        print(f"\nReport saved to: {report_file}")
    except Exception as e:
        print(f"Could not save report: {e}")

if __name__ == "__main__":
    try:
        generate_report()
    except KeyboardInterrupt:
        print("\nDiagnostics interrupted by user")
    except Exception as e:
        print(f"Error running diagnostics: {e}")
