# 달구 게시판 (DALLGOO Board)

회원 인증 + 게시판(글 / 댓글·대댓글 / 좋아요 / 파일 업로드)을 갖춘 풀스택 웹 애플리케이션.

- **백엔드**: FastAPI + SQLAlchemy 2.0 + MySQL 8.0 (Docker)
- **프론트엔드**: Vue 3 + Vite + Pinia (로컬 dev 서버)
- **인증**: JWT (Access 30분 + Refresh 14일, Rotation)

상세 규칙·스키마·API 명세는 [CLAUDE.md](./CLAUDE.md) 참고.

---

## 실행 방법

### 1. 백엔드 (Docker)

```bash
# 1) 환경변수 준비 (이미 .env가 있으면 생략 가능)
cp .env.example .env        # 필요 시 비밀번호/시크릿 수정

# 2) 컨테이너 빌드 & 기동 (backend + MySQL)
docker compose up -d --build

# 3) DB 마이그레이션 적용
docker compose exec backend alembic upgrade head
```

- API 문서(Swagger): http://localhost:8000/docs
- 헬스체크: http://localhost:8000/api/health

> 폴더명이 한글이라 `docker compose`가 프로젝트명을 못 정하는 문제를 막기 위해
> `docker-compose.yml`에 `name: dallgoo-board`를 박아두었습니다. 그냥 `docker compose up`만 치면 됩니다.

### 2. 프론트엔드 (로컬)

```bash
cd frontend
npm install
npm run dev                 # http://localhost:5173
```

Vite dev server가 `/api` 요청을 `http://localhost:8000`(백엔드 컨테이너)로 프록시합니다.

---

## 자주 쓰는 명령어

```bash
docker compose logs -f backend                  # 백엔드 로그
docker compose exec backend bash                # 컨테이너 접속
docker compose down                             # 중지
docker compose down -v                          # 중지 + 볼륨 삭제(DB 초기화)

# 마이그레이션 새로 생성
docker compose exec backend alembic revision --autogenerate -m "메시지"
docker compose exec backend alembic upgrade head
```

---

## 디렉터리

```
달구_게시판/
├── docker-compose.yml
├── .env / .env.example
├── backend/            # FastAPI (Dockerfile, alembic, app/)
│   └── app/
│       ├── core/       # config, database, security, errors
│       ├── models/     # SQLAlchemy ORM
│       ├── schemas/    # Pydantic
│       ├── crud/       # DB 접근 로직
│       └── api/routes/ # auth, users, posts, comments, files
└── frontend/           # Vue 3 + Vite
    └── src/
        ├── api/        # axios client + 인터셉터(토큰 자동 갱신)
        ├── stores/     # Pinia (auth, post)
        ├── router/
        ├── views/
        └── components/
```

---

## 참고

- 비밀번호 찾기/재설정은 메일 발송 인프라가 없어, 학습용으로 `/auth/password/forgot`
  응답에 재설정 토큰을 직접 반환합니다. (실서비스 전환 시 메일 발송으로 교체)
- 토큰 저장: access는 메모리(Pinia), refresh는 localStorage.
  운영 강화 시 refresh를 httpOnly 쿠키로 전환하는 것을 권장합니다.
