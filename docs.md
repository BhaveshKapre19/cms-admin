# Django CMS - Complete Documentation

## Table of Contents
1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Installation & Setup](#installation--setup)
4. [Data Models](#data-models)
5. [API Reference](#api-reference)
6. [Authentication & Authorization](#authentication--authorization)
7. [Usage Examples](#usage-examples)
8. [Advanced Features](#advanced-features)
9. [Deployment](#deployment)
10. [Troubleshooting](#troubleshooting)

---

## Overview

Django CMS is a headless content management system built with Django 5.2.7 and Django REST Framework 3.16.1. It provides a complete backend solution for content-driven applications with robust user management, content publishing, and file handling capabilities.

### Technology Stack

- **Backend Framework**: Django 5.2.7
- **API Framework**: Django REST Framework 3.16.1
- **Authentication**: JWT (djangorestframework-simplejwt 5.5.1)
- **Database**: SQLite (development), PostgreSQL-ready
- **CORS**: django-cors-headers 4.9.0
- **Image Processing**: Pillow 12.0.0
- **Email**: SMTP (Mailtrap for development)

### Core Applications

1. **user_management**: User authentication, profiles, OTP verification
2. **post**: Content management with categories and tags
3. **fileGallery**: File upload and management system

---

## Architecture

### Project Structure

```
CMS/
├── cms/                           # Main Django project
│   ├── __init__.py
│   ├── settings.py               # Django configuration
│   ├── urls.py                   # Root URL routing
│   ├── apis.py                   # API endpoints aggregation
│   ├── middleware.py             # Custom middleware (maintenance mode)
│   ├── wsgi.py                   # WSGI configuration
│   └── asgi.py                   # ASGI configuration
│
├── user_management/              # User management app
│   ├── models.py                 # UserModel, EmailOtp
│   ├── views.py                  # Authentication views
│   ├── serializers.py            # DRF serializers
│   ├── permissions.py            # Custom permissions
│   ├── validators.py             # Password validators
│   ├── utils.py                  # Utility functions (OTP generation)
│   └── urls.py                   # User API routes
│
├── post/                         # Post management app
│   ├── models.py                 # Post, Category models
│   ├── views.py                  # Post CRUD viewsets
│   ├── serializers.py            # Post serializers
│   └── urls.py                   # Post API routes
│
├── fileGallery/                  # File management app
│   ├── models.py                 # FileGallery model
│   ├── views.py                  # File upload views
│   ├── serializers.py            # File serializers
│   └── urls.py                   # File API routes
│
├── media/                        # User uploaded files
│   └── {user-slug}/             # User-specific folders
│       ├── {profile_pic}        # Profile pictures
│       └── posts/               # Post thumbnails
│
├── templates/                    # Django templates
│   └── maintenance.html         # Maintenance mode page
│
├── db.sqlite3                   # SQLite database
├── manage.py                    # Django CLI
└── requirements.txt             # Python dependencies
```

### Design Patterns

- **Soft Delete**: Users and posts are never permanently deleted, only marked as deleted
- **Slug-based URLs**: All resources use unique slugs for SEO-friendly URLs
- **JWT Authentication**: Stateless authentication with access/refresh tokens
- **ViewSets**: DRF ViewSets for consistent CRUD operations
- **Custom Managers**: Custom QuerySet managers for soft delete filtering

---

## Installation & Setup

### Prerequisites

- Python 3.10+
- pip
- Virtual environment tool (venv, virtualenv, conda)

### Step-by-Step Installation

#### 1. Clone and Navigate
```bash
git clone <repository-url>
cd CMS
```

#### 2. Create Virtual Environment
```bash
# Windows
python -m venv env
env\Scripts\activate

# Linux/Mac
python3 -m venv env
source env/bin/activate
```

#### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

**Dependencies** (`requirements.txt`):
```
asgiref==3.10.0
Django==5.2.7
django-cors-headers==4.9.0
django-filter==25.2
djangorestframework==3.16.1
djangorestframework_simplejwt==5.5.1
gunicorn==23.0.0
packaging==25.0
pillow==12.0.0
PyJWT==2.10.1
python-dotenv==1.1.1
sqlparse==0.5.3
tzdata==2025.2
```

#### 4. Configure Settings

Edit `cms/settings.py` for your environment:

```python
# Debug mode (set to False in production)
DEBUG = True

# Allowed hosts
ALLOWED_HOSTS = ["*"]  # Restrict in production

# Database (default SQLite)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Email configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'sandbox.smtp.mailtrap.io'
EMAIL_HOST_USER = 'your-mailtrap-username'
EMAIL_HOST_PASSWORD = 'your-mailtrap-password'
EMAIL_PORT = '2525'

# JWT settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
}

# Application settings
MAINTAINANCE = False
ALLOW_REGISTRATION = False
```

#### 5. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

#### 6. Create Superuser
```bash
python manage.py createsuperuser
```

You'll be prompted for:
- Email address (username)
- Password

Or use the default:
- Email: `admin@admin.com`
- Password: `admin`

#### 7. Run Development Server
```bash
python manage.py runserver
```

Access the API at: `http://localhost:8000/`

---

## Data Models

### UserModel

**Location**: `user_management/models.py`

Custom user model extending Django's `AbstractUser`.

```python
class UserModel(AbstractUser):
    email = models.EmailField(unique=True)          # Primary login field
    bio = models.TextField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    slug = models.SlugField(unique=True, blank=True) # Auto-generated
    profile_pic = models.ImageField(upload_to=user_profile_pic_path, blank=True, null=True)
    
    is_verified = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    
    date_joined = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
```

**Key Features**:
- Email-based authentication (`USERNAME_FIELD = 'email'`)
- Auto-generated unique slug (e.g., `john-doe-a1b2c3d4`)
- Profile picture upload to `media/{slug}/`
- Soft delete functionality
- Custom user manager for user creation

**Permissions**:
- `is_superuser`: Full admin access
- `is_staff`: Django admin panel access
- `is_verified`: Email verification status

### EmailOtp

**Location**: `user_management/models.py`

OTP storage for email verification and password reset.

```python
class EmailOtp(models.Model):
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name="otp_codes")
    email = models.EmailField()
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)
```

**Usage**:
- Email verification during registration
- Password reset flow
- 6-digit numeric OTP
- Automatic expiry (configurable in utils)

### Post

**Location**: `post/models.py`

Content management model with rich features.

```python
class Post(models.Model):
    author = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='posts')
    title = models.CharField(max_length=250)
    body = models.TextField()                    # HTML content
    excerpt = models.TextField(blank=True)       # Auto-generated summary
    tags = models.JSONField(default=list, blank=True)
    categories = models.ManyToManyField(Category, blank=True)
    thumbnail = models.ImageField(upload_to=post_upload_path)
    slug = models.SlugField(unique=True, blank=True)
    
    is_published = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
```

**Key Features**:
- HTML content support in `body` field
- Auto-generated excerpt (first 40 words, stripped HTML)
- JSON tags array for flexible tagging
- Many-to-many categories
- Thumbnail upload to `media/{user-slug}/posts/`
- Auto-generated unique slug
- Draft/publish workflow via `is_published`
- Soft delete with restore capability

**Custom Manager**:
```python
Post.objects.all()            # Only non-deleted posts
Post.all_objects.all()        # All posts including deleted
```

### Category

**Location**: `post/models.py`

Simple category model for post organization.

```python
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    slug = models.SlugField(unique=True, blank=True)
```

**Features**:
- Auto-generated slug from name
- Many-to-many relationship with posts

### FileGallery

**Location**: `fileGallery/models.py`

File upload and management system.

```python
class FileGallery(models.Model):
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='file_gallery/')
    size = models.PositiveIntegerField(null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
```

**Features**:
- Auto-title from filename
- Automatic file size calculation
- Upload to `media/file_gallery/`
- Ordered by upload time (newest first)

---

## API Reference

### Base URL
```
http://localhost:8000/api/
```

### Authentication Endpoints

#### 1. User Registration
```http
POST /api/users/register/
```

**Request**:
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "username": "johndoe"
}
```

**Response** (201 Created):
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "johndoe",
  "slug": "johndoe-a1b2c3d4",
  "is_verified": false,
  "message": "Registration successful. Please verify your email."
}
```

**Notes**:
- OTP sent to email for verification
- User cannot login until verified
- Requires `ALLOW_REGISTRATION = True` in settings

#### 2. Verify Email OTP
```http
POST /api/users/verify-otp/
```

**Request**:
```json
{
  "email": "user@example.com",
  "otp": "123456"
}
```

**Response** (200 OK):
```json
{
  "message": "Email verified successfully",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "is_verified": true
  }
}
```

#### 3. User Login
```http
POST /api/users/login/
```

**Request**:
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Response** (200 OK):
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "johndoe",
    "slug": "johndoe-a1b2c3d4",
    "is_verified": true,
    "is_staff": false,
    "is_superuser": false
  }
}
```

#### 4. Refresh Token
```http
POST /api/users/token/refresh/
```

**Request**:
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response** (200 OK):
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

#### 5. Forget Password
```http
POST /api/users/forget-password/
```

**Request**:
```json
{
  "email": "user@example.com"
}
```

**Response** (200 OK):
```json
{
  "message": "OTP sent to your email"
}
```

#### 6. Reset Password
```http
POST /api/users/reset-password/
```

**Request**:
```json
{
  "email": "user@example.com",
  "otp": "123456",
  "new_password": "NewSecurePass123!"
}
```

**Response** (200 OK):
```json
{
  "message": "Password reset successfully"
}
```

### User Management Endpoints

#### 1. Get Current User Profile
```http
GET /api/users/me/
Authorization: Bearer <access_token>
```

**Response** (200 OK):
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "johndoe",
  "slug": "johndoe-a1b2c3d4",
  "bio": "Software developer",
  "address": "123 Main St",
  "profile_pic": "http://localhost:8000/media/johndoe-a1b2c3d4/profile.jpg",
  "is_verified": true,
  "date_joined": "2025-12-18T10:00:00Z"
}
```

#### 2. List All Users (Admin)
```http
GET /api/users/
Authorization: Bearer <access_token>
```

**Query Parameters**:
- `is_verified`: Filter by verification status (true/false)
- `is_staff`: Filter by staff status
- `search`: Search by email or username

**Response** (200 OK):
```json
{
  "count": 10,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "email": "user@example.com",
      "username": "johndoe",
      "slug": "johndoe-a1b2c3d4",
      "is_verified": true,
      "is_staff": false,
      "date_joined": "2025-12-18T10:00:00Z"
    }
  ]
}
```

#### 3. Get User by Slug
```http
GET /api/users/{slug}/
Authorization: Bearer <access_token>
```

**Response** (200 OK):
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "johndoe",
  "slug": "johndoe-a1b2c3d4",
  "bio": "Software developer",
  "profile_pic": "http://localhost:8000/media/johndoe-a1b2c3d4/profile.jpg"
}
```

#### 4. Update User
```http
PUT /api/users/{slug}/
Authorization: Bearer <access_token>
Content-Type: multipart/form-data
```

**Request**:
```json
{
  "bio": "Updated bio",
  "address": "456 New St",
  "profile_pic": <file>
}
```

**Response** (200 OK):
```json
{
  "id": 1,
  "email": "user@example.com",
  "bio": "Updated bio",
  "address": "456 New St",
  "profile_pic": "http://localhost:8000/media/johndoe-a1b2c3d4/profile.jpg"
}
```

#### 5. Delete User (Soft Delete)
```http
DELETE /api/users/{slug}/
Authorization: Bearer <access_token>
```

**Response** (204 No Content)

**Notes**:
- User is marked as deleted (`is_deleted=True`)
- User is deactivated (`is_active=False`)
- Data is preserved for audit purposes

### Post Management Endpoints

#### 1. List Posts
```http
GET /api/posts/
Authorization: Bearer <access_token>
```

**Query Parameters**:
- `is_published`: Filter by publish status (true/false)
- `categories`: Filter by category slug
- `author`: Filter by author slug
- `search`: Search in title and body

**Response** (200 OK):
```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "My First Post",
      "slug": "my-first-post-abc123",
      "excerpt": "This is an auto-generated excerpt...",
      "thumbnail": "http://localhost:8000/media/johndoe/posts/thumb.jpg",
      "author": {
        "username": "johndoe",
        "slug": "johndoe-a1b2c3d4"
      },
      "categories": [
        {
          "name": "Technology",
          "slug": "technology"
        }
      ],
      "tags": ["django", "python", "web"],
      "is_published": true,
      "created_at": "2025-12-18T10:00:00Z",
      "updated_at": "2025-12-18T11:00:00Z"
    }
  ]
}
```

#### 2. Create Post
```http
POST /api/posts/
Authorization: Bearer <access_token>
Content-Type: multipart/form-data
```

**Request**:
```json
{
  "title": "My New Post",
  "body": "<p>Full HTML content here</p>",
  "tags": ["django", "tutorial"],
  "categories": [1, 2],
  "thumbnail": <file>,
  "is_published": true
}
```

**Response** (201 Created):
```json
{
  "id": 2,
  "title": "My New Post",
  "slug": "my-new-post-def456",
  "body": "<p>Full HTML content here</p>",
  "excerpt": "Full HTML content here",
  "tags": ["django", "tutorial"],
  "categories": [1, 2],
  "thumbnail": "http://localhost:8000/media/johndoe/posts/thumb.jpg",
  "is_published": true,
  "created_at": "2025-12-18T12:00:00Z"
}
```

#### 3. Get Post by Slug
```http
GET /api/posts/{slug}/
Authorization: Bearer <access_token>
```

**Response** (200 OK):
```json
{
  "id": 1,
  "title": "My First Post",
  "slug": "my-first-post-abc123",
  "body": "<p>Full HTML content...</p>",
  "excerpt": "Auto-generated excerpt...",
  "tags": ["django", "python"],
  "categories": [
    {
      "id": 1,
      "name": "Technology",
      "slug": "technology"
    }
  ],
  "thumbnail": "http://localhost:8000/media/johndoe/posts/thumb.jpg",
  "author": {
    "id": 1,
    "username": "johndoe",
    "slug": "johndoe-a1b2c3d4"
  },
  "is_published": true,
  "created_at": "2025-12-18T10:00:00Z",
  "updated_at": "2025-12-18T11:00:00Z"
}
```

#### 4. Update Post
```http
PUT /api/posts/{slug}/
Authorization: Bearer <access_token>
```

**Request**:
```json
{
  "title": "Updated Post Title",
  "body": "<p>Updated content</p>",
  "is_published": true
}
```

**Response** (200 OK):
```json
{
  "id": 1,
  "title": "Updated Post Title",
  "body": "<p>Updated content</p>",
  "updated_at": "2025-12-18T13:00:00Z"
}
```

#### 5. Delete Post (Soft Delete)
```http
DELETE /api/posts/{slug}/
Authorization: Bearer <access_token>
```

**Response** (204 No Content)

**Notes**:
- Post is marked as deleted and unpublished
- Can be restored via custom restore endpoint

### Category Endpoints

#### 1. List Categories
```http
GET /api/categories/
```

**Response** (200 OK):
```json
[
  {
    "id": 1,
    "name": "Technology",
    "slug": "technology",
    "description": "Tech-related posts"
  }
]
```

#### 2. Create Category
```http
POST /api/categories/
Authorization: Bearer <access_token>
```

**Request**:
```json
{
  "name": "Web Development",
  "description": "Posts about web dev"
}
```

**Response** (201 Created):
```json
{
  "id": 2,
  "name": "Web Development",
  "slug": "web-development",
  "description": "Posts about web dev"
}
```

### File Gallery Endpoints

#### 1. List Files
```http
GET /api/files/
Authorization: Bearer <access_token>
```

**Response** (200 OK):
```json
{
  "count": 3,
  "results": [
    {
      "id": 1,
      "title": "document.pdf",
      "file": "http://localhost:8000/media/file_gallery/document.pdf",
      "size": 1024000,
      "uploaded_at": "2025-12-18T10:00:00Z"
    }
  ]
}
```

#### 2. Upload File
```http
POST /api/files/
Authorization: Bearer <access_token>
Content-Type: multipart/form-data
```

**Request**:
```json
{
  "file": <file>,
  "title": "My Document"
}
```

**Response** (201 Created):
```json
{
  "id": 2,
  "title": "My Document",
  "file": "http://localhost:8000/media/file_gallery/my-doc.pdf",
  "size": 2048000,
  "uploaded_at": "2025-12-18T12:00:00Z"
}
```

### Health Check Endpoint

```http
GET /health-check/
```

**Response** (200 OK) - Normal:
```json
{
  "status": "healthy",
  "maintenance": false
}
```

**Response** (503 Service Unavailable) - Maintenance:
```json
{
  "detail": "The site is under maintenance. Please try again later.",
  "key": "MAINTENANCE_MODE",
  "CODE": "MAT503"
}
```

---

## Authentication & Authorization

### JWT Token Flow

1. **User Registration**:
   ```
   POST /api/users/register/ → OTP sent to email
   ```

2. **Email Verification**:
   ```
   POST /api/users/verify-otp/ → Account activated
   ```

3. **Login**:
   ```
   POST /api/users/login/ → Returns access + refresh tokens
   ```

4. **API Requests**:
   ```
   GET /api/posts/
   Headers: Authorization: Bearer <access_token>
   ```

5. **Token Refresh** (when access token expires):
   ```
   POST /api/users/token/refresh/
   Body: {"refresh": "<refresh_token>"}
   → Returns new access token
   ```

### Token Lifespans

- **Access Token**: 60 minutes
- **Refresh Token**: 7 days

### Authorization Levels

1. **Public** (no authentication):
   - Health check
   - List categories

2. **Authenticated** (valid JWT):
   - View posts
   - View files
   - View own profile

3. **Owner** (resource owner):
   - Update own posts
   - Update own profile

4. **Staff/Admin**:
   - Manage all users
   - Manage all posts
   - System settings

### Custom Permissions

Located in `user_management/permissions.py`:

```python
class IsStaffOrReadOnly(permissions.BasePermission):
    """Allow read to anyone, write to staff only"""
    
class IsOwnerOrAdmin(permissions.BasePermission):
    """Allow owner or admin to modify"""
```

---

## Usage Examples

### Example 1: Complete User Flow

```python
import requests

BASE_URL = "http://localhost:8000/api"

# 1. Register
response = requests.post(f"{BASE_URL}/users/register/", json={
    "email": "newuser@example.com",
    "password": "SecurePass123!",
    "username": "newuser"
})
print(response.json())

# 2. Verify email (get OTP from email)
response = requests.post(f"{BASE_URL}/users/verify-otp/", json={
    "email": "newuser@example.com",
    "otp": "123456"
})
print(response.json())

# 3. Login
response = requests.post(f"{BASE_URL}/users/login/", json={
    "email": "newuser@example.com",
    "password": "SecurePass123!"
})
tokens = response.json()
access_token = tokens['access']
refresh_token = tokens['refresh']

# 4. Get profile
headers = {"Authorization": f"Bearer {access_token}"}
response = requests.get(f"{BASE_URL}/users/me/", headers=headers)
print(response.json())
```

### Example 2: Creating a Post

```python
import requests

BASE_URL = "http://localhost:8000/api"
headers = {"Authorization": f"Bearer {access_token}"}

# Upload thumbnail
with open('thumbnail.jpg', 'rb') as f:
    files = {'thumbnail': f}
    data = {
        'title': 'My First Blog Post',
        'body': '<p>This is the full content of my post.</p>',
        'tags': '["python", "django", "tutorial"]',
        'is_published': 'true'
    }
    
    response = requests.post(
        f"{BASE_URL}/posts/",
        headers=headers,
        data=data,
        files=files
    )

post = response.json()
print(f"Created post: {post['slug']}")
```

### Example 3: Password Reset Flow

```python
import requests

BASE_URL = "http://localhost:8000/api"

# 1. Request OTP
response = requests.post(f"{BASE_URL}/users/forget-password/", json={
    "email": "user@example.com"
})
print(response.json())  # OTP sent

# 2. Reset password with OTP
response = requests.post(f"{BASE_URL}/users/reset-password/", json={
    "email": "user@example.com",
    "otp": "123456",
    "new_password": "NewSecurePass123!"
})
print(response.json())
```

### Example 4: Filtering Posts

```python
import requests

BASE_URL = "http://localhost:8000/api"
headers = {"Authorization": f"Bearer {access_token}"}

# Get published posts in 'Technology' category
params = {
    'is_published': 'true',
    'categories': 'technology',
    'search': 'django'
}

response = requests.get(
    f"{BASE_URL}/posts/",
    headers=headers,
    params=params
)

posts = response.json()['results']
for post in posts:
    print(f"- {post['title']} by {post['author']['username']}")
```

---

## Advanced Features

### Soft Delete System

Both `UserModel` and `Post` use soft delete:

```python
# Delete a post
post = Post.objects.get(slug='my-post')
post.delete()  # Sets is_deleted=True, is_published=False

# Query only active posts
Post.objects.all()  # Excludes deleted

# Query all posts including deleted
Post.all_objects.all()

# Restore a post
post.restore()  # Sets is_deleted=False
```

### Auto-generated Slugs

Slugs are automatically generated with UUID suffixes:

```python
# User: username + 8-char UUID
# john-doe → john-doe-a1b2c3d4

# Post: title + 6-char UUID
# my first post → my-first-post-abc123
```

### Excerpt Generation

Post excerpts are auto-generated from body HTML:

```python
def generate_excerpt(self):
    # Strip HTML tags
    clean_text = re.sub('<[^<]+?>', '', self.body)
    # Take first 40 words
    words = clean_text.split()
    return " ".join(words[:40]) + ("..." if len(words) > 40 else "")
```

### Maintenance Mode

Enable in `cms/settings.py`:

```python
MAINTAINANCE = True
```

All API requests return 503:
```json
{
  "detail": "The site is under maintenance. Please try again later.",
  "key": "MAINTENANCE_MODE",
  "CODE": "MAT503"
}
```

### File Upload Organization

Files are organized by user:

```
media/
├── johndoe-a1b2c3d4/
│   ├── profile.jpg              # Profile picture
│   └── posts/
│       ├── uuid1.jpg            # Post thumbnails
│       └── uuid2.png
└── file_gallery/
    └── document.pdf             # General files
```

---

## Deployment

### Production Checklist

#### 1. Security Settings

```python
# settings.py
DEBUG = False
SECRET_KEY = os.environ.get('SECRET_KEY')  # From environment
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']

# HTTPS
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

#### 2. Database

Use PostgreSQL in production:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': '5432',
    }
}
```

#### 3. Static Files

```bash
# Collect static files
python manage.py collectstatic

# Configure settings
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATIC_URL = '/static/'
```

#### 4. Email Service

Replace Mailtrap with production service:

```python
# SendGrid, AWS SES, etc.
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_HOST_USER = os.environ.get('SENDGRID_USERNAME')
EMAIL_HOST_PASSWORD = os.environ.get('SENDGRID_PASSWORD')
EMAIL_PORT = 587
EMAIL_USE_TLS = True
```

#### 5. CORS

Restrict CORS to your frontend domain:

```python
CORS_ALLOWED_ORIGINS = [
    "https://yourdomain.com",
    "https://www.yourdomain.com",
]
```

#### 6. Gunicorn

Run with Gunicorn:

```bash
gunicorn cms.wsgi:application --bind 0.0.0.0:8000
```

#### 7. Environment Variables

Use `.env` file (python-dotenv):

```bash
SECRET_KEY=your-secret-key
DEBUG=False
DB_NAME=your_db
DB_USER=your_user
DB_PASSWORD=your_password
EMAIL_HOST_USER=your_email_user
```

---

## Troubleshooting

### Common Issues

#### 1. OTP Not Received

**Problem**: Email with OTP not arriving

**Solutions**:
- Check Mailtrap inbox (development)
- Verify email settings in `cms/settings.py`
- Check spam folder
- Verify email backend is configured correctly

#### 2. JWT Token Expired

**Problem**: 401 Unauthorized after some time

**Solution**:
```python
# Use refresh token to get new access token
POST /api/users/token/refresh/
{"refresh": "your-refresh-token"}
```

#### 3. Permission Denied

**Problem**: 403 Forbidden on API requests

**Solutions**:
- Ensure user is authenticated
- Check if user has required permissions (staff, superuser)
- Verify token is valid and not expired
- Check resource ownership

#### 4. File Upload Fails

**Problem**: 400 Bad Request on file upload

**Solutions**:
- Use `Content-Type: multipart/form-data`
- Check file size limits
- Verify `MEDIA_ROOT` directory exists and is writable
- Ensure Pillow is installed for images

#### 5. Slug Conflicts

**Problem**: Duplicate slug error

**Solution**:
- Slugs have UUID suffixes, conflicts should be rare
- If occurs, modify slug generation in model's `save()` method

#### 6. Registration Disabled

**Problem**: Cannot register new users

**Solution**:
```python
# In settings.py
ALLOW_REGISTRATION = True
```

#### 7. Maintenance Mode Active

**Problem**: All requests return 503

**Solution**:
```python
# In settings.py
MAINTAINANCE = False
```

### Debug Mode

Enable detailed error messages:

```python
# settings.py (development only!)
DEBUG = True
```

View detailed logs:

```bash
python manage.py runserver
# Check console output for errors
```

### Database Issues

Reset database (development):

```bash
# Delete database
rm db.sqlite3

# Delete migrations
rm */migrations/0*.py

# Recreate
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

---

## API Error Codes

### Standard HTTP Codes

- `200 OK`: Success
- `201 Created`: Resource created
- `204 No Content`: Success, no response body
- `400 Bad Request`: Validation error
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Permission denied
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error
- `503 Service Unavailable`: Maintenance mode

### Custom Error Responses

**Validation Error**:
```json
{
  "email": ["This field is required."],
  "password": ["Password is too weak."]
}
```

**Authentication Error**:
```json
{
  "detail": "Authentication credentials were not provided."
}
```

**Permission Error**:
```json
{
  "detail": "You do not have permission to perform this action."
}
```

**Maintenance Mode**:
```json
{
  "detail": "The site is under maintenance. Please try again later.",
  "key": "MAINTENANCE_MODE",
  "CODE": "MAT503"
}
```

---

## Support & Contribution

### Getting Help

- Check this documentation first
- Review API examples
- Test endpoints with tools like Postman or curl
- Enable DEBUG mode to see detailed errors

### Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guide
- Write docstrings for functions and classes
- Add tests for new features
- Update documentation for API changes
- Use meaningful commit messages

---

**Last Updated**: December 18, 2025  
**Version**: 1.0  
**Author**: Bhavesh Kapre
