#!/usr/bin/env python3
"""
Тестовый скрипт для проверки восстановления пароля
"""
import requests
import json

BASE_URL = "http://localhost:5000"

def test_password_reset():
    """Тестирование восстановления пароля"""

    print("=" * 60)
    print("Тест восстановления пароля")
    print("=" * 60)

    # Тест 1: Отправка запроса на восстановление
    print("\n1. Отправка запроса на восстановление пароля...")

    email = "partner@example.com"  # Тестовый email из init_db.py

    try:
        response = requests.post(
            f"{BASE_URL}/api/password-reset/request",
            json={"email": email},
            timeout=10
        )

        print(f"   Статус: {response.status_code}")
        print(f"   Ответ: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

        if response.status_code == 200:
            result = response.json()

            if 'reset_url' in result:
                print("\n✓ Получена ссылка для восстановления!")
                print(f"  Ссылка: {result['reset_url']}")

                # Извлекаем токен из ссылки
                token = result['reset_url'].split('token=')[-1]
                print(f"  Токен: {token}")

                # Тест 2: Проверка токена
                print("\n2. Проверка токена...")
                verify_response = requests.get(
                    f"{BASE_URL}/api/password-reset/verify/{token}",
                    timeout=10
                )

                print(f"   Статус: {verify_response.status_code}")
                print(f"   Ответ: {json.dumps(verify_response.json(), indent=2, ensure_ascii=False)}")

                if verify_response.status_code == 200:
                    print("\n✓ Токен валиден!")

                    # Тест 3: Сброс пароля
                    print("\n3. Сброс пароля...")
                    new_password = "newpassword123"

                    reset_response = requests.post(
                        f"{BASE_URL}/api/password-reset/confirm",
                        json={
                            "token": token,
                            "new_password": new_password
                        },
                        timeout=10
                    )

                    print(f"   Статус: {reset_response.status_code}")
                    print(f"   Ответ: {json.dumps(reset_response.json(), indent=2, ensure_ascii=False)}")

                    if reset_response.status_code == 200:
                        print("\n✓ Пароль успешно изменён!")
                        print(f"  Новый пароль: {new_password}")

                        # Тест 4: Вход с новым паролем
                        print("\n4. Проверка входа с новым паролем...")
                        login_response = requests.post(
                            f"{BASE_URL}/api/login",
                            json={
                                "email": email,
                                "password": new_password
                            },
                            timeout=10
                        )

                        print(f"   Статус: {login_response.status_code}")

                        if login_response.status_code == 200:
                            print("\n✓ Вход успешен с новым паролем!")
                            print("\n" + "=" * 60)
                            print("ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
                            print("=" * 60)
                        else:
                            print(f"\n✗ Не удалось войти: {login_response.json()}")
                    else:
                        print(f"\n✗ Не удалось сбросить пароль")
                else:
                    print(f"\n✗ Токен невалиден")
            else:
                print("\n✓ Email отправлен (проверьте почту)")
        else:
            print(f"\n✗ Ошибка: {response.json()}")

    except requests.exceptions.Timeout:
        print("\n✗ Timeout - сервер не отвечает")
    except requests.exceptions.ConnectionError:
        print(f"\n✗ Не удалось подключиться к {BASE_URL}")
        print("   Убедитесь что сервер запущен (python app.py)")
    except Exception as e:
        print(f"\n✗ Ошибка: {e}")


if __name__ == "__main__":
    test_password_reset()
