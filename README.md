# Kakao Dify Adapter for Vercel

카카오 챗봇 스킬 요청을 받아 Vercel 위의 FastAPI 함수에서 처리하는 프로젝트입니다.

현재 기본 동작은 아래 순서입니다.

```text
Kakao
  -> /kakao/webhook
  -> FastAPI on Vercel
  -> 즉시 useCallback=true 응답
  -> 백그라운드에서 echo 또는 Dify 호출
  -> callbackUrl 로 최종 말풍선 전송
```

`callbackUrl`이 없는 경우에는 자동으로 동기 `simpleText` 응답으로 폴백됩니다. 이 덕분에 카카오 콜백 미지원 상황이나 단순 로컬 테스트에서도 동작합니다.

## 파일 구조

- `api/index.py`: Vercel Python Runtime 엔트리포인트
- `src/app.py`: FastAPI 앱과 라우트
- `src/models.py`: 카카오 요청/응답 모델
- `src/services/callback.py`: callbackUrl 후속 전송 처리
- `src/services/dify.py`: Dify API 호출
- `vercel.json`: 서울 리전(`icn1`)과 루트 rewrite 설정

## 환경 변수

`.env.example`를 복사해 `.env`로 시작하세요.

```dotenv
APP_ENV=development
BACKEND=echo
ECHO_PREFIX=echo:

# BACKEND=dify일 때
DIFY_BASE_URL=https://your-dify-host/v1
DIFY_API_KEY=app-xxxxxxxx
```

## 로컬 실행

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env
uvicorn api.index:app --reload --port 8000
```

기본 확인:

```bash
curl http://127.0.0.1:8000/health
```

동기 응답 확인:

```bash
curl -X POST http://127.0.0.1:8000/kakao/webhook \
  -H 'Content-Type: application/json' \
  -d '{
    "userRequest": {
      "utterance": "안녕",
      "user": {
        "id": "demo-user",
        "type": "botUserKey"
      }
    }
  }'
```

콜백 흐름 로컬 확인:

1. 먼저 아래 주소를 callbackUrl로 넣어 호출합니다.

```text
http://127.0.0.1:8000/debug/callback-sink
```

2. webhook 호출:

```bash
curl -X POST http://127.0.0.1:8000/kakao/webhook \
  -H 'Content-Type: application/json' \
  -d '{
    "userRequest": {
      "callbackUrl": "http://127.0.0.1:8000/debug/callback-sink",
      "utterance": "콜백 테스트",
      "user": {
        "id": "demo-user",
        "type": "botUserKey"
      }
    }
  }'
```

3. 최종 callback payload 확인:

```bash
curl http://127.0.0.1:8000/debug/callback-sink
```

## Vercel 배포

1. GitHub에 푸시합니다.
2. Vercel에서 Import Project를 선택합니다.
3. Framework Preset은 따로 필요 없습니다.
4. Python 의존성은 `requirements.txt`로 자동 설치됩니다.
5. 환경 변수에 `BACKEND`, `DIFY_BASE_URL`, `DIFY_API_KEY` 등을 넣습니다.
6. 배포 후 `https://<your-project>.vercel.app/health`를 먼저 확인합니다.
7. 카카오 챗봇 스킬 URL은 `https://<your-project>.vercel.app/kakao/webhook`를 사용합니다.

## 중요한 메모

- 카카오 callback 기능은 챗봇 관리자센터의 AI 챗봇 callback 설정이 켜진 블록에서만 동작합니다.
- 카카오 문서 기준 callbackUrl은 1분 유효, 1회 사용입니다.
- `BackgroundTasks` 기반이라 MVP에는 적합하지만, 운영 안정성이 중요하면 큐/워커 구조로 바꾸는 편이 더 안전합니다.
- Dify 대화 ID 저장소는 현재 메모리 기반이라 인스턴스 재시작 후 대화 맥락이 사라질 수 있습니다.

