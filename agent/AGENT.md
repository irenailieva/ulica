# Project: Project "Ulica" - Zero-Hardware Animal Biometric Identity System
# Role: Lead Backend & AI Architect

## 1. Project Context
We are building a highly scalable, microservices-based system for stray animal identification using computer vision, vector embeddings, and geospatial data. The system allows users to upload a photo of a stray animal with GPS coordinates, and the backend identifies the animal by comparing facial/body embeddings against a database, filtered by a geospatial radius.

## 2. Tech Stack & Architecture
- **Database:** PostgreSQL (Must use `PostGIS` for geospatial data and `pgvector` for embedding similarity search).
- **Object Storage:** MinIO / AWS S3 (For storing raw images).
- **Message Broker:** Redis (For async task queueing).
- **API Gateway/Backend:** Golang (Handles rapid HTTP ingestion, file uploads to MinIO, basic DB inserts, and publishes to Redis).
- **AI Workers:** Python (Consumes Redis tasks, runs YOLO for cropping, ResNet50/ViT for embeddings, and performs the pgvector search).

## 3. Directory Structure
Generate the project using this strict modular structure:
```text
/
├── docker-compose.yml       # Setup for Postgres (with extensions), MinIO, and Redis
├── /db
│   └── migrations/          # .sql files for DB schema setup
├── /api_gateway             # Golang backend
│   ├── main.go
│   ├── handlers/
│   └── services/
└── /ai_workers              # Python AI worker module
    ├── requirements.txt
    ├── worker.py            # Redis listener
    └── vision_pipeline.py   # YOLO and ResNet logic

```

## 4. Implementation Phases (Execute step-by-step)

### Phase 1: Database & Infrastructure (Docker & SQL)

1. Create a `docker-compose.yml` that provisions:
* PostgreSQL 15+ with `postgis` and `pgvector` extensions enabled.
* Redis container.
* MinIO container (with default bucket `animal-sightings`).


2. Write the SQL initialization scripts in `/db/migrations/`:
* `CREATE EXTENSION IF NOT EXISTS postgis;`
* `CREATE EXTENSION IF NOT EXISTS vector;`
* Table `cats`: `id (UUID)`, `first_seen_date`, `status`, `tnr_status (boolean)`.
* Table `sightings`: `id (UUID)`, `cat_id (UUID, nullable)`, `timestamp`, `location (GEOMETRY(Point, 4326))`, `image_url (text)`.
* Table `cat_embeddings`: `id`, `sighting_id`, `cat_id`, `embedding (VECTOR(512))`.



### Phase 2: The Golang Ingestion Backend

1. Initialize the Go module in `/api_gateway`.
2. Create a high-performance REST endpoint: `POST /api/v1/sightings`.
3. The endpoint must accept `multipart/form-data` containing an image file, `latitude`, and `longitude`.
4. Logic:
* Upload the image to MinIO and retrieve the URL.
* Insert a new record into the `sightings` table with the MinIO URL and PostGIS point.
* Publish a JSON message to a Redis queue (e.g., `queue:process_sighting`) containing the `sighting_id`, `image_url`, `latitude`, and `longitude`.
* Immediately return a `202 Accepted` response to the client. Do NOT wait for AI processing.



### Phase 3: The Python AI Worker (Asynchronous Processing)

1. Initialize the Python environment in `/ai_workers` with required libraries (`redis`, `psycopg2`, `torch`, `torchvision`, `ultralytics`, `numpy`).
2. Implement `worker.py` to continuously listen to the Redis queue `queue:process_sighting`.
3. Implement `vision_pipeline.py` logic upon receiving a message:
* Download the image from MinIO via URL.
* Run a pre-trained YOLO model to detect and crop the animal's face/body.
* Pass the cropped image through a pre-trained ResNet50 model to extract a 512-dimensional vector embedding.


4. Execute the Matchmaking SQL Query:
* Connect to PostgreSQL.
* Execute a hybrid query: Find the closest matching vector using `<->` (Cosine distance) from the `cat_embeddings` table, **BUT explicitly filter** the search using `ST_DWithin` to only include sightings within a 2-kilometer radius of the new sighting's `latitude`/`longitude`.
* If a match is found (distance below threshold), update the original `sightings` record with the matched `cat_id`.
* If no match is found, create a new `cats` record, assign the new `cat_id`, and insert the new embedding into `cat_embeddings`.



## 5. Coding Guidelines for the Agent

* Write clean, idiomatic Go and Python.
* Do not use bloated web frameworks in Go; use standard library `net/http` or a lightweight router like `chi`.
* Ensure proper error handling and logging, especially around DB connections and MinIO uploads.
* Handle edge cases in Python: if YOLO detects 0 or >1 animals in the frame, log the error and drop the task gracefully.