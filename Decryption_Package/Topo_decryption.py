import struct

def read_binary_file(file_path): # Reads binary from a file (obj)
    with open(file_path, 'rb') as f:
        data = f.read()
    return data

def extract_distances(binary_data):
    # Assuming the binary data is a sequence of 4-byte floats...
    distances = []
    for i in range(0, len(binary_data), 4):
        distance = struct.unpack('f', binary_data[i:i+4])[0]
        distances.append(distance)
    return distances
import struct

def extract_message_from_distances(distances): # Extracts the LSB of each floating-point number
    message_bits = ''
    
    for distance in distances:
        distance_int = struct.unpack('I', struct.pack('f', distance))[0]
        message_bits += str(distance_int & 1)
    
    message = ''
    for i in range(0, len(message_bits), 8): # Convert bits to characters (8 bits per character)
        char_bits = message_bits[i:i+8]
        if char_bits == '00000000':  # Stops when null terminator found
            break
        message += chr(int(char_bits, 2))
    
    return message

def extract_hidden_message(stego_file):
    binary_data = read_binary_file(stego_file)
    distances = extract_distances(binary_data)
    message = extract_message_from_distances(distances)
    print("Extracted Message:", message)
    return message

# Example usage:
extracted_message = extract_hidden_message(r"C:\Users\HOME\PYTHON CS\Project\Complete\Objects\taro_modified.obj")
