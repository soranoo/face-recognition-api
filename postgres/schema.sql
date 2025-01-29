-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create image table
CREATE TABLE IF NOT EXISTS images (
  id VARCHAR(255) PRIMARY KEY NOT NULL,
  tenant_id VARCHAR(255) NOT NULL,
  phash VARCHAR(255) NOT NULL,
  embedding VECTOR(128) NOT NULL
);

-- Create face table
CREATE TABLE IF NOT EXISTS faces (
  id VARCHAR(255) PRIMARY KEY,
  tenant_id VARCHAR(255) NOT NULL,
  image_id VARCHAR(255) NOT NULL,
  cluster_id VARCHAR(255) NOT NULL,
  facial_area JSONB NOT NULL, -- X,Y,W,H that represents the facial area
  is_auto_matched BOOLEAN DEFAULT FALSE, -- Indicates if the face was auto matched by the face recognition algorithm
  embedding VECTOR(128) NOT NULL,
  FOREIGN KEY (image_id) REFERENCES images(id) ON DELETE CASCADE
);

-- Create review pending table
CREATE TABLE IF NOT EXISTS review_pending (
  id SERIAL PRIMARY KEY,
  tenant_id VARCHAR(255) NOT NULL,
  cluster_id VARCHAR(255) NOT NULL,
  FOREIGN KEY (cluster_id) REFERENCES faces(cluster_id) ON DELETE CASCADE
);
