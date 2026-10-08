from abc import ABC, abstractmethod
import base64
import os
from typing import List, Optional, Union

from dotenv import load_dotenv
from openai import AsyncOpenAI


class BaseLLMAPI(ABC):
    """Simple interface for LLM backends."""

    def __init__(self, system_instructions: str, model_name: str):
        self.system_instructions = system_instructions
        self.model_name = model_name

    @abstractmethod
    async def generate_content(self, contents: List[Union[str, dict]]) -> str:
        """Generate text from the given contents."""


class BaseOpenAIAPI(BaseLLMAPI):
    """Shared implementation for OpenAI-compatible backends."""

    base_url: str = ""
    api_key_env_var: str = ""
    default_model_name: str = ""

    def __init__(
        self,
        system_instructions: str,
        model_name: Optional[str] = None,
        api_key: Optional[str] = None,
    ):
        resolved_model = model_name or self.default_model_name
        super().__init__(system_instructions, resolved_model)

        if not api_key:
            load_dotenv()
            api_key = os.getenv(self.api_key_env_var)
        # Async client with HTTP/2 and connection reuse under the hood
        self.client = AsyncOpenAI(
            base_url=self.base_url,
            api_key=api_key,
        )

    def _prepare_user_content(self, contents: List[Union[str, dict]]):
        user_content = []
        for idx, part in enumerate(contents):
            if isinstance(part, str):
                user_content.append({"type": "text", "text": part})
            elif isinstance(part, dict) and "data" in part:
                mime = part.get("mime_type", "image/jpeg")
                b64 = base64.b64encode(part["data"]).decode("utf-8")
                data_url = f"data:{mime};base64,{b64}"
                user_content.append(
                    {"type": "image_url", "image_url": {"url": data_url}}
                )
        return user_content

    async def generate_content(self, contents: List[Union[str, dict]]) -> str:
        """
        Async text+image generation. Returns the model's text string.
        """
        print(
            "[DEBUG] Sending request to LLM at ",
            self.base_url,
            " with model ",
            self.model_name,
        )
        resp = await self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": self.system_instructions},
                {"role": "user", "content": self._prepare_user_content(contents)},
            ],
        )
        # Defensive: sometimes content can be None; normalize to ""
        return resp.choices[0].message.content or ""


class OpenRouterAPI(BaseOpenAIAPI):
    """Access LLMs via the OpenRouter aggregation API."""

    base_url = "https://openrouter.ai/api/v1"
    api_key_env_var = "OPENROUTER_API_KEY"
    default_model_name = "google/gemini-2.5-pro"


class GoogleGeminiAPI(BaseOpenAIAPI):
    """Access Gemini models via Google's OpenAI-compatible endpoint."""

    base_url = "https://generativelanguage.googleapis.com/v1beta/openai/"
    api_key_env_var = "GOOGLE_API_KEY"
    default_model_name = "gemini-2.5-pro"
