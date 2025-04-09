import json
import requests
import logging
import colorama

from abc import ABC, abstractmethod
from typing import Generator

from .data_models import RequestPayLoad, RequestStreamData
from .conversation import Conversation

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())


class LLMBaseModel(ABC):
    def __init__(self, api_key: str, model_id: str, **kwargs) -> None:
        self.api_key = api_key
        self.model_id = model_id

    @abstractmethod
    def send_prompt(self, conversation: Conversation) -> str:
        raise NotImplementedError("Every LLM model must implement the generate_response method.")

    @staticmethod
    def check_api_status(response: requests.Response) -> str | None:
        if response.status_code != 200:
            error_msg: str = f"Error: {response.status_code} - {response.text}"
            logger.error(error_msg)
            print(f"{colorama.Fore.RED}Error: {error_msg}{colorama.Style.RESET_ALL}")
            return error_msg


class ClaudeModel(LLMBaseModel):
    def __init__(self, api_key: str, model_id: str) -> None:
        super().__init__(api_key, model_id)
        self.api_url = "https://api.anthropic.com/v1/messages"
        self.max_tokens = 5000
        self.temperature = 0.7
        self.stream = True
        self.header = {
            "x-api-key": self.api_key,
            "content-type": "application/json",
            "anthropic-version": "2023-06-01",
        }

    def send_prompt(self, conversation: Conversation) -> str:
        data = RequestPayLoad(
            model=self.model_id,
            messages=conversation.consolidate_msg_for_api(),
            stream=self.stream,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
        ).model_dump()

        response = requests.post(self.api_url, headers=self.header, json=data)
        super().check_api_status(response)

        return self._stream_response(response)

    def _stream_response(self, response: requests.Response) -> str:
        full_response = ""
        print(f"\n{colorama.Fore.GREEN}Claude:{colorama.Style.RESET_ALL} ", end="", flush=True)

        for chunk in self._parse_stream_response(response):
            if chunk:
                print(chunk, end="", flush=True)
                full_response += chunk
        print("\n")
        return full_response

    def _parse_stream_response(self, response: requests.Response) -> Generator[str, None, None]:
        for line in response.iter_lines():
            # logger.debug(f"{line=}")
            if not line:
                continue

            line_text = line.decode("utf-8")
            if not line_text.startswith("data: "):
                continue

            line_data = line_text[6:]  # Remove the "data: " prefix

            if line_data == "[DONE]":
                continue

            try:
                chunk_data = json.loads(line_data)
                # logger.debug(f"{chunk_data=}")

                try:
                    chunk = RequestStreamData.model_validate(chunk_data)
                    # logger.info(f"{chunk=}")
                except Exception:
                    # Fall back to direct dictionary access if model validation fails
                    chunk = chunk_data

                # Handle content blocks for newer Claude API versions
                if getattr(chunk, "type", None) == "content_block_delta" and getattr(chunk, "delta", None):
                    delta = chunk.delta
                    if hasattr(delta, "text") and delta.text:
                        # logger.debug(f"{delta=}")
                        yield delta.text

                    elif isinstance(delta, dict) and "text" in delta:
                        # logger.debug(f"{delta=}")
                        yield delta["text"]

                # Handle message deltas for newer Claude API versions
                elif getattr(chunk, "type", None) == "message_delta":
                    if hasattr(chunk, "delta") and hasattr(chunk.delta, "content"):
                        for content_block in chunk.delta.content or []:
                            if getattr(content_block, "type", None) == "text" and getattr(content_block, "text", None):
                                yield content_block.text

                    elif isinstance(chunk, dict) and "delta" in chunk and "content" in chunk["delta"]:
                        for content_block in chunk["delta"]["content"]:
                            if content_block.get("type") == "text" and "text" in content_block:
                                yield content_block["text"]

            except json.JSONDecodeError:
                continue
