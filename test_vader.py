import requests
import warnings
import logging
import allure
from urllib3.exceptions import InsecureRequestWarning

# Отключаем предупреждения о небезопасном SSL
warnings.simplefilter('ignore', InsecureRequestWarning)

# Настраиваем логирование: в файл и в консоль
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("vader_mission.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class Checking:
    """Универсальный проверяльщик статус-кодов с логированием и Allure."""

    @staticmethod
    def check_status_code(response: requests.Response, expected_code: int = 200) -> None:
        """
        Проверяет, что статус-код ответа равен ожидаемому.
        В случае несовпадения выбрасывает AssertionError.
        """
        with allure.step(f"Проверка статус-кода: ожидается {expected_code}"):
            actual_code = response.status_code
            logger.info(f"Ответ от {response.url} – статус: {actual_code}")
            if actual_code != expected_code:
                error_msg = f"❌ Ожидался статус {expected_code}, но получен {actual_code}"
                logger.error(error_msg)
                allure.attach(str(response.text), "Тело ответа", allure.attachment_type.TEXT)
                raise AssertionError(error_msg)
            logger.info(f"✅ Статус-код {actual_code} соответствует ожидаемому")


def get_json(url: str) -> dict:
    """GET-запрос с проверкой статус-кода и возвратом JSON."""
    logger.debug(f"🌐 Запрос: {url}")
    response = requests.get(url, verify=False)
    # Магическая проверка статуса
    Checking.check_status_code(response, 200)
    return response.json()


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

    with allure.step("4. Итоговая проверка"):
        assert len(names) > 0, "Список персонажей пуст!"
        logger.info("✅ Миссия выполнена успешно")
