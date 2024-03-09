import socket
import time
import signal
import sys
import csv

# Function to read patterns and corresponding activities from a text file
def read_activity_patterns(filename):
    pattern_lookup = {}
    with open(filename, 'r') as file:
        for line in file:
            pattern, activity = line.strip().split(':')
            pattern_lookup[pattern] = activity
    return pattern_lookup

def run_program():
    # Read patterns and corresponding activities from the text file
    pattern_lookup = read_activity_patterns('activity_patterns.txt')

    sock_l = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock_l.bind(('0.0.0.0', 12345))
    sock_l.listen()
    print('Waiting for connection')
    conn, addr = sock_l.accept()
    print('Connected')

    sample_number = 0
    current_data = ""

    with open('data_file.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Sample Number", "Time", "Value"])  # Write the header row

    with conn:
        while True:
            data = conn.recv(1024)
            if not data:
                print('Connection closed by the other side')
                break

            # Increment sample number
            sample_number += 1

            # Get current time
            current_time = time.strftime('%H:%M:%S')

            # Decode and print individual data samples
            decoded_data = data.decode().strip()
            for bit in decoded_data:
                print(f"{sample_number}, {current_time}, {bit}")

                # Write individual data samples to CSV
                write_data_to_csv(sample_number, current_time, bit)

            # Append the received data
            current_data += decoded_data

            # Check if we have received enough samples
            if sample_number % 10 == 0:
                
                # Check for patterns and corresponding activities
                detected_activity = check_activity(current_data, pattern_lookup)
                if detected_activity:
                    print(f"Detected activity: {detected_activity}")

                    # Print accumulated data every 10 samples
                    print(f"Sample: {sample_number}, Time: {current_time}, Pattern: {current_data}")

                # Reset current_data
                current_data = ""

def write_data_to_csv(sample_number, current_time, value):
    # Write individual data samples to a CSV file
    with open('data_file.csv', 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([sample_number, current_time, value])

def check_activity(data, pattern_lookup):
    # Look for patterns in the data and return corresponding activity
    for pattern, activity in pattern_lookup.items():
        if pattern in data:
            return activity
    return None

def check_activity(data, pattern_lookup):
    # Look for patterns in the data and return corresponding activity
    for pattern, activity in pattern_lookup.items():
        if pattern in data:
            return activity
    return None

def exit(signum, frame):
    sys.exit(0)

if __name__ == '__main__':
    original_sigint = signal.getsignal(signal.SIGINT)
    signal.signal(signal.SIGINT, exit)
    run_program()