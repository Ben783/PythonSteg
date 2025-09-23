import cv2

def binary_to_text(binary_str):
    length = len(binary_str)
    
    if length % 8 != 0:
        binary_str = binary_str[:length - (length % 8)]
    
    chunks = [binary_str[i:i + 8] for i in range(0, len(binary_str), 8)]
    
    text = ''.join([chr(int(chunk, 2)) for chunk in chunks])
    
    eot_index = text.find("\x04") # Finds the last occurrence of EOT and truncates the text
    if eot_index != -1:
        text = text[:eot_index]
    
    return text



def extractOriginalData(hammingCode):
    totalBits = len(hammingCode)
    r = 0
    
    while (2 ** r) < totalBits + 1:
        r += 1
    
    dataBits = []
    
    for i in range(1, totalBits + 1):
        if (i & (i - 1)) != 0:  # Skips parity bit positions
            dataBits.append(str(hammingCode[i - 1]))  # Converts each item to a string
    
    return ''.join(dataBits)


# Function to find modified blocks
def find_embedded_blocks(original_image, steg_image, block_size):
    height = len(original_image)
    width = len(original_image[0])
    blocks_dictionary = {}
    visited = create_2d_array(height, width, False)

    for y in range(0, height, block_size):  # Iterate over rows (top to bottom)
        for x in range(0, width, block_size):  # Iterate over columns (left to right)
            block_coordinates = []
            block_changed = False

            for dy in range(block_size):
                for dx in range(block_size):
                    if (y + dy < height) and (x + dx < width):
                        original_pixel = original_image[y + dy][x + dx]
                        steg_pixel = steg_image[y + dy][x + dx]

                        if original_pixel != steg_pixel:
                            block_changed = True

                        block_coordinates.append((y + dy, x + dx))  # (y, x) for block coordinates

            if block_changed:
                blocks_dictionary[(y, x)] = block_coordinates

    sorted_blocks = dict(sorted(blocks_dictionary.items(), key=lambda item: item[0]))

    return sorted_blocks


def create_2d_array(height, width, default_value):
    return [[default_value for _ in range(width)] for _ in range(height)]


def getLSB(num):
    return num & 1  # Returns the LSB of the number


def extractModifiedValues_inOrder(modifiedBlockCoordDict, altImg):
    lsbs = []
    for block in modifiedBlockCoordDict.values():
        for coord in block:
            altPixelVal = altImg[coord[0], coord[1]]
            lsbs.append(str(getLSB(altPixelVal)))  # Ensure the LSB is added as a string
    return ''.join(lsbs)  # Return a binary string


def decryption(image_path, alt_img_path, block_size, ECC):

    org_image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

    alt_image = cv2.imread(alt_img_path, cv2.IMREAD_GRAYSCALE)

    # Finds the modified blocks
    dictionaryOfModifiedBlockCoords = find_embedded_blocks(org_image, alt_image, block_size)

    # Extract LSBs from the modified blocks
    lsbs = extractModifiedValues_inOrder(dictionaryOfModifiedBlockCoords, alt_image)

    # Decode the original data from the extracted LSBs (Hamming code)
    if ECC == True:
        original_data = extractOriginalData(lsbs)
    else:
        original_data = lsbs

    print(f"Extracted original data: {original_data}")

    return binary_to_text(original_data)

#print(decryption(r"C:\Users\HOME\PYTHON CS\Project\Complete\Images\BenPNG.png", r"C:\Users\HOME\PYTHON CS\Project\Complete\Images\diddyBen16.png", 16))