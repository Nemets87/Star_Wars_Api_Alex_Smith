import requests
import warnings
import logging
import pytest
import allure
from urllib3.exceptions import InsecureRequestWarning

# Отключаем назойливые предупреждения SSL
warnings.simplefilter('ignore', InsecureRequestWarning)

# Настраиваем логирование: и в консоль, и в файл
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("vader_mission.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def get_json(url: str) -> dict:
    """Безопасный GET-запрос с отключённой проверкой SSL."""
    logger.debug(f"🌐 Запрос: {url}")
    resp = requests.get(url, verify=False)
    resp.raise_for_status()
    return resp.json()

@allure.feature("Star Wars API")
@allure.story("Персонажи, снимавшиеся с Дартом Вейдером")
@allure.title("Сбор имён и сохранение в файл")
def test_vader_friends():
    """Тест собирает всех персонажей из фильмов с Вейдером и сохраняет в файл без дубликатов."""
    with allure.step("1. Получить данные Дарта Вейдера"):
        vader = get_json("https://swapi.dev/api/people/4/")
        logger.info(f"🎯 Дарт Вейдер: {vader['name']}")
        allure.attach(vader['name'], "Имя цели", allure.attachment_type.TEXT)

    with allure.step("2. Собрать персонажей из его фильмов"):
        all_characters = set()
        for film_url in vader['films']:
            film = get_json(film_url)
            logger.info(f"🎬 Фильм: {film['title']} | персонажей: {len(film['characters'])}")
            all_characters.update(film['characters'])

    with allure.step("3. Получить имена и сохранить в файл"):
        names = []
        for char_url in sorted(all_characters):
            char = get_json(char_url)
            names.append(char['name'])
            logger.debug(f"   👤 {char['name']}")
        names.sort()
        with open("vader_friends.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(names))
        logger.info(f"📁 Файл 'vader_friends.txt' сохранён, имён: {len(names)}")
        allure.attach.file("vader_friends.txt", "Список имён", allure.attachment_type.TEXT)

    with allure.step("4. Проверка результата"):
        assert len(names) > 0, "Список персонажей пуст!"
        logger.info("✅ Миссия выполнена успешно")
