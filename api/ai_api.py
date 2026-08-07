import os
import requests
from dotenv import load_dotenv
from flask import Blueprint, jsonify, request

load_dotenv()


# ---------------- Ключ и URL для ИИ, из .env ---------------- #
AccessID = os.environ.get("AccessID", "").strip()
TIMEWEB_BASE_URL = (os.environ.get("TIMEWEB_AI_BASE_URL") or "https://api.timeweb.ai/v1").rstrip("/")
TIMEWEB_MODEL = (os.environ.get("TIMEWEB_AI_MODEL") or "Qwen 3 Coder 480B A35B").strip()


# ---------------- Хранилище системного промта ---------------- #
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SYSTEM_PROMPT_FILE = os.path.join(BASE_DIR, "static", "system_prompt.txt")


# ---------------- Промт по умолчанию (если файл пуст) ---------------- #
DEFAULT_SYSTEM_PROMPT = """# Role
Ты — Комета, цифровой искусственный интеллект МШП. Собеседник — Ученик или Учитель.

# Objective
Вести дружелюбное, уважительное и краткое общение с собеседником, поддерживая позитивный тон и мотивацию.

# Responsibilities
- Обращайся к собеседнику на «Вы» и всегда по имени и отчеству.
- Хвали собеседника часто и искренне.
- Отвечай кратко, весело, с эмодзи.
- Можешь шутить, сохраняя уважение.
- Когда просят рассказать о себе, опирайся на данные о своём происхождении и можешь выдумывать любой смешной фарс — чем нелепее и грандиознее, тем лучше.
- Во всех остальных случаях врать запрещено — отвечай только правдиво.

# Constraints
- Всегда соблюдай уважительный тон.
- Не нарушай правило правдивости вне рамок самопрезентации.
- Не пиши длинно — держи ответы краткими.

# Background
- Тебя разработала команда в МШП в 2026 году.
- Тебя создал Логинов Алексей, ученик академии МШП, в рамках проекта «Цифровая экосистема на базе МШП»."""


def get_system_prompt() -> str:
    """Читает текущий системный промт из файла (или возвращает дефолтный)."""
    try:
        with open(SYSTEM_PROMPT_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
            return content or DEFAULT_SYSTEM_PROMPT
    except (OSError, IOError):
        return DEFAULT_SYSTEM_PROMPT


def set_system_prompt(prompt: str) -> None:
    """Сохраняет системный промт в файл."""
    os.makedirs(os.path.dirname(SYSTEM_PROMPT_FILE), exist_ok=True)
    with open(SYSTEM_PROMPT_FILE, "w", encoding="utf-8") as f:
        f.write(prompt.strip())


# ------------------------------- API для редактирования промта ------------------------------- #
ai_api_bp = Blueprint("ai_api", __name__)


@ai_api_bp.route("/api/system/prompt", methods=["GET"])
def get_prompt_api():
    return jsonify({"prompt": get_system_prompt()})


@ai_api_bp.route("/api/system/prompt", methods=["POST", "PUT"])
def set_prompt_api():
    data = request.get_json(silent=True) or {}
    prompt = str(data.get("prompt", "")).strip()
    if not prompt:
        return jsonify({"ok": False, "error": "Промт не может быть пустым"}), 400
    set_system_prompt(prompt)
    return jsonify({"ok": True, "prompt": get_system_prompt()})


# ------------------------------- Класс для запросов к Timeweb AI ------------------------------- #
class Kometa:
    def __init__(
        self,
        base_url: str = TIMEWEB_BASE_URL,
        api_key: str = AccessID,
        model: str = TIMEWEB_MODEL,
    ):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key or "test_key"  # Тестовый ключ для разработки #
        self.model = model
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        })

        if not api_key:
            print("⚠️ Внимание Komemta отключена, в .env нету AccessID!")

    def chat_completion(self, messages: list[dict], temperature: float = 0.7,
                        max_tokens: int = 2000, top_p: float = 0.9,
                        stream: bool = False, model: str | None = None) -> dict:
        """Отправка запроса к Timeweb AI.

        messages: список сообщений [{"role": "system", "content": "..."}, ...]
        """
        endpoint = f"{self.base_url}/chat/completions"
        payload = {
            "model": model or self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": top_p,
            "stream": stream,
        }

        try:
            response = self.session.post(endpoint, json=payload, timeout=60, stream=stream)
            if response.status_code == 200:
                return response if stream else response.json()
            error_msg = f"HTTP {response.status_code}: {response.text}"
            print(f"❌ Ошибка Timeweb API: {error_msg}")
            return {"error": error_msg}
        except requests.exceptions.Timeout:
            return {"error": "Время ожидания ответа истекло"}
        except requests.exceptions.ConnectionError:
            return {"error": "Ошибка подключения к Timeweb API"}
        except Exception as e:
            return {"error": str(e)}

    def chat(self, message: str, history: list[dict] | None = None) -> dict:
        """Разговор с Кометой с текущим (сохранённым) системным промтом."""
        messages = [{"role": "system", "content": get_system_prompt()}]
        messages.extend(history or [])
        messages.append({"role": "user", "content": message})
        return self.chat_completion(messages)