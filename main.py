from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Header
import shutil
import os
import uuid
from deepface import DeepFace
import uvicorn
import imagehash
from PIL import Image
import toml
import json
from typing import List, Dict, Union
from src.sql import *
from src.utils import db_transaction

# Load configuration from config.toml
config = toml.load("config.toml")
UPLOAD_DIR = config["paths"]["upload_dir"]

MIN_FACE_CONFIDENCE = 0.9
FACENET_DIMENSION = 128
SIMILARITY_THRESHOLD = 0.85

app = FastAPI()

os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/insert-image")
async def insert_image(tenant_id: str = Form(...), image: UploadFile = File(...), token: str = Header(...)) -> Dict[str, Union[str, Dict[str, str]]]:
    """
    Insert a new image and its associated faces into the database.
    
    Args:
        tenant_id (str): The tenant ID.
        image (UploadFile): The uploaded image file.
        token (str): The authentication token.
    
    Returns:
        dict: The image ID and face IDs.
    """
    with db_transaction(token) as cur:
        # Save the uploaded image
        image_id = str(uuid.uuid4())
        image_path = os.path.join(UPLOAD_DIR, f"{image_id}.jpg")
        with open(image_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

        # Generate perceptual hash for the image
        img = Image.open(image_path)
        phash = str(imagehash.phash(img))

        # Generate embedding for the image
        image_embedding = DeepFace.represent(img, model_name="Facenet", enforce_detection=False)[0]["embedding"]

        # Extract faces from the image
        face_objs = DeepFace.extract_faces(img_path=image_path, detector_backend="mtcnn")

        # Insert image record
        sql_insert_image(cur, tenant_id, image_id, phash, image_embedding)

        # Insert face records
        face_ids: Dict[str, str] = {}
        for face_obj in face_objs:
            if face_obj["confidence"] >= MIN_FACE_CONFIDENCE:
                face_id = str(uuid.uuid4())
                new_face_embedding = DeepFace.represent(face_obj["face"], model_name="Facenet", enforce_detection=False)[0]["embedding"]
                facial_area = face_obj["facial_area"]
                facial_area_json = json.dumps({
                  "x":facial_area["x"],
                  "y":facial_area["y"],
                  "w":facial_area["w"],
                  "h":facial_area["h"],
                })

                # Check for matching faces within the same tenant
                existing_faces = sql_check_matching_faces(cur, tenant_id, new_face_embedding, SIMILARITY_THRESHOLD)
                matched_cluster_id = str(uuid.uuid4())
                if len(existing_faces) > 0:
                    # If the face is matched with an existing face
                    matched_face_id, matched_cluster_id, distance = existing_faces[0]
                    print(f"Matched face {face_id} with {matched_face_id} with distance {distance}")
                    is_auto_matched = True
                    sql_insert_face(cur, tenant_id, face_id, image_id, matched_cluster_id, facial_area_json, is_auto_matched, new_face_embedding)
                else:
                    # If the face is not matched with any existing face
                    is_auto_matched = True
                    sql_insert_face(cur, tenant_id, face_id, image_id, matched_cluster_id, facial_area_json, is_auto_matched, new_face_embedding)
                    
                    # Add record to review_pending table
                    sql_insert_review_pending(cur, tenant_id, matched_cluster_id)
                face_ids.update({face_id: matched_cluster_id})
        return {
          "image_id": image_id, 
          "face_ids": face_ids
        }

@app.delete("/image")
async def delete_image(tenant_id: str = Form(...), image_id: str = Form(...), token: str = Header(...)) -> Dict[str, str]:
    """
    Delete an image and its associated faces from the database.
    
    Args:
        tenant_id (str): The tenant ID.
        image_id (str): The image ID.
        token (str): The authentication token.
    
    Returns:
        dict: The status of the operation.
    """
    with db_transaction(token) as cur:
        # Delete faces associated with the image
        sql_delete_faces_by_image(cur, tenant_id, image_id)
        # Delete the image record
        sql_delete_image(cur, tenant_id, image_id)
        return {"status": "success"}

@app.delete("/face")
async def delete_face(tenant_id: str = Form(...), face_id: str = Form(...), token: str = Header(...)) -> Dict[str, str]:
    """
    Delete a face record from the database.
    
    Args:
        tenant_id (str): The tenant ID.
        face_id (str): The face ID.
        token (str): The authentication token.
    
    Returns:
        dict: The status of the operation.
    """
    with db_transaction(token) as cur:
        sql_delete_face(cur, tenant_id, face_id)
        return {"status": "success"}

@app.delete("/cluster")
async def delete_cluster(tenant_id: str = Form(...), cluster_id: str = Form(...), token: str = Header(...)) -> Dict[str, str]:
    """
    Delete a cluster and their associated faces and images from the database.
    
    Args:
        tenant_id (str): The tenant ID.
        cluster_id (str): The cluster ID.
        token (str): The authentication token.
    
    Returns:
        dict: The status of the operation.
    """
    with db_transaction(token) as cur:
        sql_delete_faces_by_cluster(cur, tenant_id, cluster_id)
        sql_delete_images_by_cluster(cur, tenant_id, cluster_id)
        return {"status": "success"}

@app.delete("/tenant")
async def delete_tenant(tenant_id: str = Form(...), token: str = Header(...)) -> Dict[str, str]:
    """
    Delete a tenant and their associated faces and images from the database.
    
    Args:
        tenant_id (str): The tenant ID.
        token (str): The authentication token.
    
    Returns:
        dict: The status of the operation.
    """
    with db_transaction(token) as cur:
        # Delete faces associated with the tenant
        sql_delete_faces_by_tenant(cur, tenant_id)
        # Delete images associated with the tenant
        sql_delete_images_by_tenant(cur, tenant_id)
        return {"status": "success"}

@app.get("/review-pending")
async def review_pending(tenant_id: str = Form(...), review_id: str = Form(...), token: str = Header(...)) -> Dict[str, int | str]:
    """
    Retrieve a review pending record from the database.
    
    Args:
        tenant_id (str): The tenant ID.
        review_id (str): The review ID.
        token (str): The authentication token.
    
    Returns:
        dict: The review pending record.
    """
    with db_transaction(token) as cur:
        review = sql_review_pending(cur, tenant_id, review_id)
        if review is None:
            raise HTTPException(status_code=404, detail="Review not found")
        return {"id": review[0], "cluster_id": review[1], "image_id": review[2]}

@app.get("/review-pending-list")
async def get_review_list(tenant_id: str, skip: int = 0, limit: int = 10, token: str = Header(...)) -> List[Dict[str, int | str]]:
    """
    Retrieve a list of review pending records from the database.
    
    Args:
        tenant_id (str): The tenant ID.
        skip (int): The number of records to skip.
        limit (int): The maximum number of records to return.
        token (str): The authentication token.
    
    Returns:
        list: A list of review pending records.
    """
    with db_transaction(token) as cur:
        review_list = sql_get_review_list(cur, tenant_id, limit, skip)
        return [{"id": review[0], "cluster_id": review[1], "image_id": review[2]} for review in review_list]

@app.delete("/review-pending")
async def delete_review_pending(tenant_id: str = Form(...), review_id: str = Form(...), token: str = Header(...)) -> Dict[str, str]:
    """
    Delete a review pending record from the database.
    
    Args:
        tenant_id (str): The tenant ID.
        review_id (str): The review ID.
        token (str): The authentication token.
    
    Returns:
        dict: The status of the operation.
    """
    with db_transaction(token) as cur:
        sql_delete_review_pending(cur, tenant_id, review_id)
        return {"status": "success"}

@app.post("/update-face-cluster")
async def update_face_cluster(tenant_id: str = Form(...), face_id: str = Form(...), to_cluster_id: str = Form(...), token: str = Header(...)) -> Dict[str, str]:
    """
    Update the cluster ID of a face record in the database.
    
    Args:
        tenant_id (str): The tenant ID.
        face_id (str): The face ID.
        to_cluster_id (str): The new cluster ID.
        token (str): The authentication token.
    
    Returns:
        dict: The status of the operation.
    """
    with db_transaction(token) as cur:
        sql_update_face_owner(cur, tenant_id, face_id, to_cluster_id)
        return {"status": "success"}

@app.get("/face")
async def get_face(tenant_id: str, face_id: str, token: str = Header(...)) -> Dict[str, str | bool]:
    """
    Retrieve a face record from the database.
    
    Args:
        tenant_id (str): The tenant ID.
        face_id (str): The face ID.
        token (str): The authentication token.
    
    Returns:
        dict: The face record.
    """
    with db_transaction(token) as cur:
        face = sql_get_face(cur, tenant_id, face_id)
        return {
          "cluster_id": face[0], 
          "image_id": face[1], 
          "facial_area": face[2], 
          "is_auto_matched": face[3]
        }

@app.get("/cluster")
async def get_cluster(tenant_id: str, cluster_id: str, token: str = Header(...)) -> Dict[str, int]:
    """
    Retrieve a cluster record from the database.
    
    Args:
        tenant_id (str): The tenant ID.
        cluster_id (str): The cluster ID.
        token (str): The authentication token.
    
    Returns:
        dict: The cluster record.
    """
    with db_transaction(token) as cur:
        number_of_faces, number_of_images = sql_get_cluster(cur, tenant_id, cluster_id)
        return {"number_of_faces":number_of_faces, "number_of_images": number_of_images}

@app.get("/image")
async def get_image(tenant_id: str, image_id: str, token: str = Header(...)) -> Dict[str, List[str] | str]:
    """
    Retrieve an image record from the database.
    
    Args:
        tenant_id (str): The tenant ID.
        image_id (str): The image ID.
        token (str): The authentication token.
    
    Returns:
        dict: The image record.
    """
    with db_transaction(token) as cur:
        face_ids, cluster_ids, phash = sql_get_image(cur, tenant_id, image_id)
        return {"face_ids": face_ids, "cluster_ids": cluster_ids, "phash": phash}

@app.get("/faces")
async def get_faces(tenant_id: str, image_id: str, skip: int = 0, limit: int = 10, token: str = Header(...)) -> List[Dict[str, str | bool]]:
    """
    Retrieve a list of face records from the database.
    
    Args:
        tenant_id (str): The tenant ID.
        image_id (str): The image ID.
        skip (int): The number of records to skip.
        limit (int): The maximum number of records to return.
        token (str): The authentication token.
    
    Returns:
        list: A list of face records.
    """
    with db_transaction(token) as cur:
        faces = sql_get_faces(cur, tenant_id, image_id, limit, skip)
        return [{
          "id": face[0], 
          "cluster_id": face[1], 
          "image_id": face[2], 
          "facial_area": face[3], 
          "is_auto_matched": face[4]
        } for face in faces]

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
