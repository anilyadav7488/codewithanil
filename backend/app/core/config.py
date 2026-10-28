import os
import json
from typing import List, Union
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"
    )

    PROJECT_NAME: str = "CodeWithAnil"
    ENVIRONMENT: str = "development" # "development" | "production"
    API_V1_STR: str = "/api"
    SECRET_KEY: str = "codewithanil-development-secret-key-replace-in-production-32-chars-min"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 # 24 hours
    
    # Database
    DATABASE_URL: str = "sqlite:///./codewithanil.db"
    
    # CORS
    CORS_ORIGINS: Union[List[str], str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]
    
    # Machine Learning Settings
    HF_MODEL_NAME: str = "Hello-SimpleAI/chatgpt-detector-roberta"
    INFERENCE_BACKEND: str = "onnx_int8" # "onnx_int8" | "pytorch_fp32"
    ONNX_MODEL_PATH: str = "ml/models/roberta_chatgpt_detector_int8.onnx"
    TOKENIZER_DIR: str = "ml/models/tokenizer"
    INFERENCE_DEVICE: str = "cpu"
    MAX_SEQUENCE_LENGTH: int = 512
    INCONCLUSIVE_LOWER_THRESHOLD: float = 0.40
    INCONCLUSIVE_UPPER_THRESHOLD: float = 0.60
    
    # Document limits
    MAX_UPLOAD_SIZE_MB: int = 15
    RATE_LIMIT_PER_MINUTE: int = 60

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            v_str = v.strip()
            if v_str.startswith("[") and v_str.endswith("]"):
                try:
                    return json.loads(v_str)
                except Exception:
                    pass
            return [i.strip() for i in v_str.split(",") if i.strip()]
        elif isinstance(v, (list, tuple)):
            return list(v)
        return ["http://localhost:3000", "http://127.0.0.1:3000"]

settings = Settings()
