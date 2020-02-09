import unittest
import requests
import json
import sys

from flask import Flask, request, jsonify
from flask_cors import CORS

from main import app


class TestFlaskApi(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()

    def test_service(self):
        response = self.app.get('/')
        self.assertEqual(
            json.loads(response.get_data().decode(sys.getdefaultencoding())),
            {'message': 'ok'}
        )


if __name__ == "__main__":
    unittest.main()
