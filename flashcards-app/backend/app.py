import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

app = Flask(__name__)
CORS(app)  # Разрешаем CORS для Telegram Mini App

# API ключ хранится в переменной окружения - НЕ в коде!
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
ANTHROPIC_API_URL = 'https://api.anthropic.com/v1/messages'

@app.route('/health', methods=['GET'])
def health():
    """Проверка работоспособности сервера"""
    return jsonify({'status': 'ok', 'message': 'Server is running'})

@app.route('/api/generate', methods=['POST'])
def generate_flashcards():
    """
    Генерация флеш-карточек с помощью Claude API
    """
    try:
        if not ANTHROPIC_API_KEY:
            return jsonify({'error': 'API key not configured'}), 500

        data = request.get_json()

        # Валидация входных данных
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Отправка запроса к Claude API
        headers = {
            'Content-Type': 'application/json',
            'x-api-key': ANTHROPIC_API_KEY,
            'anthropic-version': '2023-06-01'
        }

        response = requests.post(
            ANTHROPIC_API_URL,
            headers=headers,
            json=data,
            timeout=30
        )

        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({
                'error': 'API request failed',
                'status_code': response.status_code,
                'message': response.text
            }), response.status_code

    except requests.exceptions.Timeout:
        return jsonify({'error': 'Request timeout'}), 504
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Request failed: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/translate', methods=['POST'])
def translate_word():
    """
    Перевод слова с помощью Claude API
    """
    try:
        if not ANTHROPIC_API_KEY:
            return jsonify({'error': 'API key not configured'}), 500

        data = request.get_json()

        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Отправка запроса к Claude API
        headers = {
            'Content-Type': 'application/json',
            'x-api-key': ANTHROPIC_API_KEY,
            'anthropic-version': '2023-06-01'
        }

        response = requests.post(
            ANTHROPIC_API_URL,
            headers=headers,
            json=data,
            timeout=15
        )

        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({
                'error': 'API request failed',
                'status_code': response.status_code,
                'message': response.text
            }), response.status_code

    except requests.exceptions.Timeout:
        return jsonify({'error': 'Request timeout'}), 504
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Request failed: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)
