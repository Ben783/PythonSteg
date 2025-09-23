import numpy as np
from PIL import Image

alphaDictionary = {
    'a': (2,1), 'b': (2,2), 'c': (2,3), 'd': (2,4), 'e': (2,5),
    'f': (2,-1), 'g': (2,-2), 'h': (2,-3), 'i': (2,-4), 'j': (2,-5),
    'k': (4,1), 'l': (4,2), 'm': (4,3), 'n': (4,4), 'o': (4,5),
    'p': (4,-1), 'q': (4,-2), 'r': (4,-3), 's': (4,-4), 't': (4,-5),
    'u': (6,1), 'v': (6,2), 'w': (6,3), 'x': (6,4), 'y': (6,5), 'z': (6,-1),
    '!': (6,-2), '.': (6,-3), ',': (6,-4), '?': (6,-5), '\n':(8,1), ' ': (8,2)
}

def split_rgba_image(image, n):
    height, width, _ = image.shape
    pixels = image.reshape(-1, 4)
    num_pixels = pixels.shape[0]
    
    num_groups = num_pixels // n
    remainder = num_pixels % n
    
    groups = [pixels[i*n:(i+1)*n] for i in range(num_groups)]
    if remainder > 0:
        groups.append(pixels[num_groups*n:])
    
    return groups

def reverse_dictionary(original_dict):
    return {v: k for k, v in original_dict.items()}

def RGBA_decryption_distributed(orgImage, altImage, groupSize, dictionary=alphaDictionary):
    orgImage = Image.open(orgImage).convert("RGBA")
    altImage = Image.open(altImage).convert("RGBA")
    orgArray = np.array(orgImage).astype(np.int32)
    altArray = np.array(altImage).astype(np.int32) # Convert to numpy arrays as int32 to prevent overflow
    
    orgGroups = split_rgba_image(orgArray, groupSize)
    altGroups = split_rgba_image(altArray, groupSize)
    reverse_dict = reverse_dictionary(dictionary)

    decrypted_message = []

    for orgGroup, altGroup in zip(orgGroups, altGroups):
        rgb_diff = np.sum(np.abs(orgGroup[:, :3] - altGroup[:, :3])) #RGB sum of absolute differences
        
        alpha_diff = np.sum(altGroup[:, 3] - orgGroup[:, 3]) # Alpha modified minus original
        
        # Get the character or None if not found (using dictionary)
        char = reverse_dict.get((rgb_diff, alpha_diff), '')
        if char is not None:  # Only append if character is found
            decrypted_message.append(char)
        
        # Debug print for first group
        if len(decrypted_message) == 1:
            #print("\nFirst Group Analysis:")
            #print("Original pixels:\n", orgGroup)
            #print("Modified pixels:\n", altGroup)
            #print("RGB differences per pixel:", np.sum(np.abs(orgGroup[:, :3] - altGroup[:, :3]), axis=1))
            #print("Alpha differences per pixel:", orgGroup[:, 3] - altGroup[:, 3])
            print(f"Total RGB diff: {rgb_diff}, Alpha diff: {alpha_diff}")
    
    return ''.join(decrypted_message)
                




if __name__ == "__main__":  # Fixed this line
    # Load images
    orgImage = r"C:\Users\HOME\PYTHON CS\Project\Complete\Images\varying_alpha.png"
    altImage = r"C:\Users\HOME\PYTHON CS\Project\Complete\Images\expImage.png"
    groupSize = 4

    # Decrypt and print message
    message = RGBA_decryption_distributed(orgImage, altImage, groupSize)
    print("Decrypted Message:")
    print(message)