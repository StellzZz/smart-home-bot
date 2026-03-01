"""Authentication service for Smart Home Bot"""

import hashlib
import secrets
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

from config.settings import settings
from config.logging_config import logger, security_logger


class AuthService:
    """Service for handling authentication and authorization"""
    
    def __init__(self):
        self.allowed_user_ids = set(settings.TELEGRAM_USER_IDS)
        self.allowed_usernames = set(settings.ALLOWED_USERNAMES)
        self.session_tokens: Dict[str, Dict[str, Any]] = {}
        self.failed_attempts: Dict[str, List[datetime]] = {}
        self.max_failed_attempts = 5
        self.lockout_duration = timedelta(minutes=15)
        self.session_duration = timedelta(hours=24)
    
    def is_user_authorized(self, user_id: int, username: Optional[str] = None) -> bool:
        """Check if user is authorized"""
        try:
            # Check if user is locked out due to failed attempts
            if self._is_user_locked_out(str(user_id)):
                security_logger.warning(f"Locked out user attempted access: {user_id}")
                return False
            
            # Check user ID whitelist
            if self.allowed_user_ids and user_id not in self.allowed_user_ids:
                self._record_failed_attempt(str(user_id))
                security_logger.warning(f"Unauthorized user ID: {user_id}")
                return False
            
            # Check username whitelist
            if self.allowed_usernames and username:
                if username not in self.allowed_usernames:
                    self._record_failed_attempt(str(user_id))
                    security_logger.warning(f"Unauthorized username: @{username}")
                    return False
            
            # Clear failed attempts on successful authorization
            self._clear_failed_attempts(str(user_id))
            
            security_logger.info(f"User authorized: {user_id} (@{username})")
            return True
            
        except Exception as e:
            security_logger.error(f"Error in authorization check: {e}")
            return False
    
    def generate_session_token(self, user_id: int) -> str:
        """Generate session token for user"""
        try:
            # Generate secure random token
            token = secrets.token_urlsafe(32)
            
            # Store token with expiration
            expires_at = datetime.now() + self.session_duration
            self.session_tokens[token] = {
                "user_id": user_id,
                "created_at": datetime.now(),
                "expires_at": expires_at
            }
            
            security_logger.info(f"Session token generated for user {user_id}")
            return token
            
        except Exception as e:
            security_logger.error(f"Error generating session token: {e}")
            raise
    
    def validate_session_token(self, token: str) -> Optional[int]:
        """Validate session token and return user ID"""
        try:
            if token not in self.session_tokens:
                security_logger.warning("Invalid session token provided")
                return None
            
            session = self.session_tokens[token]
            
            # Check if token is expired
            if datetime.now() > session["expires_at"]:
                del self.session_tokens[token]
                security_logger.warning("Expired session token provided")
                return None
            
            security_logger.info(f"Valid session token for user {session['user_id']}")
            return session["user_id"]
            
        except Exception as e:
            security_logger.error(f"Error validating session token: {e}")
            return None
    
    def revoke_session_token(self, token: str) -> bool:
        """Revoke session token"""
        try:
            if token in self.session_tokens:
                user_id = self.session_tokens[token]["user_id"]
                del self.session_tokens[token]
                security_logger.info(f"Session token revoked for user {user_id}")
                return True
            return False
            
        except Exception as e:
            security_logger.error(f"Error revoking session token: {e}")
            return False
    
    def revoke_all_user_sessions(self, user_id: int) -> int:
        """Revoke all sessions for a user"""
        try:
            tokens_to_remove = []
            for token, session in self.session_tokens.items():
                if session["user_id"] == user_id:
                    tokens_to_remove.append(token)
            
            for token in tokens_to_remove:
                del self.session_tokens[token]
            
            security_logger.info(f"Revoked {len(tokens_to_remove)} sessions for user {user_id}")
            return len(tokens_to_remove)
            
        except Exception as e:
            security_logger.error(f"Error revoking user sessions: {e}")
            return 0
    
    def _is_user_locked_out(self, user_id: str) -> bool:
        """Check if user is locked out due to failed attempts"""
        try:
            if user_id not in self.failed_attempts:
                return False
            
            # Remove old attempts outside lockout window
            cutoff_time = datetime.now() - self.lockout_duration
            self.failed_attempts[user_id] = [
                attempt for attempt in self.failed_attempts[user_id]
                if attempt > cutoff_time
            ]
            
            # Check if user exceeded max attempts
            return len(self.failed_attempts[user_id]) >= self.max_failed_attempts
            
        except Exception as e:
            security_logger.error(f"Error checking lockout status: {e}")
            return False
    
    def _record_failed_attempt(self, user_id: str):
        """Record failed authentication attempt"""
        try:
            if user_id not in self.failed_attempts:
                self.failed_attempts[user_id] = []
            
            self.failed_attempts[user_id].append(datetime.now())
            
            # Clean old attempts
            cutoff_time = datetime.now() - self.lockout_duration
            self.failed_attempts[user_id] = [
                attempt for attempt in self.failed_attempts[user_id]
                if attempt > cutoff_time
            ]
            
            security_logger.warning(f"Failed attempt recorded for user {user_id}")
            
        except Exception as e:
            security_logger.error(f"Error recording failed attempt: {e}")
    
    def _clear_failed_attempts(self, user_id: str):
        """Clear failed attempts for user"""
        try:
            if user_id in self.failed_attempts:
                del self.failed_attempts[user_id]
                
        except Exception as e:
            security_logger.error(f"Error clearing failed attempts: {e}")
    
    def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions"""
        try:
            expired_tokens = []
            now = datetime.now()
            
            for token, session in self.session_tokens.items():
                if now > session["expires_at"]:
                    expired_tokens.append(token)
            
            for token in expired_tokens:
                del self.session_tokens[token]
            
            if expired_tokens:
                security_logger.info(f"Cleaned up {len(expired_tokens)} expired sessions")
            
            return len(expired_tokens)
            
        except Exception as e:
            security_logger.error(f"Error cleaning up expired sessions: {e}")
            return 0
    
    def get_security_stats(self) -> Dict[str, Any]:
        """Get security statistics"""
        try:
            return {
                "active_sessions": len(self.session_tokens),
                "locked_out_users": len([
                    uid for uid in self.failed_attempts.keys()
                    if self._is_user_locked_out(uid)
                ]),
                "failed_attempts_total": sum(
                    len(attempts) for attempts in self.failed_attempts.values()
                ),
                "allowed_user_ids": len(self.allowed_user_ids),
                "allowed_usernames": len(self.allowed_usernames)
            }
            
        except Exception as e:
            security_logger.error(f"Error getting security stats: {e}")
            return {}
    
    def validate_webhook_secret(self, secret_token: str) -> bool:
        """Validate Telegram webhook secret"""
        try:
            if not settings.TELEGRAM_WEBHOOK_SECRET:
                return True  # No secret configured, allow all
            
            return secrets.compare_digest(
                secret_token or "",
                settings.TELEGRAM_WEBHOOK_SECRET
            )
            
        except Exception as e:
            security_logger.error(f"Error validating webhook secret: {e}")
            return False
    
    def hash_sensitive_data(self, data: str) -> str:
        """Hash sensitive data for logging"""
        try:
            return hashlib.sha256(data.encode()).hexdigest()[:16]
        except Exception as e:
            security_logger.error(f"Error hashing data: {e}")
            return "hash_error"


# Global auth service instance
auth_service = AuthService()
