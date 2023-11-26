import unittest
import requests

class TestFlaskApi(unittest.TestCase):
    base_url = "http://127.0.0.1:5000"  
    def test_obtener_datos(self):
        response = requests.get(f"{self.base_url}/obtener_datos")
        self.assertEqual(response.status_code, 200)
      

if __name__ == '__main__':
    unittest.main()
