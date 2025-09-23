from PIL import Image
import numpy as np
import math

def logistic_map(x, r):
    return r * x * (1 - x)

def get_alpha_state():
    """Check if alpha embedding is enabled (any non-zero alpha values)"""
    return any(v[1] != 0 for v in embedding_alphabet.values())

# Generates pseudorandom coordinates
def generate_pseudorandom_coordinates(num_points, r, x0, y0, width, height, let_run):
    x, y = x0, y0
    coordinates = []
    seen = set() # 'set' allows no duplicates

    # Lets the logistic map run on and stabilize
    for run in range(let_run):
        x = logistic_map(x, r)
        y = logistic_map(y, r)
    
    # Generating UNIQUE coordinates
    while len(coordinates) < num_points:
        x = logistic_map(x, r)
        y = logistic_map(y, r)
        scaled_x = int(x * width) # scaling x & y values to be between defined parameters
        scaled_y = int(y * height)
        coord = (scaled_x, scaled_y)
        
        if coord not in seen:
            seen.add(coord)
            coordinates.append(coord)
    
    return np.array(coordinates)

# Dictionary to map characters to RGB and alpha changes
embedding_alphabet = {
    'a': (2,1), 'b': (2,2), 'c': (2,3), 'd': (2,4), 'e': (2,5),
    'f': (2,-1), 'g': (2,-2), 'h': (2,-3), 'i': (2,-4), 'j': (2,-5),
    'k': (4,1), 'l': (4,2), 'm': (4,3), 'n': (4,4), 'o': (4,5),
    'p': (4,-1), 'q': (4,-2), 'r': (4,-3), 's': (4,-4), 't': (4,-5),
    'u': (6,1), 'v': (6,2), 'w': (6,3), 'x': (6,4), 'y': (6,5), 'z': (6,-1),
    '!': (6,-2), '.': (6,-3), ',': (6,-4), '?': (6,-5), '\n':(8,1), ' ': (8,2)
}


def splitDoc(filepath):
    with open(filepath, "r", encoding="utf-8") as file:
        doc = []
        for line in file:
            for char in line:
                doc.append(char.lower())
        return doc

def calculate_grayscale(r, g, b):
    return round((0.299 * r) + (0.587 * g) + (0.114 * b))

def extract_lsb(value):
    return int(value) & 1

def find_valid_modification(r, g, b, total_change):
    original_gray = calculate_grayscale(r, g, b)
    original_lsb = extract_lsb(original_gray)

    possible_combinations = []
    for r_change in range(-total_change, total_change + 1):
        for g_change in range(-total_change, total_change + 1):
            for b_change in range(-total_change, total_change + 1):
                if abs(r_change) + abs(g_change) + abs(b_change) == total_change:
                    if 0 <= r + r_change <= 255 and 0 <= g + g_change <= 255 and 0 <= b + b_change <= 255:
                        modified_gray = calculate_grayscale(r + r_change, g + g_change, b + b_change)
                        modified_lsb = extract_lsb(modified_gray)
                        if modified_lsb == original_lsb:
                            possible_combinations.append((r + r_change, g + g_change, b + b_change))
    return possible_combinations

def least_deviation(groups, target):
    min_deviation = float('inf') # Initialise the minimum deviation to infinity
    best_group = None # Initialise the best group to None

    for group in groups:
        total_deviation = 0
        for value in group:
            total_deviation += (value - target)

        total_deviation = abs(total_deviation)

        if total_deviation < min_deviation:
            min_deviation = total_deviation
            best_group = group

    return best_group

# Map the text to the alphabet, returning the RGB and alpha changes
def map_text(text, alphabet):
    distributed_text = []
    for character in text:
        if character in alphabet:
            distributed_text.append(alphabet[character])  # Append the (RGB change, alpha change)
    return distributed_text

def disable_alpha_embedding():
    global alphaDictionary
    alphaDictionary = {k: (v[0], 0) for k, v in alphaDictionary.items()}
    #print("All alpha values set to 0")

def embedding(text_path, image_path, r, x0, y0, let_run, save_path, alphabet=embedding_alphabet):
    text = splitDoc(text_path)
    textlen = len(text)
    image = Image.open(image_path).convert("RGBA")
    distText = map_text(text, alphabet)  # Map the text to RGB and alpha changes. Returns (RGB change, alpha change)
    alpha_change = [row[1] for row in distText]  # Alpha values
    rgb_change = [row[0] for row in distText]  # RGB values

    width, height = image.width, image.height  # Image dimensions
    # Generating random coordinates...
    random_coordinates = generate_pseudorandom_coordinates(15000, r, x0, y0, width, height, let_run) # textLen is 15000 to compensate for skipping characters
    messagePos = 0

    for coordinate in random_coordinates:
        # Check if the entire message has been embedded
        if messagePos >= len(distText):
            break

        pixel = list(image.getpixel(coordinate))  # Get the current pixel as a list (RGBA)
        validMods = find_valid_modification(pixel[0], pixel[1], pixel[2], distText[messagePos][0])
        bestGroup = least_deviation(validMods, np.mean(pixel[:-1]))

        # RGB and alpha changes for the current character
        new_rgb = bestGroup
        alphaChange = alpha_change[messagePos] if messagePos < len(distText) else 0

        # Calculate the difference (debugging)
        difference = [a - b for a, b in zip(new_rgb, pixel[:-1])]
        original_pixel = pixel.copy()
        #print(f"Original Pixel (Coordinate {coordinate}): {original_pixel}")
        #print(f"RGB Difference: {difference}, Alpha Change: {alphaChange}")

        skipFlag = False
        # RGB channels: Apply the difference
        for channel in range(3):  # Represents RGB channels
            new_value = pixel[channel] + difference[channel]  # Uses difference to modify the pixel
            if new_value > 255 or new_value < 0:
                skipFlag = True
                break
            pixel[channel] = max(0, min(255, new_value))

        # Only updates alpha if RGB values are valid...
        if not skipFlag:
            # ...Apply the alpha change
            new_alpha = pixel[3] + alphaChange
            if new_alpha > 255 or new_alpha < 0:
                skipFlag = True
            pixel[3] = max(0, min(255, new_alpha))  # Ensures the alpha value is within the valid range

        if not skipFlag:
            #print(f"Altered Pixel: {pixel}")
            image.putpixel(coordinate, tuple(pixel))  # Update the pixel in the image
            messagePos += 1  # Moves onto the next character
            #print(messagePos)
        else:
            pass
            #print(f"Skipping pixel at {coordinate} due to invalid change.")


    image.save(save_path)



# r = 3.99        # Logistic map parameter
# x0 = 0.897       # Initial value for x-coordinate
# y0 = 0.87      # Initial value for y-coordinate
# let_run = 1000    # Number of iterations to let the logistic map stabilize

# # Embed the text into the image
# embedded_image = embedding(r"C:\Users\HOME\PYTHON CS\Project\Complete\Text\1st Chapter Animal Farm.sty", 
#                            r"C:\Users\HOME\PYTHON CS\Project\Complete\Images/TREE.png", r, x0, y0, let_run, 
#                            r"C:\Users\HOME\PYTHON CS\Project\Complete\Images\expImage.png")

# Save the embedded image
#embedded_image.save(r"C:\Users\HOME\PYTHON CS\Project\Complete\Images\expImage.png")