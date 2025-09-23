from PIL import Image
import numpy as np

def logistic_map(x, r): # Logistic map function to generate the next value
    return r * x * (1 - x)

# Generating pseudorandom coordinates...
def generate_pseudorandom_coordinates(num_points, r, x0, y0, width, height, let_run):
    x, y = x0, y0
    coordinates = []
    seen = set()

    for _ in range(let_run): # Letting the logistic map stabilize
        x = logistic_map(x, r)
        y = logistic_map(y, r)

    # Generates UNIQUE coordinates
    while len(coordinates) < num_points:
        x = logistic_map(x, r)
        y = logistic_map(y, r)
        scaled_x = int(x * width)
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


# Reverse the embedding alphabet for decryption
#reverse_embedding_alphabet = {tuple(val): key for key, val in embedding_alphabet.items()}


def decrypt(r, x0, y0, let_run, org_image_path, emb_image_path, max_chars=1500, alphabet=embedding_alphabet):
    org_image = Image.open(org_image_path).convert("RGBA")
    emb_image = Image.open(emb_image_path).convert("RGBA")
    widthO, heightO = org_image.width, org_image.height
    reverse_embedding_alphabet = {tuple(val): key for key, val in alphabet.items()}
    # Generate chaotic coordinates (same as encryption)
    chaotic_coords = generate_pseudorandom_coordinates(num_points=max_chars, r=r, x0=x0, y0=y0, width=widthO, height=heightO, let_run=let_run)

    decrypted_message = []

    for coordinate in chaotic_coords:
        org_pixel = org_image.getpixel(coordinate)
        emb_pixel = emb_image.getpixel(coordinate)

        #Check if the pixels are different
        if org_pixel != emb_pixel:
            # Calculating RGB and alpha differences
            rgb_diff = sum(abs(emb_pixel[i] - org_pixel[i]) for i in range(3))  # Difference in RGB channels
            alpha_diff = emb_pixel[3] - org_pixel[3]  # Difference in alpha


            # Show the differences between the current coordinate and original pixel (debugging)
            print(f"Coordinate: {coordinate}, Original Pixel: {org_pixel}, Embedded Pixel: {emb_pixel}")
            print(f"RGB Difference: {rgb_diff}, Alpha Difference: {alpha_diff}")

            #Check if the differences correspond to character in the reverse alphabet
            if (rgb_diff, alpha_diff) in reverse_embedding_alphabet:
                decrypted_message.append(reverse_embedding_alphabet[(rgb_diff, alpha_diff)])
                print(reverse_embedding_alphabet[(rgb_diff, alpha_diff)])

        #Stops when maximum number of characters reached
        if len(decrypted_message) >= max_chars:
            break

    return( "".join(decrypted_message))

# r = 3.99        # Logistic map parameter
# x0 = 0.897       # Initial value for x-coordinate
# y0 = 0.87      # Initial value for y-coordinate
# let_run = 1000    # Number of iterations to let the logistic map stabilize

# org = r"C:\Users\HOME\PYTHON CS\Project\Complete\Images\TREE.png"
# mod = r"C:\Users\HOME\PYTHON CS\Project\Complete\Images\expImage.png"
# print(decrypt(r, x0, y0, let_run, org, mod))
