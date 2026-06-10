import os
import logging
import warnings

logging.getLogger("google_genai.models").addFilter(
    lambda r: "AFC is disabled" not in r.getMessage()
)

warnings.filterwarnings(
    "ignore", message=".*quota project.*", module="google.auth._default"
)

# Agent Runtime のデプロイリージョンとは独立して
# モデル推論は常に global エンドポイントを使うよう強制
os.environ["GOOGLE_CLOUD_LOCATION"] = "global"

from . import agent
