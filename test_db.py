import unittest

from lib import (
    create_user,
    create_book,
    create_booking,
    delete_booking,
    response
)

class TestCreateUser(unittest.TestCase):
    def test_create_user_success(self):
        """
        Успешное создание пользователя.
        Проверяем, что объект user возвращается.
        """
        user_obj = create_user('testuser', 'testuser@example.com')
        self.assertIsNotNone(user_obj)
        self.assertEqual(user_obj.email, 'testuser@example.com')

    def test_create_user_duplicate(self):
        """
        Попытка создать пользователя с уже существующим email.
        Ожидаем None.
        """
        _ = create_user('dupuser', 'dupuser@example.com')
        duplicate = create_user('another', 'dupuser@example.com')
        self.assertIsNone(duplicate)

class TestCreateBook(unittest.TestCase):
    def test_create_new_book(self):
        """
        Создание новой книги.
        Функция возвращает None при успехе.
        """
        result = create_book('Unique Title', 'Unique Author', 3)
        self.assertIsNone(result)

    def test_increment_copies(self):
        """
        Увеличение количества копий у существующей книги.
        """
        create_book('Common Title', 'Common Author', 1)
        result = create_book('Common Title', 'Common Author', 2)
        self.assertIsNone(result)

class TestCreateBooking(unittest.TestCase):
    def test_booking_nonexistent_user(self):
        """
        Бронирование с несуществующим email.
        Проверяем status и INFO.
        """
        resp = create_booking('no_user@example.com', 'any', 'any')
        self.assertIsInstance(resp, response)
        self.assertEqual(resp.status, 404)
        self.assertEqual(resp.INFO, 'Пользователь с таким email не найден')

    def test_booking_nonexistent_book(self):
        """
        Бронирование несуществующей книги.
        """
        _ = create_user('bookuser', 'bookuser@example.com')
        resp = create_booking('bookuser@example.com', 'Unknown', 'Unknown')
        self.assertIsInstance(resp, response)
        self.assertEqual(resp.status, 404)
        self.assertEqual(resp.INFO, 'Книга с указанными данными не найдена')

    def test_booking_no_copies(self):
        """
        Попытка брони, когда нет доступных копий.
        """
        # Создаем книгу с 0 копий
        create_book('Zero Title', 'Zero Author', 0)
        _ = create_user('zero_user', 'zero@example.com')
        resp = create_booking('zero@example.com', 'Zero Author', 'Zero Title')
        self.assertIsInstance(resp, response)
        self.assertEqual(resp.status, 400)
        self.assertEqual(resp.INFO, 'Нет экземпляров книги в наличии')

class TestDeleteBooking(unittest.TestCase):
    def test_delete_nonexistent_booking(self):
        """
        Удаление несуществующего бронирования.
        Возвращает None.
        """
        result = delete_booking('no_user@example.com', 'no', 'no')
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()
