import requests
from transformers import AutoTokenizer
from config import logger
from typing import TypeAlias
from error import TooLongTask

Error: TypeAlias = str
Answer: TypeAlias = str


# "mistralai/Mistral-7B-Instruct-v0.2"
class GPT:
    def __init__(self,
                 max_tokens_in_task: int = 1024,
                 max_tokens_in_answer: int = 1024,
                 model_name: str = 'mistralai/Mistral-7B-Instruct-v0.2',
                 url: str = r'http://localhost:1234/v1/chat/completions',
                 assistant: str = "Let's talk: "):
        self.max_tokens_in_task = max_tokens_in_task
        self.max_tokens_in_answer = max_tokens_in_answer
        self.answer = ''
        self.assistant = assistant
        self.model_name = model_name
        self.URL = url

    def question(self, system: str, user: str, max_tokens: int,
                 assistant: str = '') -> Answer | Error:
        if self.correct_user_content(user):
            data = {
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                "temperature": 1,
                "max_tokens": self.max_tokens_in_answer if self.max_tokens_in_answer < max_tokens else max_tokens
            }
            print(f'MAX_TOKENS: {data['max_tokens']}')
            if assistant:
                data['messages'].append({
                    "role": "assistant",
                    "content": assistant
                })

            try:
                resp = requests.post(
                    self.URL,
                    headers={"Content-Type": "application/json"},

                    json=data
                )
            except Exception as error:
                error_msg = f"Ошибка: {error}"
                logger.error(error_msg)
                return error_msg
            if resp.status_code == 200 and 'choices' in resp.json():
                result = resp.json()['choices'][0]['message']['content']
                if result == "":
                    return "Объяснение закончено"

                self.answer += result
                print(f'"{self.answer}"')
                return result

            error_msg = f'Статус код: {resp.status_code}'
            logger.error(error_msg)
            return 'Не удалось получить ответ от нейросети. ' + error_msg

        raise TooLongTask('Задача слишком длинная. Пожалуйста, уменьшите объем задачи.')

    def correct_user_content(self, user_content: str) -> bool | Error:
        try:
            tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            if len(tokenizer.encode(user_content)) > self.max_tokens_in_task:
                return False
            return True
        except Exception as error:
            error_msg = f"Ошибка: {error}"
            logger.error(error_msg)
            return error_msg

    def all_answer(self) -> str:
        return self.answer

    def can_use_continue(self) -> bool:
        if self.answer:
            return True
        return False

    @staticmethod
    def count_tokens(text: str, folder_id: str, iam_token: str) -> int:
        data = {
            "modelUri": f"gpt://{folder_id}/yandexgpt-lite/latest",
            "text": text,
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {iam_token}",
            "x-folder-id": f"{folder_id}",
        }
        url = "https://llm.api.cloud.yandex.net/foundationModels/v1/tokenize"

        response = requests.post(
            url=url,
            headers=headers,
            json=data
        )
        return len(response.json()['tokens'])

    # new, continue, end
    def question_to_yagpt(self, system: str, user: str, max_tokens: int,
                          iam_token: str, assistant: str = ''):
        """Запрос к Yandex GPT"""

        url = f"https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
        headers = {
            'Authorization': f'Bearer {iam_token}',
            'Content-Type': 'application/json'
        }

        data = {
            "modelUri": f"gpt://b1gnr8vgjubhf0if6ft1/yandexgpt-lite/latest",
            "completionOptions": {
                "stream": False,
                "temperature": 0.7,
                "maxTokens": str(self.max_tokens_in_answer) if self.max_tokens_in_answer < max_tokens else str(
                    max_tokens)
            },
            "messages": [
                {
                    "role": "system",
                    "text": system
                },
                {
                    "role": "user",
                    "text": user
                }
            ]
        }

        if assistant:
            data['messages'].append({
                "role": "assistant",
                "text": assistant
            })

        try:
            response = requests.post(url, headers=headers, json=data)

        except Exception as error:
            error_msg = f"Ошибка: {error}"
            logger.error(error_msg)
            return error_msg

        else:
            if response.status_code != 200:
                print("Ошибка при получении ответа:", response.status_code)
            else:
                result = response.json()['result']['alternatives'][0]['message']['text']
                return result


if __name__ == "__main__":
    gpt = GPT()
    print(gpt.question('hi', 'hi', 100))
