from typing import Dict, List, Any
from datetime import datetime

# In-memory storage (replace with real database in production)
users_db: Dict[str, dict] = {}
verification_codes: Dict[str, dict] = {}
analysis_db: Dict[str, dict] = {}
reports_db: Dict[str, dict] = {}
# steps removed from workflow
hire_requests_db: Dict[str, dict] = {}
contact_requests_db: Dict[str, dict] = {}

class DatabaseService:
    """Service class for database operations"""
    
    @staticmethod
    def get_user(email: str) -> dict | None:
        return users_db.get(email)
    
    @staticmethod
    def create_user(email: str, name: str, is_verified: bool = False) -> dict:
        user_data = {
            "email": email,
            "name": name,            
            "is_verified": is_verified,
            "created_at": datetime.now()
        }
        users_db[email] = user_data
        return user_data
    
    @staticmethod
    def update_user_verification(email: str) -> bool:
        if email in users_db:
            users_db[email]["is_verified"] = True
            users_db[email]["verified_at"] = datetime.now()
            return True
        return False
    
    @staticmethod
    def get_verification_code(email: str) -> dict | None:
        return verification_codes.get(email)
    
    @staticmethod
    def set_verification_code(email: str, code: str, expires_at: datetime) -> None:
        verification_codes[email] = {
            "code": code,
            "expires_at": expires_at,
            "attempts": 0
        }
    
    @staticmethod
    def increment_verification_attempts(email: str) -> int:
        if email in verification_codes:
            verification_codes[email]["attempts"] += 1
            return verification_codes[email]["attempts"]
        return 0
    
    @staticmethod
    def delete_verification_code(email: str) -> None:
        verification_codes.pop(email, None)
    
    @staticmethod
    def create_analysis(analysis_id: str, url: str, summary: str, score: int, status: str = "ready") -> dict:
        analysis_data = {
            "url": url,
            "summary": summary,
            "status": status,
            "score": score
        }
        analysis_db[analysis_id] = analysis_data
        return analysis_data
    
    @staticmethod
    def get_analysis(analysis_id: str) -> dict | None:
        return analysis_db.get(analysis_id)
    
    @staticmethod
    def update_analysis(analysis_id: str, updates: Dict[str, Any]) -> dict | None:
        if analysis_id in analysis_db:
            analysis_db[analysis_id].update(updates)
            return analysis_db[analysis_id]
        return None
    
    @staticmethod
    # Steps-related methods removed
    
    @staticmethod
    def create_hire_request(request_id: str, hire_data: dict) -> dict:
        hire_requests_db[request_id] = hire_data
        return hire_data 

    @staticmethod
    def create_contact_request(request_id: str, contact_data: dict) -> dict:
        contact_requests_db[request_id] = {
            **contact_data,
            "received_at": datetime.now(),
        }
        return contact_requests_db[request_id]