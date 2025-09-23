from PIL import Image

dictionary = {
    'a': (2,1), 'b': (2,2), 'c': (2,3), 'd': (2,4), 'e': (2,5),
    'f': (2,-1), 'g': (2,-2), 'h': (2,-3), 'i': (2,-4), 'j': (2,-5),
    'k': (4,1), 'l': (4,2), 'm': (4,3), 'n': (4,4), 'o': (4,5),
    'p': (4,-1), 'q': (4,-2), 'r': (4,-3), 's': (4,-4), 't': (4,-5),
    'u': (6,1), 'v': (6,2), 'w': (6,3), 'x': (6,4), 'y': (6,5), 'z': (6,-1),
    '!': (6,-2), '.': (6,-3), ',': (6,-4), '?': (6,-5), '\n': (8,1), ' ': (8,2)
}

def get_dictionary():
    return dictionary

def set_dictionary(new_dict):
    global dictionary
    dictionary = new_dict

def decode(org_path, alt_path, alpha_dict = dictionary):

    org_img = Image.open(org_path).convert("RGBA")
    alt_img = Image.open(alt_path).convert("RGBA")

    org_pixels = list(org_img.getdata())
    alt_pixels = list(alt_img.getdata())

    diffs = [(sum(abs(alt[channel] - org[channel]) for channel in range(3)), alt[3] - org[3]) 
             for org, alt in zip(org_pixels, alt_pixels)]

    reverse_dict = {val: key for key, val in alpha_dict.items()}
    decoded_text = "".join(reverse_dict.get(diff, '?') for diff in diffs if diff != (0,0))

    return decoded_text

