# Blui Expense Tracker - Backend API

Backend API untuk aplikasi Blui Expense Tracker dibangun dengan FastAPI dan SQLAlchemy.

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Setup Environment

Salin file `.env` dan sesuaikan konfigurasi:

```bash
cp .env .env.local
```

### 3. Create Database

```bash
python create_db.py
```

### 4. Run Server

```bash
python run.py
```

API akan berjalan di `http://localhost:8000`

## 🐳 Docker Setup (Recommended)

Untuk setup yang lebih mudah dan konsisten, gunakan Docker Compose:

### Prerequisites

- Docker
- Docker Compose

### Quick Start with Docker

1. **Clone repository dan masuk ke folder backend:**

   ```bash
   cd Blui-Backend
   ```

2. **Jalankan aplikasi dengan Docker Compose:**

   ```bash
   # Linux/Mac (gunakan script)
   ./start.sh

   # Windows (gunakan batch file)
   start.bat

   # Atau manual
   docker-compose up --build
   ```

3. **Akses API:**
   - API: http://localhost:8000
   - Dokumentasi: http://localhost:8000/docs
   - Database: localhost:5432 (PostgreSQL)

### Docker Commands

```bash
# Jalankan di background
docker-compose up -d --build

# Stop aplikasi
docker-compose down

# Lihat logs
docker-compose logs -f app

# Rebuild dan jalankan
docker-compose up --build --force-recreate

# Hapus volumes (data akan hilang)
docker-compose down -v
```

### Environment Variables

Docker Compose sudah menyediakan konfigurasi default. Untuk production, sesuaikan environment variables di `docker-compose.yml`:

- `SECRET_KEY`: Ganti dengan secret key yang aman
- `POSTGRES_PASSWORD`: Ganti password database
- Database credentials sudah dikonfigurasi di docker-compose.yml

### Database Setup

Database PostgreSQL akan otomatis diinisialisasi dengan tabel-tabel yang diperlukan saat pertama kali menjalankan Docker Compose. Aplikasi akan menjalankan migration Alembic secara otomatis.

### Troubleshooting

```bash
# Jika ada masalah dengan database
docker-compose down -v  # Hapus volumes
docker-compose up --build  # Rebuild dari awal

# Lihat logs aplikasi
docker-compose logs -f app

# Lihat logs database
docker-compose logs -f db
```

### File Uploads

Aplikasi mendukung upload foto profil yang disimpan dalam Docker volume:

- **Lokasi penyimpanan**: `/app/uploads/{user_id}/`
- **URL akses**: `http://localhost:8000/uploads/{user_id}/{filename}`
- **Format yang didukung**: JPG, JPEG, PNG, GIF
- **Volume Docker**: `uploads_data` untuk persistensi data

## 📁 Project Structure

```
Blui-Backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── api.py              # Main API router
│   │       └── endpoints/          # API endpoints
│   │           ├── auth.py
│   │           ├── categories.py
│   │           ├── transactions.py
│   │           ├── summary.py
│   │           └── user.py
│   ├── core/
│   │   ├── config.py               # App configuration
│   │   ├── database.py             # Database connection
│   │   ├── deps.py                 # FastAPI dependencies
│   │   └── security.py             # JWT & password utilities
│   ├── models/
│   │   └── models.py               # SQLAlchemy models
│   ├── schemas/
│   │   └── schemas.py              # Pydantic schemas
│   ├── services/
│   │   └── services.py             # Business logic
│   └── utils/                      # Utility functions
├── requirements.txt
├── .env
├── create_db.py
├── run.py
├── Dockerfile                    # Docker image configuration
├── docker-compose.yml           # Docker Compose setup
├── .dockerignore               # Docker ignore file
├── uploads/                    # Uploaded files directory (created by Docker)
└── README.md
```

## 🔐 Authentication

API menggunakan JWT (JSON Web Tokens) untuk authentication.

### Register

```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "fullName": "John Doe",
  "email": "john@example.com",
  "password": "password123",
  "dateOfBirth": "1990-01-01"
}
```

### Login

```http
POST /api/v1/auth/login
Content-Type: application/x-www-form-urlencoded

username=john@example.com&password=password123
```

### Using JWT Token

Tambahkan header Authorization pada request yang memerlukan authentication:

```
Authorization: Bearer <your-jwt-token>
```

## 📚 API Endpoints

### Authentication

- `POST /api/v1/auth/register` - Register user baru
- `POST /api/v1/auth/login` - Login user

### User Profile

- `GET /api/v1/user/profile` - Get user profile
- `PUT /api/v1/user/profile` - Update user profile
- `POST /api/v1/user/photo` - Upload profile photo

### Categories

- `GET /api/v1/categories` - Get all user categories
- `POST /api/v1/categories` - Create new category
- `DELETE /api/v1/categories/{id}` - Delete category

### Transactions

- `GET /api/v1/transactions` - Get transactions (dengan filter)
- `GET /api/v1/transactions/grouped` - Get transactions grouped by date
- `POST /api/v1/transactions` - Create new transaction
- `PUT /api/v1/transactions/{id}` - Update transaction
- `DELETE /api/v1/transactions/{id}` - Delete transaction

### Summary

- `GET /api/v1/summary` - Get monthly balance summary
- `GET /api/v1/summary/history` - Get summary history

## 🗄️ Database Schema

### Users

- `id`: UUID primary key
- `full_name`: String
- `email`: String (unique)
- `hashed_password`: String
- `date_of_birth`: String (optional)
- `photo_url`: String (optional)
- `is_active`: Boolean
- `created_at`, `updated_at`: DateTime

### Categories

- `id`: UUID primary key
- `user_id`: Foreign key to Users
- `name`: String
- `icon`: String
- `color`: String
- `created_at`, `updated_at`: DateTime

### Transactions

- `id`: UUID primary key
- `user_id`: Foreign key to Users
- `category_id`: Foreign key to Categories
- `type`: String ("income" or "expense")
- `name`: String
- `amount`: Float
- `date`: String (YYYY-MM-DD)
- `note`: Text (optional)
- `created_at`, `updated_at`: DateTime

## 🔧 Configuration

### Environment Variables (.env)

```env
DATABASE_URL=sqlite:///./blui.db
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DEBUG=True
APP_NAME=Blui Expense Tracker API
APP_VERSION=1.0.0
ALLOWED_ORIGINS=["http://localhost:3000", "http://localhost:8080"]
```

### Database

Default menggunakan SQLite untuk development. Untuk production, gunakan PostgreSQL:

```env
DATABASE_URL=postgresql://username:password@localhost:5432/blui_db
```

## 🧪 Testing

### Run Tests

```bash
pytest
```

### API Documentation

Kunjungi `http://localhost:8000/docs` untuk interactive API documentation (Swagger UI).

### Health Check

```bash
curl http://localhost:8000/health
```

## 🚀 Deployment

### Development

```bash
python run.py
```

### Production

Gunakan ASGI server seperti uvicorn atau gunicorn:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN python create_db.py

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 📝 Notes

- Semua endpoint yang memerlukan authentication akan otomatis memverifikasi JWT token
- Data user di-isolate berdasarkan user_id
- Password di-hash menggunakan bcrypt
- API responses menggunakan snake_case sesuai konvensi Python
- Frontend Android app mengirim request dengan camelCase, FastAPI otomatis mengkonversi

## 🤝 Contributing

1. Fork repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request
