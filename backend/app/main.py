import json

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from sqlalchemy.exc import IntegrityError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.base import BaseHTTPMiddleware

from app.api.routes import (
    admin,
    auth,
    comments,
    files,
    notifications,
    posts,
    transport,
    users,
)
from app.core.config import settings
from app.core.errors import AppError

# 검증 에러 메시지를 한국어로 — 필드명 매핑
_FIELD_KR = {
    "username": "아이디",
    "email": "이메일",
    "nickname": "닉네임",
    "password": "비밀번호",
    "new_password": "새 비밀번호",
    "current_password": "현재 비밀번호",
    "title": "제목",
    "content": "내용",
}


def _error_field(err: dict) -> str:
    loc = err.get("loc", [])
    return next(
        (str(p) for p in reversed(loc) if str(p) not in ("body", "query", "path")),
        "",
    )


def _error_message(err: dict) -> str:
    field = _error_field(err)
    etype = err.get("type", "")
    msg = err.get("msg", "")
    if etype == "missing":
        return f"{_FIELD_KR.get(field, field)} 항목을 입력해주세요."
    # 커스텀 validator가 던진 한국어 메시지: "Value error, <메시지>"
    if msg.startswith("Value error, "):
        return msg[len("Value error, ") :]
    if field == "email":
        return "올바른 이메일 형식이 아닙니다."
    return f"{_FIELD_KR.get(field, '입력값')} 형식이 올바르지 않습니다."


def envelope(success: bool, code: str, message, data):
    return {"success": success, "code": code, "message": message, "data": data}


app = FastAPI(title="DALLGOO Board API", version="1.0.0")


# ===========================================================
# 공통 응답 봉투 미들웨어 (CLAUDE.md §9)
#   - /api 하위의 성공 JSON 응답을 {success, code, message, data}로 감싼다.
#   - 이미 봉투면 통과, 파일 다운로드(스트리밍)·문서(/docs)·비JSON은 제외.
#   - 28개 엔드포인트를 개별 수정하지 않기 위한 단일 지점.
# ===========================================================
class ResponseEnvelopeMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        if not request.url.path.startswith("/api"):
            return response
        ctype = response.headers.get("content-type", "")
        if not ctype.startswith("application/json"):
            return response  # 파일 다운로드 등은 그대로

        body = b""
        async for chunk in response.body_iterator:
            body += chunk
        try:
            payload = json.loads(body)
        except (ValueError, UnicodeDecodeError):
            return Response(
                content=body,
                status_code=response.status_code,
                media_type=ctype,
            )

        # 이미 봉투 형태면 그대로 재전송
        if isinstance(payload, dict) and "success" in payload and "data" in payload:
            wrapped = payload
        elif response.status_code < 400:
            # 메시지만 반환하는 응답({"detail": "..."})은 message로, 나머지는 data로
            if isinstance(payload, dict) and set(payload.keys()) == {"detail"}:
                wrapped = envelope(True, "SUCCESS", payload["detail"], None)
            else:
                wrapped = envelope(True, "SUCCESS", None, payload)
        else:
            # 우리 핸들러를 거치지 않은 기본 에러(404/405 등)도 봉투로
            detail = payload.get("detail") if isinstance(payload, dict) else str(payload)
            code = payload.get("code", "ERROR") if isinstance(payload, dict) else "ERROR"
            wrapped = envelope(False, code, detail, None)

        return JSONResponse(content=wrapped, status_code=response.status_code)


# 미들웨어 등록 순서: 안쪽(Envelope) → 바깥(CORS). CORS가 최종 응답에 헤더를 단다.
app.add_middleware(ResponseEnvelopeMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ===== 공통 에러 봉투 =====
@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    return JSONResponse(
        status_code=exc.status_code,
        content=envelope(False, exc.code, exc.detail, None),
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=envelope(False, "HTTP_ERROR", exc.detail, None),
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    field_errors = [
        {"field": _error_field(e), "message": _error_message(e)} for e in errors
    ]
    # 사용자에게 보일 대표 메시지는 첫 필드 메시지로(데이터 errors에 전체 동봉).
    top = field_errors[0]["message"] if field_errors else "입력값을 확인해주세요."
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=envelope(False, "VALIDATION_ERROR", top, {"errors": field_errors}),
    )


@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError):
    # UNIQUE 제약 등 — 라우트에서 못 잡은 경우의 최종 방어선.
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content=envelope(False, "DUPLICATE", "이미 사용 중인 값입니다.", None),
    )


# ===== 라우터 등록 (prefix: /api) =====
api_prefix = "/api"
app.include_router(auth.router, prefix=api_prefix)
app.include_router(users.router, prefix=api_prefix)
app.include_router(posts.router, prefix=api_prefix)
app.include_router(comments.post_router, prefix=api_prefix)
app.include_router(comments.router, prefix=api_prefix)
app.include_router(files.router, prefix=api_prefix)
app.include_router(admin.router, prefix=api_prefix)
app.include_router(notifications.router, prefix=api_prefix)
app.include_router(transport.router, prefix=api_prefix)


@app.get("/api/health", tags=["health"])
def health():
    return {"status": "ok"}
