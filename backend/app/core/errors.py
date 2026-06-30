from fastapi import HTTPException, status


class AppError(HTTPException):
    """공통 에러 — detail(한국어) + code(머신용)."""

    def __init__(self, status_code: int, detail: str, code: str):
        super().__init__(status_code=status_code, detail=detail)
        self.code = code


def not_found(detail: str = "대상을 찾을 수 없습니다.", code: str = "NOT_FOUND") -> AppError:
    return AppError(status.HTTP_404_NOT_FOUND, detail, code)


def forbidden(detail: str = "권한이 없습니다.", code: str = "FORBIDDEN") -> AppError:
    return AppError(status.HTTP_403_FORBIDDEN, detail, code)


def conflict(detail: str, code: str = "CONFLICT") -> AppError:
    return AppError(status.HTTP_409_CONFLICT, detail, code)


def bad_request(detail: str, code: str = "BAD_REQUEST") -> AppError:
    return AppError(status.HTTP_400_BAD_REQUEST, detail, code)


def unauthorized(detail: str = "인증이 필요합니다.", code: str = "UNAUTHORIZED") -> AppError:
    return AppError(status.HTTP_401_UNAUTHORIZED, detail, code)


def too_many(detail: str, code: str = "TOO_MANY_ATTEMPTS") -> AppError:
    return AppError(status.HTTP_429_TOO_MANY_REQUESTS, detail, code)
