import unittest
from datetime import datetime
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from Backend.password_entry import PasswordEntry

class TestPasswordEntry(unittest.TestCase):
    def test_init_default_values(self):
        # Test PasswordEntry initialization with default values
        entry = PasswordEntry(1, "Dummy Service", "random user", "password123")

        self.assertEqual(entry.id, 1)
        self.assertEqual(entry.service, "Dummy Service")
        self.assertEqual(entry.username, "random user")
        self.assertEqual(entry.password, "password123")
        self.assertEqual(entry.strength, "Unknown")
        self.assertEqual(entry.notes, "")
        self.assertIsInstance(entry.created_at, datetime)
        self.assertIsInstance(entry.last_updated, datetime)

    def test_init_custom_values(self):
        # Test PasswordEntry initialization with custom values
        created = datetime(2026, 1, 1, 12, 0, 0)
        updated = datetime(2026, 1, 2, 12, 0, 0)

        entry = PasswordEntry(
            id=2,
            service="custom",
            username="special user",
            password="big password",
            strength="Strong",
            notes="",
            created_at=created,
            last_updated=updated
        )

        self.assertEqual(entry.id, 2)
        self.assertEqual(entry.service, "custom")
        self.assertEqual(entry.username, "special user")
        self.assertEqual(entry.password, "big password")
        self.assertEqual(entry.strength, "Strong")
        self.assertEqual(entry.notes, "")
        self.assertEqual(entry.created_at, created)
        self.assertEqual(entry.last_updated, updated)

    def test_to_dict(self):
        # Test to_dict method
        created = datetime(2026, 1, 1, 12, 0, 0)
        updated = datetime(2026, 1, 2, 12, 0, 0)

        entry = PasswordEntry(
            id=3,
            service="dict",
            username="dict user",
            password="dict pass",
            strength="Medium",
            notes="",
            created_at=created,
            last_updated=updated
        )

        result = entry.to_dict()

        expected = {
            'id': 3,
            'service': "dict",
            'username': "dict user",
            'password': "dict pass",
            'strength': "Medium",
            'notes': "",
            'created_at': created.isoformat(),
            'last_updated': updated.isoformat()
        }

        self.assertEqual(result, expected)

    def test_to_dict_none_dates(self):
        # Test to_dict method with None dates
        entry = PasswordEntry(4, "None", "none user", "none pass")
        entry.created_at = None
        entry.last_updated = None

        result = entry.to_dict()

        self.assertIsNone(result['created_at'])
        self.assertIsNone(result['last_updated'])

if __name__ == '__main__':
    unittest.main()