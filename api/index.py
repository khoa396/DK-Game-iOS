from flask import Flask, render_template, jsonify, request
import requests
from bs4 import BeautifulSoup

app = Flask(__name__, template_folder='../templates', static_folder='../static')

# ================= CẤU HÌNH API & DATA =================
API_TOKEN = "67fe08df2741353b9475dd73"  # Token của bạn
LINK4M_API = "https://link4m.co/api-shorten/v2"

# Danh sách game (Database giả lập)
# Bạn thêm game mới vào đây. 
# 'source_url': là link gốc TruongMods mà game đó cần lấy key.
GAMES = [
    {
        "id": "lien_quan",
        "name": "Liên Quân",
        "image": "lq.jpg", # Tên file trong thư mục static/images
        "desc": "làm bố thiên hạ",
        "download_link": "https://www.mediafire.com/file/fdm8d4ylklz0hyp/TruongMod_1.61.11572693_1769095705.ipa/file",
        "source_url": "https://ios.truongmods.net/lay-link.php?id=4&user=Truongmod&zarsrc=410&utm_source=zalo&utm_medium=zalo&utm_campaign=zalo"
    },
    {
        "id": "blox_fruit",
        "name": "Roblox - Blox Fruit",
        "image": "blox.jpg",
        "desc": "Auto Farm, Auto Raid, Fruit Finder",
        "download_link": "https://example.com/download-roblox",
        "source_url": "https://ios.truongmods.net/lay-link.php?id=4&user=Truongmod&zarsrc=410&utm_source=zalo&utm_medium=zalo&utm_campaign=zalo"
    }
]

# ================= HÀM XỬ LÝ LOGIC (PRIVATE) =================
def process_get_key(source_url):
    try:
        # Bước 1: Lấy link gốc từ web nguồn
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(source_url, headers=headers)
        if res.status_code != 200: return None
        
        soup = BeautifulSoup(res.text, 'html.parser')
        link_element = soup.find('b', class_='link-value')
        
        if not link_element: return None
        
        original_link = link_element.text.strip()
        
        # Bước 2: Chèn ký tự '---'
        modified_link = original_link.replace("link4m", "link---4m")
        
        # Bước 3: Rút gọn qua API Link4m
        params = {'api': API_TOKEN, 'url': modified_link}
        api_res = requests.get(LINK4M_API, params=params)
        data = api_res.json()
        
        if data.get('status') == 'success':
            return data.get('shortenedUrl').replace('\\', '')
        return None
        
    except Exception as e:
        print(f"Error: {e}")
        return None

# ================= ROUTES (ĐƯỜNG DẪN) =================

@app.route('/')
def home():
    # Hiển thị giao diện trang chủ
    return render_template('index.html', games=GAMES)

@app.route('/api/get-key/<game_id>', methods=['POST'])
def get_key_api(game_id):
    # API này nhận yêu cầu từ nút bấm của người dùng
    game = next((g for g in GAMES if g["id"] == game_id), None)
    
    if not game:
        return jsonify({"success": False, "message": "Game không tồn tại"}), 404

    # Gọi hàm xử lý logic phía trên
    final_link = process_get_key(game['source_url'])
    
    if final_link:
        return jsonify({"success": True, "url": final_link})
    else:
        return jsonify({"success": False, "message": "Không thể lấy Key lúc này. Thử lại sau!"}), 500

# Dành cho môi trường dev local
if __name__ == '__main__':
    app.run(debug=True)