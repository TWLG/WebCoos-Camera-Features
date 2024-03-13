import unittest
import flask_app
from unittest.mock import patch


class TestFlaskApp(unittest.TestCase):

    @patch('flask_app.requests.get')
    def test_check_key(self, mock_get):
        # Mocking the response from requests.get
        mock_get.return_value.status_code = 200

        # Call the function
        result = flask_app.check_key()

        # Assert that the function returned 'Valid API key.'
        self.assertEqual(result, 'Valid API key.')

    @patch('flask_app.predict_image')
    def test_run_filter_model(self, mock_predict_image):
        # Mocking the response from predict_image
        mock_predict_image.return_value = 'Mocked result'

        # Call the function
        flask_app.run_filter_model()

        # Assert that predict_image was called with the correct argument
        mock_predict_image.assert_called_once_with(flask_app.API_KEY)


if __name__ == '__main__':
    unittest.main()
