package services

import (
	"context"
	"encoding/json"
	"os"

	"github.com/redis/go-redis/v9"
)

var redisClient *redis.Client

type SightingTask struct {
	SightingID string  `json:"sighting_id"`
	ImageURL   string  `json:"image_url"`
	Latitude   float64 `json:"latitude"`
	Longitude  float64 `json:"longitude"`
}

func InitRedis() error {
	addr := os.Getenv("REDIS_ADDR")
	if addr == "" {
		addr = "localhost:6379"
	}
	
	redisClient = redis.NewClient(&redis.Options{
		Addr: addr,
	})

	return redisClient.Ping(context.Background()).Err()
}

func PublishSightingTask(sightingID, imageURL string, lat, lon float64) error {
	task := SightingTask{
		SightingID: sightingID,
		ImageURL:   imageURL,
		Latitude:   lat,
		Longitude:  lon,
	}

	taskJSON, err := json.Marshal(task)
	if err != nil {
		return err
	}

	return redisClient.RPush(context.Background(), "queue:process_sighting", taskJSON).Err()
}
