import json
import logging
from typing import TYPE_CHECKING, Any

import openai

if TYPE_CHECKING:
    from openai.types.chat.chat_completion import ChatCompletion

log = logging.getLogger(__name__)


class VacancyAIAnalyst:
    """AI Analyst for Vacancy."""

    def __init__(self, base_url: str, api_key: str, model: str) -> None:
        """Initialize the AI Analyst."""
        self._client = openai.AsyncOpenAI(
            api_key=api_key,
            base_url=base_url,
        )
        self._model = model
        log.info("AI Analyst initialized")

    async def analyze_score(
        self, vacancy_text: str, resume_text: str
    ) -> dict[str, Any]:
        """Analyze vacancy match with resume text."""
        prompt = f"""
        Ты — эксперт по найму в IT. Твоя задача — сравнить резюме кандидата с текстом вакансии.

        РЕЗЮМЕ КАНДИДАТА:
        {resume_text}

        ТЕКСТ ВАКАНСИИ:
        {vacancy_text}

        Верни ответ строго в формате JSON со следующими полями:
        - score: число от 0 до 100 (насколько кандидат подходит).
        - main_reasons: Ключевая причина такой оценки, опыт работы не учитывай, максимольно до 100 символов.
        - missing_skills: список навыков из вакансии, которых нет в резюме, нужно перечисление стека через запятую, максимольно до 100 символов.
        """  # noqa: E501, RUF001

        try:
            response: ChatCompletion = await self._client.chat.completions.create(  # noqa: E501
                model=self._model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Ты профессиональный HR-аналитик. "
                            "Отвечай ТОЛЬКО валидным JSON. "
                            "Не используй markdown, не оборачивай ответ в ```json ... ```. "  # noqa: E501, RUF001
                            "Первый символ ответа должен быть '{', последний — '}'."  # noqa: E501
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                n=1,
                # response_format={"type": "json_object"},  # noqa: E501, ERA001, W505
                temperature=0.0,
            )

            content: str | None = response.choices[0].message.content
            if content is None:
                raise ValueError("Model returned empty response")

            jnon_content: dict[str, Any] = json.loads(content)
            return jnon_content

        except Exception as e:  # noqa: BLE001
            log.error("AI Analysis error: %s", e)

            return {"score": 0}
