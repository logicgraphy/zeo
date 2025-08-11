# API Structure Documentation

This document describes the refactored API structure for better maintainability and organization.

## Directory Structure

```
api/
├── __init__.py              # Package initialization
├── models.py                # Pydantic models for request/response
├── utils.py                 # Utility functions (auth, email, etc.)
├── database.py              # Database service layer (in-memory for now)
└── routers/                 # Route handlers organized by domain
    ├── __init__.py
    ├── auth.py              # Authentication endpoints
    ├── users.py             # User management endpoints  
    ├── analysis.py          # Website analysis endpoints
    └── hire.py              # Hire request endpoints
```

## Benefits of This Structure

### 1. **Separation of Concerns**
- **Models**: All Pydantic models in one place
- **Utils**: Reusable utility functions
- **Database**: Centralized data access layer
- **Routers**: Domain-specific route handlers

### 2. **Maintainability**
- Easy to find and modify specific functionality
- Clear boundaries between different components
- Easier testing and debugging

### 3. **Scalability**
- Easy to add new routers for new features
- Simple to replace in-memory database with real database
- Clear path to microservices if needed

## API Endpoints

### Authentication (`/auth`)
- `POST /auth/register` - Register new user
- `POST /auth/verify-email` - Verify email with code
- `POST /auth/resend-verification` - Resend verification code

### Users (`/users`)
- `GET /users/{email}` - Get user information

### Analysis (`/`)
- `POST /analyze/quick` - Quick website analysis
- `POST /report/request` - Request detailed report
- `POST /auth/verify-email` - Verify email for report access
- `GET /report/status/{analysis_id}` - Get report status
- `GET /report/{analysis_id}` - Generate and return a detailed report (runs full-site analysis)

### Hire (`/hire`)
- `POST /hire/request` - Submit hire request

## Models

### Core Models
- `UserRegister` - User registration data
- `EmailVerification` - Email verification request
- `UserResponse` - User information response
- `MessageResponse` - Generic message response

### Analysis Models
- `QuickAnalyzeRequest` - Quick analysis request
- `ReportRequest` - Report generation request
- `AnalysisResponse` - Analysis result response
- `ReportStatus` - Report status response
- `ReportResponse` - Detailed report response

### Step Models
- `StepResponse` - Individual step information
- `StepUpdate` - Step completion update
- `StepsResponse` - Collection of steps
- `StepPriority` - Step priority enum

### Hire Models
- `HireRequest` - Hire request data

## Database Service

The `DatabaseService` class provides a clean interface for data operations:

```python
# User operations
DatabaseService.get_user(email)
DatabaseService.create_user(email, name, password, is_verified=False)
DatabaseService.update_user_verification(email)

# Verification codes
DatabaseService.get_verification_code(email)
DatabaseService.set_verification_code(email, code, expires_at)
DatabaseService.delete_verification_code(email)

# Analysis operations
DatabaseService.create_analysis(analysis_id, url, grade, summary, score)
DatabaseService.get_analysis(analysis_id)

# Steps operations
DatabaseService.create_steps(analysis_id, steps)
DatabaseService.get_steps(analysis_id)
DatabaseService.update_step(step_id, completed)
```

## Future Improvements

### 1. **Real Database Integration**
Replace `database.py` with actual database operations using SQLAlchemy and the existing models in `db/model.py`.

### 2. **Authentication Middleware**
Add JWT token-based authentication for protected routes.

### 3. **Input Validation**
Add more comprehensive validation using Pydantic validators.

### 4. **Error Handling**
Implement consistent error handling and logging across all routers.

### 5. **Testing**
Add unit tests for each router and service function.

### 6. **API Versioning**
Implement API versioning when breaking changes are needed.

## Migration Notes

The refactoring maintains 100% backward compatibility with the original API. All existing endpoints work exactly the same way, just organized better internally.

### Key Changes:
- ✅ All endpoints moved to appropriate routers
- ✅ Models extracted to separate file
- ✅ Utilities organized in utils.py
- ✅ Database operations centralized
- ✅ Fixed type errors and improved type safety
- ✅ Maintained all existing functionality 