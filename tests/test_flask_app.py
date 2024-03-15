import unittest
from flask import Flask
from blueprints.latest_image_v1_bp import latest_image_v1_bp


class TestLatestImageRoutes(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.register_blueprint(latest_image_v1_bp)
        self.client = self.app.test_client()

    def test_update_interval_route(self):
        response = self.client.post('/latestImageV1/updateInterval')
        self.assertEqual(response.status_code, 200)

    def test_start_route(self):
        response = self.client.post('/latestImageV1/start')
        self.assertEqual(response.status_code, 200)

    def test_stop_route(self):
        response = self.client.post('/latestImageV1/stop')
        self.assertEqual(response.status_code, 200)

    def test_status_route(self):
        response = self.client.post('/latestImageV1/status')
        self.assertEqual(response.status_code, 200)


class TestLatestImageInterface(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.client = self.app.test_client()

    def test_index_page_loads(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    unittest.main()
