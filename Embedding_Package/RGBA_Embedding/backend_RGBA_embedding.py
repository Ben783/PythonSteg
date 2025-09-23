
import math
from PIL import Image
import numpy as np


def calculate_grayscale(r, g, b):
    return round((0.299 * r) + (0.587 * g) + (0.114 * b))

def extract_lsb(value):
    return int(value) & 1

def find_valid_modification(r, g, b, total_change):
    """Find valid RGB modifications where sum(|Δr| + |Δg| + |Δb|) == total_change"""
    r, g, b = int(r), int(g), int(b)
    original_lsb = calculate_grayscale(r, g, b) & 1
    possible_combinations = []
    
    # Generate all possible changes where sum of absolute deltas equals total_change
    for delta_r in range(-min(total_change, r), min(total_change, 255 - r) + 1):
        remaining_after_r = total_change - abs(delta_r)
        for delta_g in range(-min(remaining_after_r, g), min(remaining_after_r, 255 - g) + 1):
            delta_b = remaining_after_r - abs(delta_g)
            for delta_b in [delta_b, -delta_b] if delta_b != 0 else [0]:
                new_r, new_g, new_b = r + delta_r, g + delta_g, b + delta_b
                if 0 <= new_b <= 255:
                    if (calculate_grayscale(new_r, new_g, new_b) & 1) == original_lsb:
                        actual_change = abs(delta_r) + abs(delta_g) + abs(delta_b)
                        if actual_change == total_change:  # Critical check
                            possible_combinations.append((new_r, new_g, new_b))
    
    return possible_combinations

def least_deviation(groups, target):
    min_deviation = float('inf')
    best_group = None

    for group in groups:
        total_deviation = 0
        for value in group:
            total_deviation += (value - target)

        total_deviation = abs(total_deviation)

        if total_deviation < min_deviation:
            min_deviation = total_deviation
            best_group = group

    return best_group


alphaDictionary = {
    'a': (2,1), 'b': (2,2), 'c': (2,3), 'd': (2,4), 'e': (2,5),
    'f': (2,-1), 'g': (2,-2), 'h': (2,-3), 'i': (2,-4), 'j': (2,-5),
    'k': (4,1), 'l': (4,2), 'm': (4,3), 'n': (4,4), 'o': (4,5),
    'p': (4,-1), 'q': (4,-2), 'r': (4,-3), 's': (4,-4), 't': (4,-5),
    'u': (6,1), 'v': (6,2), 'w': (6,3), 'x': (6,4), 'y': (6,5), 'z': (6,-1),
    '!': (6,-2), '.': (6,-3), ',': (6,-4), '?': (6,-5), '\n':(8,1), ' ': (8,2)
}

def disable_alpha_embedding():
    """Set all alpha values to 0 in the dictionary"""
    global alphaDictionary
    alphaDictionary = {k: (v[0], 0) for k, v in alphaDictionary.items()}

def enable_alpha_embedding():
    """Restore original alpha values to the dictionary"""
    global alphaDictionary
    alphaDictionary = {
        'a': (2,1), 'b': (2,2), 'c': (2,3), 'd': (2,4), 'e': (2,5),
        'f': (2,-1), 'g': (2,-2), 'h': (2,-3), 'i': (2,-4), 'j': (2,-5),
        'k': (4,1), 'l': (4,2), 'm': (4,3), 'n': (4,4), 'o': (4,5),
        'p': (4,-1), 'q': (4,-2), 'r': (4,-3), 's': (4,-4), 't': (4,-5),
        'u': (6,1), 'v': (6,2), 'w': (6,3), 'x': (6,4), 'y': (6,5), 'z': (6,-1),
        '!': (6,-2), '.': (6,-3), ',': (6,-4), '?': (6,-5), '\n':(8,1), ' ': (8,2)
    }

def get_alpha_state():
    """Check if alpha embedding is enabled (any non-zero alpha values)"""
    return any(v[1] != 0 for v in alphaDictionary.values())

def findDenaryText(text, dictionary=None):
    dictionary = dictionary or alphaDictionary
    denaryText = []
    for character in text:
        if character in dictionary:
            denaryText.append(dictionary[character][0])
    return denaryText

def splitDoc(filepath):
    with open(filepath, "r", encoding="utf-8", errors="replace") as file:
        doc = [char.lower() for line in file for char in line]
    return doc
    
def optimalDistriution3(denaryText):
    distributedArray = []
    for integer in denaryText:
        if integer % 3 == 0:
            distVal = integer // 3
            distributedArray.append([distVal, distVal, distVal]) 
        elif integer % 3 == 1:
            num1 = math.floor(integer / 3)
            num2 = math.ceil(integer / 3)
            distributedArray.append([num1, num1, num2])
        else:
            num1 = math.floor(integer / 3)
            num2 = math.ceil(integer / 3)
            distributedArray.append([num1, num2, num2])
    return distributedArray

def findAlphaValues(dictionary, splitText):
    alphaVal = []
    for char in splitText:
        if char in dictionary:
            alphaVal.append(dictionary[char][1])
    return alphaVal

def alpha_RGB_Embedding(fileArray, distributedText, splitText, denaryText, dictionary=None):
    dictionary = dictionary or alphaDictionary
    alphaVal = findAlphaValues(dictionary, splitText) # Isolates alpha values
    messagePos = 0
    
    for row in range(fileArray.height):
        for column in range(fileArray.width):
            if messagePos >= len(distributedText): # EOT
                return fileArray, True
            
            channelPos = 0
            pixel = list(fileArray.getpixel((column, row))) # Original pixel for manipulation
            original_pixel = pixel.copy()
            skip_pixel = False # Set skip flag

            if messagePos < len(distributedText) and channelPos < len(distributedText[messagePos]):
                change = denaryText[messagePos]
                new_value_options = find_valid_modification(pixel[0], pixel[1], pixel[2], change)
                
                if not new_value_options:
                    skip_pixel = True
                    break
                
                best_new_value = least_deviation(new_value_options, np.mean(pixel[:-1]))
                pixel[0], pixel[1], pixel[2] = best_new_value

            if not skip_pixel and messagePos < len(alphaVal):
                alpha_change = alphaVal[messagePos]
                new_alpha = pixel[3] + alpha_change
                if 0 <= new_alpha <= 255:
                    pixel[3] = new_alpha
                else:
                    skip_pixel = True
                    break

            if not skip_pixel:
                fileArray.putpixel((column, row), tuple(pixel))
                messagePos += 1

    if messagePos < len(denaryText):
        complete = False
    else:
        complete = True

    return fileArray, complete

def complete_save(filepath, textPath, fileSavePath, custom_dict=None):
    effective_dict = custom_dict if custom_dict is not None else alphaDictionary
    
    splitText = splitDoc(textPath)
    denaryText = findDenaryText(splitText, effective_dict)
    distributedRGBText = optimalDistriution3(denaryText)
    imageFile = Image.open(filepath).convert("RGBA")
    RGBAImage, complete = alpha_RGB_Embedding(
        imageFile, 
        distributedRGBText, 
        splitText, 
        denaryText, 
        effective_dict
    )
    
    RGBAImage.save(fileSavePath)
    return complete
