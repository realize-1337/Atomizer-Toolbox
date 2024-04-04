import cv2
import numpy as np
import matplotlib.pyplot as plt

# Load images
droplets_img = cv2.imread(r'H:\Duese_4\Wasser\2_60_68,4\Unten\frame_0026.png')
background_img = cv2.imread(r'H:\Duese_4\Wasser\Unten_ref.tif')

# Preprocess images (if needed, e.g., convert to grayscale)
# For example, if the droplets are in grayscale and background in color
droplets_gray = cv2.cvtColor(droplets_img, cv2.COLOR_BGR2GRAY)
background_gray = cv2.cvtColor(background_img, cv2.COLOR_BGR2GRAY)

# Find the difference between the two images
diff_img = cv2.absdiff(droplets_gray, background_gray)


_, thresholded_img = cv2.threshold(diff_img, 60, 255, cv2.THRESH_BINARY)
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
        circularity_threshold = 0.85
        
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

cv2.circle(circle_img, (int(x), int(y)), 5*int(radius), (255, 255, 255), 5)

# Overlay the circle image on the original droplets_gray image
result_img = cv2.cvtColor(droplets_gray, cv2.COLOR_GRAY2BGR)
result_img = cv2.addWeighted(result_img, 1, cv2.cvtColor(circle_img, cv2.COLOR_GRAY2BGR), 0.5, 0)


# Display the result
fig, axs = plt.subplots(1, 2, figsize=(2*result_img.shape[1]/100.0, result_img.shape[0]/100.0), dpi=50)

axs[0].imshow(cv2.cvtColor(result_img, cv2.COLOR_BGR2RGB))
axs[0].set_title(f'Highlighted Circle')
axs[1].imshow(thresholded_img, cmap='gray')
axs[1].set_title('Thresholded Image')



plt.tight_layout()
axs[0].set_xticks([])
axs[0].set_yticks([])
axs[1].set_xticks([])
axs[1].set_yticks([])
plt.show()
# plt.savefig



# # Display the result
# cv2.imshow('Largest Circle Highlighted', result_img)
# cv2.waitKey(0)
# cv2.destroyAllWindows()