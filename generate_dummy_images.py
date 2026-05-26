import os
from PIL import Image

def create_image(color, filename):
    img = Image.new('RGB', (224, 224), color=color)
    img.save(filename)

if __name__ == '__main__':
    # Create some "database" images
    os.makedirs('cat_images', exist_ok=True)
    create_image('red', 'cat_images/cat_red.jpg')
    create_image('blue', 'cat_images/cat_blue.jpg')
    create_image('green', 'cat_images/cat_green.jpg')
    
    # Create a query image (similar to the red one)
    create_image((255, 50, 50), 'query_image.jpg')
    print("Dummy images created.")
