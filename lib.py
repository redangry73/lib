from sqlalchemy import (
    create_engine,
    DateTime,
    func,
    ForeignKey,
    select,
    delete
)
from sqlalchemy.orm import (
    declarative_base,
    mapped_column,
    Mapped,
    Session,
    sessionmaker
)
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
import psycopg2
import datetime

# Настройки подключения
DATABASE_URL = "postgresql+psycopg2://postgres:1234@localhost:5432/library"
engine = create_engine(DATABASE_URL)

# Базовый класс моделей
Base = declarative_base()

# Фабрика сессий
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

class response():
    """
    Простой контейнер для возврата кода статуса и сообщения.
    """
    def __init__(self, status, INFO):
        self.status = status
        self.INFO = INFO


def get_session():
    """
    Возвращает новую сессию SQLAlchemy.
    Вызовите session = get_session(), а после работы — session.close().
    """
    return SessionLocal()

class user(Base):
    """
    Модель пользователя.
    Поля:
      - id: первичный ключ
      - name: имя пользователя
      - email: уникальный email
    """
    __tablename__ = 'user'

    id: Mapped[int]    = mapped_column(primary_key=True)
    name: Mapped[str]  = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(nullable=False, unique=True)

    def __repr__(self):
        """
        Возвращает строковое представление пользователя.
        """
        return f"<User(id={self.id}, name={self.name!r}, email={self.email!r})>"

class book(Base):
    """
    Модель книги.
    Поля:
      - id: первичный ключ
      - title: название книги
      - author: автор книги
      - copies_available: количество доступных копий
    """
    __tablename__ = 'book'

    id:               Mapped[int] = mapped_column(primary_key=True)
    title:            Mapped[str] = mapped_column(nullable=False)
    author:           Mapped[str] = mapped_column(nullable=False)
    copies_available: Mapped[int] = mapped_column()

class booking(Base):
    """
    Модель бронирования.
    Поля:
      - id: первичный ключ
      - user_id: внешний ключ к пользователю
      - book_id: внешний ключ к книге
      - booking_date: дата бронирования (по умолчанию NOW())
    """
    __tablename__ = 'booking'

    id:            Mapped[int]              = mapped_column(primary_key=True)
    user_id:       Mapped[int]              = mapped_column(ForeignKey('user.id'), nullable=False)
    book_id:       Mapped[int]              = mapped_column(ForeignKey('book.id'), nullable=False)
    booking_date:  Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

# Создание таблиц в БД
Base.metadata.create_all(engine)

# Функции работы с данными

def create_user(name: str, email: str):
    """
    Создаёт нового пользователя с указанными именем и email.
    Обрабатывает ошибки уникальности и внешнего ключа.
    Возвращает объект user или None при ошибке.
    """
    session = get_session()
    new_user = user(name=name, email=email)
    session.add(new_user)

    try:
        session.commit()
        session.refresh(new_user)
        print(f"[INFO] Пользователь создан успешно: {new_user}")

    except IntegrityError as ie:
        session.rollback()
        print("=== IntegrityError при попытке создать пользователя ===")
        print("Класс исключения:", ie.__class__.__name__)
        print("Сообщение SQLAlchemy:", str(ie.orig))

        if isinstance(ie.orig, psycopg2.Error):
            pgerr: psycopg2.Error = ie.orig
            print(">>> Подробности от psycopg2:")
            print("   pgcode:", pgerr.pgcode)
            print("   pgerror:", pgerr.pgerror)
            print("   constraint_name:", getattr(pgerr.diag, 'constraint_name', None))
            print("   message_detail:", getattr(pgerr.diag, 'message_detail', None))

            if pgerr.pgcode == '23505':
                print("[ERROR] Нельзя создать пользователя: email уже используется (UniqueViolation).")
            elif pgerr.pgcode == '23503':
                print("[ERROR] Нарушение внешнего ключа (ForeignKeyViolation).")
        return None

    except Exception as exc:
        session.rollback()
        print("=== Неожиданная ошибка при create_user ===")
        print("Класс исключения:", exc.__class__.__name__)
        print("Сообщение:", str(exc))
        return None

    return new_user


def create_book(title: str, author: str, copies_available: int):
    """
    Создаёт новую книгу или увеличивает количество копий, если такая запись уже есть.
    """
    session = get_session()
    new_book = book(
        title=title,
        author=author,
        copies_available=copies_available
    )

    book_check = select(book).where(book.title == title, book.author == author)
    result_book_check = session.execute(book_check).scalars().first()

    if result_book_check is None:
        session.add(new_book)
    else:
        result_book_check.copies_available += copies_available
        session.add(result_book_check)

    session.commit()


def create_booking(email: str, author: str, title: str):
    """
    Создаёт бронирование книги для пользователя по email.
    Проверяет существование пользователя, книги и доступность копий.
    Возвращает response со статусом и сообщением.
    """
    session = get_session()

    result_email = session.execute(
        select(user).where(user.email == email)
    ).scalars().first()
    if result_email is None:
        print('Пользователя с таким email не существует')
        return response(404, 'Пользователь с таким email не найден')

    book_obj = session.execute(
        select(book).where(book.author == author, book.title == title)
    ).scalars().first()
    if book_obj is None:
        print('Книга с указанными данными не найденна')
        return response(404, 'Книга с указанными данными не найдена')

    if book_obj.copies_available == 0:
        print('Нет экземпляров книги в наличии')
        return response(400, 'Нет экземпляров книги в наличии')

    new_booking = booking(user_id=result_email.id, book_id=book_obj.id)
    book_obj.copies_available -= 1
    session.add(new_booking)
    session.add(book_obj)
    session.commit()

    return response(200, 'Запрос успешен')


def delete_booking(email: str, author: str, title: str):
    """
    Удаляет старейшее бронирование книги для пользователя по email.
    Восстанавливает количество доступных копий книги.
    """
    session = get_session()

    user_obj = session.execute(
        select(user).where(user.email == email)
    ).scalars().first()
    if user_obj is None:
        print('Пользователя с таким email не существует')
        return

    book_obj = session.execute(
        select(book).where(book.author == author, book.title == title)
    ).scalars().first()
    if book_obj is None:
        print('Книга с указанными данными не найденна')
        return

    booking_obj = session.execute(
        select(booking)
        .where(booking.user_id == user_obj.id, booking.book_id == book_obj.id)
        .order_by(booking.booking_date.asc())
    ).scalars().first()
    if booking_obj is None:
        print('Бронирование не найдено')
        return

    print(booking_obj.id)
    session.execute(delete(booking).where(booking.id == booking_obj.id))

    book_obj.copies_available += 1
    session.add(book_obj)
    session.commit()

# Примеры вызова (раскомментировать для тестирования)
# delete_booking('redangry73', 'ddssad', 'sheih')
create_booking('negr', 'umni', 'sadas')
# assert create_booking('redangry73', 'ddssad', 'sheih').status == 200
# create_booking('redangry73', 'ddssad', 'sheih')
