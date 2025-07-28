# SG AI Backend

FastAPI backend with email verification functionality, designed for GCP deployment.

## Features

- User registration with email verification
- Email verification with 6-digit codes
- Password hashing with bcrypt
- CORS support for frontend integration
- Input validation with Pydantic
- Rate limiting for verification attempts
- PostgreSQL database with SQLAlchemy ORM
- Alembic migrations for schema management
- GCP Cloud SQL ready

## Setup

### Prerequisites

- Python 3.8+
- pip
- PostgreSQL (for local development) or GCP Cloud SQL

### Installation

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

3. Activate the virtual environment:
   ```bash
   # On macOS/Linux
   source venv/bin/activate
   
   # On Windows
   venv\Scripts\activate
   ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Configure environment variables:
   ```bash
   cp env.example .env
   # Edit .env with your database and email configuration
   ```

### Database Setup

#### Local Development
1. Install PostgreSQL locally
2. Create a database:
   ```sql
   CREATE DATABASE mydb;
   ```
3. Update `.env` with your local PostgreSQL credentials
4. Run migrations:
   ```bash
   alembic upgrade head
   ```

#### GCP Cloud SQL
1. Create a Cloud SQL PostgreSQL instance
2. Update `DATABASE_URL` in `.env` with Cloud SQL connection string
3. For Cloud SQL Proxy connection:
   ```bash
   DATABASE_URL=postgresql+asyncpg://username:password@/database?host=/cloudsql/project:region:instance
   ```

### Running the Application

Start the FastAPI development server:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

## API Endpoints

### POST /register
Register a new user and send verification email.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword",
  "name": "John Doe"
}
```

**Response:**
```json
{
  "email": "user@example.com",
  "name": "John Doe",
  "is_verified": false
}
```

### POST /verify-email
Verify user email with verification code.

**Request Body:**
```json
{
  "email": "user@example.com",
  "code": "123456"
}
```

**Response:**
```json
{
  "message": "Email verified successfully",
  "user": {
    "email": "user@example.com",
    "name": "John Doe",
    "is_verified": true
  }
}
```

### POST /resend-verification
Resend verification code to user email.

**Request Body:**
```json
{
  "email": "user@example.com"
}
```

### GET /users/{email}
Get user information by email.

**Response:**
```json
{
  "email": "user@example.com",
  "name": "John Doe",
  "is_verified": true
}
```

## Database Management

### Migrations
Generate new migration:
```bash
alembic revision --autogenerate -m "description"
```

Apply migrations:
```bash
alembic upgrade head
```

View migration history:
```bash
alembic history
```

## Development Notes

### Email Verification
Currently using mock email sending (prints to console). For production:

1. Uncomment email sending code in `send_verification_email()`
2. Configure SMTP settings in `.env` file
3. Use services like SendGrid, AWS SES, or Gmail SMTP

### Database
- **Development**: PostgreSQL local instance
- **Production**: GCP Cloud SQL for PostgreSQL
- **ORM**: SQLAlchemy with async support
- **Migrations**: Alembic

### Security Features
- Password hashing with bcrypt
- Verification code expiration (5 minutes)
- Maximum 3 verification attempts
- Input validation with Pydantic
- Environment variable configuration

## Testing

Use the interactive docs at http://localhost:8000/docs to test the API endpoints.

### Example Flow:

1. **Register**: POST to `/register` with user details
2. **Check Console**: Look for printed verification code
3. **Verify**: POST to `/verify-email` with email and code
4. **Check Status**: GET `/users/{email}` to confirm verification

## GCP Deployment

### Cloud Run Deployment

1. **Build Docker image**:
   ```bash
   gcloud builds submit --tag gcr.io/PROJECT_ID/sg-ai-backend
   ```

2. **Deploy to Cloud Run**:
   ```bash
   gcloud run deploy sg-ai-backend \
     --image gcr.io/PROJECT_ID/sg-ai-backend \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated
   ```

3. **Set environment variables**:
   ```bash
   gcloud run services update sg-ai-backend \
     --set-env-vars DATABASE_URL="your-cloud-sql-url" \
     --set-env-vars SECRET_KEY="your-secret-key"
   ```

### Cloud SQL Setup

1. **Create PostgreSQL instance**:
   ```bash
   gcloud sql instances create sg-ai-db \
     --database-version=POSTGRES_14 \
     --tier=db-f1-micro \
     --region=us-central1
   ```

2. **Create database**:
   ```bash
   gcloud sql databases create mydb --instance=sg-ai-db
   ```

3. **Create user**:
   ```bash
   gcloud sql users create appuser \
     --instance=sg-ai-db \
     --password=your-password
   ```

### Environment Variables for GCP
- `DATABASE_URL`: Cloud SQL connection string
- `SECRET_KEY`: Application secret key
- `SMTP_*`: Email service configuration
- `GOOGLE_CLOUD_PROJECT`: Your GCP project ID

## Production Deployment Checklist

- [ ] Set up Cloud SQL PostgreSQL instance
- [ ] Configure environment variables
- [ ] Set up email service (SendGrid/Gmail SMTP)
- [ ] Configure Cloud Run with proper resource limits
- [ ] Set up Cloud Load Balancer (if needed)
- [ ] Configure domain and SSL certificate
- [ ] Set up monitoring and logging
- [ ] Run database migrations 