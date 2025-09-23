import matplotlib.pyplot as plt

# Splitting document into its constituent characters
def splitDoc(filepath):
    with open(filepath, "r") as file: # Opens the file in read mode
        doc = [] # Empty list to store the characters
        for line in file: # Iterates through the lines in the file
            for char in line: # Iterates through the characters in the line
                char = char.lower() # Converts the character to lowercase
                doc.append(char) # Appends the character to 'doc' array
        return doc


# Frequency analysis of the document
def frequencyAnalysis(doc):
    frequency = {} # Empty dictionary to store the frequency of each character
    for char in doc: 
        if char in frequency: # If the character is already in the dictionary...
            frequency[char] += 1 # Increment the frequency of the character
        else: # If the character is not in the dictionary...
            frequency[char] = 1 # Add the character to the dictionary with a frequency of 1
    sortedfrequencydict = dict(sorted(frequency.items(), key=lambda item: item[1], reverse=True)) # Sort the dictionary in descending order
    return sortedfrequencydict

def plotting(text_path):

    splitTxt = splitDoc(text_path)

    freqAn = frequencyAnalysis(splitTxt)

    keys = list(freqAn.keys())
    values = list(freqAn.values())

    plt.figure(figsize=(10, 5))
    plt.bar(keys, values, color='skyblue')
    plt.xlabel('Characters')
    plt.ylabel('Frequency')
    plt.title('Character Frequency')
    plt.show()
