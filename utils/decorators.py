"""Decorators for Smart Home Bot"""

import asyncio
import functools
import time
from typing import Callable, Any, Dict, Optional
from collections import defaultdict, deque

from config.logging_config import logger, security_logger
from config.settings import settings


class RateLimiter:
    """Simple in-memory rate limiter"""
    
    def __init__(self, requests: int, period: int):
        self.requests = requests
        self.period = period
        self.clients: Dict[str, deque] = defaultdict(deque)
    
    def is_allowed(self, client_id: str) -> bool:
        """Check if client is allowed to make a request"""
        now = time.time()
        client_requests = self.clients[client_id]
        
        # Remove old requests
        while client_requests and client_requests[0] < now - self.period:
            client_requests.popleft()
        
        # Check if under limit
        if len(client_requests) < self.requests:
            client_requests.append(now)
            return True
        
        return False


# Global rate limiter instance
rate_limiter = RateLimiter(settings.RATE_LIMIT_REQUESTS, settings.RATE_LIMIT_PERIOD)


def rate_limit(func: Callable) -> Callable:
    """Decorator to apply rate limiting"""
    
    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs):
        # Extract user_id from update if available
        update = next((arg for arg in args if hasattr(arg, 'effective_user')), None)
        client_id = str(update.effective_user.id) if update else 'unknown'
        
        if not rate_limiter.is_allowed(client_id):
            security_logger.warning(f"Rate limit exceeded for user {client_id}")
            raise Exception("Rate limit exceeded. Please try again later.")
        
        return await func(*args, **kwargs)
    
    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs):
        # Extract user_id from update if available
        update = next((arg for arg in args if hasattr(arg, 'effective_user')), None)
        client_id = str(update.effective_user.id) if update else 'unknown'
        
        if not rate_limiter.is_allowed(client_id):
            security_logger.warning(f"Rate limit exceeded for user {client_id}")
            raise Exception("Rate limit exceeded. Please try again later.")
        
        return func(*args, **kwargs)
    
    return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper


def authorized_users_only(func: Callable) -> Callable:
    """Decorator to check if user is authorized"""
    
    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs):
        # Extract user from update
        update = next((arg for arg in args if hasattr(arg, 'effective_user')), None)
        
        if not update:
            security_logger.error("No update found in function arguments")
            raise Exception("Unauthorized: No user information available")
        
        user = update.effective_user
        user_id = user.id
        username = user.username or ""
        
        # Check user ID
        if settings.TELEGRAM_USER_IDS and user_id not in settings.TELEGRAM_USER_IDS:
            security_logger.warning(f"Unauthorized access attempt by user ID {user_id} (@{username})")
            raise Exception("Unauthorized: Access denied")
        
        # Check username if configured
        if settings.ALLOWED_USERNAMES and username not in settings.ALLOWED_USERNAMES:
            security_logger.warning(f"Unauthorized access attempt by @{username} (ID: {user_id})")
            raise Exception("Unauthorized: Access denied")
        
        logger.info(f"Authorized access: {user.full_name} (@{username}, ID: {user_id})")
        return await func(*args, **kwargs)
    
    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs):
        # Extract user from update
        update = next((arg for arg in args if hasattr(arg, 'effective_user')), None)
        
        if not update:
            security_logger.error("No update found in function arguments")
            raise Exception("Unauthorized: No user information available")
        
        user = update.effective_user
        user_id = user.id
        username = user.username or ""
        
        # Check user ID
        if settings.TELEGRAM_USER_IDS and user_id not in settings.TELEGRAM_USER_IDS:
            security_logger.warning(f"Unauthorized access attempt by user ID {user_id} (@{username})")
            raise Exception("Unauthorized: Access denied")
        
        # Check username if configured
        if settings.ALLOWED_USERNAMES and username not in settings.ALLOWED_USERNAMES:
            security_logger.warning(f"Unauthorized access attempt by @{username} (ID: {user_id})")
            raise Exception("Unauthorized: Access denied")
        
        logger.info(f"Authorized access: {user.full_name} (@{username}, ID: {user_id})")
        return func(*args, **kwargs)
    
    return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper


def handle_errors(func: Callable) -> Callable:
    """Decorator to handle errors gracefully"""
    
    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {str(e)}", exc_info=True)
            
            # Try to extract update for error response
            update = next((arg for arg in args if hasattr(arg, 'message')), None)
            if update and hasattr(update, 'message'):
                await update.message.reply_text(
                    "❌ Произошла ошибка. Пожалуйста, попробуйте позже."
                )
            raise
    
    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {str(e)}", exc_info=True)
            raise
    
    return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper


def timeout(seconds: int = 30):
    """Decorator to add timeout to functions"""
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                return await asyncio.wait_for(func(*args, **kwargs), timeout=seconds)
            except asyncio.TimeoutError:
                logger.warning(f"Function {func.__name__} timed out after {seconds} seconds")
                raise Exception(f"Operation timed out after {seconds} seconds")
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            # For sync functions, we can't easily implement timeout
            # This would require threading or other mechanisms
            return func(*args, **kwargs)
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    
    return decorator
