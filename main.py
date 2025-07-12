from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

app = FastAPI(title="Система управління користувачами")

# Глобальний список для зберігання користувачів
users = []

# Модель для створення/редагування користувача
class UserCreate(BaseModel):
    login: str
    name: str
    surname: str
    birth_year: int

class UserUpdate(BaseModel):
    name: Optional[str] = None
    surname: Optional[str] = None
    birth_year: Optional[int] = None

# Функція для обчислення віку
def calculate_age(birth_year: int) -> int:
    current_year = datetime.now().year
    return current_year - birth_year

# Функція для пошуку користувача за логіном
def find_user_by_login(login: str):
    for user in users:
        if user["login"] == login:
            return user
    return None

@app.get("/", response_class=HTMLResponse)
def home():
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Система управління користувачами</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
            h1 { color: #333; text-align: center; }
            .nav { margin: 20px 0; }
            .nav a { display: inline-block; margin: 10px; padding: 10px 20px; background: #007bff; color: white; text-decoration: none; border-radius: 5px; }
            .nav a:hover { background: #0056b3; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🏠 Система управління користувачами</h1>
            <div class="nav">
                <a href="/user/get-all">📋 Всі користувачі</a>
                <a href="/user/add-form">➕ Додати користувача</a>
            </div>
            <p>Ласкаво просимо до системи управління користувачами! Використовуйте меню вище для навігації.</p>
            <p>Створено: 28.06.2025</p>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html)

@app.post("/user/add")
def add_user(user: UserCreate):
    # Перевірка на унікальність логіну
    if find_user_by_login(user.login):
        raise HTTPException(status_code=400, detail="Користувач з таким логіном вже існує")
    
    # Обчислення віку
    age = calculate_age(user.birth_year)
    
    # Створення нового користувача
    new_user = {
        "login": user.login,
        "name": user.name,
        "surname": user.surname,
        "age": age
    }
    
    users.append(new_user)
    return {"message": "Користувач успішно доданий", "user": new_user}

@app.get("/user/add-form", response_class=HTMLResponse)
def add_user_form():
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Додати користувача</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }
            .container { max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
            h1 { color: #333; text-align: center; }
            .form-group { margin: 15px 0; }
            label { display: block; margin-bottom: 5px; font-weight: bold; }
            input { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; box-sizing: border-box; }
            button { background: #28a745; color: white; padding: 12px 30px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; }
            button:hover { background: #218838; }
            .back-link { display: inline-block; margin-bottom: 20px; color: #007bff; text-decoration: none; }
            .back-link:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <div class="container">
            <a href="/" class="back-link">← Назад на головну</a>
            <h1>➕ Додати нового користувача</h1>
            <form id="userForm">
                <div class="form-group">
                    <label for="login">Логін:</label>
                    <input type="text" id="login" name="login" required>
                </div>
                <div class="form-group">
                    <label for="name">Ім'я:</label>
                    <input type="text" id="name" name="name" required>
                </div>
                <div class="form-group">
                    <label for="surname">Прізвище:</label>
                    <input type="text" id="surname" name="surname" required>
                </div>
                <div class="form-group">
                    <label for="birth_year">Рік народження:</label>
                    <input type="number" id="birth_year" name="birth_year" min="1900" max="2024" required>
                </div>
                <button type="submit">Додати користувача</button>
            </form>
        </div>
        <script>
            document.getElementById('userForm').onsubmit = async function(e) {
                e.preventDefault();
                const formData = new FormData(e.target);
                const userData = Object.fromEntries(formData);
                userData.birth_year = parseInt(userData.birth_year);
                
                try {
                    const response = await fetch('/user/add', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify(userData)
                    });
                    
                    if (response.ok) {
                        alert('Користувач успішно доданий!');
                        window.location.href = '/user/get-all';
                    } else {
                        const error = await response.json();
                        alert('Помилка: ' + error.detail);
                    }
                } catch (error) {
                    alert('Помилка мережі: ' + error.message);
                }
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html)

@app.put("/user/edit/{login}")
def edit_user(login: str, user_update: UserUpdate):
    user = find_user_by_login(login)
    if not user:
        raise HTTPException(status_code=404, detail="Користувача не знайдено")
    
    # Оновлення полів користувача
    if user_update.name is not None:
        user["name"] = user_update.name
    if user_update.surname is not None:
        user["surname"] = user_update.surname
    if user_update.birth_year is not None:
        user["age"] = calculate_age(user_update.birth_year)
    
    return {"message": "Інформація про користувача оновлена", "user": user}

@app.delete("/user/delete/{login}")
def delete_user(login: str):
    user = find_user_by_login(login)
    if not user:
        raise HTTPException(status_code=404, detail="Користувача не знайдено")
    
    users.remove(user)
    return {"message": f"Користувач {login} успішно видалений"}

@app.get("/user/get-all", response_class=HTMLResponse)
def get_all_users():
    if not users:
        users_list = "<p>📭 Список користувачів порожній</p>"
    else:
        users_list = """
        <table>
            <thead>
                <tr>
                    <th>Логін</th>
                    <th>Ім'я</th>
                    <th>Прізвище</th>
                    <th>Вік</th>
                    <th>Дії</th>
                </tr>
            </thead>
            <tbody>
        """
        for user in users:
            users_list += f"""
                <tr>
                    <td>{user['login']}</td>
                    <td>{user['name']}</td>
                    <td>{user['surname']}</td>
                    <td>{user['age']}</td>
                    <td>
                        <button onclick="editUser('{user['login']}')" class="edit-btn">✏️ Редагувати</button>
                        <button onclick="deleteUser('{user['login']}')" class="delete-btn">🗑️ Видалити</button>
                    </td>
                </tr>
            """
        users_list += "</tbody></table>"
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Всі користувачі</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }}
            .container {{ max-width: 1000px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }}
            h1 {{ color: #333; text-align: center; }}
            table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
            th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
            th {{ background-color: #f8f9fa; font-weight: bold; }}
            tr:hover {{ background-color: #f5f5f5; }}
            .edit-btn {{ background: #ffc107; color: black; border: none; padding: 5px 10px; border-radius: 3px; cursor: pointer; margin-right: 5px; }}
            .delete-btn {{ background: #dc3545; color: white; border: none; padding: 5px 10px; border-radius: 3px; cursor: pointer; }}
            .edit-btn:hover {{ background: #e0a800; }}
            .delete-btn:hover {{ background: #c82333; }}
            .back-link {{ display: inline-block; margin-bottom: 20px; color: #007bff; text-decoration: none; }}
            .back-link:hover {{ text-decoration: underline; }}
            .add-btn {{ background: #28a745; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; text-decoration: none; display: inline-block; margin-bottom: 20px; }}
            .add-btn:hover {{ background: #218838; }}
        </style>
    </head>
    <body>
        <div class="container">
            <a href="/" class="back-link">← Назад на головну</a>
            <h1>📋 Всі користувачі</h1>
            <a href="/user/add-form" class="add-btn">➕ Додати користувача</a>
            <a href="/user/get-all/json" class="add-btn" style="background: #17a2b8; margin-left: 10px;">📄 JSON дані</a>
            <button onclick="testAlert()" class="add-btn" style="background: #6f42c1; margin-left: 10px;">🧪 Тест JS</button>
            {users_list}
        </div>
        <script>
            console.log('JavaScript завантажено успішно');
            
            async function deleteUser(login) {{
                console.log('deleteUser викликано для:', login);
                if (confirm(`Ви впевнені, що хочете видалити користувача ${{login}}?`)) {{
                    try {{
                        console.log('Надсилання DELETE запиту...');
                        const response = await fetch(`/user/delete/${{login}}`, {{
                            method: 'DELETE'
                        }});
                        
                        console.log('Відповідь отримана:', response.status);
                        if (response.ok) {{
                            alert('Користувач успішно видалений!');
                            location.reload();
                        }} else {{
                            const error = await response.json();
                            console.error('Помилка сервера:', error);
                            alert('Помилка: ' + error.detail);
                        }}
                    }} catch (error) {{
                        console.error('Помилка мережі:', error);
                        alert('Помилка мережі: ' + error.message);
                    }}
                }}
            }}
            
            function editUser(login) {{
                console.log('editUser викликано для:', login);
                const newName = prompt('Введіть нове ім\\'я (залиште порожнім, щоб не змінювати):');
                const newSurname = prompt('Введіть нове прізвище (залиште порожнім, щоб не змінювати):');
                const newBirthYear = prompt('Введіть новий рік народження (залиште порожнім, щоб не змінювати):');
                
                const updateData = {{}};
                if (newName && newName.trim()) updateData.name = newName.trim();
                if (newSurname && newSurname.trim()) updateData.surname = newSurname.trim();
                if (newBirthYear && newBirthYear.trim()) updateData.birth_year = parseInt(newBirthYear.trim());
                
                console.log('Дані для оновлення:', updateData);
                
                if (Object.keys(updateData).length === 0) {{
                    alert('Нічого не змінено');
                    return;
                }}
                
                console.log('Надсилання PUT запиту...');
                fetch(`/user/edit/${{login}}`, {{
                    method: 'PUT',
                    headers: {{'Content-Type': 'application/json'}},
                    body: JSON.stringify(updateData)
                }})
                .then(response => {{
                    console.log('Відповідь PUT отримана:', response.status);
                    if (response.ok) {{
                        alert('Користувач успішно оновлений!');
                        location.reload();
                    }} else {{
                        return response.json().then(error => {{
                            console.error('Помилка PUT:', error);
                            throw new Error(error.detail);
                        }});
                    }}
                }})
                .catch(error => {{
                    console.error('Помилка PUT catch:', error);
                    alert('Помилка: ' + error.message);
                }});
            }}
            
            // Тестова функція для перевірки
            function testAlert() {{
                alert('JavaScript працює!');
            }}
            
            console.log('Функції визначено. deleteUser:', typeof deleteUser, 'editUser:', typeof editUser);
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html)

@app.get("/user/get-all/json")
def get_all_users_json():
    if not users:
        return {"message": "Список користувачів порожній", "users": []}
    return {"users": users}

@app.get("/user/{login}")
def get_user(login: str):
    user = find_user_by_login(login)
    if not user:
        raise HTTPException(status_code=404, detail="Користувача не знайдено")
    
    return user



if __name__ == "__main__":
    import uvicorn
    print("🚀 Запуск сервера на http://127.0.0.1:8001")
    print("📱 Відкрийте браузер і перейдіть за адресою: http://127.0.0.1:8001")
    uvicorn.run(app, host="127.0.0.1", port=8001)
