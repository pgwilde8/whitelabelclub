from cryptography.fernet import Fernet
import base64
import os
from typing import Optional
from app.core.config import settings


class EncryptionService:
    def __init__(self):
        # Use encryption key from settings
        self.key = settings.ENCRYPTION_KEY.encode()
        self.cipher = Fernet(self.key)
    
    def encrypt(self, plaintext: str) -> Optional[str]:
        """Encrypt sensitive data before storing in DB"""
        if not plaintext:
            return None
        try:
            encrypted_bytes = self.cipher.encrypt(plaintext.encode())
            return base64.b64encode(encrypted_bytes).decode()
        except Exception:
            return None
    
    def decrypt(self, encrypted_text: str) -> Optional[str]:
        """Decrypt data from DB"""
        if not encrypted_text:
            return None
        try:
            encrypted_bytes = base64.b64decode(encrypted_text.encode())
            decrypted_bytes = self.cipher.decrypt(encrypted_bytes)
            return decrypted_bytes.decode()
        except Exception:
            return None


# Global encryption service instance
encryption_service = EncryptionService()
