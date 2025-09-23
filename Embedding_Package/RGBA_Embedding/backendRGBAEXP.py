
import math
from PIL import Image
import numpy as np


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


alphaDictionary = {
    'a': (2,1), 'b': (2,2), 'c': (2,3), 'd': (2,4), 'e': (2,5),
    'f': (2,-1), 'g': (2,-2), 'h': (2,-3), 'i': (2,-4), 'j': (2,-5),
    'k': (4,1), 'l': (4,2), 'm': (4,3), 'n': (4,4), 'o': (4,5),
    'p': (4,-1), 'q': (4,-2), 'r': (4,-3), 's': (4,-4), 't': (4,-5),
    'u': (6,1), 'v': (6,2), 'w': (6,3), 'x': (6,4), 'y': (6,5), 'z': (6,-1),
    '!': (6,-2), '.': (6,-3), ',': (6,-4), '?': (6,-5), '\n':(8,1), ' ': (8,2)
}

def findDenaryText(text, alphaDictionary):
    denaryText = []
    for character in text:
        if character in alphaDictionary:
            denaryText.append(alphaDictionary[character][0])
    return denaryText

def splitDoc(filepath):
    with open(filepath, "r", encoding="latin-1", errors = "replace") as file:
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

def findAlphaValues(alphaDictionary, splitText):
    alphaVal = []
    for char in splitText:
        if char in alphaDictionary:
            alphaVal.append(alphaDictionary[char][1])
    return alphaVal

def alpha_RGB_Embedding(fileArray, distributedText, splitText, denaryText):
    alphaVal = findAlphaValues(alphaDictionary, splitText)
    print(f"alphaVal: {alphaVal}")
    messagePos = 0  # Tracks the current position in the message
    for row in range(fileArray.height):
        for column in range(fileArray.width):
            if messagePos >= len(distributedText):  # Check if the entire message has been embedded
                #print("Entire message has been embedded.")
                return fileArray  # Exit the function once the message is fully embedded
            
            channelPos = 0
            pixel = list(fileArray.getpixel((column, row)))  # Get the pixel at the current position
            original_pixel = pixel.copy()  # Make a copy of the original pixel to compare later
            skip_pixel = False  # Flag to skip the current pixel (False: do not skip, True: skip)


            if messagePos < len(distributedText) and channelPos < len(distributedText[messagePos]):
                change = denaryText[messagePos]  # Get the change value
                #print(f"change: {change}")
                new_value_options = find_valid_modification(pixel[0], pixel[1], pixel[2], change)  # Find valid modifications
                #print(pixel[0], pixel[1], pixel[2])
                
                if not new_value_options:  # If there are no valid modifications...
                    skip_pixel = True  # Skip the current pixel
                    break
                
                best_new_value = least_deviation(new_value_options, np.mean(pixel[:-1]))  # Find the best modification

                #print(f"Best new value:{best_new_value}")

            pixel[0], pixel[1], pixel[2] = best_new_value  # Update the pixel values
                
                

            if not skip_pixel:  # If the pixel is not skipped, carry out the alpha modification also 
                if messagePos < len(alphaVal):  # If there are alpha values left...
                    alpha_change = alphaVal[messagePos]  # Get the alpha value
                    new_alpha = pixel[3] + alpha_change  # Update the alpha value
                    if new_alpha >= 0 and new_alpha <= 255:  # If the new alpha value is within the valid range...
                        pixel[3] = new_alpha  # Update the alpha value
                    else:
                        skip_pixel = True  # Skip if alpha goes out of bounds
                        break

            if not skip_pixel:  # If the pixel has not been skipped, update the pixel in the image
                # Compare the original and modified pixels
                if pixel != original_pixel:  # If the pixel was modified
                    #print(f"Original Pixel (Row: {row}, Column: {column}): {original_pixel}")
                    #print(f"Modified Pixel (Row: {row}, Column: {column}): {pixel}")
                    pass
                
                # Update the pixel in the image with the modified pixel values
            fileArray.putpixel((column, row), tuple(pixel))
            messagePos += 1

    return fileArray




def complete_save(filepath, textPath, fileSavePath):
    splitText = splitDoc(textPath)
    denaryText = findDenaryText(splitText, alphaDictionary)
    distributedRGBText = optimalDistriution3(denaryText)
    imageFile = Image.open(filepath).convert("RGBA")
    RGBAImage = alpha_RGB_Embedding(imageFile, distributedRGBText, splitText, denaryText)
    
    RGBAImage.save(fileSavePath)
    return f"Image saved at {fileSavePath}"




#def integrated_function():
    complete_save(filepath, textPath)

#integrated_function()
