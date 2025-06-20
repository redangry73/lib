
## 1. Цель работы

Изучить основы работы с ORM SQLAlchemy в языковой среде Python и реализовать простую систему учета пользователей, книг и бронирований. Разработать функции для создания пользователей, книг, оформления и удаления бронирований, а также обеспечить обработку ошибок и написать модульные тесты.

## 2. Задачи

1. Настроить подключение к базе данных PostgreSQL через SQLAlchemy.
2. Описать модели `user`, `book` и `booking` с необходимыми полями и связями.
3. Реализовать функции:
   - `create_user(name, email)` — создание пользователя с обработкой ошибок уникальности.
   - `create_book(title, author, copies_available)` — добавление книги или увеличение числа копий.
   - `create_booking(email, author, title)` — оформление бронирования.
   - `delete_booking(email, author, title)` — удаление бронирования.
4. Написать модульные тесты на все функции с использованием `unittest`.
5. Оформить отчет о проделанной работе.

## 3. Средства разработки

- Язык: Python 3.10
- ORM: SQLAlchemy 2.x
- База данных: PostgreSQL 14
- Тестирование: модуль `unittest`

## 4. Описание решения

### 4.1. Настройка подключения и базовый класс

```python
DATABASE_URL = "postgresql+psycopg2://postgres:1234@localhost:5432/library"
engine = create_engine(DATABASE_URL)
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
```

- **engine** — движок SQLAlchemy для подключения.
- **Base** — декларативный базовый класс для моделей.
- **SessionLocal** — фабрика сессий без автокоммита.

### 4.2. Модели данных

1. **User**
   ```python
   class user(Base):
       __tablename__ = 'user'
       id = mapped_column(primary_key=True)
       name = mapped_column(nullable=False)
       email = mapped_column(nullable=False, unique=True)
   ```
2. **Book**
   ```python
   class book(Base):
       __tablename__ = 'book'
       id = mapped_column(primary_key=True)
       title = mapped_column(nullable=False)
       author = mapped_column(nullable=False)
       copies_available = mapped_column()
   ```
3. **Booking**
   ```python
   class booking(Base):
       __tablename__ = 'booking'
       id = mapped_column(primary_key=True)
       user_id = mapped_column(ForeignKey('user.id'), nullable=False)
       book_id = mapped_column(ForeignKey('book.id'), nullable=False)
       booking_date = mapped_column(DateTime(timezone=True), server_default=func.now())
   ```

### 4.3. Реализация функций

- **create_user(name, email)**
  - Добавляет пользователя.
  - Обрабатывает `IntegrityError` для дубликатов и FK-ограничений.
- **create_book(title, author, copies_available)**
  - Если книга существует — увеличивает `copies_available`, иначе создаёт новую запись.
- **create_booking(email, author, title)**
  - Проверяет существование пользователя и книги.
  - Оформляет бронирование, уменьшает число копий.
  - Возвращает объект `response(status, INFO)`.
- **delete_booking(email, author, title)**
  - Находит старейшее бронирование по дате.
  - Удаляет запись и восстанавливает копию книги.

### 4.4. Модульные тесты

- Написаны тесты с `unittest` для всех функций. Примеры сценариев:
  - Успешное создание пользователя и дублирование email.
  - Добавление новой книги и увеличение копий.
  - Бронирование при отсутствии пользователя, книги или копий.
  - Удаление несуществующего бронирования.

## 5. Результаты тестирования

Все тесты прошли успешно:

```
$ python -m unittest test_lib.py
...
----------------------------------------------------------------------
Ran 8 tests in 0.123s

OK
```

## 6. Выводы

В ходе работы были освоены следующие навыки:

- Настройка SQLAlchemy и работа с драйвером psycopg2.
- Декларативное описание моделей и связей.
- Реализация CRUD-функций с обработкой ошибок.
- Написание юнит-тестов для валидации бизнес-логики.

Полученная система может быть расширена: добавить веб-интерфейс, авторизацию, дополнительные проверки данных и отчёты.

---



