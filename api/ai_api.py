import os
import time
from flask import render_template
import requests
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.environ["OPENROUTER_API_KEY"]

# Модель OpenRouter по умолчанию
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "google/gemini-3.5-flash-lite")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_REFERRER = os.getenv("OPENROUTER_HTTP_REFERER", "https://msp.local")
OPENROUTER_TITLE = os.getenv("OPENROUTER_APP_NAME", "MSP-System")


# Command Show #
AI_SHOW_COMMAND = {
    "start": False,
    "timestamp": 0
}


# In-memory cache for congratulations
congratulations_cache = {}


def ask_openrouter(
    prompt,
    system_prompt=None,
    model=OPENROUTER_MODEL,
    temperature=0.7,
    max_tokens=1024,
    timeout=60,
):
    """Отправляет запрос в OpenRouter и возвращает текст ответа.

    Args:
        prompt (str): пользовательский запрос.
        system_prompt (str, optional): системная инструкция.
        model (str): идентификатор модели OpenRouter.
        temperature (float): температура выборки.
        max_tokens (int): лимит токенов ответа.
        timeout (int): таймаут запроса в секундах.

    Returns:
        str: текст ответа модели.
        None: при ошибке запроса.

    Raises:
        RuntimeError: если API-ключ отсутствует.
    """
    if not OPENROUTER_API_KEY:
        raise RuntimeError("OPENROUTER_API_KEY не задан в .env")

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": OPENROUTER_REFERRER,
        "X-Title": OPENROUTER_TITLE,
    }

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    try:
        resp = requests.post(
            OPENROUTER_URL,
            headers=headers,
            json=payload,
            timeout=timeout,
        )
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]
    except (requests.RequestException, KeyError, IndexError) as exc:
        return None


def stream_openrouter(
    prompt,
    system_prompt=None,
    model=OPENROUTER_MODEL,
    temperature=0.7,
    max_tokens=1024,
    timeout=60,
):
    """Потоковый запрос к OpenRouter.

    Возвращает генератор строк (чанков) текста ответа.
    """
    if not OPENROUTER_API_KEY:
        raise RuntimeError("OPENROUTER_API_KEY не задан в .env")

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": OPENROUTER_REFERRER,
        "X-Title": OPENROUTER_TITLE,
    }

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": True,
    }

    with requests.post(
        OPENROUTER_URL, headers=headers, json=payload, timeout=timeout, stream=True
    ) as resp:
        resp.raise_for_status()
        for line in resp.iter_lines(decode_unicode=True):
            if not line or not line.startswith("data:"):
                continue
            data = line[5:].strip()
            if data == "[DONE]":
                break
            try:
                import json
                chunk = json.loads(data)
                delta = chunk["choices"][0]["delta"].get("content")
                if delta:
                    yield delta
            except (ValueError, KeyError, IndexError):
                continue



@app.route("/ai/chat")
def ai_chat():
    return render_template("ai.html")