import unittest
from unittest.mock import patch, mock_open, MagicMock
import os
import tempfile
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from Backend.password_manager import PasswordManager

class TestPasswordManager(unittest.TestCase):
    def setUp(self):
        # Set up test
        with patch('Backend.password_manager.PasswordManager.check_vault_exists', return_value=False):
            self.pm = PasswordManager()

    def tearDown(self):
        # Cancel any running auto-lock timer to prevent hanging
        if self.pm.auto_lock_timer:
            self.pm.auto_lock_timer.cancel()
            self.pm.auto_lock_timer = None

    def test_init(self):
        # Test PasswordManager initialization
        self.assertIsNone(self.pm.key)
        self.assertFalse(self.pm.is_unlocked)
        self.assertIsNone(self.pm.master_password_hash)
        self.assertEqual(self.pm.auto_lock_minutes, 5)
        self.assertTrue(self.pm.auto_lock_active)
        self.assertIsInstance(self.pm.password_dict, dict)

    @patch('os.path.exists')
    def test_check_vault_exists(self, mock_exists):
        # Test check_vault_exists method
        mock_exists.return_value = True
        self.assertTrue(self.pm.check_vault_exists())

        mock_exists.return_value = False
        self.assertFalse(self.pm.check_vault_exists())

    def test_generate_password_default(self):
        # Test password generation with default parameters
        password = self.pm.generate_password()
        self.assertEqual(len(password), 16)
        # Should contain mix of characters
        self.assertTrue(any(c.isupper() for c in password))
        self.assertTrue(any(c.islower() for c in password))
        self.assertTrue(any(c.isdigit() for c in password))
        self.assertTrue(any(c in "!@#$%^&*" for c in password))

    def test_generate_password_custom(self):
        # Test password generation with custom parameters
        password = self.pm.generate_password(
            length=10,
            use_uppercase=False,
            use_lowercase=True,
            use_digits=False,
            use_special=False
        )
        self.assertEqual(len(password), 10)
        self.assertTrue(all(c.islower() for c in password))

    def test_generate_password_no_characters(self):
        # Test password generation with no character types selected
        password = self.pm.generate_password(
            use_uppercase=False,
            use_lowercase=False,
            use_digits=False,
            use_special=False
        )
        self.assertEqual(password, "")

    def test_check_password_strength_weak(self):
        # Test password strength checking - weak passwords
        self.assertEqual(self.pm.check_password_strength("123"), "Weak")
        self.assertEqual(self.pm.check_password_strength("password"), "Weak")

    def test_check_password_strength_medium(self):
        # Test password strength checking - medium passwords
        self.assertEqual(self.pm.check_password_strength("Password123"), "Medium")
        self.assertEqual(self.pm.check_password_strength("password123"), "Medium")

    def test_check_password_strength_strong(self):
        # Test password strength checking - strong passwords
        self.assertEqual(self.pm.check_password_strength("Password123!@#"), "Strong")
        self.assertEqual(self.pm.check_password_strength("VeryLongPassword123!@#"), "Strong")

    def test_setup_master_password_vault_exists(self):
        # Test setup_master_password when vault already exists
        self.pm.vault_exists = True
        result = self.pm.setup_master_password("testpassword")
        self.assertFalse(result['success'])
        self.assertIn('already exists', result['error'])

    def test_setup_master_password_short_password(self):
        # Test setup_master_password with short password
        self.pm.vault_exists = False
        result = self.pm.setup_master_password("12345")
        self.assertFalse(result['success'])
        self.assertIn('at least 6 characters', result['error'])

    @patch('Backend.password_manager.sqlite3')
    @patch('builtins.open', new_callable=mock_open)
    @patch('Backend.password_manager.Fernet')
    def test_setup_master_password_success(self, mock_fernet, mock_file, mock_sqlite):
        # Test setup_master_password success
        self.pm.vault_exists = False

        # Mock Fernet
        mock_key = b'test_key'
        mock_fernet.generate_key.return_value = mock_key

        # Mock sqlite
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_sqlite.connect.return_value = mock_conn

        result = self.pm.setup_master_password("testpassword123")

        self.assertTrue(result['success'])
        self.assertIn('created successfully', result['message'])
        self.assertTrue(self.pm.vault_exists)
        self.assertEqual(self.pm.key, mock_key)

        # Verify database operations
        mock_sqlite.connect.assert_called()
        mock_cursor.execute.assert_called()
        mock_conn.commit.assert_called()

        # Verify file operations
        mock_file.assert_called()

    def test_verify_master_password_no_vault(self):
        # Test verify_master_password when no vault exists
        self.pm.vault_exists = False
        result = self.pm.verify_master_password("password")
        self.assertFalse(result['success'])
        self.assertIn('No vault found', result['error'])

    @patch('Backend.password_manager.sqlite3')
    @patch('builtins.open', new_callable=mock_open, read_data=b'test_key')
    @patch('Backend.password_manager.Fernet')
    def test_verify_master_password_success(self, mock_fernet, mock_file, mock_sqlite):
        # Test verify_master_password success
        self.pm.vault_exists = True

        # Mock database
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        import hashlib
        correct_hash = hashlib.sha256("testpassword".encode()).hexdigest()
        mock_cursor.fetchone.return_value = (correct_hash,)
        mock_conn.cursor.return_value = mock_cursor
        mock_sqlite.connect.return_value = mock_conn

        result = self.pm.verify_master_password("testpassword")

        self.assertTrue(result['success'])
        self.assertIn('unlocked successfully', result['message'])
        self.assertTrue(self.pm.is_unlocked)

    def test_lock_vault(self):
        # Test lock_vault method
        # Set up unlocked state
        self.pm.is_unlocked = True
        self.pm.password_dict = {1: 'test'}
        self.pm.master_password_hash = 'hash'

        result = self.pm.lock_vault()

        self.assertTrue(result['success'])
        self.assertFalse(self.pm.is_unlocked)
        self.assertIsNone(self.pm.master_password_hash)
        self.assertEqual(self.pm.password_dict, {})

    def test_set_auto_lock_minutes_invalid(self):
        # Test set_auto_lock_minutes with invalid value
        result = self.pm.set_auto_lock_minutes(0)
        self.assertFalse(result['success'])
        self.assertIn('at least 1', result['error'])

    def test_set_auto_lock_minutes_valid(self):
        # Test set_auto_lock_minutes with valid value
        result = self.pm.set_auto_lock_minutes(10)
        self.assertTrue(result['success'])
        self.assertEqual(self.pm.auto_lock_minutes, 10)

    def test_get_vault_status(self):
        # Test get_vault_status method
        status = self.pm.get_vault_status()
        expected_keys = ['is_unlocked', 'passwords_count', 'database_exists', 'auto_lock_active', 'auto_lock_minutes']
        for key in expected_keys:
            self.assertIn(key, status)

    @patch('os.path.exists')
    @patch('os.remove')
    def test_reset_vault(self, mock_remove, mock_exists):
        # Test reset_vault method
        mock_exists.return_value = True

        # Set up state
        self.pm.is_unlocked = True
        self.pm.vault_exists = True
        self.pm.key = b'test_key'

        result = self.pm.reset_vault()

        self.assertTrue(result['success'])
        self.assertFalse(self.pm.is_unlocked)
        self.assertFalse(self.pm.vault_exists)
        self.assertIsNone(self.pm.key)

        # Verify files were removed
        self.assertEqual(mock_remove.call_count, 2)

if __name__ == '__main__':
    unittest.main()