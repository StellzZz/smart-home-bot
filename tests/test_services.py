"""Tests for service layer"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

from services.auth_service import AuthService
from services.voice_service import VoiceService


class TestAuthService:
    """Test AuthService class"""
    
    def setup_method(self):
        """Setup test environment"""
        self.auth_service = AuthService()
    
    def test_is_user_authorized_valid_user(self):
        """Test authorization for valid user"""
        # Add user to allowed list
        self.auth_service.allowed_user_ids.add(123456)
        
        # Test authorization
        assert self.auth_service.is_user_authorized(123456) is True
        assert self.auth_service.is_user_authorized(123456, "testuser") is True
    
    def test_is_user_authorized_invalid_user(self):
        """Test authorization for invalid user"""
        # Test with no allowed users configured
        assert self.auth_service.is_user_authorized(999999) is False
        
        # Test with allowed users configured
        self.auth_service.allowed_user_ids.add(123456)
        assert self.auth_service.is_user_authorized(999999) is False
    
    def test_is_user_authorized_username(self):
        """Test authorization by username"""
        # Add username to allowed list
        self.auth_service.allowed_usernames.add("testuser")
        
        # Test authorization
        assert self.auth_service.is_user_authorized(123456, "testuser") is True
        assert self.auth_service.is_user_authorized(123456, "invaliduser") is False
    
    def test_generate_session_token(self):
        """Test session token generation"""
        user_id = 123456
        token = self.auth_service.generate_session_token(user_id)
        
        # Check token is generated
        assert token is not None
        assert len(token) > 20
        assert token in self.auth_service.session_tokens
        
        # Check token data
        session = self.auth_service.session_tokens[token]
        assert session["user_id"] == user_id
        assert session["expires_at"] > datetime.now()
    
    def test_validate_session_token(self):
        """Test session token validation"""
        user_id = 123456
        token = self.auth_service.generate_session_token(user_id)
        
        # Test valid token
        validated_user_id = self.auth_service.validate_session_token(token)
        assert validated_user_id == user_id
        
        # Test invalid token
        assert self.auth_service.validate_session_token("invalid_token") is None
    
    def test_validate_expired_session_token(self):
        """Test expired session token validation"""
        user_id = 123456
        token = self.auth_service.generate_session_token(user_id)
        
        # Manually expire token
        self.auth_service.session_tokens[token]["expires_at"] = datetime.now() - timedelta(days=1)
        
        # Test expired token
        assert self.auth_service.validate_session_token(token) is None
        assert token not in self.auth_service.session_tokens
    
    def test_revoke_session_token(self):
        """Test session token revocation"""
        user_id = 123456
        token = self.auth_service.generate_session_token(user_id)
        
        # Test revocation
        assert self.auth_service.revoke_session_token(token) is True
        assert token not in self.auth_service.session_tokens
        
        # Test revoking non-existent token
        assert self.auth_service.revoke_session_token("non_existent") is False
    
    def test_revoke_all_user_sessions(self):
        """Test revoking all user sessions"""
        user_id = 123456
        
        # Generate multiple tokens for user
        token1 = self.auth_service.generate_session_token(user_id)
        token2 = self.auth_service.generate_session_token(user_id)
        token3 = self.auth_service.generate_session_token(789012)  # Different user
        
        # Revoke all sessions for user
        revoked_count = self.auth_service.revoke_all_user_sessions(user_id)
        assert revoked_count == 2
        assert token1 not in self.auth_service.session_tokens
        assert token2 not in self.auth_service.session_tokens
        assert token3 in self.auth_service.session_tokens
    
    def test_user_lockout(self):
        """Test user lockout mechanism"""
        user_id = "123456"
        
        # Add failed attempts
        for _ in range(self.auth_service.max_failed_attempts):
            self.auth_service._record_failed_attempt(user_id)
        
        # User should be locked out
        assert self.auth_service._is_user_locked_out(user_id) is True
        
        # Authorization should fail
        assert self.auth_service.is_user_authorized(123456) is False
    
    def test_cleanup_expired_sessions(self):
        """Test cleanup of expired sessions"""
        # Generate tokens
        token1 = self.auth_service.generate_session_token(123456)
        token2 = self.auth_service.generate_session_token(789012)
        
        # Expire one token
        self.auth_service.session_tokens[token1]["expires_at"] = datetime.now() - timedelta(days=1)
        
        # Cleanup expired sessions
        cleaned_count = self.auth_service.cleanup_expired_sessions()
        assert cleaned_count == 1
        assert token1 not in self.auth_service.session_tokens
        assert token2 in self.auth_service.session_tokens
    
    def test_get_security_stats(self):
        """Test security statistics"""
        # Add some data
        self.auth_service.allowed_user_ids.add(123456)
        self.auth_service.allowed_usernames.add("testuser")
        token = self.auth_service.generate_session_token(123456)
        
        # Get stats
        stats = self.auth_service.get_security_stats()
        
        assert stats["active_sessions"] == 1
        assert stats["allowed_user_ids"] == 1
        assert stats["allowed_usernames"] == 1
        assert "failed_attempts_total" in stats
        assert "locked_out_users" in stats
    
    def test_validate_webhook_secret(self):
        """Test webhook secret validation"""
        # Test with no secret configured
        assert self.auth_service.validate_webhook_secret("") is True
        assert self.auth_service.validate_webhook_secret(None) is True
        
        # Set secret
        self.auth_service.webhook_secret = "test_secret"
        
        # Test valid secret
        assert self.auth_service.validate_webhook_secret("test_secret") is True
        
        # Test invalid secret
        assert self.auth_service.validate_webhook_secret("wrong_secret") is False


class TestVoiceService:
    """Test VoiceService class"""
    
    def setup_method(self):
        """Setup test environment"""
        self.voice_service = VoiceService()
    
    def test_is_voice_recognition_available(self):
        """Test voice recognition availability check"""
        # This test depends on whether speech_recognition is installed
        result = self.voice_service.is_voice_recognition_available()
        assert isinstance(result, bool)
    
    def test_is_speech_synthesis_available(self):
        """Test speech synthesis availability check"""
        # This test depends on whether pyttsx3 is installed
        result = self.voice_service.is_speech_synthesis_available()
        assert isinstance(result, bool)
    
    def test_get_supported_languages(self):
        """Test supported languages"""
        languages = self.voice_service.get_supported_languages()
        assert isinstance(languages, list)
        assert "ru-RU" in languages
        assert "en-US" in languages
    
    @patch('services.voice_service.sr')
    def test_recognize_from_file_mock(self, mock_sr):
        """Test speech recognition from file (mocked)"""
        # Mock speech recognition
        mock_recognizer = Mock()
        mock_sr.Recognizer.return_value = mock_recognizer
        mock_sr.AudioFile.return_value.__enter__.return_value = Mock()
        mock_recognizer.record.return_value = Mock()
        mock_recognizer.recognize_google.return_value = "test text"
        
        # Create voice service with mocked recognizer
        voice_service = VoiceService()
        voice_service.recognizer = mock_recognizer
        
        # Test recognition
        import asyncio
        result = asyncio.run(voice_service.recognize_from_file("test.wav"))
        assert result == "test text"
    
    @patch('services.voice_service.pyttsx3')
    def test_synthesize_speech_mock(self, mock_pyttsx3):
        """Test speech synthesis (mocked)"""
        # Mock pyttsx3
        mock_engine = Mock()
        mock_pyttsx3.init.return_value = mock_engine
        
        # Create voice service with mocked engine
        voice_service = VoiceService()
        voice_service.synthesis_engine = mock_engine
        
        # Test synthesis
        import asyncio
        result = asyncio.run(voice_service.synthesize_speech("test text"))
        # For save_to_file=False, result should be None
        assert result is None
    
    def test_process_voice_command_no_recognition(self):
        """Test voice command processing without recognition"""
        # Mock voice service without recognition
        voice_service = VoiceService()
        voice_service.recognizer = None
        
        # Test processing
        import asyncio
        result = asyncio.run(voice_service.process_voice_command(b"audio data"))
        assert "error" in result
        assert result["error"] == "Could not recognize speech"


if __name__ == "__main__":
    pytest.main([__file__])
