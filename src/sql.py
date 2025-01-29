from typing import List, Tuple
from fastapi import HTTPException
import psycopg2

def sql_insert_image(cur: psycopg2.extensions.cursor, tenant_id: str, image_id: str, phash: str, embedding: List[float]) -> None:
    """
    Insert a new image record into the images table.
    
    Args:
        cur (psycopg2.extensions.cursor): Database cursor object.
        tenant_id (str): The tenant ID.
        image_id (str): The image ID.
        phash (str): The perceptual hash of the image.
        embedding (List[float]): The embedding vector of the image.
    """
    cur.execute("INSERT INTO images (tenant_id, id, phash, embedding) VALUES (%s, %s, %s, %s)", (tenant_id, image_id, phash, embedding))

def sql_insert_face(cur: psycopg2.extensions.cursor, tenant_id: str, face_id: str, image_id: str, cluster_id: str, facial_area_json: str, is_auto_matched: bool, embedding: List[float]) -> None:
    """
    Insert a new face record into the faces table.
    
    Args:
        cur (psycopg2.extensions.cursor): Database cursor object.
        tenant_id (str): The tenant ID.
        face_id (str): The face ID.
        image_id (str): The image ID.
        cluster_id (str): The cluster ID.
        facial_area_json (str): The facial area in JSON format.
        is_auto_matched (bool): Indicates if the face was auto matched by the face recognition algorithm.
        embedding (List[float]): The embedding vector of the face.
    """
    cur.execute("INSERT INTO faces (tenant_id, id, image_id, cluster_id, facial_area, is_auto_matched, embedding) VALUES (%s, %s, %s, %s, %s, %s, %s)", 
                (tenant_id, face_id, image_id, cluster_id, facial_area_json, is_auto_matched, embedding))

def sql_insert_review_pending(cur: psycopg2.extensions.cursor, tenant_id: str, cluster_id: str) -> None:
    """
    Insert a new review pending record into the review_pending table.
    
    Args:
        cur (psycopg2.extensions.cursor): Database cursor object.
        tenant_id (str): The tenant ID.
        cluster_id (str): The cluster ID.
    """
    cur.execute("INSERT INTO review_pending (tenant_id, cluster_id) VALUES (%s, %s)", (tenant_id, cluster_id))

def sql_delete_faces_by_image(cur: psycopg2.extensions.cursor, tenant_id: str, image_id: str) -> None:
    """
    Delete face records associated with a specific image.
    
    Args:
        cur (psycopg2.extensions.cursor): Database cursor object.
        tenant_id (str): The tenant ID.
        image_id (str): The image ID.
    """
    cur.execute("DELETE FROM faces WHERE tenant_id = %s AND image_id = %s", (tenant_id, image_id))

def sql_delete_image(cur: psycopg2.extensions.cursor, tenant_id: str, image_id: str) -> None:
    """
    Delete an image record from the images table.
    
    Args:
        cur (psycopg2.extensions.cursor): Database cursor object.
        tenant_id (str): The tenant ID.
        image_id (str): The image ID.
    """
    cur.execute("DELETE FROM images WHERE tenant_id = %s AND id = %s", (tenant_id, image_id))

def sql_delete_face(cur: psycopg2.extensions.cursor, tenant_id: str, face_id: str) -> None:
    """
    Delete a face record from the faces table.
    
    Args:
        cur (psycopg2.extensions.cursor): Database cursor object.
        tenant_id (str): The tenant ID.
        face_id (str): The face ID.
    """
    cur.execute("DELETE FROM faces WHERE tenant_id = %s AND id = %s", (tenant_id, face_id))

def sql_delete_faces_by_cluster(cur: psycopg2.extensions.cursor, tenant_id: str, cluster_id: str) -> None:
    """
    Delete face records associated with a specific cluster.
    
    Args:
        cur (psycopg2.extensions.cursor): Database cursor object.
        tenant_id (str): The tenant ID.
        cluster_id (str): The cluster ID.
    """
    cur.execute("DELETE FROM faces WHERE tenant_id = %s AND cluster_id = %s", (tenant_id, cluster_id))

def sql_delete_images_by_cluster(cur: psycopg2.extensions.cursor, tenant_id: str, cluster_id: str) -> None:
    """
    Delete image records associated with a specific cluster.
    
    Args:
        cur (psycopg2.extensions.cursor): Database cursor object.
        tenant_id (str): The tenant ID.
        cluster_id (str): The cluster ID.
    """
    cur.execute("DELETE FROM images WHERE tenant_id = %s AND cluster_id = %s", (tenant_id, cluster_id))

def sql_delete_faces_by_tenant(cur: psycopg2.extensions.cursor, tenant_id: str) -> None:
    """
    Delete face records associated with a specific tenant.
    
    Args:
        cur (psycopg2.extensions.cursor): Database cursor object.
        tenant_id (str): The tenant ID.
    """
    cur.execute("DELETE FROM faces WHERE tenant_id = %s", (tenant_id,))

def sql_delete_images_by_tenant(cur: psycopg2.extensions.cursor, tenant_id: str) -> None:
    """
    Delete image records associated with a specific tenant.
    
    Args:
        cur (psycopg2.extensions.cursor): Database cursor object.
        tenant_id (str): The tenant ID.
    """
    cur.execute("DELETE FROM images WHERE tenant_id = %s", (tenant_id,))

def sql_review_pending(cur: psycopg2.extensions.cursor, tenant_id: str, review_id: str) -> Tuple[int, str, str]:
    """
    Retrieve a review pending record from the review_pending table.
    
    Args:
        cur (psycopg2.extensions.cursor): Database cursor object.
        tenant_id (str): The tenant ID.
        review_id (str): The review ID.
    
    Returns:
        tuple: The review pending record.
    """
    cur.execute("SELECT id, cluster_id, image_id FROM review_pending WHERE tenant_id = %s AND id = %s", (tenant_id, review_id))
    result = cur.fetchone()
    if result is None:
        raise HTTPException(status_code=404, detail="Review not found")
    return result

def sql_get_review_list(cur: psycopg2.extensions.cursor, tenant_id: str, limit: int, skip: int) -> List[Tuple[int, str, str]]:
    """
    Retrieve a list of review pending records from the review_pending table.
    
    Args:
        cur (psycopg2.extensions.cursor): Database cursor object.
        tenant_id (str): The tenant ID.
        limit (int): The maximum number of records to retrieve.
        skip (int): The number of records to skip.
    
    Returns:
        list: A list of review pending records.
    """
    cur.execute("SELECT id, cluster_id, image_id FROM review_pending WHERE tenant_id = %s LIMIT %s OFFSET %s", (tenant_id, limit, skip))
    return cur.fetchall()

def sql_delete_review_pending(cur: psycopg2.extensions.cursor, tenant_id: str, review_id: str) -> None:
    """
    Delete a review pending record from the review_pending table.
    
    Args:
        cur (psycopg2.extensions.cursor): Database cursor object.
        tenant_id (str): The tenant ID.
        review_id (str): The review ID.
    """
    cur.execute("DELETE FROM review_pending WHERE tenant_id = %s AND id = %s", (tenant_id, review_id))

def sql_update_face_owner(cur: psycopg2.extensions.cursor, tenant_id: str, face_id: str, to_cluster_id: str) -> None:
    """
    Update the owner of a face record in the faces table.
    
    Args:
        cur (psycopg2.extensions.cursor): Database cursor object.
        tenant_id (str): The tenant ID.
        face_id (str): The face ID.
        to_cluster_id (str): The new cluster ID.
    """
    cur.execute("UPDATE faces SET cluster_id = %s WHERE tenant_id = %s AND id = %s", (to_cluster_id, tenant_id, face_id))

def sql_get_face(cur: psycopg2.extensions.cursor, tenant_id: str, face_id: str) -> Tuple[str, str, str, bool]:
    """
    Retrieve a face record from the faces table.
    
    Args:
        cur (psycopg2.extensions.cursor): Database cursor object.
        tenant_id (str): The tenant ID.
        face_id (str): The face ID.
    
    Returns:
        tuple: The face record.
    """
    cur.execute("SELECT cluster_id, image_id, facial_area, is_auto_matched FROM faces WHERE tenant_id = %s AND id = %s", (tenant_id, face_id))
    result = cur.fetchone()
    if result is None:
        raise HTTPException(status_code=404, detail="Face not found")
    return result

def sql_get_cluster(cur: psycopg2.extensions.cursor, tenant_id: str, cluster_id: str) -> Tuple[int, int]:
    """
    Retrieve cluster statistics from the faces table.
    
    Args:
        cur (psycop2.extensions.cursor): Database cursor object.
        tenant_id (str): The tenant ID.
        cluster_id (str): The cluster ID.
    
    Returns:
        tuple: The cluster statistics.
    """
    cur.execute("SELECT COUNT(id), COUNT(DISTINCT image_id) FROM faces WHERE tenant_id = %s AND cluster_id = %s", (tenant_id, cluster_id))
    result = cur.fetchone()
    if result is None:
        raise HTTPException(status_code=404, detail="Cluster not found")
    return result

def sql_get_image(cur: psycopg2.extensions.cursor, tenant_id: str, image_id: str) -> Tuple[List[str], List[str], str]:
    """
    Retrieve an image record and associated faces and clusters from the database.
    
    Args:
        cur (psycopg2.extensions.cursor): Database cursor object.
        tenant_id (str): The tenant ID.
        image_id (str): The image ID.
    
    Returns:
        tuple: The faces, clusters, and perceptual hash of the image.
    """
    cur.execute("""
        SELECT 
            ARRAY(SELECT id FROM faces WHERE tenant_id = %s AND image_id = %s) AS face_ids,
            ARRAY(SELECT DISTINCT cluster_id FROM faces WHERE tenant_id = %s AND image_id = %s) AS cluster_ids,
            phash
        FROM images
        WHERE tenant_id = %s AND id = %s
    """, (tenant_id, image_id, tenant_id, image_id, tenant_id, image_id))
    result = cur.fetchone()
    if result is None:
        raise HTTPException(status_code=404, detail="Image not found")
    return result

def sql_get_faces(cur: psycopg2.extensions.cursor, tenant_id: str, image_id: str, limit: int, skip: int) -> List[Tuple[str, str, str, str, bool]]:
    """
    Retrieve a list of face records associated with a specific image.
    
    Args:
        cur (psycopg2.extensions.cursor): Database cursor object.
        tenant_id (str): The tenant ID.
        image_id (str): The image ID.
        limit (int): The maximum number of records to retrieve.
        skip (int): The number of records to skip.
    
    Returns:
        list: A list of face records.
    """
    cur.execute("SELECT id, cluster_id, image_id, facial_area, is_auto_matched FROM faces WHERE tenant_id = %s AND image_id = %s LIMIT %s OFFSET %s", (tenant_id, image_id, limit, skip))
    return cur.fetchall()

def sql_check_matching_faces(cur: psycopg2.extensions.cursor, tenant_id: str, new_face_embedding: List[float], similarity_threshold: float) -> List[Tuple[str, str, float]]:
    """
    Check for matching faces within the same tenant.
    
    Args:
        cur (psycopg2.extensions.cursor): Database cursor object.
        tenant_id (str): The tenant ID.
        new_face_embedding (List[float]): The embedding vector of the new face.
        similarity_threshold (float): The similarity threshold for matching faces.
    
    Returns:
        list: A list of matching faces with their IDs, cluster IDs, and distances.
    """
    cur.execute("""
        WITH RankedFaces AS (
            SELECT id, cluster_id, embedding <=> %s::vector AS distance
            FROM faces
            WHERE tenant_id = %s
        )
        SELECT id, cluster_id, distance
        FROM RankedFaces
        WHERE distance <= %s
        ORDER BY distance
        LIMIT 1
    """, (new_face_embedding, tenant_id, similarity_threshold))
    return cur.fetchall()
