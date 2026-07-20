# CLAUDE.md — 주식회사 달구 게시판 (DALLGOO Board)

> 이 문서는 Claude Code가 본 프로젝트를 빌드·수정할 때 따르는 단일 기준 문서다.
> 새 코드를 생성하기 전에 항상 이 문서의 규칙(스키마 / API 명세 / 컨벤션)을 준수한다.

---

## 1. 프로젝트 개요

주식회사 달구(DALLGOO Inc.)의 게시판 웹 애플리케이션.
회원 인증과 게시판(글 / 댓글·대댓글 / 좋아요 / 파일 업로드)을 갖춘 풀스택 서비스.

- **백엔드**: Docker 컨테이너로 구동 (FastAPI + MySQL)
- **프론트엔드**: 로컬에서 `npm run dev` (Vite dev server)
- **인증**: JWT — Access Token + Refresh Token 병행

---

## 2. 기술 스택 (고정)

| 영역 | 선택 | 버전 |
|------|------|------|
| 백엔드 언어 | Python | 3.12 |
| 백엔드 프레임워크 | FastAPI | 0.115.x |
| ORM | SQLAlchemy 2.0 | 2.0.x |
| 마이그레이션 | Alembic | 1.14.x |
| DB | MySQL | 8.0 |
| DB 드라이버 | PyMySQL | 1.1.x |
| 인증 | python-jose (JWT) + passlib(bcrypt) | — |
| 프론트엔드 | Vue 3 + Vite | Vue 3.4 / Vite 5 |
| 상태관리 | Pinia | 2.x |
| 라우팅 | Vue Router | 4.x |
| HTTP 클라이언트 | Axios | 1.x |
| 컨테이너 | Docker Compose | v2 |

> 스택 변경 금지. 새 라이브러리 추가가 필요하면 먼저 `requirements.txt` / `package.json`에 반영하고 이 표를 갱신한다.

---

## 3. 아키텍처

```
┌─────────────────────────┐         ┌──────────────────────────────┐
│  Frontend (로컬)         │         │  Docker Compose               │
│  Vue3 + Vite             │  HTTP   │  ┌────────────┐ ┌──────────┐ │
│  localhost:5173          │ ──────► │  │ backend    │ │ db       │ │
│  (npm run dev)           │  /api   │  │ FastAPI    │─│ MySQL8.0 │ │
│  Vite proxy → :8000      │         │  │ :8000      │ │ :3306    │ │
└─────────────────────────┘         │  └────────────┘ └──────────┘ │
                                     │   volume: uploads, db_data    │
                                     └──────────────────────────────┘
```

- 프론트는 컨테이너 밖에서 실행. Vite `server.proxy`로 `/api` → `http://localhost:8000` 프록시.
- 업로드 파일은 도커 볼륨(`uploads`)에 저장. 컨테이너 재시작에도 보존.
- DB 데이터도 볼륨(`db_data`)에 보존.

---

## 4. 디렉토리 구조

```
dallgoo-board/
├── CLAUDE.md                 # 이 문서
├── docker-compose.yml
├── .env.example              # → 복사해서 .env 생성
├── .env                      # (git ignore) 실제 환경변수
├── .gitignore
│
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── alembic.ini
│   ├── alembic/
│   │   ├── env.py
│   │   └── versions/
│   ├── uploads/              # 업로드 파일 (볼륨 마운트)
│   └── app/
│       ├── main.py           # FastAPI 앱 진입점, 라우터 등록, CORS
│       ├── core/
│       │   ├── config.py     # pydantic-settings, .env 로드
│       │   ├── database.py   # engine, SessionLocal, Base, get_db
│       │   └── security.py   # 비밀번호 해싱, JWT 생성/검증
│       ├── models/           # SQLAlchemy ORM 모델
│       │   ├── __init__.py
│       │   ├── user.py
│       │   ├── post.py
│       │   ├── comment.py
│       │   ├── like.py
│       │   ├── file.py
│       │   └── token.py      # refresh_token, password_reset_token
│       ├── schemas/          # Pydantic 요청/응답 스키마
│       │   ├── user.py
│       │   ├── auth.py
│       │   ├── post.py
│       │   ├── comment.py
│       │   └── common.py     # 페이지네이션, 에러 응답
│       ├── crud/             # DB 접근 로직 (라우터와 분리)
│       │   ├── user.py
│       │   ├── post.py
│       │   ├── comment.py
│       │   └── like.py
│       └── api/
│           ├── deps.py       # get_current_user 등 의존성
│           └── routes/
│               ├── auth.py
│               ├── users.py
│               ├── posts.py
│               ├── comments.py
│               └── files.py
│
└── frontend/
    ├── package.json
    ├── vite.config.js        # /api proxy 설정 포함
    ├── index.html
    └── src/
        ├── main.js
        ├── App.vue
        ├── router/
        │   └── index.js      # 라우트 + 인증 가드
        ├── stores/
        │   ├── auth.js       # Pinia: 토큰, 로그인 상태
        │   └── post.js
        ├── api/
        │   ├── client.js     # axios 인스턴스 + 인터셉터(토큰 자동 갱신)
        │   ├── auth.js
        │   ├── post.js
        │   └── comment.js
        ├── views/
        │   ├── LoginView.vue
        │   ├── SignupView.vue
        │   ├── MyPageView.vue
        │   ├── PasswordResetView.vue
        │   ├── PostListView.vue
        │   ├── PostDetailView.vue
        │   ├── PostCreateView.vue
        │   └── PostEditView.vue
        └── components/
            ├── PostCard.vue
            ├── CommentList.vue
            ├── CommentItem.vue   # 대댓글 재귀 렌더
            ├── LikeButton.vue
            ├── FileUploader.vue
            └── Pagination.vue
```

---

## 5. 개발 환경 실행

### 최초 1회
```bash
# 1. 환경변수 준비
cp .env.example .env          # .env 안의 비밀번호/시크릿 값 수정

# 2. 백엔드 + DB 컨테이너 빌드 & 기동
docker compose up -d --build

# 3. DB 마이그레이션 (컨테이너 내부에서)
docker compose exec backend alembic upgrade head

# 4. 프론트엔드 의존성 설치 & 실행 (로컬)
cd frontend
npm install
npm run dev                   # http://localhost:5173
```

### 일상 명령어
```bash
docker compose up -d                         # 백엔드 기동
docker compose logs -f backend               # 백엔드 로그
docker compose exec backend bash             # 컨테이너 쉘 진입
docker compose down                          # 중지
docker compose down -v                       # 중지 + 볼륨 삭제(DB 초기화)

# 마이그레이션 생성/적용
docker compose exec backend alembic revision --autogenerate -m "메시지"
docker compose exec backend alembic upgrade head
```

- 백엔드 API 문서: `http://localhost:8000/docs` (Swagger), `http://localhost:8000/redoc`
- 백엔드 컨테이너는 `--reload` 모드라 코드 수정 시 자동 반영(볼륨 마운트).

---

## 6. 데이터베이스 스키마

> 모든 테이블에 `created_at`, `updated_at` (DATETIME, default now / on update now).
> PK는 `id BIGINT AUTO_INCREMENT`. 외래키는 인덱스 필수.

### users — 회원
| 컬럼 | 타입 | 제약 |
|------|------|------|
| id | BIGINT | PK |
| username | VARCHAR(50) | UNIQUE, NOT NULL — 로그인 아이디 |
| email | VARCHAR(255) | UNIQUE, NOT NULL |
| nickname | VARCHAR(50) | UNIQUE, NOT NULL |
| password_hash | VARCHAR(255) | NOT NULL |
| is_active | BOOLEAN | default TRUE — 탈퇴 시 소프트/하드 결정 |
| created_at / updated_at | DATETIME | |

### posts — 게시글
| 컬럼 | 타입 | 제약 |
|------|------|------|
| id | BIGINT | PK |
| user_id | BIGINT | FK→users.id, ON DELETE CASCADE, INDEX |
| title | VARCHAR(200) | NOT NULL |
| content | TEXT | NOT NULL |
| view_count | INT | default 0 |
| created_at / updated_at | DATETIME | INDEX(created_at) — 정렬용 |

### comments — 댓글 / 대댓글
| 컬럼 | 타입 | 제약 |
|------|------|------|
| id | BIGINT | PK |
| post_id | BIGINT | FK→posts.id, ON DELETE CASCADE, INDEX |
| user_id | BIGINT | FK→users.id, ON DELETE CASCADE, INDEX |
| parent_id | BIGINT | FK→comments.id, NULLABLE — 대댓글이면 부모 댓글 id |
| content | TEXT | NOT NULL |
| is_deleted | BOOLEAN | default FALSE — 자식 댓글 있을 때 "삭제된 댓글입니다" 표시용 |
| created_at / updated_at | DATETIME | |

> 대댓글은 1단계까지만(parent_id가 가리키는 댓글은 top-level이어야 함). UI는 댓글 → 대댓글 2계층.

### post_likes — 게시글 좋아요
| 컬럼 | 타입 | 제약 |
|------|------|------|
| id | BIGINT | PK |
| post_id | BIGINT | FK→posts.id, ON DELETE CASCADE |
| user_id | BIGINT | FK→users.id, ON DELETE CASCADE |
| | | **UNIQUE(post_id, user_id)** — 중복 좋아요 방지 |

### comment_likes — 댓글 좋아요
| 컬럼 | 타입 | 제약 |
|------|------|------|
| id | BIGINT | PK |
| comment_id | BIGINT | FK→comments.id, ON DELETE CASCADE |
| user_id | BIGINT | FK→users.id, ON DELETE CASCADE |
| | | **UNIQUE(comment_id, user_id)** |

### files — 첨부파일
| 컬럼 | 타입 | 제약 |
|------|------|------|
| id | BIGINT | PK |
| post_id | BIGINT | FK→posts.id, **ON DELETE CASCADE**, INDEX |
| original_name | VARCHAR(255) | 원본 파일명 |
| stored_name | VARCHAR(255) | 서버 저장명 (UUID 기반) |
| file_size | BIGINT | 바이트 |
| content_type | VARCHAR(100) | MIME |
| created_at | DATETIME | |

> **글 삭제 시 첨부파일 동시 삭제**: DB는 CASCADE로 레코드 삭제 + CRUD 로직에서 디스크의 실제 파일(`uploads/`)도 `os.remove`로 삭제한다. 둘 다 반드시 처리.

### refresh_tokens — 리프레시 토큰
| 컬럼 | 타입 | 제약 |
|------|------|------|
| id | BIGINT | PK |
| user_id | BIGINT | FK→users.id, ON DELETE CASCADE, INDEX |
| token | VARCHAR(512) | UNIQUE — 해시 저장 권장 |
| expires_at | DATETIME | |
| revoked | BOOLEAN | default FALSE |

### password_reset_tokens — 비밀번호 재설정
| 컬럼 | 타입 | 제약 |
|------|------|------|
| id | BIGINT | PK |
| user_id | BIGINT | FK→users.id |
| token | VARCHAR(255) | UNIQUE |
| expires_at | DATETIME | 발급 후 30분 |
| used | BOOLEAN | default FALSE |

### site_settings — 사이트 운영 설정 (key-value)
| 컬럼 | 타입 | 제약 |
|------|------|------|
| key | VARCHAR(50) | PK — 설정 키 |
| value | TEXT | NOT NULL — 설정 값 |
| updated_at | DATETIME | on update now |

> 관리자가 코드 수정 없이 바꾸는 값을 담는다. **설정이 늘어나도 마이그레이션 없이** 키만 추가하면 되도록 key-value 한 테이블로 둔다.
> 허용 키와 기본값은 `crud/setting.py`의 `DEFAULTS`에서 관리하며, **DEFAULTS에 없는 키는 저장을 거부**한다(임의 키 주입 방지).
> 레코드가 없으면 기본값을 쓰므로 초기 시딩이 필요 없다.
> 현재 키: `intro_video_url` — 랜딩 회사 소개 영상(유튜브 주소).

---

## 7. API 명세

- 기본 prefix: `/api`
- 인증 필요 표시: 🔒 (Authorization: `Bearer <access_token>`)
- 성공 응답: `2xx` + JSON body. 실패: 공통 에러 포맷(§9).

### 7.1 인증 / 회원 — `/api/auth`, `/api/users`

| Method | Path | 인증 | 설명 | Body / Query |
|--------|------|------|------|------|
| POST | `/auth/signup` | — | 회원가입 | `{username, email, nickname, password}` |
| GET | `/auth/check-username` | — | 아이디 중복확인 | `?username=` → `{available: bool}` |
| GET | `/auth/check-email` | — | 이메일 중복확인 | `?email=` |
| GET | `/auth/check-nickname` | — | 닉네임 중복확인 | `?nickname=` |
| POST | `/auth/login` | — | 로그인 | `{username, password}` → `{access_token, refresh_token, token_type}` |
| POST | `/auth/logout` | 🔒 | 로그아웃 | refresh_token revoke |
| POST | `/auth/refresh` | — | 토큰 재발급 | `{refresh_token}` → 새 access(+refresh) |
| POST | `/auth/password/forgot` | — | 비밀번호 찾기(재설정 토큰 발급) | `{email}` |
| POST | `/auth/password/reset` | — | 비밀번호 재설정 | `{token, new_password}` |
| GET | `/users/me` | 🔒 | 마이페이지(내 정보) | → user + 내 글/댓글 수 |
| PATCH | `/users/me` | 🔒 | 회원정보 수정 | `{nickname?, email?}` |
| PATCH | `/users/me/password` | 🔒 | 비밀번호 변경 | `{current_password, new_password}` |
| DELETE | `/users/me` | 🔒 | 회원 탈퇴 | `{password}` 확인 |

### 7.2 게시글 — `/api/posts`

| Method | Path | 인증 | 설명 |
|--------|------|------|------|
| POST | `/posts` | 🔒 | 글쓰기 (multipart: title, content, files[]) |
| GET | `/posts` | — | 목록 + 페이지네이션 + 검색 + 정렬 |
| GET | `/posts/{id}` | — | 상세 (조회수 +1, 댓글·파일·좋아요수 포함) |
| PATCH | `/posts/{id}` | 🔒 | 수정 (작성자만) |
| DELETE | `/posts/{id}` | 🔒 | 삭제 (작성자만, 첨부파일 동시 삭제) |
| POST | `/posts/{id}/like` | 🔒 | 좋아요 |
| DELETE | `/posts/{id}/like` | 🔒 | 좋아요 취소 |

**목록 쿼리 파라미터** (`GET /posts`):
- `page` (default 1), `size` (default 10, max 50)
- `sort`: `latest`(default) | `oldest` | `views` | `likes`
- `search_type`: `title` | `content` | `title_content` | `author`
- `keyword`: 검색어 (없으면 전체)
- 응답: §9 페이지네이션 포맷

### 7.3 댓글 — `/api/posts/{post_id}/comments`, `/api/comments`

| Method | Path | 인증 | 설명 |
|--------|------|------|------|
| GET | `/posts/{post_id}/comments` | — | 댓글 목록 (대댓글 중첩 구조) |
| POST | `/posts/{post_id}/comments` | 🔒 | 댓글/대댓글 작성 (`{content, parent_id?}`) |
| PATCH | `/comments/{id}` | 🔒 | 댓글 수정 (작성자만) |
| DELETE | `/comments/{id}` | 🔒 | 댓글 삭제 (작성자만, 자식 있으면 soft delete) |
| POST | `/comments/{id}/like` | 🔒 | 댓글 좋아요 |
| DELETE | `/comments/{id}/like` | 🔒 | 댓글 좋아요 취소 |

### 7.4 파일 — `/api/files`

| Method | Path | 인증 | 설명 |
|--------|------|------|------|
| GET | `/files/{id}/download` | — | 첨부파일 다운로드 |
| DELETE | `/files/{id}` | 🔒 | 파일 개별 삭제 (글 작성자만) |

> 파일 업로드는 글 작성/수정 API에서 multipart로 처리. 별도 업로드 엔드포인트는 선택사항.

### 7.5 사이트 설정 — `/api/settings`

| Method | Path | 인증 | 설명 |
|--------|------|------|------|
| GET | `/settings` | — | 공개 설정 조회 (랜딩페이지가 비로그인으로 호출) |
| PATCH | `/settings` | 🔒 관리자 | 설정 변경 → 변경된 전체 설정 반환 |

**`intro_video_url`** — 랜딩 회사 소개 영상.
- `watch?v=` / `youtu.be` / `shorts` / `embed` / 11자리 ID 전부 입력 가능. 저장 시 `https://www.youtube.com/watch?v={ID}` **표준형으로 정규화**해 프론트가 형태를 신경 쓰지 않게 한다.
- 유튜브 주소가 아니면 422(한국어 메시지). 빈 문자열은 허용 — 영상 섹션이 자리표시로 바뀐다.
- 관리자 전용은 `PATCH`뿐. `GET`은 비로그인 공개다(랜딩이 써야 하므로).

---

## 8. 인증 플로우 (JWT — Access + Refresh)

```
[로그인]
  POST /auth/login {username, password}
  → 비밀번호 검증(bcrypt)
  → access_token(만료 30분) + refresh_token(만료 14일) 발급
  → refresh_token은 DB(refresh_tokens)에 저장

[보호된 요청]
  Authorization: Bearer <access_token>
  → deps.get_current_user 에서 access_token 검증 → user 주입

[access 만료]
  401 수신 → 프론트 axios 인터셉터가 자동으로
  POST /auth/refresh {refresh_token}
  → DB의 refresh_token 유효성/revoked 확인
  → 새 access_token 발급 (+ refresh 회전 시 새 refresh도 발급, 기존 revoke)
  → 원래 요청 재시도

[로그아웃]
  POST /auth/logout → 해당 refresh_token revoked = TRUE

[탈퇴]
  DELETE /users/me → 사용자의 모든 refresh_token revoke + 계정 처리
```

규칙:
- Access는 짧게(30분), Refresh는 길게(14일). 값은 `.env`로 조정.
- Refresh Token Rotation 적용(재발급 시 기존 토큰 revoke) — 탈취 방어.
- 비밀번호는 절대 평문 저장/로깅 금지. bcrypt 해시만 저장.
- access token에는 `sub`(user_id), `exp`, `type: "access"`. refresh에는 `type: "refresh"`.
- 프론트 토큰 저장: 학습/내부용 → access는 메모리(Pinia), refresh는 localStorage 허용.
  운영 강화 시 refresh는 httpOnly 쿠키로 전환(이 경우 `/auth/refresh`는 쿠키 기반으로 변경).

---

## 9. 공통 응답 포맷

### 페이지네이션
```json
{
  "items": [ ... ],
  "page": 1,
  "size": 10,
  "total": 137,
  "total_pages": 14
}
```

### 에러
```json
{
  "detail": "이미 사용 중인 닉네임입니다.",
  "code": "NICKNAME_DUPLICATE"
}
```
- HTTP status 적절히 사용: 400 / 401 / 403 / 404 / 409(중복) / 422(검증).
- FastAPI 전역 exception handler로 포맷 통일.
- 사용자에게 보이는 메시지는 한국어.

---

## 10. 코딩 컨벤션

### 백엔드 (Python / FastAPI)
- 레이어 분리 엄수: `routes`(HTTP) → `crud`(DB) → `models`. 라우터에 비즈니스 로직·쿼리 직접 작성 금지.
- 모든 DB 세션은 `Depends(get_db)`로 주입.
- 요청/응답은 반드시 Pydantic 스키마로. ORM 모델을 그대로 응답에 노출 금지(`from_attributes=True`로 변환).
- 비밀번호·토큰은 응답 스키마에서 제외.
- 타입힌트 필수. async 라우터 사용, DB는 동기 SQLAlchemy(혼용 주의 — `run_in_threadpool` 불필요하게 쓰지 말 것).
- 네이밍: 함수/변수 snake_case, 클래스 PascalCase.

### 프론트엔드 (Vue 3)
- Composition API + `<script setup>` 사용.
- API 호출은 `src/api/*`로 일원화. 컴포넌트에서 axios 직접 호출 금지.
- 인증 상태는 Pinia `auth` store 단일 소스.
- axios 인터셉터에서 401 → refresh 자동 처리(§8). 무한 루프 방지(refresh 자체 실패 시 로그아웃).
- 라우터 가드로 인증 필요 페이지 보호(`meta: { requiresAuth: true }`).
- 컴포넌트 PascalCase 파일명.

### 공통
- 커밋 메시지: `feat:`, `fix:`, `refactor:`, `chore:` prefix.
- 시크릿/비밀번호는 코드·로그·커밋에 절대 포함 금지. `.env`만 사용.

---

## 11. 파일 업로드 규칙

- 저장 위치: `backend/uploads/` (도커 볼륨). 파일명은 `{uuid4}.{ext}`로 충돌 방지.
- 허용 확장자/용량은 `.env`의 `MAX_UPLOAD_SIZE_MB`로 제한(기본 10MB). 검증 실패 시 422.
- 한 글에 다중 파일 허용.
- **글 삭제 시**: `files` 레코드 CASCADE 삭제 + `crud/post.delete`에서 디스크 실제 파일 삭제까지 수행.
- 다운로드는 `FileResponse`로 `original_name` 보존(Content-Disposition).

---

## 12. 보안 체크리스트

- [ ] 비밀번호 bcrypt 해싱, 평문 미저장
- [ ] JWT 시크릿은 충분히 긴 랜덤값(`.env`)
- [ ] Refresh Token Rotation + revoke
- [ ] 작성자 검증: 글/댓글 수정·삭제는 본인만(403)
- [ ] CORS는 프론트 origin만 허용
- [ ] SQL은 ORM 사용(인젝션 방지). raw query 지양
- [ ] 파일 업로드 확장자·용량 검증, 경로 traversal 방지(저장명 UUID 강제)
- [ ] 중복확인/회원가입에서 username·email·nickname 각각 UNIQUE 보장
- [ ] 에러 응답에 스택트레이스·내부정보 노출 금지

---

## 13. 구현 순서 (권장 빌드 단계)

1. **인프라**: `docker-compose.yml`, `backend/Dockerfile`, `.env`, `config.py`, `database.py` → 컨테이너 기동 + DB 연결 확인.
2. **모델 & 마이그레이션**: 전체 ORM 모델 작성 → `alembic upgrade head`.
3. **인증**: `security.py`(해싱/JWT), `auth` 라우트(회원가입·중복확인·로그인·refresh·로그아웃), `deps.get_current_user`.
4. **회원**: `users/me` CRUD(마이페이지·수정·비번변경·탈퇴), 비밀번호 찾기/재설정.
5. **게시글**: CRUD + 목록(페이지네이션·검색·정렬) + 좋아요.
6. **댓글**: 작성·대댓글·수정·삭제 + 좋아요.
7. **파일**: 업로드(글 작성/수정 연동) + 다운로드 + 글 삭제 시 파일 삭제.
8. **프론트엔드**: 라우터/스토어/axios 인터셉터 → 로그인·회원가입 → 게시판 목록·상세·작성 → 댓글·좋아요·파일 UI.
9. **마무리**: 에러 포맷 통일, CORS, README, 시드 데이터(선택).

---

## 14. 환경변수 (`.env`)

`.env.example` 복사 후 사용. 핵심 키:

| 키 | 설명 |
|----|------|
| `MYSQL_DATABASE` / `MYSQL_USER` / `MYSQL_PASSWORD` / `MYSQL_ROOT_PASSWORD` | MySQL 컨테이너 초기화 |
| `DATABASE_URL` | 백엔드 DB 접속 (`mysql+pymysql://user:pw@db:3306/dbname`) — 호스트는 `db`(컨테이너명) |
| `JWT_SECRET_KEY` | JWT 서명 시크릿 (긴 랜덤값) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | 기본 30 |
| `REFRESH_TOKEN_EXPIRE_DAYS` | 기본 14 |
| `CORS_ORIGINS` | `http://localhost:5173` |
| `MAX_UPLOAD_SIZE_MB` | 기본 10 |

> 운영 전환 시: `--reload` 제거, 시크릿 교체, refresh 토큰 쿠키화, HTTPS 적용.

---

## 15. 빠른 참조 (Claude Code 작업 시)

- 새 API는 §7 명세에 먼저 추가 → 라우트/스키마/CRUD 동시 작성.
- 새 테이블·컬럼은 §6 갱신 → 모델 수정 → alembic revision 생성.
- 응답 포맷은 §9 고정. 에러는 한국어 메시지.
- 인증 동작은 §8을 단일 기준으로. 임의로 토큰 정책 바꾸지 말 것.
- 글/댓글 수정·삭제는 항상 작성자 검증.
