import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

# --- КОНФИГУРАЦИЯ ---
DATA_FILE = 'books.json'

# --- 1. МОДЕЛЬ ДАННЫХ (КЛАСС УПРАВЛЕНИЯ) ---
class BookManager:
    """Отвечает за загрузку, сохранение и фильтрацию данных о книгах."""
    def __init__(self, filename):
        self.filename = filename
        self.books = self.load_books()

    def load_books(self):
        """Загружает данные из JSON. Если файла нет, возвращает пустой список."""
        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def save_books(self):
        """Сохраняет текущий список книг в JSON."""
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(self.books, f, ensure_ascii=False, indent=2)

    def add_book(self, title, author, genre, pages):
        """Добавляет новую книгу в список и сохраняет файл."""
        self.books.append({
            "title": title,
            "author": author,
            "genre": genre,
            "pages": pages
        })
        self.save_books()

    def filter_books(self, genre_filter="", min_pages=None):
        """
        Фильтрует книги по жанру и/или количеству страниц.
        genre_filter: строка для поиска в названии жанра (без учета регистра).
        min_pages: число. Показывать книги, где страниц >= min_pages.
        """
        filtered = self.books.copy()
        
        # Фильтр по жанру
        if genre_filter:
            filtered = [b for b in filtered if genre_filter.lower() in b['genre'].lower()]
        
        # Фильтр по количеству страниц
        if min_pages is not None:
            try:
                min_pages = int(min_pages)
                filtered = [b for b in filtered if b['pages'] >= min_pages]
            except ValueError:
                pass # Если введено не число, просто игнорируем этот фильтр
        
        return filtered

# --- 2. ГРАФИЧЕСКИЙ ИНТЕРФЕЙС (КЛАСС ПРИЛОЖЕНИЯ) ---
class BookTrackerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Book Tracker")
        self.geometry("900x600")
        
        self.manager = BookManager(DATA_FILE)
        
        self.create_widgets()

    def create_widgets(self):
        # --- РАМКА ДЛЯ ДОБАВЛЕНИЯ КНИГИ ---
        add_frame = ttk.LabelFrame(self, text="Добавить новую книгу", padding="10")
        add_frame.pack(fill='x', padx=10, pady=5)

        # Название
        ttk.Label(add_frame, text="Название:").grid(row=0, column=0, sticky='w')
        self.title_entry = ttk.Entry(add_frame)
        self.title_entry.grid(row=0, column=1, sticky='ew', padx=5)

        # Автор
        ttk.Label(add_frame, text="Автор:").grid(row=1, column=0, sticky='w')
        self.author_entry = ttk.Entry(add_frame)
        self.author_entry.grid(row=1, column=1, sticky='ew', padx=5)

        # Жанр
        ttk.Label(add_frame, text="Жанр:").grid(row=2, column=0, sticky='w')
        self.genre_entry = ttk.Entry(add_frame)
        self.genre_entry.grid(row=2, column=1, sticky='ew', padx=5)

         # Количество страниц
         ttk.Label(add_frame, text="Страниц:").grid(row=3, column=0, sticky='w')
         self.pages_entry = ttk.Entry(add_frame)
         self.pages_entry.grid(row=3, column=1, sticky='ew', padx=5)
         
         # Кнопка действия
         ttk.Button(add_frame, text="Добавить книгу", command=self.add_book).grid(
             row=4, column=0, columnspan=2, pady=10)
         
         # --- РАМКА ДЛЯ ФИЛЬТРАЦИИ ---
         filter_frame = ttk.LabelFrame(self, text="Фильтрация", padding="10")
         filter_frame.pack(fill='x', padx=10, pady=5)
         
         # Фильтр по жанру
         ttk.Label(filter_frame, text="Жанр:").grid(row=0, column=0)
         self.filter_genre_var = tk.StringVar()
         ttk.Entry(filter_frame, textvariable=self.filter_genre_var).grid(row=0, column=1)
         
         # Фильтр по страницам (больше чем...)
         ttk.Label(filter_frame, text="Страниц >").grid(row=1, column=0)
         self.filter_pages_var = tk.StringVar()
         ttk.Entry(filter_frame, textvariable=self.filter_pages_var).grid(row=1, column=1)
         
         # Кнопка применения фильтра
         ttk.Button(filter_frame, text="Применить фильтр", command=self.apply_filter).grid(
             row=2, column=0, columnspan=2)

         # --- ТАБЛИЦА ДЛЯ ОТОБРАЖЕНИЯ КНИГ ---
         columns = ("title", "author", "genre", "pages")
         self.tree = ttk.Treeview(self, columns=columns, show="headings")
         
         for col in columns:
             self.tree.heading(col, text={"title": "Название", "author": "Автор", "genre": "Жанр", "pages": "Страниц"}[col])
             self.tree.column(col, minwidth=0, width=200)
             
         self.tree.pack(fill='both', expand=True)

    # --- 3. ЛОГИКА ОБРАБОТКИ СОБЫТИЙ ---
    def add_book(self):
       """Обрабатывает добавление книги с проверкой ввода."""
       title = self.title_entry.get()
       author = self.author_entry.get()
       genre = self.genre_entry.get()
       pages_str = self.pages_entry.get()
       
       # Валидация: проверка на пустые поля
       if not title or not author or not genre or not pages_str:
           messagebox.showerror("Ошибка", "Все поля должны быть заполнены.")
           return

       # Валидация: количество страниц должно быть целым числом > 0
       try:
           pages = int(pages_str)
           if pages <= 0:
               raise ValueError("Количество страниц должно быть больше нуля.")
       except ValueError as e:
           messagebox.showerror("Ошибка", f"Неверный формат страниц: {e}")
           return

       # Если все проверки пройдены - добавляем запись
       self.manager.add_book(title.strip(), author.strip(), genre.strip(), pages)
       
       # Очистка полей ввода и обновление таблицы
       self.title_entry.delete(0, 'end')
       self.author_entry.delete(0, 'end')
       self.genre_entry.delete(0, 'end')
       self.pages_entry.delete(0, 'end')
       
       messagebox.showinfo("Успех", "Книга успешно добавлена!")
       
    def apply_filter(self):
       """Обрабатывает нажатие кнопки фильтрации."""
       genre_filter = self.filter_genre_var.get()
       min_pages_str = self.filter_pages_var.get()
       
       min_pages = int(min_pages_str) if min_pages_str.isdigit() else None

       # Очищаем таблицу перед обновлением
       for i in self.tree.get_children():
           self.tree.delete(i)
           
      filtered_data = self.manager.filter_books(genre_filter.strip(), min_pages)
      
      for item in filtered_data:
          self.tree.insert("", "end", values=(item['title'], item['author'], item['genre'], item['pages']))
          
# --- 4. ЗАПУСК ПРИЛОЖЕНИЯ ---
if __name__ == "__main__":
    app = BookTrackerApp()
    app.mainloop()
