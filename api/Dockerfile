# # Python 3.12 slim 이미지 사용
# # Use Python 3.12 slim image
# FROM python:3.12-slim-bookworm

# # 작업 디렉토리 설정
# # Set working directory
# WORKDIR /app

# # 최신 uv 바이너리 복사
# # Copy the latest uv binaries
# COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# # 실행 파일을 환경 경로의 앞에 배치
# # Place executables in the environment at the front of the path
# # Ref: https://docs.astral.sh/uv/guides/integration/docker/#using-the-environment
# ENV PATH="/app/.venv/bin:$PATH"

# # 바이트코드 컴파일
# # Compile bytecode
# # Ref: https://docs.astral.sh/uv/guides/integration/docker/#compiling-bytecode
# ENV UV_COMPILE_BYTECODE=1

# # uv 캐시
# # uv Cache
# # Ref: https://docs.astral.sh/uv/guides/integration/docker/#caching
# ENV UV_LINK_MODE=copy

# # 시스템 의존성 설치 (PostgreSQL 클라이언트 등)
# # Install system dependencies (e.g., PostgreSQL client)
# RUN apt-get update && apt-get install -y \
#     gcc \
#     g++ \
#     libpq-dev \
#     curl \
#     ca-certificates \
#     && rm -rf /var/lib/apt/lists/*

# # Python 의존성 파일 복사
# # Copy Python dependency file
# COPY requirements.txt ./

# # uv를 사용하여 의존성 설치 (production 환경)
# # Install dependencies using uv (production environment)
# RUN --mount=type=cache,target=/root/.cache/uv \
#     --mount=type=bind,source=uv.lock,target=uv.lock \
#     --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
#     uv sync --frozen --no-install-project

# # 애플리케이션 코드 복사
# # Copy application code
# COPY . .

# # 프로젝트 동기화
# # Sync the project
# # Ref: https://docs.astral.sh/uv/guides/integration/docker/#intermediate-layers
# RUN --mount=type=cache,target=/root/.cache/uv \
#     uv sync

# # 포트 8000 노출
# # Expose port 8000
# EXPOSE 8000

# # 비루트 사용자 생성 및 전환
# # Create and switch to non-root user
# # RUN useradd -m -s /bin/bash appuser && chown -R appuser:appuser /app
# # USER appuser

# # FastAPI 애플리케이션 실행
# # Run FastAPI application
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"] 






FROM python:3.12-slim-bookworm

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
ENV PATH="/app/.venv/bin:$PATH"
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

RUN apt-get update && apt-get install -y \
    gcc g++ libpq-dev curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project

COPY . .

# Create non-root user to match host UID/GID
ARG API_UID=1000
ARG API_GID=1000
RUN groupadd -g $API_GID apiuser \
    && useradd -m -u $API_UID -g apiuser apiuser \
    && chown -R apiuser:apiuser /app

USER apiuser

# Set environment variables
ENV DATA_PATH=/shared-data
ENV API_PORT=${API_PORT:-8005}

# Expose API port
EXPOSE ${API_PORT:-8005}

# Run FastAPI - now main.py is at /app/app/main.py, so we use app.main:app
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8005"]
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
