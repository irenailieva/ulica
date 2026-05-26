package main

import (
	"log"
	"net/http"
	"os"

	"ulica/api_gateway/handlers"
	"ulica/api_gateway/services"

	"github.com/go-chi/chi/v5"
	"github.com/go-chi/chi/v5/middleware"
)

func main() {
	// Initialize services
	if err := services.InitDB(); err != nil {
		log.Fatalf("Failed to initialize DB: %v", err)
	}
	defer services.CloseDB()

	if err := services.InitRedis(); err != nil {
		log.Fatalf("Failed to initialize Redis: %v", err)
	}

	if err := services.InitMinIO(); err != nil {
		log.Fatalf("Failed to initialize MinIO: %v", err)
	}

	// Setup Router
	r := chi.NewRouter()
	r.Use(middleware.Logger)
	r.Use(middleware.Recoverer)

	r.Route("/api/v1", func(r chi.Router) {
		r.Post("/sightings", handlers.HandleCreateSighting)
	})

	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}

	log.Printf("Starting API Gateway on port %s", port)
	if err := http.ListenAndServe(":"+port, r); err != nil {
		log.Fatalf("Server failed: %v", err)
	}
}
