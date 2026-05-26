package handlers

import (
	"encoding/json"
	"log"
	"net/http"
	"strconv"
	"ulica/api_gateway/services"
)

type SightingResponse struct {
	Message    string `json:"message"`
	SightingID string `json:"sighting_id"`
}

func HandleCreateSighting(w http.ResponseWriter, r *http.Request) {
	err := r.ParseMultipartForm(10 << 20) // 10 MB limit
	if err != nil {
		http.Error(w, "Failed to parse multipart form", http.StatusBadRequest)
		return
	}

	// 1. Get lat/lon
	latStr := r.FormValue("latitude")
	lonStr := r.FormValue("longitude")
	
	lat, err := strconv.ParseFloat(latStr, 64)
	if err != nil {
		http.Error(w, "Invalid latitude", http.StatusBadRequest)
		return
	}
	lon, err := strconv.ParseFloat(lonStr, 64)
	if err != nil {
		http.Error(w, "Invalid longitude", http.StatusBadRequest)
		return
	}

	// 2. Get Image
	file, header, err := r.FormFile("image")
	if err != nil {
		http.Error(w, "Image file is required", http.StatusBadRequest)
		return
	}
	defer file.Close()

	// 3. Upload to MinIO
	imageURL, err := services.UploadImage(file, header.Filename, header.Size, header.Header.Get("Content-Type"))
	if err != nil {
		log.Printf("MinIO Upload Error: %v", err)
		http.Error(w, "Failed to upload image", http.StatusInternalServerError)
		return
	}

	// 4. Insert into PostgreSQL
	sightingID, err := services.InsertSighting(lat, lon, imageURL)
	if err != nil {
		log.Printf("DB Insert Error: %v", err)
		http.Error(w, "Failed to save sighting", http.StatusInternalServerError)
		return
	}

	// 5. Publish to Redis Queue
	err = services.PublishSightingTask(sightingID, imageURL, lat, lon)
	if err != nil {
		log.Printf("Redis Publish Error: %v", err)
		// We still return 202 Accepted because the image and sighting were saved
	}

	// 6. Return 202 Accepted immediately
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusAccepted)
	json.NewEncoder(w).Encode(SightingResponse{
		Message:    "Sighting received and queued for processing",
		SightingID: sightingID,
	})
}
