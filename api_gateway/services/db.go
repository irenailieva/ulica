package services

import (
	"database/sql"
	"fmt"
	"os"

	_ "github.com/lib/pq"
)

var DB *sql.DB

func InitDB() error {
	connStr := os.Getenv("DATABASE_URL")
	if connStr == "" {
		connStr = "postgres://ulica_user:ulica_password@localhost:5432/ulica_db?sslmode=disable"
	}
	
	var err error
	DB, err = sql.Open("postgres", connStr)
	if err != nil {
		return err
	}

	return DB.Ping()
}

func CloseDB() {
	if DB != nil {
		DB.Close()
	}
}

func InsertSighting(lat, lon float64, imageURL string) (string, error) {
	var id string
	query := `
		INSERT INTO sightings (location, image_url)
		VALUES (ST_SetSRID(ST_MakePoint($1, $2), 4326), $3)
		RETURNING id
	`
	err := DB.QueryRow(query, lon, lat, imageURL).Scan(&id)
	if err != nil {
		return "", fmt.Errorf("failed to insert sighting: %w", err)
	}
	return id, nil
}
