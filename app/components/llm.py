from langchain_openai import ChatOpenAI
from app.config.config import OPENROUTER_API_KEY, LLM_MODEL
from app.common.logger import get_logger
from app.common.custom_exception import CustomException

logger = get_logger(__name__)

def load_llm(
    model_name: str = LLM_MODEL,
    openrouter_api_key: str = OPENROUTER_API_KEY,
    temperature: float = 0.0,
    max_tokens: int = 1024,
):
    try:
        logger.info(f"Loading LLM via OpenRouter ({model_name})...")

        if not openrouter_api_key:
            raise CustomException("OPENROUTER_API_KEY is not set or missing.")

        llm = ChatOpenAI(
            model=model_name,
            openai_api_key=openrouter_api_key,
            openai_api_base="https://openrouter.ai/api/v1",
            temperature=temperature,
            max_tokens=max_tokens,
        )

        logger.info("LLM loaded successfully from OpenRouter.")
        return llm

    except Exception as e:
        error_message = CustomException("Failed to load LLM from OpenRouter", e)
        logger.error(str(error_message))
        return None
