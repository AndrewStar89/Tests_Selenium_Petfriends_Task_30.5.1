import pytest
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By

@pytest.fixture(autouse=True)
def testing():
    pytest.driver = webdriver.Chrome('./chromedriver.exe')
    pytest.driver.implicitly_wait(15)  # Задаем неявное ожидание 10 сек.
    pytest.driver.set_window_size(1920, 1080)

    yield

    pytest.driver.quit()

def indexes_of_matching_elements(data):
    """ Поиск совпадающих элементов в списке. Если есть, возвращает список кортежей с индексами
    совпадающих элементов. Если нет совпадений, возвращает none."""
    if len(data) != len(set(data)):
        equal = []
        for i in range(len(data) - 1):
            j = i + 1
            while j != len(data):
                if data[i] == data[j]:
                    a = (i, j)
                    equal.append(a)
                j += 1
        return equal

def test_show_all_pets():
    """Тест на наличие фото, имени, вида и возраста у всех питомцев на главной странице пользователя"""

    # Переходим на страницу авторизации
    pytest.driver.get('http://petfriends.skillfactory.ru/login')
    # Вводим email
    pytest.driver.find_element(By.ID, 'email').send_keys('Something@something')
    # Вводим пароль
    pytest.driver.find_element(By.ID, 'pass').send_keys('Something')
    # Нажимаем на кнопку входа в аккаунт
    pytest.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
    # Проверяем, что мы оказались на главной странице пользователя
    assert pytest.driver.find_element(By.TAG_NAME, 'h1').text == "PetFriends"

    images = pytest.driver.find_elements(By.CSS_SELECTOR, '.card-deck .card-img-top')  # получение фото питомцев
    names = pytest.driver.find_elements(By.CSS_SELECTOR, '.card-deck .card-title')  # получение имён питомцев
    descriptions = pytest.driver.find_elements(By.CSS_SELECTOR, '.card-deck .card-text')  # получение описаний питомцев

    for i in range(len(names)):
        assert images[i].get_attribute('src') != '', 'Не у всех питомцев есть фото'
        assert names[i].text != '', 'Не у всех питомцев есть имя'
        assert descriptions[i].text != '', 'Не у всех питомцев есть описания'
        assert ', ' in descriptions[i].text, 'Описание состоит из двух элементов'
        parts = descriptions[i].text.split(", ")
        assert len(parts[0]) > 0, 'Не у всех питомцев есть порода'
        # Проверяем возраст, он хранится в формате "Х лет",
        # При разделении строки, длина 2 при заданном возрасте и 1 при пустом
        age = parts[1].split()
        assert len(age) == 1, 'Не у всех питомцев есть возраст'

def test_show_my_pets():
    '''Проверка того, что переход на страницу "Мои питомцы" осуществляется'''

    # Переходим на страницу авторизации
    pytest.driver.get('http://petfriends.skillfactory.ru/login')

    # Явное ожидание перехода на страницу авторизации
    element_email = WebDriverWait(pytest.driver, 5).until(ec.presence_of_element_located((By.ID, 'email')))
    # Проверяем, что мы оказались на странице авторизации
    assert ('pass' in pytest.driver.find_element(By.ID, 'pass').get_attribute('id')) and \
           ('email' in element_email.get_attribute('id')), 'Не загрузилась страница авторизации'

    # Вводим email
    pytest.driver.find_element(By.ID, 'email').send_keys('Something@something')
    # Вводим пароль
    pytest.driver.find_element(By.ID, 'pass').send_keys('Something')
    # Нажимаем на кнопку входа в аккаунт
    pytest.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()

    # Явное ожидание перехода на главную страницу
    element_name_h1 = WebDriverWait(pytest.driver, 10).until(ec.presence_of_element_located((By.TAG_NAME, 'h1')))
    # Проверяем, что мы оказались на главной странице
    assert element_name_h1.text == "PetFriends", 'Не загрузилась главная страница'

    # Нажимаем на кнопку Мои питомцы
    pytest.driver.find_element(By.LINK_TEXT, 'Мои питомцы').click()

    # Явное ожидание перехода на страницу Мои питомцы
    element_name_h2 = WebDriverWait(pytest.driver, 10).until(ec.presence_of_element_located((By.TAG_NAME, 'h2')))
    # Проверяем, что мы оказались на странице пользователя
    assert element_name_h2.text != "", 'Не загрузилась страница пользователя'

    # Получение фото питомцев
    images = pytest.driver.find_elements(By.CSS_SELECTOR, 'div#all_my_pets > table > tbody > tr > th > img')
    # Получение таблицы атрибутов (имя, порода, возраст) питомцев, по четыре элемента на одного питомца
    parts = pytest.driver.find_elements(By.CSS_SELECTOR, 'div#all_my_pets > table > tbody > tr > td')
    # Получение данных пользователя
    custom = pytest.driver.find_element(By.CSS_SELECTOR, '.\\.col-sm-4.left')

    # Сравнение количества питомцев из блока статистики пользователя
    # с количеством питомцев в таблице - должны быть равны
    assert int(custom.text.split()[2]) == len(parts)/4, 'Не все питомцы отображены'

    # Извлечение атрибутов из общего списка и их проверка
    names = []
    breeds = []
    ages = []
    count_photo = 0
    for i in range(len(images)):
        if images[i].get_attribute('src') != '':
            count_photo += 1  # подсчет количества питомцев с фото
        # Проверка, что у всех питомцев есть имя, возраст и порода.
        assert parts[i * 4].text != '' and parts[i * 4 + 1].text != '' and parts[
            i * 4 + 2].text != '', 'Есть питомцы с незаполненными данными'
        # Создание списков имен, пород и возрастов питомцев
        names.append(parts[i * 4].text)
        breeds.append(parts[i * 4 + 1].text)
        ages.append(parts[i * 4 + 2].text)

    # Проверка, что хотя бы у половины питомцев есть фото.
    assert count_photo >= len(images)/2, 'Нет фото более чем у половины питомцев'

    equal_name = indexes_of_matching_elements(names)  # Поиск повторяющихся имён
    equal_breeds = indexes_of_matching_elements(breeds)  # Поиск повторяющихся пород
    equal_ages = indexes_of_matching_elements(ages)  # Поиск повторяющихся возрастов

    # Поиск питомцев с одинаковыми именем, породой и возрастом и вывод на печать имён и позиций в таблице
    if equal_name and equal_breeds and equal_ages:
        intersections_elements = (set(set(equal_name).intersection(equal_breeds)).intersection(equal_ages))
        for i in intersections_elements:
            print(f'\nПовторение питомца {names[i[0]]} в позициях {i[0] + 1} и {i[1] + 1}.')
        raise AssertionError('Присутствуют повторяющиеся питомцы с одинаковыми именем, породой и возрастом.')
    # Поиск питомцев с одинаковыми именами
    if equal_name:
        raise AssertionError('Присутствуют питомцы с повторяющимися именами')

#   python -m pytest -v --driver Chrome --driver-path /tests/chromedriver tests/test_selenium_petfriends_task.py
