"""
User Profile Manager Module

Handles user profile storage and retrieval.
Designed with future database integration in mind.
"""

from typing import Dict, Optional

from app.models.user import UserProfile


class UserProfileManager:
    """
    Manages user profiles.
    
    Current implementation uses in-memory storage as a placeholder.
    Future versions will integrate with SQLite/PostgreSQL.
    
    This class provides a stable interface for user profile operations,
    allowing the storage backend to change without affecting consumers.
    """
    
    # In-memory storage (placeholder for database)
    _profiles: Dict[str, UserProfile] = {}
    
    def __init__(self):
        """Initialize UserProfileManager."""
        pass
    
    def get_profile(self, user_id: str) -> Optional[UserProfile]:
        """
        Retrieve a user profile by ID.
        
        Args:
            user_id: The unique user identifier
            
        Returns:
            UserProfile if found, None otherwise
        """
        return self._profiles.get(user_id)
    
    def create_or_update_profile(self, profile: UserProfile) -> UserProfile:
        """
        Create a new profile or update an existing one.
        
        Args:
            profile: The UserProfile to store
            
        Returns:
            The stored UserProfile
        """
        self._profiles[profile.user_id] = profile
        return profile
    
    def get_or_create_default(self, user_id: str, name: str = "朋友") -> UserProfile:
        """
        Get existing profile or create a default one.
        
        This is useful for first-time users who haven't set up a profile.
        
        Args:
            user_id: The user ID to look up or create
            name: Default name if creating new profile
            
        Returns:
            Existing or newly created UserProfile
        """
        existing = self.get_profile(user_id)
        if existing:
            return existing
        
        # Create default profile
        default_profile = UserProfile(
            user_id=user_id,
            name=name,
            meditation_level="beginner",
        )
        return self.create_or_update_profile(default_profile)
    
    def profile_exists(self, user_id: str) -> bool:
        """
        Check if a profile exists for the given user ID.
        
        Args:
            user_id: The user ID to check
            
        Returns:
            True if profile exists, False otherwise
        """
        return user_id in self._profiles
