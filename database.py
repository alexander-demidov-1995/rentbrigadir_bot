"""
Модуль для работы с базой данных SQLite.
"""

import sqlite3
import csv
from data.config import DATABASE_PATH, CSV_FILE_PATH

class Database:
    """Класс для управления взаимодействием с базой данных SQLite."""
    
    def __init__(self, db_path=DATABASE_PATH):
        self.db_path = db_path
        self.conn = None
        self.cursor = None
    
    def connect(self):
        """Устанавливает подключение к базе данных и создает необходимые таблицы."""
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        # Включение поддержки внешних ключей
        self.cursor.execute("PRAGMA foreign_keys = ON")
        self.create_tables()

    def create_tables(self):
        """Создает все необходимые таблицы, если они еще не существуют."""
        
        # Таблица пользователей
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT,
                full_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Таблица категорий
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            )
        ''')
        
        # Таблица инструментов
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS tools (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                category_id INTEGER,
                price_1_day INTEGER,
                price_2_days INTEGER,
                price_3_days INTEGER,
                price_4_days INTEGER,
                price_5_days INTEGER,
                price_6_days INTEGER,
                price_7_days INTEGER,
                price_14_days INTEGER,
                price_30_days INTEGER,
                deposit INTEGER,
                image_url TEXT,
                available BOOLEAN DEFAULT TRUE
            )
        ''')
        
        # Таблица заявок
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                service_name TEXT,
                rental_period TEXT,
                application_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                customer_name TEXT,
                phone TEXT,
                status TEXT DEFAULT 'new'
            )
        ''')
        
        # Добавляем категории и инструменты
        self.add_categories()
        self.import_tools_from_csv()
        
        self.conn.commit()
        print("✅ База данных инициализирована")

    def add_categories(self):
        """Добавление категорий"""
        categories = [
            'Алмазное бурение',
            'Бензорезы',
            'Виброплиты',
            'Вышки туры',
            'Гвоздезабивные пистолеты',
            'Генераторы бензиновые',
            'Генераторы сварочные',
            'Генераторы дизельные',
            'Клининговое оборудование',
            'Компрессоры',
            'Лестницы',
            'Малярное оборудование',
            'Оборудование для бетона',
            'Подъемное оборудование',
            'Сантехнический инструмент'
        ]
        
        # Преобразуем в правильный формат
        categories_data = [(name,) for name in categories]

        self.cursor.executemany('''
            INSERT OR IGNORE INTO categories (name) VALUES (?)
        ''', categories_data)
        self.conn.commit()
        print(f"✅ Добавлено {len(categories)} категорий")

    def import_tools_from_csv(self, csv_file_path='tools.csv'):
        """Импорт инструментов из CSV файла"""
        try:
            with open(csv_file_path, 'r', encoding='utf-8') as file:
                csv_reader = csv.DictReader(file)
                tools = []
                
                for row in csv_reader:
                    tools.append((
                        row['name'],
                        row['description'],
                        int(row['category_id']),
                        int(row['price_1_day']),
                        int(row['price_2_days']),
                        int(row['price_3_days']),
                        int(row['price_4_days']),
                        int(row['price_5_days']),
                        int(row['price_6_days']),
                        int(row['price_7_days']),
                        int(row['price_14_days']),
                        int(row['price_30_days']),
                        int(row['deposit']),
                        row.get('image_url', '')
                    ))
                
                # Очищаем и заполняем таблицу
                self.cursor.execute("DELETE FROM tools")
                self.cursor.executemany('''
                    INSERT INTO tools 
                    (name, description, category_id, price_1_day, price_2_days, price_3_days, price_4_days, 
                     price_5_days, price_6_days, price_7_days, price_14_days, price_30_days, deposit, image_url)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', tools)
                
                self.conn.commit()
                print(f"✅ Загружено {len(tools)} инструментов из tools.csv")
                
        except FileNotFoundError:
            print("❌ Файл tools.csv не найден. Создайте файл с инструментами.")
        except Exception as e:
            print(f"❌ Ошибка загрузки инструментов: {e}")

    

    def add_user(self, user_id, username, full_name):
        """Добавление пользователя"""
        self.cursor.execute('''
            INSERT OR IGNORE INTO users (id, username, full_name) 
            VALUES (?, ?, ?)
        ''', (user_id, username, full_name))
        self.conn.commit()

    def add_application(self, user_id, service_name, customer_name, phone, rental_period="не указан"):
        """Добавление заявки в базу"""
        self.cursor.execute('''
            INSERT INTO applications (user_id, service_name, customer_name, phone, rental_period)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, service_name, customer_name, phone, rental_period))
        self.conn.commit()
        return self.cursor.lastrowid

    def get_all_categories(self):
        """Получить все категории"""
        self.cursor.execute("SELECT * FROM categories ORDER BY name")
        return self.cursor.fetchall()

    def get_tools_by_category(self, category_id):
        """Получить инструменты по категории"""
        self.cursor.execute('''
            SELECT * FROM tools 
            WHERE category_id = ? AND available = TRUE 
            ORDER BY price_1_day
        ''', (category_id,))
        return self.cursor.fetchall()

    def get_category_by_id(self, category_id):
        """Получить категорию по ID"""
        self.cursor.execute("SELECT * FROM categories WHERE id = ?", (category_id,))
        return self.cursor.fetchone()

    def get_tool_by_id(self, tool_id):
        """Получить инструмент по ID"""
        self.cursor.execute("SELECT * FROM tools WHERE id = ?", (tool_id,))
        return self.cursor.fetchone()
    
    def get_new_applications(self):
        """Получить новые заявки"""
        self.cursor.execute('''
            SELECT a.*, u.username, u.full_name as user_full_name 
            FROM applications a 
            LEFT JOIN users u ON a.user_id = u.id 
            WHERE a.status = 'new' 
            ORDER BY a.application_date DESC
        ''')
        return self.cursor.fetchall()

    def mark_application_processed(self, application_id):
        """Пометить заявку как обработанную"""
        self.cursor.execute('''
            UPDATE applications SET status = 'processed' WHERE id = ?
        ''', (application_id,))
        self.conn.commit()

    def get_application_by_id(self, application_id):
        """Получить заявку по ID"""
        self.cursor.execute('''
            SELECT a.*, u.username, u.full_name as user_full_name 
            FROM applications a 
            LEFT JOIN users u ON a.user_id = u.id 
            WHERE a.id = ?
        ''', (application_id,))
        return self.cursor.fetchone()

# Создаем глобальный экземпляр БД
db = Database()