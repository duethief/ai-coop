# AI-Coop: AI Agent 기반 협업 개발 플랫폼 (Phase 1 MVP)

여러 개발자가 각자 보유한 AI 서비스(Claude Max, Gemini Pro, ChatGPT/Codex 등)를 프로젝트의 공동 개발 자원(AI Resource Pool)으로 제공하고, 자율 코딩 에이전트를 통해 개발 파이프라인을 자동화하는 플랫폼의 **Phase 1: Core Pipeline MVP** 구현체입니다.

---

## 🚀 Phase 1 주요 기능

1. **Autonomous Issue-to-PR Pipeline**:
   * 자연어 태스크 또는 GitHub Issue 번호를 입력받아 전용 Feature Branch를 자동 생성합니다.
   * 코딩 에이전트(Antigravity SDK / Aider / Gemini CLI)가 코드를 분석 및 수정합니다.
   * `QualityGate`가 단위 테스트 및 린트를 실행하고, 실패 시 에러 로그를 분석하여 최대 N회 자동 피드백/재수정 루프를 수행합니다.
   * 테스트 통과 시 구조화된 커밋을 생성하고 원격 리포지토리에 푸시하여 Pull Request를 자동 발행합니다.

2. **Pluggable Agent Runner Architecture**:
   * **AntigravityRunner**: Google Antigravity Python SDK (`google-antigravity`) 기반의 네이티브 비동기 에이전트 러너. (개발자 로컬 인증 직접 활용, 사고 및 도구 실행 실시간 가로채기 지원)
   * **AiderRunner**: Aider CLI 기반의 헤드리스 서브프로세스 러너. (Tree-sitter repo-map 및 다중 모델 지원)
   * **GeminiCliRunner**: Gemini CLI (`gemini-cli`) 기반 러너. (대용량 컨텍스트 윈도우 지원)

3. **Robust Safety & Quality Gate**:
   * 미커밋 변경사항 감지 및 격리된 브랜치 분기 (`GitManager`)
   * 실패 시 안전한 롤백 (`rollback_changes`)
   * 컨텍스트 폭발을 방지하는 스마트 에러 로그 요약 추출기 (`QualityGate`)

---

## 📂 프로젝트 구조

```text
d:\dev\ai\ai-coop\
├── src\
│   └── aicoop\
│       ├── __init__.py               # 패키지 메타데이터
│       ├── config.py                 # Pydantic 기반 환경설정
│       ├── cli.py                    # Typer 기반 CLI 엔트리포인트
│       ├── core\
│       │   ├── task.py               # Task 데이터 모델 및 생명주기
│       │   ├── git_manager.py        # Git 브랜치, 커밋, diff, 롤백 관리
│       │   ├── quality_gate.py       # 테스트 실행 및 에러 요약 추출
│       │   ├── github_client.py      # GitHub Issue 및 PR 연동 클라이언트
│       │   └── pipeline.py           # Core E2E 오케스트레이터 (피드백 루프)
│       ├── runners\
│       │   ├── __init__.py           # 에이전트 러너 팩토리
│       │   ├── base.py               # 러너 추상 인터페이스
│       │   ├── antigravity_runner.py # Google Antigravity SDK/CLI 러너
│       │   ├── aider_runner.py       # Aider CLI 러너
│       │   └── gemini_runner.py      # Gemini CLI 러너
│       └── utils\
│           └── logger.py             # Rich 기반 컬러 로깅
├── tests\                            # 단위 및 통합 파이프라인 테스트
│   ├── test_git_manager.py
│   ├── test_pipeline.py
│   ├── test_quality_gate.py
│   └── test_task.py
├── .env.example                      # 환경설정 템플릿
├── pyproject.toml                    # 패키지 빌드 명세
└── requirements.txt                  # 종속성 목록
```

---

## 🛠 설치 및 사용 방법

### 1. 가상환경 및 종속성 설치
```bash
# 가상환경 활성화 (Windows PowerShell)
.\.venv\Scripts\Activate.ps1

# editable 모드 설치
pip install -e .
```

### 2. 환경 설정 (`.env`)
```bash
cp .env.example .env
# .env 파일에서 GITHUB_TOKEN, REPO_PATH, AGENT_TYPE 등을 설정
```

### 3. CLI 명령어

#### 환경 설정 상태 점검
```bash
python -m aicoop.cli config-check
```

#### 자연어 태스크 실행 (Ad-hoc Task)
```bash
# Antigravity SDK 러너로 작업 실행 (기본)
python -m aicoop.cli run --task "GET /health 헬스체크 엔드포인트를 추가하고 단위 테스트를 작성해줘"

# Aider 러너로 실행하고 완료 시 PR 생성까지 수행
python -m aicoop.cli run --task "DB 커넥션 풀 타임아웃 처리 로직 추가" --agent aider --push --pr
```

#### GitHub Issue 번호로 자동 해결 (Issue-to-PR)
```bash
python -m aicoop.cli issue 42 --agent antigravity --push --pr
```

---

## 🧪 테스트 실행
```bash
pytest tests/ -v
```
모든 단위 테스트(GitManager, QualityGate, Task 모델, CorePipeline 재시도 루프)가 완전히 검증되었습니다.
