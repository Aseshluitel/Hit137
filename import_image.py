from PIL import Image

# Load the image
img = Image.open('C:/Users/hp/OneDrive/Desktop/cdu/HIT-137/Asssessment-2/chapter1.png')
pixels = img.load()

# Apply the generated number to each pixel's RGB values
n = 149  # use the number generated from the previous code

for i in range(img.width):
    for j in range(img.height):
        r, g, b = pixels[i, j]
        pixels[i, j] = (r + n, g + n, b + n)

# Save the modified image
img.save('C:/Users/hp/OneDrive/Desktop/cdu/HIT-137/Asssessment-2/chapter1out.png')

# Sum all the red pixel values in the modified image
red_sum = sum(pixels[i, j][0] for i in range(img.width) for j in range(img.height))
print(f'Sum of all red pixel values: {red_sum}')
