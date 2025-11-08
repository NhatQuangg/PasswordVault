from datetime import datetime

class PasswordEntry:
    def __init__(self, id, service, username, password, strength="Unknown", notes="", created_at=None, last_updated=None):
        self.id = id
        self.service = service
        self.username = username
        self.password = password
        self.strength = strength
        self.notes = notes
        self.created_at = created_at or datetime.now()
        self.last_updated = last_updated or datetime.now()
    
    def to_dict(self):
        return {
            'id': self.id,
            'service': self.service,
            'username': self.username,
            'password': self.password,
            'strength': self.strength,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None
        }