# [PoC] Face Recognition API

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
![GitHub repo size](https://img.shields.io/github/repo-size/soranoo/face-recognition-api)
![GitHub top language](https://img.shields.io/github/languages/top/soranoo/face-recognition-api)
&nbsp;[![Donation](https://img.shields.io/static/v1?label=Donation&message=❤️&style=social)](https://github.com/soranoo/Donation)

This API provides endpoints for managing similar faces in a database. The API is built using FastAPI and PostgreSQL with PGVector for storing face embeddings.

> [!WARNING]\
> This API is not intended for production use. It is a proof-of-concept implementation and should be used for educational purposes only.

Give me a ⭐ if you like it.

## 📑 Table of Contents

- [Example Config File](#example-config-file)
- [Endpoints](#endpoints)
  - [Insert Image](#insert-image)
  - [Delete Image](#delete-image)
  - [Delete Face](#delete-face)
  - [Delete Cluster](#delete-cluster)
  - [Delete Tenant](#delete-tenant)
  - [Review Pending](#review-pending)
  - [Review Pending List](#review-pending-list)
  - [Delete Review Pending](#delete-review-pending)
  - [Update Face Cluster](#update-face-cluster)
  - [Get Face](#get-face)
  - [Get Cluster](#get-cluster)
  - [Get Image](#get-image)
  - [Get Faces](#get-faces)

## ⚓ Requirements
* Python 3.8.1 or latest (*Developed in Python 3.12.5)
* PostgreSQL 13.5 or latest / Run the [Docker Compose](./docker-compose.yml) file to start a PostgreSQL instance.

## 📝 Example Config File

Create a `config.toml` file in the root directory with the following content:

```toml
[database]
dbname = "facerec_db"
user = "admin"
password = "admin"
host = "localhost"
port = "5432"

[paths]
upload_dir = "uploads"

[auth]
token = "<your-own-bearer-token>"
```

> [!NOTE]\
> The `auth.token` value is used to authenticate requests to the API. You can generate a random token using the following JavaScript code: `require('crypto').randomBytes(64).toString('hex')`.

## 📬 Endpoints

### Insert Image

**POST /insert-image**

The `insert-image` endpoint is used to upload an image file and detect faces in it. The system will try to match the detected faces with the existing faces in the database within the same tenant. If a match is found, the detected face will be assigned the same `cluster_id` as the matched face. If no match is found, the detected face will be assigned a new `cluster_id` and marked as pending review.

> [!NOTE]\
> `mtcnn` and `Facenet` are used for face detection and generation of face embeddings, respectively.

| Parameter | Type       | Description                     |
|-----------|------------|---------------------------------|
| tenant_id | str        | The tenant ID.                  |
| image     | UploadFile | The uploaded image file.        |
| token     | str        | The authentication token.       |

**Returns:**
- `dict`: The image ID and face IDs.

### Delete Image

**DELETE /image**

| Parameter | Type | Description               |
|-----------|------|---------------------------|
| tenant_id | str  | The tenant ID.            |
| image_id  | str  | The image ID.             |
| token     | str  | The authentication token. |

**Returns:**
- `dict`: The status of the operation.

### Delete Face

**DELETE /face**

| Parameter | Type | Description               |
|-----------|------|---------------------------|
| tenant_id | str  | The tenant ID.            |
| face_id   | str  | The face ID.              |
| token     | str  | The authentication token. |

**Returns:**
- `dict`: The status of the operation.

### Delete Cluster

**DELETE /cluster**

| Parameter | Type | Description               |
|-----------|------|---------------------------|
| tenant_id | str  | The tenant ID.            |
| cluster_id| str  | The cluster ID.           |
| token     | str  | The authentication token. |

**Returns:**
- `dict`: The status of the operation.

### Delete Tenant

**DELETE /tenant**

| Parameter | Type | Description               |
|-----------|------|---------------------------|
| tenant_id | str  | The tenant ID.            |
| token     | str  | The authentication token. |

**Returns:**
- `dict`: The status of the operation.

### Review Pending

**GET /review-pending**

| Parameter | Type | Description               |
|-----------|------|---------------------------|
| tenant_id | str  | The tenant ID.            |
| review_id | str  | The review ID.            |
| token     | str  | The authentication token. |

**Returns:**
- `dict`: The review pending record.

### Review Pending List

**GET /review-pending-list**

| Parameter | Type | Description               |
|-----------|------|---------------------------|
| tenant_id | str  | The tenant ID.            |
| skip      | int  | The number of records to skip. |
| limit     | int  | The maximum number of records to return. |
| token     | str  | The authentication token. |

**Returns:**
- `list`: A list of review pending records.

### Delete Review Pending

**DELETE /review-pending**

| Parameter | Type | Description               |
|-----------|------|---------------------------|
| tenant_id | str  | The tenant ID.            |
| review_id | str  | The review ID.            |
| token     | str  | The authentication token. |

**Returns:**
- `dict`: The status of the operation.

### Update Face Cluster

**POST /update-face-cluster**

| Parameter | Type | Description               |
|-----------|------|---------------------------|
| tenant_id | str  | The tenant ID.            |
| face_id   | str  | The face ID.              |
| to_cluster_id| str | The new cluster ID.     |
| token     | str  | The authentication token. |

**Returns:**
- `dict`: The status of the operation.

### Get Face

**GET /face**

| Parameter | Type | Description               |
|-----------|------|---------------------------|
| tenant_id | str  | The tenant ID.            |
| face_id   | str  | The face ID.              |
| token     | str  | The authentication token. |

**Returns:**
- `dict`: The face record.

### Get Cluster

**GET /cluster**

| Parameter | Type | Description               |
|-----------|------|---------------------------|
| tenant_id | str  | The tenant ID.            |
| cluster_id| str  | The cluster ID.           |
| token     | str  | The authentication token. |

**Returns:**
- `dict`: The cluster record.

### Get Image

**GET /image**

| Parameter | Type | Description               |
|-----------|------|---------------------------|
| tenant_id | str  | The tenant ID.            |
| image_id  | str  | The image ID.             |
| token     | str  | The authentication token. |

**Returns:**
- `dict`: The image record.

### Get Faces

**GET /faces**

| Parameter | Type | Description               |
|-----------|------|---------------------------|
| tenant_id | str  | The tenant ID.            |
| image_id  | str  | The image ID.             |
| skip      | int  | The number of records to skip. |
| limit     | int  | The maximum number of records to return. |
| token     | str  | The authentication token. |

**Returns:**
- `list`: A list of face records.

## ☕ Donation
Love the program? Consider a donation to support my work.

[!["Donation"](https://raw.githubusercontent.com/soranoo/Donation/main/resources/image/DonateBtn.png)](https://github.com/soranoo/Donation) <- click me~
