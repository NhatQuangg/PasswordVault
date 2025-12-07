import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from Backend.vault_api import (
    initialize_vault, get_vault_instance, setup_master_password,
    verify_master_password, lock_vault, get_all_passwords, add_password,
    update_password, delete_password, get_password, generate_password,
    get_password_suggestions, check_password_strength, set_auto_lock_minutes,
    get_auto_lock_status, register_activity, get_vault_status,
    export_backup, reset_vault, change_master_password,
    get_password_count, generate_strong_password, check_strength,
    format_password_for_display, prepare_password_list, get_session_info
)

class TestVaultAPI(unittest.TestCase):
    def setUp(self):
        # Set up test fixtures
        # Reset global instance
        import Backend.vault_api as vault_api
        vault_api._vault_instance = None

    @patch('Backend.vault_api.PasswordManager')
    def test_initialize_vault(self, mock_pm_class):
        # Test initialize_vault function
        mock_instance = MagicMock()
        mock_pm_class.return_value = mock_instance

        result = initialize_vault()

        mock_pm_class.assert_called_once()
        self.assertEqual(result, mock_instance)

    @patch('Backend.vault_api.PasswordManager')
    def test_get_vault_instance_new(self, mock_pm_class):
        # Test get_vault_instance when no instance exists
        mock_instance = MagicMock()
        mock_pm_class.return_value = mock_instance

        result = get_vault_instance()

        mock_pm_class.assert_called_once()
        self.assertEqual(result, mock_instance)

    @patch('Backend.vault_api._vault_instance')
    def test_get_vault_instance_existing(self, mock_instance):
        # Test get_vault_instance when instance already exists
        mock_instance = MagicMock()
        import Backend.vault_api as vault_api
        vault_api._vault_instance = mock_instance

        result = get_vault_instance()

        self.assertEqual(result, mock_instance)

    @patch('Backend.vault_api.get_vault_instance')
    def test_setup_master_password(self, mock_get_instance):
        # Test setup_master_password API
        mock_instance = MagicMock()
        mock_instance.setup_master_password.return_value = {'success': True}
        mock_get_instance.return_value = mock_instance

        result = setup_master_password("testpass")

        mock_instance.setup_master_password.assert_called_once_with("testpass")
        self.assertEqual(result, {'success': True})

    @patch('Backend.vault_api.get_vault_instance')
    def test_verify_master_password(self, mock_get_instance):
        # Test verify_master_password API
        mock_instance = MagicMock()
        mock_instance.verify_master_password.return_value = {'success': True}
        mock_get_instance.return_value = mock_instance

        result = verify_master_password("testpass")

        mock_instance.verify_master_password.assert_called_once_with("testpass")
        self.assertEqual(result, {'success': True})

    @patch('Backend.vault_api.get_vault_instance')
    def test_lock_vault(self, mock_get_instance):
        # Test lock_vault API
        mock_instance = MagicMock()
        mock_instance.lock_vault.return_value = {'success': True}
        mock_get_instance.return_value = mock_instance

        result = lock_vault()

        mock_instance.lock_vault.assert_called_once()
        self.assertEqual(result, {'success': True})

    @patch('Backend.vault_api.get_vault_instance')
    def test_get_all_passwords(self, mock_get_instance):
        # Test get_all_passwords API
        mock_instance = MagicMock()
        mock_instance.get_all_passwords.return_value = {'success': True, 'passwords': []}
        mock_get_instance.return_value = mock_instance

        result = get_all_passwords()

        mock_instance.get_all_passwords.assert_called_once()
        self.assertEqual(result, {'success': True, 'passwords': []})

    @patch('Backend.vault_api.get_vault_instance')
    def test_add_password(self, mock_get_instance):
        # Test add_password API
        mock_instance = MagicMock()
        mock_instance.add_password_to_db.return_value = {'success': True, 'id': 1}
        mock_get_instance.return_value = mock_instance

        result = add_password("service", "user", "pass", "notes")

        mock_instance.add_password_to_db.assert_called_once_with("service", "user", "pass", "notes")
        self.assertEqual(result, {'success': True, 'id': 1})

    @patch('Backend.vault_api.get_vault_instance')
    def test_update_password(self, mock_get_instance):
        # Test update_password API
        mock_instance = MagicMock()
        mock_instance.update_password_to_db.return_value = {'success': True}
        mock_get_instance.return_value = mock_instance

        result = update_password(1, "service", "user", "pass", "notes")

        mock_instance.update_password_to_db.assert_called_once_with(1, "service", "user", "pass", "notes")
        self.assertEqual(result, {'success': True})

    @patch('Backend.vault_api.get_vault_instance')
    def test_delete_password(self, mock_get_instance):
        # Test delete_password API
        mock_instance = MagicMock()
        mock_instance.delete_password_from_db.return_value = {'success': True}
        mock_get_instance.return_value = mock_instance

        result = delete_password(1)

        mock_instance.delete_password_from_db.assert_called_once_with(1)
        self.assertEqual(result, {'success': True})

    @patch('Backend.vault_api.get_vault_instance')
    def test_get_password(self, mock_get_instance):
        # Test get_password API
        mock_instance = MagicMock()
        mock_instance.get_password_from_db.return_value = {'success': True, 'password': {}}
        mock_get_instance.return_value = mock_instance

        result = get_password(1)

        mock_instance.get_password_from_db.assert_called_once_with(1)
        self.assertEqual(result, {'success': True, 'password': {}})

    @patch('Backend.vault_api.get_vault_instance')
    def test_generate_password(self, mock_get_instance):
        # Test generate_password API
        mock_instance = MagicMock()
        mock_instance.generate_password.return_value = "generated_pass"
        mock_get_instance.return_value = mock_instance

        result = generate_password(length=12)

        mock_instance.generate_password.assert_called_once_with(length=12)
        self.assertEqual(result, {'success': True, 'password': 'generated_pass'})

    def test_get_password_suggestions(self):
        # Test get_password_suggestions API
        result = get_password_suggestions()

        self.assertTrue(result['success'])
        self.assertIn('suggestions', result)
        self.assertIsInstance(result['suggestions'], list)
        self.assertGreater(len(result['suggestions']), 0)

    @patch('Backend.vault_api.get_vault_instance')
    def test_check_password_strength(self, mock_get_instance):
        # Test check_password_strength API
        mock_instance = MagicMock()
        mock_instance.check_password_strength.return_value = "Strong"
        mock_get_instance.return_value = mock_instance

        result = check_password_strength("password123!")

        mock_instance.check_password_strength.assert_called_once_with("password123!")
        self.assertEqual(result['success'], True)
        self.assertEqual(result['strength'], "Strong")
        self.assertIn('color', result)

    @patch('Backend.vault_api.get_vault_instance')
    def test_set_auto_lock_minutes(self, mock_get_instance):
        # Test set_auto_lock_minutes API
        mock_instance = MagicMock()
        mock_instance.set_auto_lock_minutes.return_value = {'success': True}
        mock_get_instance.return_value = mock_instance

        result = set_auto_lock_minutes(10)

        mock_instance.set_auto_lock_minutes.assert_called_once_with(10)
        self.assertEqual(result, {'success': True})

    @patch('Backend.vault_api.get_vault_instance')
    def test_get_auto_lock_status(self, mock_get_instance):
        # Test get_auto_lock_status API
        mock_instance = MagicMock()
        mock_instance.get_auto_lock_status.return_value = {'active': True}
        mock_get_instance.return_value = mock_instance

        result = get_auto_lock_status()

        mock_instance.get_auto_lock_status.assert_called_once()
        self.assertEqual(result, {'active': True})

    @patch('Backend.vault_api.get_vault_instance')
    def test_register_activity(self, mock_get_instance):
        # Test register_activity API
        mock_instance = MagicMock()
        mock_instance.register_activity.return_value = {'success': True}
        mock_get_instance.return_value = mock_instance

        result = register_activity()

        mock_instance.register_activity.assert_called_once()
        self.assertEqual(result, {'success': True})

    @patch('Backend.vault_api.get_vault_instance')
    def test_get_vault_status(self, mock_get_instance):
        # Test get_vault_status API
        mock_instance = MagicMock()
        mock_instance.get_vault_status.return_value = {'is_unlocked': False}
        mock_get_instance.return_value = mock_instance

        result = get_vault_status()

        mock_instance.get_vault_status.assert_called_once()
        self.assertEqual(result, {'is_unlocked': False})

    @patch('Backend.vault_api.get_vault_instance')
    def test_export_backup(self, mock_get_instance):
        # Test export_backup API
        mock_instance = MagicMock()
        mock_instance.export_backup.return_value = {'success': True}
        mock_get_instance.return_value = mock_instance

        result = export_backup("/path/to/backup")

        mock_instance.export_backup.assert_called_once_with("/path/to/backup")
        self.assertEqual(result, {'success': True})

    @patch('Backend.vault_api.get_vault_instance')
    def test_reset_vault(self, mock_get_instance):
        # Test reset_vault API
        mock_instance = MagicMock()
        mock_instance.reset_vault.return_value = {'success': True}
        mock_get_instance.return_value = mock_instance

        result = reset_vault()

        mock_instance.reset_vault.assert_called_once()
        self.assertEqual(result, {'success': True})

    @patch('Backend.vault_api.get_vault_instance')
    def test_change_master_password(self, mock_get_instance):
        # Test change_master_password API
        mock_instance = MagicMock()
        mock_instance.change_master_password.return_value = {'success': True}
        mock_get_instance.return_value = mock_instance

        result = change_master_password("oldpass", "newpass")

        mock_instance.change_master_password.assert_called_once_with("oldpass", "newpass")
        self.assertEqual(result, {'success': True})

    @patch('Backend.vault_api.get_vault_instance')
    def test_generate_strong_password(self, mock_get_instance):
        # Test generate_strong_password API
        mock_instance = MagicMock()
        mock_instance.generate_password.return_value = "StrongPass123!"
        mock_get_instance.return_value = mock_instance

        result = generate_strong_password()

        mock_instance.generate_password.assert_called_once_with(
            length=16,
            use_lowercase=True,
            use_uppercase=True,
            use_digits=True,
            use_special=True
        )
        self.assertEqual(result, "StrongPass123!")

    def test_format_password_for_display(self):
        # Test format_password_for_display function
        password_data = {
            'id': 1,
            'service': 'test',
            'username': 'test user',
            'password': 'test pass',
            'strength': 'Strong',
            'notes': '',
            'last_updated': '2026-01-01',
            'created_at': '2026-01-01'
        }

        result = format_password_for_display(password_data)

        self.assertEqual(result['id'], 1)
        self.assertEqual(result['service'], 'test')
        self.assertEqual(result['username'], 'test user')
        self.assertEqual(result['password'], 'test pass')
        self.assertEqual(result['strength'], 'Strong')

    def test_format_password_for_display_none(self):
        # Test format_password_for_display with None input
        result = format_password_for_display(None)
        self.assertIsNone(result)

    def test_prepare_password_list(self):
        # Test prepare_password_list function
        passwords_result = {
            'success': True,
            'passwords': [
                {'id': 1, 'service': 'Service1'},
                {'id': 2, 'service': 'Service2'}
            ]
        }

        result = prepare_password_list(passwords_result)

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['id'], 1)
        self.assertEqual(result[1]['id'], 2)

    def test_prepare_password_list_failure(self):
        # Test prepare_password_list with failed result
        passwords_result = {'success': False}

        result = prepare_password_list(passwords_result)

        self.assertEqual(result, [])

    @patch('Backend.vault_api.get_vault_status')
    @patch('Backend.vault_api.get_auto_lock_status')
    def test_get_session_info(self, mock_auto_lock, mock_status):
        # Test get_session_info function
        mock_status.return_value = {
            'is_unlocked': True,
            'passwords_count': 5
        }
        mock_auto_lock.return_value = {
            'active': True,
            'lock_minutes': 10,
            'formatted_time': '5:00'
        }

        result = get_session_info()

        self.assertEqual(result['vault_unlocked'], True)
        self.assertEqual(result['password_count'], 5)
        self.assertEqual(result['auto_lock_active'], True)
        self.assertEqual(result['auto_lock_minutes'], 10)
        self.assertEqual(result['time_remaining'], '5:00')

if __name__ == '__main__':
    unittest.main()