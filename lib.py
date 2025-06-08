from sqlalchemy import create_engine, DateTime, func, ForeignKey
from sqlalchemy.orm import declarative_base, mapped_column, Mapped, Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
import psycopg2
import datetime
from sqlalchemy import select
from sqlalchemy import delete
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql+psycopg2://postgres:1234@localhost:5432/library"

engine = create_engine(DATABASE_URL)

Base = declarative_base()

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

class response():
    def __init__(self, status, INFO):
        self.status = status
        self.INFO = INFO 

def get_session():
    """
    Возвращает новую SQLAlchemy-сессию.
    Вызовите session = get_session(), а после работы — session.close().
    """
    return SessionLocal()

class user(Base):
    __tablename__ = 'user'
    email:Mapped [str] = mapped_column(nullable=False, unique=True)
    id:Mapped [int] = mapped_column(primary_key=True)
    name:Mapped [str] = mapped_column(nullable=False)
    

    def __repr__(self):
        return f"<User(id={self.id}, name={self.name!r}, email={self.email!r})>"


class book(Base):
    __tablename__ = 'book'
    id:Mapped [int] = mapped_column(primary_key=True)
    title:Mapped [str] = mapped_column(nullable=False)
    author:Mapped [str] = mapped_column(nullable=False)
    copies_available:Mapped [int] = mapped_column()

class booking(Base):
    __tablename__ = 'booking'
    id:Mapped [int] =  mapped_column(primary_key=True)
    user_id:Mapped [int] = mapped_column(ForeignKey('user.id'), nullable=False)
    book_id:Mapped [int] = mapped_column(ForeignKey('book.id'), nullable=False)
    booking_date: Mapped[datetime.datetime] = mapped_column(
    DateTime(timezone=True),
    server_default=func.now(),
    nullable=False
    )

Base.metadata.create_all(engine)





def create_user(name: str, email: str):
    session = get_session()

    """
    Пытается создать пользователя с указанным name/email.
    Если возникает IntegrityError (например, дубликат email), 
    выводит детальную информацию об ошибке от psycopg2.
    """
    new_user = user(name=name, email=email)
    session.add(new_user)

    try:
        session.commit()
        session.refresh(new_user)
        print(f"[INFO] Пользователь создан успешно: {new_user}")

    except IntegrityError as ie:
        # Откатим транзакцию, чтобы сессия снова стала «чистой»
        session.rollback()

        # 1) Печатаем базовую информацию о SQLAlchemy-ошибке
        print("=== IntegrityError при попытке создать пользователя ===")
        print("Класс исключения:", ie.__class__.__name__)
        # ie.orig — это «сырое» исключение от psycopg2
        print("Сообщение SQLAlchemy:", str(ie.orig))

        # 2) Если orig — объект psycopg2.Error, то можно вывести дополнительные поля
        if isinstance(ie.orig, psycopg2.Error):
            pgerr: psycopg2.Error = ie.orig
            print(">>> Подробности от psycopg2:")
            print("   pgcode:", pgerr.pgcode)
            print("   pgerror:", pgerr.pgerror)
            # Если нужно, можно также достать имя ограничения и детали
            print("   constraint_name:", getattr(pgerr.diag, 'constraint_name', None))
            print("   message_detail:", getattr(pgerr.diag, 'message_detail', None))

            # Дополнительно, если вы хотите «человеческую» расшифровку
            if pgerr.pgcode == '23505':
                print("[ERROR] Нельзя создать пользователя: email уже используется (UniqueViolation).")
            elif pgerr.pgcode == '23503':
                print("[ERROR] Нарушение внешнего ключа (ForeignKeyViolation).")
            # ... и т. д. для других pgcode

        # 3) Можно вернуть None или пробросить исключение дальше, 
        #    если эта функция должна “говорить” вызывателю о неуспехе.
        return None

    except Exception as exc:
        # На случай, если упало что-то неожиданное (не IntegrityError)
        session.rollback()
        print("=== Неожиданная ошибка при create_user ===")
        print("Класс исключения:", exc.__class__.__name__)
        print("Сообщение:", str(exc))
        return None

    # Если всё прошло без ошибок, возвращаем созданный объект
    return new_user

def create_book(title: str, author: str, copies_available: int):
    session = get_session()

    new_book = book(title = title , author =  author, copies_available = copies_available)

    book_check = select(book).where(book.title == title,  book.author == author)
    result_book_check = session.execute(book_check).scalars().first()
    if result_book_check == None:
        session.add(new_book)
    else:
        result_book_check.copies_available += copies_available
        session.add(result_book_check)

    session.commit()




#Бронированние книги 
    """
    Передаем email пользователя, ищем книгу по  названию и автору  

    """
def create_booking(email: str, author: str, title: str):
    session = get_session()

    #делаем запрос в бд чтобы получить выборку с данными пользователя
    query_email = select(user).where(user.email == email)
    result_email = session.execute(query_email)
    
    #проверяем что наша выборка не пустая
    flag_1 = True

    for user_obj in result_email.scalars():
        flag_1 = False
        break

    if flag_1 == True:
        print('Пользователя с таким email не существует')    
        return response(404, 'Пользователь с таким email не найден')
    
    flag_1 = True

    query_book = select(book).where(book.author == author, book.title == title)
    resul_book = session.execute(query_book)

    for book_obj in  resul_book.scalars():
        flag_1 = False
        break
    

    if flag_1 == True:
        print('Книга с указанными данными не найденна')    
        return response(404, 'Книга с указанными дайнными не найдена')

    if book_obj.copies_available == 0:
        print('Нет экзепляров книги  в наличии')
        return response(400, 'Нет экземпляров книги в наличии')

    new_booking = booking(user_id = user_obj.id, book_id = book_obj.id)
    book_obj.copies_available -= 1
    session.add(new_booking)
    session.add(book_obj)
    session.commit()
    return response(200, 'Зарос успешен')
#_____________________________Удаление Бронирования_____________________________________________________
def delete_booking(email: str, author: str, title: str):
    session = get_session()

    #делаем запрос в бд чтобы получить выборку с данными пользователя
    query_email = select(user).where(user.email == email)
    result_email = session.execute(query_email)
    
    #проверяем что наша выборка не пустая
    flag_1 = True

    for user_obj in result_email.scalars():
        flag_1 = False
        break

    if flag_1 == True:
        print('Пользователя с таким email не существует')    
        return
    
    flag_1 = True

    query_book = select(book).where(book.author == author, book.title == title)
    resul_book = session.execute(query_book)

    for book_obj in  resul_book.scalars():
        flag_1 = False
        break
    

    if flag_1 == True:
        print('Книга с указанными данными не найденна')    
        return


    query_booking = select(booking).where(booking.user_id == user_obj.id, booking.book_id == book_obj.id).order_by(booking.booking_date.asc())
    booking_obj = session.execute(query_booking).scalars().first()
    print(booking_obj.id)   
    delete_current_booking = delete(booking).where(booking.id == booking_obj.id)
    book_obj.copies_available += 1
    session.execute(delete_current_booking)
    session.add(book_obj)
    session.commit()

# delete_booking('redangry73', 'ddssad', 'sheih')
# create_book('negr', 'umni',2)
                    

# def test_function():
#     assert create_booking('redangry73', 'ddssad', 'sheih') == 200

# create_booking('redangry73', 'ddssad', 'sheih')