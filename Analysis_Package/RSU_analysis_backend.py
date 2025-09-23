import numpy as np
from PIL import Image
import matplotlib.pyplot as plt

def discrimination_function(group): # Calculates the sum of absolute differences between adjacent pixels in a group. Others can be used
    return np.sum(np.abs(np.diff(group)))

def F1(group): # Simulates LSBR
    return group ^ 1

def F_minus_1(group): # Simulates LSBM
    return np.where(np.random.randint(0, 2, size=group.shape), group ^ 1, group)

def classify_groups(image, n=4): # Organise into R, S, U groups
    rows, cols = image.shape
    R, S, U = 0, 0, 0

    for i in range(rows):
        for j in range(0, cols, n):
            group = image[i, j:j+n]
            if len(group) < n:
                continue  # Skips incomplete groups

            # Original noise
            f_original = discrimination_function(group)

            # Noise after F1
            group_F1 = F1(group)
            f_F1 = discrimination_function(group_F1)

            # Noise after F-1
            group_F_minus_1 = F_minus_1(group)
            f_F_minus_1 = discrimination_function(group_F_minus_1)

            # Classify groups
            if f_F1 > f_original:
                R += 1
            elif f_F1 < f_original:
                S += 1
            else:
                U += 1

            if f_F_minus_1 > f_original:
                R += 1
            elif f_F_minus_1 < f_original:
                S += 1
            else:
                U += 1

    return R, S, U

def visualise_rs_analysis(original_image, altered_image, n=4): # Plots and visualises results

    R_original, S_original, U_original = classify_groups(original_image, n)
    R_altered, S_altered, U_altered = classify_groups(altered_image, n)

    # Apply F1 and F-1 to the altered image and classify groups
    altered_F1 = F1(altered_image)
    R_F1, S_F1, U_F1 = classify_groups(altered_F1, n)

    altered_F_minus_1 = F_minus_1(altered_image)
    R_F_minus_1, S_F_minus_1, U_F_minus_1 = classify_groups(altered_F_minus_1, n)

    # Print the results (Debugging)
    print(f"Original Image: R={R_original}, S={S_original}, U={U_original}")
    print(f"Altered Image: R={R_altered}, S={S_altered}, U={U_altered}")
    print(f"After F1: R={R_F1}, S={S_F1}, U={U_F1}")
    print(f"After F-1: R={R_F_minus_1}, S={S_F_minus_1}, U={U_F_minus_1}")

    labels = ['Original', 'Altered', 'After F1', 'After F-1'] # Plotting...
    R_values = [R_original, R_altered, R_F1, R_F_minus_1]
    S_values = [S_original, S_altered, S_F1, S_F_minus_1]

    x = np.arange(len(labels)) 
    width = 0.35 

    fig, ax = plt.subplots()
    rects1 = ax.bar(x - width/2, R_values, width, label='Regular Groups (R)', color='blue')
    rects2 = ax.bar(x + width/2, S_values, width, label='Singular Groups (S)', color='orange')


    ax.set_xlabel('Image State')
    ax.set_ylabel('Number of Groups')
    ax.set_title('RS Analysis: Original vs Altered Image')
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend()

    def autolabel(rects):
        for rect in rects:
            height = rect.get_height()
            ax.annotate(f'{height}',
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3),  # 3 points vertical offset
                        textcoords="offset points",
                        ha='center', va='bottom')

    autolabel(rects1)
    autolabel(rects2)

    plt.tight_layout()
    plt.show()

def main(original_image_path, altered_image_path): # Clean-up function

    original_image = np.array(Image.open(original_image_path).convert("L"))  # Convert to grayscale
    altered_image = np.array(Image.open(altered_image_path).convert("L")) 

    visualise_rs_analysis(original_image, altered_image)

#main(r"C:\Users\HOME\PYTHON CS\Project\Complete\Images\BenPNG.png",r"C:\Users\HOME\PYTHON CS\Project\Complete\Images\NoiseBen1Chap.png")
