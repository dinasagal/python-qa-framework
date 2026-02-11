import os
import requests
import allure

from dotenv import load_dotenv


load_dotenv()


class APIClient:
    def __init__(self, base_url):
        self.base_url = base_url
        self.token = os.getenv("GOREST_TOKEN")

        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

    def get(self, endpoint):
        response = requests.get(
            f"{self.base_url}{endpoint}",
            headers=self.headers
        )
        allure.attach(
        response.text,
        name="Response body",
        attachment_type=allure.attachment_type.JSON
        )

        return response

    def post(self, endpoint, payload):
        response = requests.post(
            f"{self.base_url}{endpoint}",
            json=payload,
            headers=self.headers
        )
        allure.attach(
            response.text,
            name="Response body",
            attachment_type=allure.attachment_type.JSON
        )

        return response
        

    def delete(self, endpoint):
        response = requests.delete(
            f"{self.base_url}{endpoint}",
            headers=self.headers
        )
        allure.attach(
            response.text,
            name="Response body",
            attachment_type=allure.attachment_type.JSON
        )

        return response
        
