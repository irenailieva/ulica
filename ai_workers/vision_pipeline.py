import os
import urllib.request
import logging
import psycopg2
from psycopg2.extras import execute_values
import torch
import torchvision.transforms as transforms
import torchvision.models as models
from ultralytics import YOLO
from PIL import Image

logger = logging.getLogger(__name__)

# Initialize YOLO model (using YOLOv8 nano for speed)
# In production, use a model fine-tuned for cats/dogs
yolo_model = YOLO("yolov8n.pt")

# Initialize ResNet50 for embedding extraction
# We remove the final classification layer to get the 2048-d vector,
# but the requirement states 512-d. ResNet18 gives 512-d. Let's use ResNet18.
resnet_model = models.resnet18(weights=models.ResNet18_Weights.IMAGENET1K_V1)
# Remove the final fully connected layer to get the 512-d features
resnet_model = torch.nn.Sequential(*(list(resnet_model.children())[:-1]))
resnet_model.eval()

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

def get_db_connection():
    db_url = os.getenv("DATABASE_URL", "postgresql://ulica_user:ulica_password@localhost:5432/ulica_db")
    return psycopg2.connect(db_url)

def extract_embedding(image_path):
    # YOLO detection
    results = yolo_model(image_path)
    
    # Check if anything was detected
    if len(results) == 0 or len(results[0].boxes) == 0:
        raise ValueError("No animals detected in the image.")
    if len(results[0].boxes) > 1:
        logger.warning("Multiple detections found. Using the one with the highest confidence.")
    
    # Get the bounding box of the highest confidence detection
    box = results[0].boxes[0].xyxy[0].cpu().numpy()
    x1, y1, x2, y2 = map(int, box)
    
    # Crop the image
    img = Image.open(image_path).convert('RGB')
    cropped_img = img.crop((x1, y1, x2, y2))
    
    # Extract features using ResNet18 (512-dimensional)
    input_tensor = transform(cropped_img).unsqueeze(0)
    with torch.no_grad():
        features = resnet_model(input_tensor)
        
    embedding = features.squeeze().numpy()
    return embedding

def process_sighting(task):
    sighting_id = task['sighting_id']
    image_url = task['image_url']
    lat = task['latitude']
    lon = task['longitude']
    
    temp_image_path = f"/tmp/{sighting_id}.jpg"
    
    try:
        # Download image from MinIO
        # Replace minio host if running locally
        local_image_url = image_url.replace("minio:9000", "localhost:9000")
        urllib.request.urlretrieve(local_image_url, temp_image_path)
        
        # Extract 512-d embedding
        embedding = extract_embedding(temp_image_path)
        embedding_list = embedding.tolist()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Hybrid Matchmaking SQL Query
        # Match within 2km (2000 meters) using PostGIS ST_DWithin and PostGIS Geography
        # Vector search using pgvector cosine distance (<->)
        match_query = """
        SELECT c.cat_id, c.embedding <-> %s::vector AS distance
        FROM cat_embeddings c
        JOIN sightings s ON c.sighting_id = s.id
        WHERE ST_DWithin(s.location::geography, ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography, 2000)
        ORDER BY distance ASC
        LIMIT 1;
        """
        
        cursor.execute(match_query, (embedding_list, lon, lat))
        result = cursor.fetchone()
        
        distance_threshold = 0.3 # Adjust this based on empirical testing
        
        matched_cat_id = None
        if result and result[1] < distance_threshold:
            matched_cat_id = result[0]
            logger.info(f"Match found! Cat ID: {matched_cat_id}, Distance: {result[1]}")
        else:
            # Insert new cat
            cursor.execute("INSERT INTO cats (status) VALUES ('unverified') RETURNING id;")
            matched_cat_id = cursor.fetchone()[0]
            logger.info(f"No match found. Created new Cat ID: {matched_cat_id}")
            
            # Insert embedding
            cursor.execute(
                "INSERT INTO cat_embeddings (sighting_id, cat_id, embedding) VALUES (%s, %s, %s);",
                (sighting_id, matched_cat_id, embedding_list)
            )
        
        # Update sighting with cat_id
        cursor.execute(
            "UPDATE sightings SET cat_id = %s WHERE id = %s;",
            (matched_cat_id, sighting_id)
        )
        
        conn.commit()
        
    finally:
        if 'conn' in locals():
            cursor.close()
            conn.close()
        if os.path.exists(temp_image_path):
            os.remove(temp_image_path)
