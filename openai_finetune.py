import requests
import time
import os
from pathlib import Path

class OpenAIClient:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("API key is required")
        self.headers = {"Authorization": f"Bearer {self.api_key}"}
        self.base_url = "https://api.openai.com/v1"

    def upload_file(self, file_path):
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        with open(file_path, "rb") as file:
            response = requests.post(
                f"{self.base_url}/files",
                headers=self.headers,
                files={"file": (file_path.name, file, "application/jsonl")},
                data={"purpose": "fine-tune"}
            )
        return self._handle_response(response)

    def start_finetune(self, file_id, base_model="gpt-4-0613"):
        data = {"training_file": file_id, "model": base_model}
        response = requests.post(
            f"{self.base_url}/fine-tunes",
            headers=self.headers,
            json=data
        )
        return self._handle_response(response)

    def check_finetune_status(self, fine_tune_id, timeout=86400, check_interval=60):
        start_time = time.time()
        while time.time() - start_time < timeout:
            response = requests.get(
                f"{self.base_url}/fine-tunes/{fine_tune_id}",
                headers=self.headers
            )
            status_data = self._handle_response(response)
            status = status_data.get("status")
            
            if status == "succeeded":
                return "Fine-tuning completed successfully!"
            elif status == "failed":
                return "Fine-tuning failed!"
            
            time.sleep(check_interval)
        return "Fine-tuning process timed out."

    def _handle_response(self, response):
        try:
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            if response.status_code != 200:
                print(f"Response: {response.text}")
            return None

def get_user_input():
    api_key = input("Enter your OpenAI API key (or press Enter to use the environment variable): ").strip()
    if not api_key:
        api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("API key is required. Please provide it.")

    file_path = input("Enter the path to the dataset file (e.g., 'dataset.jsonl'): ").strip()
    if not file_path:
        raise ValueError("File path is required.")

    return api_key, file_path

def main():
    api_key, file_path = get_user_input()
    openai_client = OpenAIClient(api_key)

    try:
        file_id = openai_client.upload_file(file_path)
        if not file_id:
            print("File upload failed.")
            return
        
        fine_tune_id = openai_client.start_finetune(file_id)
        if not fine_tune_id:
            print("Fine-tune process failed to start.")
            return
        
        result = openai_client.check_finetune_status(fine_tune_id)
        print(result)

    except (ValueError, FileNotFoundError) as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
