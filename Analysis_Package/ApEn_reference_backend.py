import cv2
import numpy as np
import itertools
import math

def load_image(image_path):
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE) # Converts to greyscale
    if img is None:
        raise ValueError("Image not found or invalid format.")
    return img

def divide_into_blocks(image, block_size): # Divides image into blocks
    h, w = image.shape
    blocks = []
    
    for i in range(0, h, block_size):
        for j in range(0, w, block_size):
            block = image[i:i+block_size, j:j+block_size]
            if block.shape == (block_size, block_size): 
                blocks.append(block.flatten())  # Flattens the block into a 1D array
                
    return np.array(blocks)

def compute_embedding(blocks, scale_factor=1.0):  # Computes each block's embedded vector
    return blocks * scale_factor  # Simple linear scaling (SF of 1)

def compute_distances(embedded_vectors): # Computes euclidean distance between embedded vectors
    num_vectors = len(embedded_vectors)
    distances = []
    
    for (vec1, vec2) in itertools.combinations(embedded_vectors, 2):
        dist = np.linalg.norm(vec1 - vec2)  # Euclidean distance
        distances.append(dist)
    
    return np.array(distances)

def count_similar_pairs(distances, threshold): #Counts pairs with a distance below the similarity threshold
    return np.sum(distances < threshold)

def compute_average_similarity(distances): #Computes the average similarity across all pairs
    return np.mean(distances)

def compute_entropy(similar_pairs, total_pairs): # Uses Shannon entropy formula
    if total_pairs == 0:
        return 0  # Avoids division by zero
    
    p = similar_pairs / total_pairs
    if p == 0 or p == 1:
        return 0  # Avoids log(0)
    
    return -p * math.log2(p) - (1 - p) * math.log2(1 - p)

def analyze_image(image_path, block_size=8, scale_factor=1.0, similarity_threshold=10.0):
    img = load_image(image_path)
    blocks = divide_into_blocks(img, block_size)
    embedded_vectors = compute_embedding(blocks, scale_factor)
    
    distances = compute_distances(embedded_vectors)
    similar_pairs = count_similar_pairs(distances, similarity_threshold)
    total_pairs = len(distances)
    avg_similarity = compute_average_similarity(distances)
    entropy = compute_entropy(similar_pairs, total_pairs)

    return {
        "Total Blocks": len(blocks),
        "Total Pairs": total_pairs,
        "Similar Pairs": similar_pairs,
        "Average Similarity": round(avg_similarity, 4),
        "Approximate Entropy": round(entropy, 4)
    }
