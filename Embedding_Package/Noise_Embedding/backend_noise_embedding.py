import cv2
import numpy as np
import copy
import math
from PIL import Image
import os

def numberOfRedundancyBits(n):
    for i in range(n):
        if (2**i >= n + i + 1):
            return i

def generateHammingCode(dataBits):
    n = len(dataBits)
    r = numberOfRedundancyBits(n)
    totalBits = n + r

    hammingCode = ['0'] * totalBits
    j = 0

    for i in range(1, totalBits + 1):
        if (i & (i - 1)) == 0:
            hammingCode[i - 1] = '0'
        else:
            hammingCode[i - 1] = dataBits[j]
            j += 1

    for i in range(r):
        position = 2 ** i
        value = 0
        for j in range(1, totalBits + 1):
            if (j & position) != 0:
                value = value ^ int(hammingCode[j - 1])
        hammingCode[position - 1] = str(value)

    return ''.join(hammingCode)

def find_width(image):
    return len(image[0])

def find_height(image):
    return len(image)

def create_block_coord_dictionary(blockSize, image):
    block_dictionary = {}
    blockIndex = 0

    numCols = find_width(image)
    numRows = find_height(image)

    for row in range(0, numRows, blockSize):  # Removed -1
        for col in range(0, numCols, blockSize):
            coordinates = []
            for i in range(0, blockSize):
                rowIndex = row + i
                if rowIndex >= numRows:
                    break

                for j in range(0, blockSize):
                    colIndex = col + j
                    if colIndex >= numCols:
                        break
                    coordinates.append([rowIndex, colIndex])
            block_dictionary[blockIndex] = coordinates
            blockIndex += 1
            
    return block_dictionary

def create_blockValues_dictionary(image, blockSize):
    blockValuesDict = {}
    blockIndex = 0
    numRows = find_height(image)
    numCols = find_width(image)

    for row in range(0, numRows, blockSize):
        for col in range(0, numCols, blockSize):
            block = []
            for i in range(blockSize):
                rowIndex = row + i
                if rowIndex >= numRows:
                    break
                
                blockRow = []
                for j in range(blockSize):
                    colIndex = col + j
                    if colIndex >= numCols:
                        break
                    blockRow.append(image[rowIndex][colIndex])
                block.append(blockRow)
            blockValuesDict[blockIndex] = block
            blockIndex += 1
    return blockValuesDict


def block_variance_dictionary(blockValues_dictionary):
    variance_dictionary = {}
    
    def measureVariance(block_values):
        total_pixels = len(block_values) * len(block_values[0])
        sum_intensities = 0.0
        sum_of_squares = 0.0
    
        for row in block_values:
            for pixel in row:
                sum_intensities += pixel
                sum_of_squares += pixel ** 2
                
        mean_intensity = sum_intensities / total_pixels
        variance = (sum_of_squares / total_pixels) - (mean_intensity ** 2)
    
        return variance
            
    for key in blockValues_dictionary:
        block_values = blockValues_dictionary[key]
        variance = measureVariance(block_values)
        variance_dictionary[key] = variance
        
    return variance_dictionary

def block_entropy_dictionary(block_values_dictionary):
    entropy_dictionary = {}

    def measureEntropy(block_values):
        pixel_counts = {}
        total_pixels = 0
    
        for pixel in block_values:
            if pixel in pixel_counts:
                pixel_counts[pixel] += 1
            else:
                pixel_counts[pixel] = 1
            total_pixels += 1
    
        entropy = 0
        for count in pixel_counts.values():
            probability = count / total_pixels
            entropy -= probability * math.log2(probability)
    
        return entropy

    for key in block_values_dictionary:
        block_values = block_values_dictionary[key]
        array_1d = [element for row in block_values for element in row]
        entropy = measureEntropy(array_1d)
        entropy_dictionary[key] = entropy

    return entropy_dictionary

def measure_entropy(values):
    value_counts = {}
    total_values = len(values)
    
    for value in values:
        if value in value_counts:
            value_counts[value] += 1
        else:
            value_counts[value] = 1
    
    entropy = 0
    for count in value_counts.values():
        probability = count / total_values
        entropy -= probability * math.log2(probability)
    
    return entropy

def sort_indexes_variance(block_variance_dict):
    return sorted(block_variance_dict, key=block_variance_dict.get, reverse=True)

def sort_indexes_entropy(block_entropy_dict):
    return sorted(block_entropy_dict, key=block_entropy_dict.get, reverse=True)

def suitable_blocks(sorted_variance_indexes, entropyDict, varianceDict):
    thresholdEntropy = meanEntropy(entropyDict)*1.5
    thresholdVariance = meanVariance(varianceDict)*1.5
    suitableBlocks_index = []
    for index in sorted_variance_indexes:
        if varianceDict[index] >= thresholdVariance:
            if entropyDict[index] >= thresholdEntropy:
                suitableBlocks_index.append(index)
    return suitableBlocks_index

def meanEntropy(entropyDict):
    return sum(entropyDict.values()) / len(entropyDict)

def meanVariance(varianceDict):
    return sum(varianceDict.values()) / len(varianceDict)

def create_averageEntropy_variance_dictionary(blockEntropyDict, blockVarianceDict):
    averageDict = {}
    for key in blockEntropyDict:
        averageDict[key] = (blockEntropyDict[key] + blockVarianceDict[key]) / 2
    return averageDict

def suitableBlocksOrdered_Index(binaryMessage, avgDictEntropyVariance, blockSize):
    messagelen = len(binaryMessage)
    blocksRequired = math.ceil(messagelen/blockSize**2)
    sortedBlocks = sorted(avgDictEntropyVariance, key=avgDictEntropyVariance.get, reverse=True)
    selectedBlocks = sortedBlocks[:blocksRequired]
    sortedSelectedBlocks = sorted(selectedBlocks, reverse=False)
    return sortedSelectedBlocks

def splitDoc(textPath):
    with open(textPath, "r", encoding="utf-8") as file:  # Ensures UTF-8 encoding
        doc = []
        for line in file:
            for char in line:
                # Convert character to lowercase and check if it's within the ASCII range
                char = char.lower()
                if ord(char) < 128:  # Only accepts characters with Unicode code points < 128 (1-byte characters)
                    doc.append(char)  # Appends only these characters
        return doc

def embedding(image_matrix, blocksToEmbed, hammingText):
    bit_index = 0
    binaryLength = len(hammingText)
    print(len(hammingText))
    new_image = copy.deepcopy(image_matrix)
    
    changes = 0
    matches = 0
    
    for block in blocksToEmbed:
        for coord in block:
            if bit_index < binaryLength:
                pixelValue = new_image[coord[0]][coord[1]]
                currentBit = hammingText[bit_index]
                newPixelValue = (pixelValue & 0xFE) | int(currentBit)
                if pixelValue != newPixelValue:
                    changes += 1
                else:
                    matches += 1
                new_image[coord[0]][coord[1]] = newPixelValue
                bit_index += 1
                
                #print(f"Embedding at {coord}: Original Pixel Value: {pixelValue}, Current Bit: {currentBit}, New Pixel Value: {newPixelValue}, Changes: {changes}, Matches: {matches}")

    return new_image

def highlight_embedded_blocks(image_matrix, blocksToEmbed, blockSize):
    highlighted_image = cv2.cvtColor(np.array(image_matrix), cv2.COLOR_GRAY2RGB)
    for block in blocksToEmbed:
        top_left = (block[0][1], block[0][0])
        bottom_right = (block[0][1] + blockSize - 1, block[0][0] + blockSize - 1)
        cv2.rectangle(highlighted_image, top_left, bottom_right, (0, 255, 0), 2)
    return highlighted_image


def count_differences(matrix1, matrix2):
    if len(matrix1) != len(matrix2) or len(matrix1[0]) != len(matrix2[0]):
        raise ValueError("Matrices must have the same dimensions")
    
    differences = 0
    
    for i in range(len(matrix1)):
        for j in range(len(matrix1[0])):
            if matrix1[i][j] != matrix2[i][j]:
                differences += 1
    
    return differences


def complete_save(textPath, filePath, fileSavePath, blockSize, correctingCode):
    charDoc = splitDoc(textPath)
    binaryPlainText = ''.join([format(ord(char), '08b') for char in charDoc])
    binaryPlainText += format(4, '08b')  # Append EOT as an 8-bit binary string
    binaryLength = len(binaryPlainText)
    if correctingCode == "Hamming Code":
        hammingText = generateHammingCode(binaryPlainText)
        binaryLength = len(hammingText)
        print("Hamming")
    else:
        hammingText = binaryPlainText
        print("Normal")

    # Verify the image file exists
    image_path = os.path.abspath(filePath)
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image file not found: {image_path}")

    # Read the image
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    height, width = image.shape[:2]
    
    if image is None:
        raise ValueError(f"Unable to read image. Check file format and integrity: {image_path}")

    blockCoordDict = create_block_coord_dictionary(blockSize, image)
    blockValuesDict = create_blockValues_dictionary(image, blockSize)
    block_entropy_dict = block_entropy_dictionary(blockValuesDict)
    block_variance_dict = block_variance_dictionary(blockValuesDict)
    avgDictEntropyVariance = create_averageEntropy_variance_dictionary(block_entropy_dict, block_variance_dict)
    suitableBlocksIndex = suitableBlocksOrdered_Index(hammingText, avgDictEntropyVariance, blockSize)
    suitableBlocksCoord = [blockCoordDict[index] for index in suitableBlocksIndex]

    new_image_matrix = embedding(image, suitableBlocksCoord, hammingText)
    new_image = np.array(new_image_matrix, dtype=np.uint8)
    new_image = Image.fromarray(new_image)
    
    new_image.save(fileSavePath)
    highlighted_image = highlight_embedded_blocks(new_image_matrix, suitableBlocksCoord, blockSize)
    highlighted_image_pil = Image.fromarray(highlighted_image)
    highlighted_image_pil.show()

    imageEligibility = check_image_eligibility(binaryLength, height, width)
    
    return imageEligibility

def check_image_eligibility(textLength, imageHeight, imageWidth):
    imageArea = imageHeight * imageWidth
    if imageArea >= textLength:
        return True
    else:
        return False