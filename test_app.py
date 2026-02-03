import unittest
from unittest.mock import patch, MagicMock
from main import app, is_logged_in
from datetime import datetime

class TestRestaurantApp(unittest.TestCase):
    
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
    
    def test_home_page_loads(self):
        """Test that home page returns 200 status"""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
    
    def test_menu_page_loads(self):
        """Test that menu page is accessible"""
        with patch('main.engine') as mock_engine:
            mock_conn = MagicMock()
            mock_engine.connect.return_value.__enter__.return_value = mock_conn
            mock_conn.execute.return_value = []
            
            response = self.app.get('/menu')
            self.assertEqual(response.status_code, 200)
    
    def test_order_page_requires_login(self):
        """Test that order page redirects if not logged in"""
        response = self.app.get('/order')
        self.assertEqual(response.status_code, 302)  # Redirect
    
    def test_api_menu_returns_json(self):
        """Test that API menu endpoint returns JSON"""
        with patch('main.engine') as mock_engine:
            mock_conn = MagicMock()
            mock_engine.connect.return_value.__enter__.return_value = mock_conn
            mock_result = MagicMock()
            mock_result._mapping = {
                'id': 1, 
                'name': 'Test Item', 
                'description': 'Test', 
                'price': 10.99, 
                'category': 'Main'
            }
            mock_conn.execute.return_value = [mock_result]
            
            response = self.app.get('/api/menu')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.content_type, 'application/json')
    
    def test_is_logged_in_helper_function(self):
        """Test the is_logged_in helper function"""
        with self.app.session_transaction() as sess:
            sess['user'] = {'email': 'test@example.com', 'name': 'Test User'}
        
        with self.app:
            self.app.get('/')
            self.assertTrue(is_logged_in())

if __name__ == '__main__':
    unittest.main()
