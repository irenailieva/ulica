package services

import (
	"context"
	"fmt"
	"io"
	"os"

	"github.com/google/uuid"
	"github.com/minio/minio-go/v7"
	"github.com/minio/minio-go/v7/pkg/credentials"
)

var minioClient *minio.Client
const bucketName = "animal-sightings"

func InitMinIO() error {
	endpoint := os.Getenv("MINIO_ENDPOINT")
	if endpoint == "" {
		endpoint = "localhost:9000"
	}
	accessKeyID := os.Getenv("MINIO_ROOT_USER")
	if accessKeyID == "" {
		accessKeyID = "minioadmin"
	}
	secretAccessKey := os.Getenv("MINIO_ROOT_PASSWORD")
	if secretAccessKey == "" {
		secretAccessKey = "minioadmin"
	}
	useSSL := false

	var err error
	minioClient, err = minio.New(endpoint, &minio.Options{
		Creds:  credentials.NewStaticV4(accessKeyID, secretAccessKey, ""),
		Secure: useSSL,
	})
	if err != nil {
		return err
	}

	return nil
}

func UploadImage(file io.Reader, filename string, size int64, contentType string) (string, error) {
	ctx := context.Background()
	
	if contentType == "" {
		contentType = "application/octet-stream"
	}

	// Generate unique filename
	objectName := uuid.New().String() + "-" + filename

	_, err := minioClient.PutObject(ctx, bucketName, objectName, file, size, minio.PutObjectOptions{
		ContentType: contentType,
	})
	if err != nil {
		return "", fmt.Errorf("failed to put object in minio: %w", err)
	}

	// Return a constructed URL (assumes public access as set by docker-compose)
	endpoint := os.Getenv("MINIO_ENDPOINT")
	if endpoint == "" {
		endpoint = "localhost:9000"
	}
	url := fmt.Sprintf("http://%s/%s/%s", endpoint, bucketName, objectName)
	return url, nil
}
