import requests
from config import logger


class SpeechKit:
    def __init__(self, folderId: str,
                 topic: str = 'general',
                 lang: str = 'ru-RU',
                 voice: str = 'filipp'):
        self.folderId = folderId
        self.lang = lang
        self.voice = voice
        self.topic = topic

    def speech_to_text(self, iam_token: str, data):
        params = "&".join([
            f"topic={self.topic}",
            f"folderId={self.folderId}",
            f"lang={self.lang}"
        ])

        headers = {
            'Authorization': f'Bearer {iam_token}',
        }

        response = requests.post(
            f"https://stt.api.cloud.yandex.net/speech/v1/stt:recognize?{params}",
            headers=headers,
            data=data
        )

        # Читаем json в словарь
        decoded_data = response.json()

        # Проверяем, не произошла ли ошибка при запросе
        if decoded_data.get("error_code") is None:
            return decoded_data.get("result")
        else:
            logger.error(f'Сетевая ошибка: {response.status_code}')
            raise ConnectionError(f'Сетевая ошибка: {response.status_code}')

    def text_to_speech(self, text: str, iam_token: str):
        headers = {
            'Authorization': f'Bearer {iam_token}',
        }
        data = {
            'text': text,
            'lang': self.lang,
            'voice': self.voice,
            'folderId': self.folderId,
        }

        response = requests.post('https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize',
                                 headers=headers,
                                 data=data)

        if response.status_code == 200:
            return response.content
        logger.error(f'Сетевая ошибка: {response.status_code}')
        raise ConnectionError(f'Сетевая ошибка: {response.status_code}')
