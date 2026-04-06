import requests
import os
from typing import List

def get_synonyms(word: str) -> List[str]:
    """
    Lấy danh sách các từ đồng nghĩa (synonyms) của một từ tiếng Anh bất kỳ.
    
    Args:
        word (str): Từ tiếng Anh cần tìm từ đồng nghĩa.
        
    Returns:
        List[str]: Một danh sách chứa các từ đồng nghĩa. Trả về danh sách rỗng nếu không có kết quả hoặc gặp lỗi.
    """
    # Lấy API Key từ biến môi trường để bảo mật
    api_key = os.environ.get("API_NINJAS_KEY")
    
    if not api_key:
        print("Lỗi: Chưa cấu hình biến môi trường 'API_NINJAS_KEY'.")
        return []

    # Endpoint của API Ninjas Thesaurus
    api_url = f"https://api.api-ninjas.com/v1/thesaurus?word={word}"
    headers = {'X-Api-Key': api_key}

    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status() # Bắt các lỗi HTTP (như 401 Unauthorized, 404 Not Found)
        
        data = response.json()
        
        # API Ninjas trả về JSON dạng: {"word": "...", "synonyms": [...], "antonyms": [...]}
        synonyms = data.get("synonyms", [])
        return synonyms

    except requests.exceptions.RequestException as e:
        print(f"Đã xảy ra lỗi khi kết nối với API: {e}")
        return []

# --- Ví dụ cách sử dụng (Agent sẽ tự động gọi hàm này) ---
if __name__ == "__main__":
    # Thay 'YOUR_API_KEY' bằng key thật của bạn để test thử, 
    # nhưng thực tế nên set biến môi trường: export API_NINJAS_KEY="your_key"
    os.environ["API_NINJAS_KEY"] = "YOUR_API_KEY_HERE" 
    
    test_word = "happy"
    print(f"Các từ đồng nghĩa của '{test_word}':")
    print(get_synonyms(test_word))