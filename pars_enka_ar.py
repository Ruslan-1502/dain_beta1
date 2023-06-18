import requests
from bs4 import BeautifulSoup
import re





async def get_ar(uid):
# Установить URL-адрес сайта, с которого хотим считывать информацию
    url = f"https://enka.network/u/{uid}/"

    response = requests.get(url)
    content = response.text

    soup = BeautifulSoup(content, "html.parser")
    details_div = soup.find("div", class_="details svelte-grjiuv")
    ar_div = details_div.find("div", class_="ar svelte-grjiuv")
    ar_text = ar_div.text.strip()

    ar_value = ar_text.split()[1]

    return ar_value





async def get_nickname(uid):
    url = f"https://enka.network/u/{uid}/"
    response = requests.get(url)

# Проверяем успешность запроса
    if response.status_code == 200:
    # Используем BeautifulSoup для парсинга HTML-кода страницы
     soup = BeautifulSoup(response.content, 'html.parser')

    # Находим элемент по селектору CSS
     element = soup.select_one('.details.svelte-grjiuv h1.svelte-grjiuv')
    
    # Выводим текст найденного элемента
     if element:
        text = element.text.strip()
        return text
     else:
        await ("Элемент не найден.")
    else:
     error_message = f"Error occurred: {response.status_code}"
     return error_message