import os
import torch
import torchvision.models as models
import torchvision.transforms as transforms
from PIL import Image
import numpy as np
import faiss

class AnimalIdentifier:
    def __init__(self, db_folder='cat_images'):
        self.db_folder = db_folder
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Load pre-trained ResNet50 model
        # We remove the final fully connected layer to get feature embeddings
        self.model = models.resnet50(weights=models.ResNet50_Weights.DEFAULT)
        # Replace the classifier with an identity mapping
        self.model.fc = torch.nn.Identity()
        self.model.eval()
        self.model.to(self.device)
        
        # Standard preprocessing for ResNet models
        self.preprocess = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])
        
        # Initialize FAISS index
        # ResNet50 output dimension is 2048
        self.dimension = 2048
        # Using L2 distance for similarity search
        self.index = faiss.IndexFlatL2(self.dimension)
        self.image_paths = []
        
        # Build the database if folder exists
        self.build_database()
        
    def extract_embedding(self, image_path):
        """Extracts a 2048-dimensional embedding vector for a given image."""
        try:
            image = Image.open(image_path).convert('RGB')
        except Exception as e:
            print(f"Error opening image {image_path}: {e}")
            return None
            
        input_tensor = self.preprocess(image)
        input_batch = input_tensor.unsqueeze(0).to(self.device)
        
        with torch.no_grad():
            output = self.model(input_batch)
            
        # Convert to numpy and normalize (optional, but good practice for L2 search)
        embedding = output.cpu().numpy()[0]
        faiss.normalize_L2(np.expand_dims(embedding, axis=0))
        return embedding

    def build_database(self):
        """Processes all images in the database folder and adds them to the FAISS index."""
        if not os.path.exists(self.db_folder):
            os.makedirs(self.db_folder)
            print(f"Created folder '{self.db_folder}'. Add images to this folder.")
            return

        supported_formats = ('.png', '.jpg', '.jpeg')
        files = [f for f in os.listdir(self.db_folder) if f.lower().endswith(supported_formats)]
        
        if not files:
            print(f"No images found in '{self.db_folder}'.")
            return
            
        print(f"Building database from {len(files)} images...")
        embeddings = []
        
        for file in files:
            path = os.path.join(self.db_folder, file)
            emb = self.extract_embedding(path)
            if emb is not None:
                embeddings.append(emb)
                self.image_paths.append(path)
                
        if embeddings:
            embeddings_np = np.array(embeddings).astype('float32')
            # The embeddings were normalized, so they are ready for the index
            self.index.add(embeddings_np)
            print(f"Database built successfully. Added {self.index.ntotal} images to the index.")

    def find_closest_match(self, query_image_path):
        """Finds the closest matching cat in the database to the provided query image."""
        if self.index.ntotal == 0:
            print("The database is empty. Add images to the database folder first.")
            return None, None
            
        print(f"Querying image: {query_image_path}")
        query_embedding = self.extract_embedding(query_image_path)
        
        if query_embedding is None:
            return None, None
            
        query_np = np.array([query_embedding]).astype('float32')
        faiss.normalize_L2(query_np)
        
        # Search the index (k=1 returns the single closest match)
        k = 1
        distances, indices = self.index.search(query_np, k)
        
        closest_index = indices[0][0]
        distance_score = distances[0][0]
        
        closest_image_path = self.image_paths[closest_index]
        return closest_image_path, distance_score

if __name__ == '__main__':
    # Usage Example
    identifier = AnimalIdentifier(db_folder='cat_images')
    
    # Check if a query image is passed, otherwise prompt the user
    print("\nTo test, you can drop an image in 'query_image.jpg' in this folder.")
    query_img = 'query_image.jpg'
    
    if os.path.exists(query_img):
        match_path, distance = identifier.find_closest_match(query_img)
        if match_path:
            print("\n--- Result ---")
            print(f"Closest match found: {match_path}")
            print(f"Distance score (L2): {distance:.4f} (Lower is more similar)")
    else:
        print(f"\nPlace a query image named '{query_img}' to see the matching result.")
