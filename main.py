import os
from fastapi import FastAPI, Request
import httpx

app = FastAPI()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"


@app.post("/webhook")
async def handle_dialog(request: Request):
  data = await request.json()

  is_new_session = data.get("session", {}).get("new", False)
  user_command = data.get("request", {}).get("command", "").strip()

  # Приветствие при старте диалога или пустом вводе
  if is_new_session or not user_command:
    return {
        "response": {
            "text": "Привет! Я подключена к быстрой нейросети. О чем спросите?",
            "end_session": False,
        },
        "version": "1.0",
    }

  headers = {
      "Authorization": f"Bearer {GROQ_API_KEY}",
      "Content-Type": "application/json",
  }
  payload = {
      "model": "llama-3.1-8b-instant",
      "messages": [
          {
              "role": "system",
              "content": (
                  "Ты голосовой ассистент Алиса. Отвечай коротко, емко и по"
                  " сути на русском языке. Категорически не используй"
                  " спецсимволы разметки (звездочки *, решетки #, обратные"
                  " кавычки `), так как весь твой ответ будет зачитываться"
                  " голосом через колонку."
              ),
          },
          {"role": "user", "content": user_command},
      ],
      "max_tokens": 350,
  }

  try:
    async with httpx.AsyncClient(timeout=15.0) as client:
      response = await client.post(GROQ_URL, headers=headers, json=payload)
      res_json = response.json()
      reply_text = res_json["choices"][0]["message"]["content"]
  except Exception as e:
    print(f"Error: {repr(e)}")
    reply_text = "Не удалось связаться с сервером. Попробуйте еще раз."

  return {
      "response": {"text": reply_text, "end_session": False},
      "version": "1.0",
  }
