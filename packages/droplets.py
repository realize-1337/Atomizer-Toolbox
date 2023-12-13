import cv2
import numpy as np
import matplotlib.pyplot as plt

# Load images
droplets_img = cv2.imread(r'M:\Duese_3\Wasser\4,1_11,7_17,2\Unten\frame_0888.png')
background_img = cv2.imread(r'M:\Duese_3\Wasser\Unten_ref.tif')

# Preprocess images (if needed, e.g., convert to grayscale)
# For example, if the droplets are in grayscale and background in color
droplets_gray = cv2.cvtColor(droplets_img, cv2.COLOR_BGR2GRAY)
background_gray = cv2.cvtColor(background_img, cv2.COLOR_BGR2GRAY)

# Find the difference between the two images
diff_img = cv2.absdiff(droplets_gray, background_gray)

_, thresholded_img = cv2.threshold(diff_img, 40, 255, cv2.THRESH_BINARY)
contours, _ = cv2.findContours(thresholded_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# Find the largest droplet
largest_area = 0
largest_contour = None

round_contours = []
for contour in contours:
    perimeter = cv2.arcLength(contour, True)
    area = cv2.contourArea(contour)
    if perimeter > 0:
        circularity = (4 * 3.1416 * area) / (perimeter * perimeter)
        
        # Define circularity threshold (adjust as needed)
        circularity_threshold = 0.6
        
        if circularity > circularity_threshold:
            round_contours.append(contour)

# Draw the detected round contours on a blank image
# contour_img = np.zeros_like(droplets_img)
# cv2.drawContours(contour_img, round_contours, -1, (0, 255, 0), 2)

for contour in round_contours:
    area = cv2.contourArea(contour)
    if area > largest_area:
        largest_area = area
        largest_contour = contour

(x, y), radius = cv2.minEnclosingCircle(largest_contour)

# Calculate diameter from the radius
diameter = 2 * radius

print(f"The diameter of the largest contour is: {diameter}")

circle_img = np.zeros_like(droplets_gray)

cv2.circle(circle_img, (int(x), int(y)), int(radius), (255, 255, 255), 2)

# Overlay the circle image on the original droplets_gray image
result_img = cv2.cvtColor(droplets_gray, cv2.COLOR_GRAY2BGR)
result_img = cv2.addWeighted(result_img, 1, cv2.cvtColor(circle_img, cv2.COLOR_GRAY2BGR), 0.5, 0)


# Display the result
fig, axs = plt.subplots(1, 3, figsize=(12, 6))

axs[0].text(0.5, 0.5, f'Largest Droplet\n{"%.2f" % diameter} px', ha='center', va='center', fontsize=12)
axs[0].axis('off')
axs[1].imshow(cv2.cvtColor(result_img, cv2.COLOR_BGR2RGB))
axs[1].set_title(f'Highlighted Circle')
axs[2].imshow(thresholded_img, cmap='gray')
axs[2].set_title('Thresholded Image')



plt.tight_layout()
plt.show()
plt.savefig



# # Display the result
# cv2.imshow('Largest Circle Highlighted', result_img)
# cv2.waitKey(0)
# cv2.destroyAllWindows()