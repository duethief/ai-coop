# AI Agent 기반 공동 개발 협업 플랫폼 오픈소스 생태계 종합 분석 보고서

---

## ① Executive Summary

### 1. 현 오픈소스 생태계 진단
여러 개발자가 각자 보유한 AI 서비스(Claude Max, Gemini Pro, ChatGPT/Codex 등)를 단일 프로젝트의 공동 개발 자원(AI Resource Pool)으로 제공하고, 이를 바탕으로 작업을 분배·실행·리뷰하며, 기여도를 AI Credit으로 정산하는 **AI Agent 기반 협업 개발 플랫폼**은 **2026년 현재 오픈소스 생태계에 100% 턴키(Turnkey)로 존재하는 단일 솔루션은 없습니다.**

그러나 플랫폼을 구성하는 **개별 단위 인프라 블록**은 고도로 성숙해 있습니다.
* **자율 코딩 에이전트(Autonomous Coding Agent)**: `OpenHands`, `Aider`, `Goose`, `Cline` 등이 실무 수준의 코드 생성, Git 제어, 터미널 실행 능력을 확보했습니다.
* **Git PR 자동화 및 코드 리뷰**: `Qodo PR-Agent` 등이 PR 생성부터 정밀 코드 리뷰, 피드백 루프까지 자동화하고 있습니다.
* **LLM 게이트웨이 및 사용량 추적**: `LiteLLM`이 100개 이상의 모델 추상화와 가상 키(Virtual Keys), 팀 버짓을 제공하며, `OpenMeter`가 이벤트 기반 실시간 미터링을 지원합니다.
* **분산 워크플로우/태스크 큐**: `Temporal`과 `Hatchet`이 장기 실행(Long-running) 에이전트 태스크의 장애 복구와 상태 관리를 완벽히 보장합니다.
* **실행 격리 샌드박스**: `E2B` (Firecracker 기반 microVM)가 격리된 코드 실행 환경을 제공합니다.

### 2. 본 서비스의 본질적인 기술적/법적 장벽과 해결 모델
기존 오픈소스들이 해결하지 못하고 있는 가장 결정적인 차이점은 **"개인 구독 플랜(Claude Max/Pro, ChatGPT Plus 등)을 어떻게 프로젝트의 공용 자원으로 취급할 것인가"**입니다.
* **중앙 집중식 프록시의 한계**: 사용자의 개인 웹 세션/OAuth 토큰을 중앙 서버에 수집하여 대리 호출하는 것은 각 LLM 공급사(Anthropic, OpenAI 등)의 **이용약관(ToS) 상 '제3자 중계 및 계정 공유 금지'에 정면으로 저촉**되며, 세션 탈취 및 계정 영구 정지(Ban)의 위험이 있습니다.
* **해결을 위한 아키텍처 전환**: 이 서비스가 실현되려면 중앙 서버가 API를 쏘는 방식이 아니라, **"GitLab Runner / GitHub Actions Self-Hosted Runner / BOINC" 방식의 분산 워커(Distributed Agent Runner) 아키텍처**를 채택해야 합니다. 즉, 개발자의 로컬 머신에 에이전트 데몬을 띄워 로컬 인증 자격을 유지하고, 중앙 오케스트레이터는 작업(Task)만 큐로 분배하여 결과(Git Commit/PR)를 수거하는 구조입니다.

결론적으로, **기존 오픈소스를 75% 수준으로 조합하여 기초 런타임/오케스트레이션/샌드박스를 구축하고, 나머지 25%에 해당하는 "분산 에이전트 노드 프로토콜", "가용 Resource Pool 라우터", "기여도 원장(Contribution Ledger & Credit System)"을 독자 개발하는 전략이 최적**입니다.

---

## ② Top 15 Open Source Projects

본 플랫폼 구축에 직접적으로 활용 가능한 상위 15개 오픈소스 프로젝트를 분석합니다. (단순 순위가 아니며 역할별 최적 프로젝트입니다.)

### Top 15 프로젝트 비교 분석표

| Project | GitHub | License | Stars (약) | Language | Architecture | Self-Hosted | Docker/K8s | Provider 지원 (Claude/Gemini/OpenAI) | Multi-Agent / Routing | API & Headless | 이번 프로젝트 활용 영역 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **OpenHands** | `All-Hands-AI/OpenHands` | MIT | 46k+ | Python/TS | Agent Platform + Docker Sandbox | O | O / O | O / O / O | O (SDK/Resolver) | O (REST/WS/CLI) | **핵심 코딩 에이전트 런타임** |
| **Aider** | `Aider-AI/aider` | Apache-2.0 | 32k+ | Python | Terminal Git-Centric Pair Agent | O | O / O | O / O / O | 부분적 (Architect/Editor) | O (CLI/Python API) | **Git 커밋/파일 수정 엔진** |
| **Goose** | `aaif-goose/goose` | Apache-2.0 | 12k+ | Rust | On-Machine Extensible Agent (MCP) | O | O / O | O / O / O | O (MCP Extensions) | O (CLI/IPC) | **로컬 분산 워커 에이전트 노드** |
| **Cline** | `cline/cline` | Apache-2.0 | 28k+ | TS | IDE/CLI Autonomous Agent | O | O / O | O / O / O | X (단일 태스크 중심) | O (CLI/Headless) | **로컬 코딩 워커 추상화 참고** |
| **SWE-agent** | `princeton-nlp/SWE-agent` | MIT | 16k+ | Python | Issue-to-PR Benchmark Agent | O | O / O | O / O / O | X (벤치마크/파이프라인) | O (CLI/Docker) | **Issue 해결 및 ACI 벤치마크** |
| **Qodo PR-Agent** | `qodo-ai/pr-agent` | Apache-2.0 | 6k+ | Python | Git PR/MR Review & Automation | O | O / O | O / O / O | X (PR 전용 파이프라인) | O (Webhook/CLI/API) | **PR 자동 생성 및 AI 코드 리뷰** |
| **LiteLLM** | `BerriAI/litellm` | MIT | 24k+ | Python | Universal AI Gateway & Proxy | O | O / O | O / O / O | 라우팅/폴백/로드밸런싱 | O (OpenAI Spec API) | **AI 통합 게이트웨이 & 가상 키** |
| **Temporal** | `temporalio/temporal` | MIT | 13k+ | Go | Durable Distributed Orchestrator | O | O / O | 독립적 (Workflow 엔진) | O (분산 워커 오케스트레이션) | O (gRPC/REST) | **작업 큐 & 상태머신 오케스트레이터** |
| **Hatchet** | `hatchet-dev/hatchet` | Apache-2.0 | 6k+ | Go/TS/Py | Distributed Task Queue for AI | O | O / O | 독립적 (DAG 큐 엔진) | O (동시성/재시도/스트림) | O (gRPC/REST) | **경량 AI 태스크 분배 큐 대안** |
| **E2B** | `e2b-dev/E2B` | Apache-2.0 | 8k+ | Go/TS/Py | Firecracker microVM Sandbox | O (Cloud/On-prem) | Firecracker/K8s | 독립적 (실행 환경) | O (에이전트별 세션 격리) | O (SDK/API) | **원격 보안 실행 격리 샌드박스** |
| **Daytona** | `daytonaio/daytona` | **AGPL-3.0** | 15k+ | Go | Dev Environment & Workspace Mgr | O | O / O | 독립적 (워크스페이스) | O (에이전트별 환경 프로비저닝)| O (CLI/API) | **에이전트별 Git 워크스페이스 관리** |
| **OpenMeter** | `openmeterio/openmeter` | Apache-2.0 | 3k+ | Go | Real-time Usage Metering Engine | O | O / O | 독립적 (이벤트 미터링) | X (미터링 전용) | O (REST/Kafka/CloudEvent)| **AI Credit 실시간 집계/원장** |
| **MetaGPT** | `geekan/MetaGPT` | MIT | 47k+ | Python | Multi-Agent Role-based Dev SOP | O | O / X | O / O / O | O (SOP 기반 역할분담) | O (Python SDK/CLI) | **작업 분석/역할 분담 아키텍처** |
| **Plane** | `makeplane/plane` | **AGPL-3.0** | 33k+ | TS/Python | Project & Issue Management UI | O | O / O | 독립적 (프로젝트 UI) | 부분적 (웹훅 연동) | O (REST API) | **프로젝트/태스크/칸반 협업 UI** |
| **CopilotKit** | `CopilotKit/CopilotKit` | MIT | 16k+ | TS/React | AI Copilot & Generative UI Stack | O | O / O | O / O / O | O (AG-Grid/LangGraph 연동)| O (React Hooks/SDK) | **실시간 에이전트 액티비티 UI** |

---

### 각 프로젝트별 상세 분석 및 적합성 평가

#### 1. OpenHands (구 OpenDevin)
* **역할**: 자율 소프트웨어 엔지니어링 에이전트의 완성형 플랫폼.
* **장점**: 브라우징, 터미널 실행, 코드 편집, Git 커밋, GitHub PR 생성을 자체 포함하며, Docker 컨테이너 내에서 안전하게 동작함. Headless 모드(`openhands-resolver`) 및 REST API를 갖추고 있어 중앙 오케스트레이터가 작업 단위로 호출하기 가장 적합함.
* **한계/주의점**: 시스템 리소스를 많이 소모하며, 기본적으로 단일 사용자/단일 프로젝트 세션 중심 구조임. 다중 사용자 크레딧이나 분산 워커 풀 기능은 직접 감싸서 구현해야 함.

#### 2. Aider
* **역할**: 터미널 기반 Git 페어 프로그래밍의 표준 도구.
* **장점**: Tree-sitter 기반 `repo-map`을 통해 프로젝트 전체 컨텍스트를 압축 전달하는 능력이 가장 뛰어남. 자동 커밋 메시지 생성, Git conflict 해결 능력이 검증됨.
* **한계/주의점**: 대화형 CLI 도구로 설계되어 있어 백그라운드 데몬/헤드리스 서비스로 구동하려면 Python 래퍼 스크립트(`aider --yes --message ...`)를 통한 서브프로세스 제어가 필요함.

#### 3. Goose (Agentic AI Foundation / 구 Block)
* **역할**: 온머신(On-machine) 확장형 로컬 에이전트 런타임.
* **장점**: Rust 기반으로 가볍고 빠르며, MCP(Model Context Protocol)를 1급 객체로 지원함. 개발자 개인 PC에서 백그라운드 데몬으로 상주하며 로컬 CLI 인증(Claude Code 등)을 활용해 작업을 실행하는 "분산 워커 노드"의 기반 베이스로 최적임.
* **한계/주의점**: 중앙 집중형 서버 관리가 아닌 로컬 CLI 중심이므로, 중앙 오케스트레이터와 통신하는 에이전트 하네스(Worker Daemon)를 덧씌워야 함.

#### 4. Cline (구 Claude Dev)
* **역할**: IDE 및 CLI 환경 자율 코딩 에이전트.
* **장점**: Anthropic, OpenRouter, Gemini 등 다양한 Provider에 대한 BYO-Key 처리가 매우 정교하며, 파일 읽기/쓰기/명령어 실행 전 사용자 승인(Human-in-the-loop) 인터페이스가 잘 갖춰짐.
* **한계/주의점**: VS Code 익스텐션 종속성이 강했으나 최근 CLI/독립형으로 발전 중. 서버 사이드 멀티 테넌트 구동에는 부적합하며 로컬 러너 참고용으로 적합.

#### 5. SWE-agent
* **역할**: GitHub Issue를 입력받아 자동으로 PR을 생성하는 학술/산업계 벤치마크 기준 에이전트.
* **장점**: ACI(Agent-Computer Interface)를 통해 에이전트가 파일 검색, 린트 확인, 테스트 실행을 정밀하게 수행하도록 특화됨.
* **한계/주의점**: 대규모 배치 작업이나 벤치마크 평가용 파이프라인 성격이 강하여 실시간 협업 플랫폼의 반응형 에이전트로 쓰기에는 속도와 유연성이 떨어짐.

#### 6. Qodo PR-Agent
* **역할**: Git PR 생성, 리뷰, 테스트 자동화 도구.
* **장점**: GitHub/GitLab 웹훅과 완벽히 연동되어 PR이 생성되면 자동으로 `/review`, `/describe`, `/improve`, `/generate_tests`를 수행함. 다중 Git 플랫폼 지원이 매우 뛰어남.
* **한계/주의점**: 코드를 처음부터 작성하는 에이전트가 아니라, 작성된 코드를 '검증/리뷰'하는 에이전트임. 아키텍처의 "Review / Test / Merge" 블록에 배치하는 것이 최적임.

#### 7. LiteLLM
* **역할**: 범용 AI Gateway, 모델 라우팅 및 가상 키/예산 관리 프록시.
* **장점**: 단일 OpenAI 규격 엔드포인트로 100개 이상의 LLM을 호출 가능. 팀별/사용자별 Virtual Key 발급, 분당 요청 수(RPM), 일일 예산(Budget), 로드 밸런싱, Fallback 메커니즘을 기본 제공함.
* **한계/주의점**: 공식 API 키(Pay-as-you-go) 연동에 특화되어 있음. 웹 세션 기반의 개인 구독(Claude Max, ChatGPT Plus)은 지원하지 않음(API 키 형태의 자원 풀링에만 즉시 사용 가능).

#### 8. Temporal
* **역할**: 장기 실행(Long-running) 분산 워크플로우 오케스트레이션 엔진.
* **장점**: 코딩 에이전트의 작업은 수 분~수십 분이 소요되고 네트워크 단절, 프로세스 크래시가 잦음. Temporal은 작업의 실행 상태(Event History)를 완전히 보존하여 워커가 재부팅되어도 중단 지점부터 재개(Durable Execution)할 수 있음.
* **한계/주의점**: Go/Java 기반 서버 클러스터 러닝 커브가 있으며, 워크플로우 코드가 결정론적(Deterministic)이어야 하므로 비즈니스 로직 설계에 엄격함이 요구됨.

#### 9. Hatchet
* **역할**: AI 에이전트 및 백그라운드 작업을 위해 설계된 모던 분산 큐.
* **장점**: PostgreSQL 기반으로 가볍고 빠르게 배포 가능하며, DAG(방향성 비순환 그래프) 형태의 작업 파이프라인, 실시간 로그 스트리밍, 동시성 제어(Concurrency limits)를 직관적인 TypeScript/Python SDK로 제공함.
* **한계/주의점**: Temporal에 비해 초대규모 엔터프라이즈 레퍼런스가 적으나, 중소규모 플랫폼 구축 시 개발 속도 면에서 압도적으로 유리함.

#### 10. E2B
* **역할**: AI 에이전트 전용 클라우드 보안 샌드박스 (Firecracker 기반).
* **장점**: AI 에이전트가 임의의 셸 명령어나 악성 패키지를 실행할 위험을 방지하기 위해 150ms 이내에 완전히 격리된 경량 가상 머신(microVM)을 띄우고 회수함.
* **한계/주의점**: 자체 호스팅(On-premise) 시 KVM 지원 Linux 서버 및 복잡한 인프라 설정이 필요함.

#### 11. Daytona
* **역할**: 개발 환경 및 워크스페이스 관리 플랫폼.
* **장점**: 에이전트에게 필요한 Git 리포지토리 클론, 종속성 설치, 런타임 환경 구성을 표준화된 OCI 컨테이너 스냅샷으로 자동화함.
* **한계/주의점**: **AGPL-3.0 라이선스**이므로, Daytona 소스 코드를 수정하거나 네트워크 서비스로 제공할 경우 전체 플랫폼의 소스 코드 공개 리스크가 발생함(외부 격리 마이크로서비스로만 연동 필요).

#### 12. OpenMeter
* **역할**: 고성능 실시간 이벤트 기반 사용량 미터링 엔진.
* **장점**: Kafka와 ClickHouse 기반으로 수백만 건의 에이전트 액션(입출력 토큰, 실행 시간, 도구 호출 횟수)을 CloudEvents 표준으로 수집하고, 이를 집계하여 사용자별/프로젝트별 Quota 관리 및 정산 원장을 생성함.
* **한계/주의점**: 순수 미터링 엔진이므로, "토큰 수를 AI Credit으로 환산하고 프로젝트 지분율로 배분하는 고유 비즈니스 룰"은 상위 애플리케이션에서 별도로 정의해야 함.

#### 13. MetaGPT
* **역할**: 표준 소프트웨어 개발 절차(SOP) 기반 멀티에이전트 협업 프레임워크.
* **장점**: 요구사항 분석(Product Manager), 아키텍처 설계(Architect), 코드 작성(Engineer), 품질 검증(QA) 등의 역할을 에이전트별로 나누어 체계적인 산출물을 만들어냄.
* **한계/주의점**: 에이전트 간 정형화된 텍스트 문서 교환 중심이며, 실제 복잡한 기존 대규모 Git 리포지토리에 대한 정밀한 브랜치/머지 제어는 부족함.

#### 14. Plane
* **역할**: 오픈소스 이슈 트래커 및 프로젝트 관리 플랫폼 (Linear/Jira 대안).
* **장점**: 작업 티켓, 칸반 보드, 스프린트, 기여도 트래킹 등 UI가 매우 미려하며 완성도가 높음. 풍부한 REST API 및 웹훅 지원.
* **한계/주의점**: **AGPL-3.0 라이선스**. 상업용 SaaS 플랫폼 내부 프론트엔드로 직접 임베딩(fork/embed)하기에는 법적 위험이 크며, 독립된 별도 서버로 띄워 API 연동만 해야 함.

#### 15. CopilotKit
* **역할**: React/Next.js 기반 AI 코파일럿 및 실시간 상호작용 UI 라이브러리.
* **장점**: 에이전트의 사고 과정(Chain of Thought), 도구 실행 상태, 실시간 진행률, 제너레이티브 UI 컴포넌트를 웹 프론트엔드에 손쉽게 통합할 수 있는 프레임워크 제공.
* **한계/주의점**: 프론트엔드 UI 렌더링 계층이므로 백엔드 오케스트레이터 및 Git 인프라는 전적으로 자체 구축해야 함.

---

## ③ Architecture Mapping

목표 시스템 구조와 오픈소스 프로젝트의 매핑 다이어그램입니다.

```text
                                ┌──────────────────────────────────────────────────────────┐
                                │                    Web / Frontend                        │
                                │  • UI Framework: Next.js + TailwindCSS (직접 개발)       │
                                │  • AI Agent 상태/채팅 컴포넌트: CopilotKit (재사용)        │
                                │  • 이슈/칸반/기여도 대시보드: 직접 개발 (Plane API 연동)  │
                                └────────────────────────────┬─────────────────────────────┘
                                                             │ REST / WebSocket
                                ┌────────────────────────────▼─────────────────────────────┐
                                │                 Project & Task Management                │
                                │  • 프로젝트 생성, 참여자 관리, 작업 명세 정의             │
                                │  • Issue 트래커 연동 (GitHub Issues / GitLab Issues)     │
                                └────────────────────────────┬─────────────────────────────┘
                                                             │
                                ┌────────────────────────────▼─────────────────────────────┐
                                │             AI Resource Pool & Routing Core              │
                                │                   ★ [100% 독자 개발] ★                   │
                                │  • 등록된 Worker 상태 관리 (온라인/오프라인/Busy)         │
                                │  • Task 특성 분석 (작업 크기, 요구 모델, 언어)           │
                                │  • 최적 Worker 매칭 알고리즘 (가용 Credit, 성능 기반)   │
                                └────────────────────────────┬─────────────────────────────┘
                                                             │
                                ┌────────────────────────────▼─────────────────────────────┐
                                │            Task Orchestrator (Workflow Engine)           │
                                │  • 분산 트랜잭션/상태머신: Temporal (또는 Hatchet)       │
                                │  • Retry, Timeout, Worker 장애 시 재할당 관리            │
                                └──────────────┬────────────────────────────┬──────────────┘
                                               │ gRPC Task Dispatch         │
                     ┌─────────────────────────┴────────┐                   │
                     ▼                                  ▼                   ▼
    ┌─────────────────────────────────┐ ┌─────────────────────────────────┐ ┌─────────────────────────────────┐
    │     [Type A: BYO-Worker Node]   │ │     [Type A: BYO-Worker Node]   │ │     [Type B: BYO-Key Pool]      │
    │      Developer A 로컬 머신       │ │      Developer B 로컬 머신       │ │     중앙 서버 실행 클라우드      │
    │  • Daemon: Goose / Aider Wrapper│ │  • Daemon: Goose / Aider Wrapper│ │  • Gateway: LiteLLM           │
    │  • Auth: Claude Max 로컬 CLI    │ │  • Auth: Gemini CLI 로컬 인증   │ │  • Auth: Developer C OpenAI Key│
    │  • Sandbox: Local Docker Engine │ │  • Sandbox: Local Docker Engine │ │  • Sandbox: E2B microVM Cloud │
    │  • Execution: OpenHands Runner  │ │  • Execution: OpenHands Runner  │ │  • Execution: OpenHands Runner│
    └────────────────┬────────────────┘ └────────────────┬────────────────┘ └────────────────┬────────────────┘
                     │                                  │                                   │
                     └──────────────────────────────────┼───────────────────────────────────┘
                                                        │ Git Push / Pull Request
                                ┌───────────────────────▼──────────────────────────┐
                                │                  Git Repository                  │
                                │  • GitHub / GitLab (On-premise or Cloud)         │
                                │  • 작업 전용 Feature Branch 자동 생성 및 커밋     │
                                └───────────────────────┬──────────────────────────┘
                                                        │ Webhook (PR Open)
                                ┌───────────────────────▼──────────────────────────┐
                                │               Automated Review & Test            │
                                │  • 자동 PR 요약/개선/리뷰: Qodo PR-Agent         │
                                │  • CI 파이프라인 (GitHub Actions / GitLab CI)    │
                                │  • 인간 개발자 승인 (Human-in-the-loop)          │
                                └───────────────────────┬──────────────────────────┘
                                                        │ Merge Event
                                ┌───────────────────────▼──────────────────────────┐
                                │        Metering, Credit & Contribution Ledger    │
                                │  • 실시간 사용량 측정: OpenMeter (토큰/시간 수집) │
                                │  • AI Credit 산정 및 기여도 원장: ★ [직접 개발] ★ │
                                └──────────────────────────────────────────────────┘
```

---

## ④ Recommended Stack

| 레이어 | 권장 기술 / 오픈소스 | 선정 이유 |
| :--- | :--- | :--- |
| **Frontend** | **Next.js 15 + CopilotKit + TailwindCSS** | 실시간 에이전트 스트리밍 UI와 제너레이티브 컴포넌트를 가장 빠르게 조합 가능하며, 독자 브랜딩 및 복잡한 크레딧 정산 화면을 완벽히 커스터마이징 가능함. |
| **Project / Task API** | **FastAPI (Python) 또는 NestJS (TypeScript)** | GitHub/GitLab 웹훅 수신, Temporal 클라이언트 연동, 인증/인가 관리에 표준적이며 생산성이 높음. |
| **Task Orchestration** | **Temporal (Go 백엔드 + Python SDK)** | 에이전트 작업은 수십 분 동안 실행되는 특성이 있음. 네트워크 단절이나 에이전트 워커 다운 시에도 워크플로우 상태를 잃지 않고 재시도/장애 복구하는 기능에서 업계 최고 수준의 신뢰성 제공. (경량화를 원할 경우 **Hatchet** 채택) |
| **Agent Routing Core** | **직접 개발 (FastAPI/Go)** | 사용자가 제공한 서로 다른 형태의 AI 자원(로컬 러너, API 키)을 추적하고 최적의 워커에 작업을 라우팅하는 핵심 로직으로, 기존 오픈소스가 전무함. |
| **Agent Worker Runtime** | **OpenHands SDK + Aider (하이브리드)** | 복잡한 셸 명령/테스트 실행은 OpenHands의 Docker 샌드박스를 사용하고, 고난도 코드 리팩토링 및 정밀 커밋 생성은 Aider의 Tree-sitter repo-map 엔진을 차용. |
| **Local Runner Daemon** | **Goose (Rust) 기반 커스텀 포크** | 메모리 점유율이 낮고 확장성이 뛰어난 Rust 기반 CLI 러너로, 개발자 개인 PC에서 백그라운드로 실행되어 중앙 Temporal 서버와 통신하는 에이전트 데몬으로 최적. |
| **AI Gateway (API 전용)** | **LiteLLM Proxy** | 개발자가 'API Key' 형태로 기여한 자원에 대해 로드밸런싱, 가상 키 발급, 폴백, 토큰 비용 산정을 즉시 처리. |
| **Sandbox (클라우드 실행)** | **E2B (또는 Docker-in-Docker)** | 중앙 서버에서 API 키로 코드를 생성하고 실행할 때 완벽한 커널 격리(Firecracker microVM)를 제공하여 호스트 오염 방지. |
| **Git Review & Automation** | **Qodo PR-Agent** | PR이 열렸을 때 다른 에이전트(예: Claude가 짠 코드를 Gemini가 리뷰)가 자동으로 코드 리뷰, 보안 취약점 검증, PR 설명 생성을 수행하도록 파이프라인 구성. |
| **Usage Metering** | **OpenMeter** | Kafka/ClickHouse 기반으로 에이전트별 토큰 사용량, API 호출 횟수, 실행 시간을 CloudEvents 표준 규격으로 실시간 수집. |
| **Database & Cache** | **PostgreSQL + Redis** | Temporal 내부 상태 저장, 프로젝트 메타데이터, 사용자 인증, 실시간 작업 큐 버퍼링. |

---

## ⑤ Build vs Reuse 분석

| 기능 영역 | 기존 OSS 활용 | 재사용 수준 | 직접 개발 필요 영역 | 상세 설명 |
| :--- | :---: | :---: | :---: | :--- |
| **코딩 에이전트 실행 (Runtime)** | `OpenHands`, `Aider` | **높음 (80%)** | **낮음 (20%)** | 파일 편집, 셸 실행, 린트/테스트, Git 커밋 등은 OpenHands와 Aider를 그대로 호출하여 재사용. 독자 작업 지시서 템플릿만 작성. |
| **태스크 큐 & 오케스트레이션** | `Temporal`, `Hatchet` | **높음 (85%)** | **낮음 (15%)** | 분산 큐, 타임아웃, 재시도, 동시성 제어는 Temporal 엔진에 완전히 위임. 태스크 정의 워크플로우 코드만 작성. |
| **Git/PR 자동화 및 AI 리뷰** | `Qodo PR-Agent` | **높음 (85%)** | **낮음 (15%)** | PR 생성, 자동 리뷰 코멘트, 단위 테스트 생성은 PR-Agent를 웹훅 트리거로 연결. 머지 정책 판정 로직만 추가. |
| **공식 API 추상화 (BYO-Key)** | `LiteLLM` | **높음 (90%)** | **낮음 (10%)** | OpenAI/Anthropic/Gemini API 키 풀링, 로드밸런싱, 예산 제한은 LiteLLM Proxy로 즉시 해결. |
| **실행 격리 샌드박스** | `E2B`, `Docker` | **높음 (85%)** | **낮음 (15%)** | microVM 및 컨테이너 생명주기 관리는 E2B SDK 및 Docker Engine API 재사용. |
| **공동 AI Resource Pool 라우터** | 없음 | **매우 낮음 (0%)** | **매우 높음 (100%)** | **핵심 개발 영역 1**: 접속 중인 분산 워커(Claude, Gemini 등)의 가용 상태를 모니터링하고, 작업 성격에 맞게 분배하는 라우팅 엔진. |
| **개인 구독 연동 분산 데몬** | `Goose` 참고 | **중간 (40%)** | **높음 (60%)** | **핵심 개발 영역 2**: 개발자 PC에서 로컬 구독 세션을 보호하며 중앙 플랫폼의 태스크를 받아 실행하는 Self-hosted Runner 데몬. |
| **AI Credit 환산 & 기여도 원장** | `OpenMeter` (기초) | **중간 (30%)** | **높음 (70%)** | **핵심 개발 영역 3**: 이종 모델(Claude 토큰 vs Gemini 토큰)을 단일 'AI Credit'으로 환산하는 가치 평가 알고리즘 및 기여도 분배 원장. |
| **협업 웹 대시보드** | `CopilotKit` (부분) | **중간 (40%)** | **높음 (60%)** | 전체 프로젝트, 실시간 에이전트 작업 현황, 크레딧 보유량, 기여도 그래프를 보여주는 프론트엔드 UI. |

---

## ⑥ 가장 중요한 Gap 분석

### "여러 사용자가 서로 다른 AI 구독/Agent를 제공하여 공동 Pool로 사용하고, 기여도를 측정하는 시스템"

기존 오픈소스 생태계를 면밀히 조사한 결과, **이 기능은 기존 프로젝트에 완전히 '부재(Absent)'하며 본 서비스 팀이 100% 독자적으로 설계해야 하는 절대적 공백(Gap)**입니다.

#### 1. 왜 기존 오픈소스에는 이 기능이 없는가?
1. **API 키 중심의 오픈소스 철학**: 기존 도구(LiteLLM, Langfuse, OpenHands)는 **"단일 조직/관리자가 API 키를 중앙에 등록하고 팀원들에게 분배하는 방식(Central-to-Users)"**입니다. 반면 본 서비스는 정반대로 **"개별 사용자가 각자의 자원을 중앙 풀로 공여하는 방식(Users-to-Central Pool)"**입니다.
2. **개인 구독(Subscription)과 API의 기술적 괴리**:
   * **API**: `sk-ant-...` 같은 문자열 키로, 헤더에 담아 전송하면 어디서나 작동하며 토큰당 비용이 명확함.
   * **개인 구독 (Claude Max, ChatGPT Plus)**: 브라우저 쿠키, 세션 토큰, 로컬 CLI OAuth로 인증되며 정액제(Flat-rate)이고, 동시 세션 제한 및 캡(Cap)이 존재함.
   * 기존 오픈소스는 API Key를 관리하도록 설계되었지, 타인의 로컬 CLI 세션을 빌려 쓰는 모델을 지원하지 않습니다.

#### 2. 결정적 아키텍처 해법: "Distributed Agent Runner Pattern"
중앙 서버가 모든 사용자의 계정 인증 정보를 저장하려 하면 보안 파탄과 약관 위반에 직면합니다. 유일한 기술적 해법은 **GitHub Actions Self-Hosted Runner** 모델입니다.

```text
[중앙 협업 플랫폼]
  - Task Orchestrator (Temporal)
  - Task Queue (Public Tasks: "로그인 JWT 추가", "테스트 코드 작성")
          │
          │ gRPC (작업 할당 Polling)
          ▼
[개발자 A의 로컬 머신]
  ┌────────────────────────────────────────────────────────┐
  │ Agent Runner Daemon (Goose 기반 경량 프로세스)          │
  │  - 인증: 개발자 A의 로컬 Claude Code CLI / Session 유지 │
  │  - 샌드박스: 개발자 로컬 Docker에서 Git Clone & 코드 수정│
  │  - 실행: Aider / OpenHands 런타임                      │
  │  - 완료 보고: Git Commit Push 후 중앙 서버로 완료 신호  │
  └────────────────────────────────────────────────────────┘
```
* **보안 확보**: 인증 자격 증명이 개발자 개인 PC 밖으로 단 1바이트도 유출되지 않음.
* **약관 준수**: 개발자 본인의 컴퓨터에서 본인의 계정으로 CLI 도구가 실행되므로 제3자 대리 호출(Intermediation) 약관 위반 소지를 최소화함.
* **비용 절감**: 플랫폼이 중앙에서 거대한 GPU/컨테이너 인프라를 유지할 필요 없이 연산 리소스를 개발자 머신으로 분산(Edge Computing)함.

---

## ⑦ MVP 개발 계획

### Phase 1: 파이프라인 최소 검증 (Core Pipeline MVP)
* **목표**: 1명의 개발자가 단일 Agent(Claude Code 또는 Aider)를 통해 Issue → Code → Commit → PR 자동화 파이프라인을 검증.
* **사용할 오픈소스**: `Aider`, `Qodo PR-Agent`, `GitHub API`.
* **직접 개발할 기능**: GitHub Issue 생성 시 웹훅을 받아 Aider 헤드리스 프로세스를 실행하고, 브랜치 생성 및 PR을 올리는 경량 Python 백엔드.
* **예상 난이도**: **보통 (2/5)**
* **주요 리스크**: 에이전트의 코드 수정 실패 시 무한 루프 발생 가능성 → Step 제한(Max Iteration) 필수.

### Phase 2: 멀티 에이전트 오케스트레이션 (Multi-Agent Routing)
* **목표**: 작업 특성에 따라 Claude(아키텍처/로직), Gemini(문서/대규모 컨텍스트), GPT(테스트/리팩토링)를 선택하여 작업 분배.
* **사용할 오픈소스**: `Temporal` (워크플로우), `LiteLLM` (공식 API 게이트웨이), `OpenHands` (실행 런타임), `E2B` (샌드박스).
* **직접 개발할 기능**:
  * 작업 프롬프트를 분석하여 적절한 에이전트를 매핑하는 Rule/LLM 기반 작업 분석기(Task Classifier).
  * Temporal 워크플로우 정의 (작업 생성 → 에이전트 실행 → 테스트 실패 시 재시도).
* **예상 난이도**: **높음 (3.5/5)**
* **주요 리스크**: Temporal 클러스터 운영 및 이벤트 히스토리 디버깅 오버헤드.

### Phase 3: AI Resource Pool & Distributed Runner
* **목표**: 개발자 A, B, C가 각자의 머신에 'Agent Runner Daemon'을 설치하고, 프로젝트 풀에 연결하여 다른 사람의 작업을 대신 수행.
* **사용할 오픈소스**: `Goose` (러너 데몬 베이스), `Docker Engine API`.
* **직접 개발할 기능**:
  * **Agent Worker Daemon**: 로컬 머신에서 백그라운드로 돌며 중앙 플랫폼과 gRPC로 통신하는 클라이언트.
  * **Resource Pool Manager**: 워커의 가용 상태(CPU, 온라인 여부, 제공 모델)를 등록받고 관리하는 중앙 서비스.
  * 중앙-로컬 간 안전한 코드 Diff 전송 및 Git 인증 위임 프로토콜.
* **예상 난이도**: **매우 높음 (4.5/5)**
* **주요 리스크**: 분산 워커가 작업을 수주한 뒤 로컬 PC를 끄거나 네트워크가 끊겼을 때의 Heartbeat 감지 및 작업 재할당 메커니즘.

### Phase 4: AI Credit & 기여도 원장 (Contribution Ledger)
* **목표**: 각 개발자의 Agent가 처리한 작업량(토큰, 시간, 난이도)을 'AI Credit'으로 환산하고 프로젝트 기여도로 기록.
* **사용할 오픈소스**: `OpenMeter` (이벤트 수집), `PostgreSQL` (원장 저장).
* **직접 개발할 기능**:
  * **Credit Exchange Formula**: 서로 다른 모델의 가치 환산 로직 (예: Claude 3.5 Sonnet 1k Output = 3.0 Credit, Gemini 1.5 Flash 1k Output = 0.5 Credit).
  * 성공적인 PR 머지 시 기여도 원장에 기록하는 정산 엔진(Settlement Engine).
  * 실시간 크레딧 잔고 및 랭킹 대시보드.
* **예상 난이도**: **보통~높음 (3.5/5)**
* **주요 리스크**: 단순 토큰 소모를 노린 악의적/무의미한 코드 생성(Gaming the system) 방지책 필요 (반드시 PR 머지 성공 및 테스트 통과 조건과 연동해야 함).

### Phase 5: 프로젝트 수익/보상 분배 (Revenue Distribution)
* **목표**: 프로젝트가 획득한 상금, 펀딩, 또는 외주 수익을 누적된 AI Credit 기여도 지분에 따라 배분.
* **사용할 오픈소스**: Stripe Connect API 또는 Web3 스마트 컨트랙트.
* **직접 개발할 기능**: 프로젝트 지분 산정 알고리즘, 에스크로 정산 시스템, 세금 및 인보이스 자동 발행.
* **예상 난이도**: **높음 (4/5, 법률/세무 이슈 포함)**
* **주요 리스크**: 각 국가별 금융/암호화폐 규제 및 세무 처리.

---

## ⑧ 라이선스 / 상업적 사용 위험 & Provider 약관(ToS)

### 1. 핵심 오픈소스 라이선스 검토

| Project | License | 상업적 SaaS 사용 | 소스 공개 의무 | 주의사항 및 법적 리스크 |
| :--- | :--- | :---: | :---: | :--- |
| **OpenHands** | MIT | **안전** | 없음 | 자유롭게 수정 및 비공개 상업화 가능. 저작권 고지문만 유지. |
| **Aider** | Apache-2.0 | **안전** | 없음 | 특허 라이선스 포함. 수정 사항 표기 및 저작권 유지 필요. |
| **Goose** | Apache-2.0 | **안전** | 없음 | Agentic AI Foundation 관리. 기업 상업화 문제없음. |
| **Qodo PR-Agent** | Apache-2.0 | **안전** | 없음 | 자유롭게 SaaS 백엔드로 연동 가능. |
| **LiteLLM** | MIT | **안전** | 없음 | 프록시 서버로 상업적 서비스 구축 완벽 허용. |
| **Temporal** | MIT | **안전** | 없음 | Temporal Server는 MIT. 사내 구축 및 상업용 백엔드 사용 안전. |
| **OpenMeter** | Apache-2.0 | **안전** | 없음 | 핵심 엔진 Apache-2.0. 상업적 미터링 인프라로 사용 가능. |
| **Daytona** | **AGPL-3.0** | **주의** | **네트워크 제공 시 발생** | Daytona 소스코드를 수정하여 네트워크 서비스로 제공할 경우 플랫폼 전체 소스코드를 공개해야 할 위험이 있음. 반드시 **수정 없이 독립된 격리 프로세스로 실행하고 API로만 통신**해야 함. |
| **Plane** | **AGPL-3.0** | **주의** | **네트워크 제공 시 발생** | 웹 UI 코드를 포크하여 상업용 SaaS에 통합하면 소스 공개 의무 발생. 독립된 온프레미스 인스턴스로 분리 연동 권장. |

### 2. AI Provider 약관(Terms of Service) 충돌 및 법적 위험 (매우 중요)

본 프로젝트의 비즈니스 모델상 가장 치명적인 위험 요소는 오픈소스 라이선스가 아니라 **LLM 공급사의 이용약관**입니다.

#### ① Anthropic (Claude)
* **약관 확인 결과**: Anthropic의 *Commercial Terms of Service*는 **"제3자를 대신하여 Claude 사용을 중계(intermediate)하거나 재판매(resell)하는 행위"**를 명시적으로 금지합니다.
* **위험 분석**: 사용자 A의 Claude Pro/Max 세션 토큰을 중앙 서버가 보관하고, 사용자 B가 요청한 작업을 중앙 서버에서 실행하는 구조는 **"명백한 계정 공유 및 무단 중계"**로 간주되어 사용자 A의 계정과 플랫폼 IP가 영구 정지될 수 있습니다.
* **합법적 대응 방안**:
  * **API Key 방식**: 사용자가 자신의 공식 Anthropic API Key를 등록하여 소비하는 BYO-Key 모델은 허용됩니다.
  * **Distributed Worker 방식**: 사용자 A의 개인 PC에서 로컬 Runner가 작업을 수행하고 커밋만 Git으로 올리는 형태는 "사용자 A 본인의 환경에서 본인의 세션으로 도구를 실행한 결과물을 공유"하는 것이므로 약관 위반 해석의 여지를 대폭 줄일 수 있습니다.

#### ② OpenAI (ChatGPT / Codex)
* **약관 확인 결과**: OpenAI의 *Business & Consumer Terms*는 계정 인증 자격 증명(Credentials)을 타인과 공유하는 것을 금지하며, 서비스 자동 스크래핑 및 비공식 리버스 엔지니어링 API 생성을 금지합니다.
* **위험 분석**: ChatGPT Plus 계정의 액세스 토큰을 추출하여 플랫폼 풀에 물리는 것은 비인가 접근(Unauthorized Access)에 해당합니다.
* **합법적 대응 방안**: 공식 OpenAI API를 사용하는 BYO-Key 방식 또는 공식 CLI 세션을 로컬 머신에서만 소화하는 분산 노드 방식을 채택해야 합니다.

#### ③ Google (Gemini)
* **약관 확인 결과**: Google Cloud Vertex AI / AI Studio API는 명확한 SLA와 결제 정책을 따르나, 일반 개인용 Google One AI Premium (Gemini Advanced) 웹 인터페이스의 비공식 연동은 Google 이용약관 상 자동화된 쿼리 전송 금지 조항에 위배됩니다.

> **최종 법적 권고**:
> "개인 구독 플랜(Claude Max, ChatGPT Plus)의 중앙 집중식 프록시 공유"는 비즈니스 모델로 지속 불가능합니다.
> 플랫폼은 반드시 **① 공식 API Key 풀링(BYO-Key via LiteLLM)**과 **② 개발자 로컬 머신에서 도는 자율 워커(Self-Hosted Worker via Goose)**의 투 트랙(Two-Track)으로만 설계되어야 법적 리스크에서 안전합니다.

---

## ⑨ 4개 카테고리 분류

조사된 오픈소스들을 재사용 및 아키텍처 수용 방식에 따라 4개 카테고리로 분류합니다.

### Category 1: 바로 가져다 사용할 수 있는 프로젝트 (Out-of-the-box)
* **LiteLLM**: 공식 API(OpenAI, Anthropic, Gemini)의 가상 키 관리, 로드밸런싱, 예산 제어를 즉시 프록시로 구동 가능.
* **Temporal / Hatchet**: 장기 실행 워크플로우 엔진으로 즉시 클러스터를 구축하여 작업 상태 머신으로 활용.
* **Qodo PR-Agent**: GitHub/GitLab 웹훅 리스너로 띄워 PR 자동 리뷰 파이프라인으로 즉시 투입 가능.
* **E2B**: 클라우드 샌드박스 런타임으로 즉시 SDK를 호출해 임의의 코드를 안전하게 격리 실행.
* **OpenMeter**: 이벤트 기반 사용량 수집 엔진으로 즉시 배포하여 토큰 및 실행 시간 메트릭 저장.

### Category 2: 핵심 코드를 참고하여 일부를 가져올 수 있는 프로젝트 (Code Extraction & Adaptation)
* **OpenHands (`openhands-resolver` & SDK)**: 자율 코딩 에이전트의 셸 실행, 파일 수정 루프, Git PR 생성 모듈 코드를 추출하여 독자 워커 런타임에 이식.
* **Aider**: Tree-sitter를 활용하여 프로젝트 전체의 심볼과 구조를 파악하는 `repo-map` 생성 모듈 및 자동 커밋 메시지 생성 로직을 라이브러리로 임베딩.
* **Goose**: Rust 기반 경량 프로세스 아키텍처와 MCP 연동 구조를 가져와 '로컬 에이전트 러너 데몬'의 기반 코드로 채택.

### Category 3: 아키텍처 참고용 프로젝트 (Architectural Reference Only)
* **SWE-agent**: 복잡한 버그 해결을 위해 에이전트와 터미널 간 상호작용을 인터페이스화한 ACI(Agent-Computer Interface) 설계 철학 차용.
* **MetaGPT / ChatDev**: PM → Architect → Engineer → QA로 이어지는 정형화된 소프트웨어 개발 절차(SOP)와 역할 분담 프롬프트 엔지니어링 기법 참고.
* **BOINC / GitLab Runner**: 중앙 서버의 작업을 받아 로컬에서 안전하게 처리하고 반환하는 분산 워커의 통신 프로토콜 및 하트비트 아키텍처 참고.

### Category 4: 기능은 유사하나 본 프로젝트와 구조가 다른 프로젝트 (Non-applicable / Distinct Structure)
* **Daytona / Devcontainer**: 훌륭한 개발 환경 관리자이나, 본 플랫폼이 요구하는 '경량 분산 에이전트 실행'에 비해 인프라 오버헤드가 크고 AGPL-3.0 라이선스 위험이 존재함.
* **Plane / Taiga**: 훌륭한 프로젝트 관리 도구이나, 일반적인 인간용 이슈 트래커 구조로 되어 있어 'AI Agent 전용 태스크 라이프사이클 및 크레딧 원장'을 담기에는 DB 스키마와 UX가 부적합함.
* **CrewAI / AutoGen Studio**: 단일 세션 내 대화형 멀티에이전트 데모에는 적합하나, 다수의 외부 개발자가 참여하는 대규모 실무 Git 저장소의 지속적 엔지니어링 플랫폼으로는 적합하지 않음.

---

## ⑩ 최종 아키텍처 제안 및 핵심 차별화 영역

### 1. 개발 영역 분구도 (Build vs Buy/Reuse Map)

```text
┌────────────────────────────────────────────────────────────────────────┐
│                        1. Web / Frontend UI                            │
│  [직접 개발 60%] Next.js 대시보드 + [재사용 40%] CopilotKit 에이전트 UI  │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────────┐
│                    2. Project / Task Management                        │
│  [직접 개발 80%] 협업 프로젝트 및 AI 전용 Task API                     │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────────┐
│            3. AI Resource Pool & Task Routing Core                     │
│  ★ [100% 직접 개발 - 플랫폼의 독점적 Core IP] ★                        │
│  - 분산 워커 가용성 추적 (Claude/Gemini/Codex 풀)                      │
│  - 작업 복잡도 분석 및 최적 워커 라우팅                                 │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────────┐
│                    4. Distributed Task Orchestrator                    │
│  [오픈소스 재사용 90%] Temporal / Hatchet + [직접 개발 10%] 워크플로우 │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        ▼                           ▼                           ▼
┌──────────────────┐        ┌──────────────────┐        ┌──────────────────┐
│ Claude Agent Node│        │ Gemini Agent Node│        │ Codex Agent Node │
│ [포크/조합 80%]  │        │ [포크/조합 80%]  │        │ [오픈소스 재사용]│
│ Goose+Aider+로컬CLI│      │ Goose+Aider+로컬CLI│      │ LiteLLM + E2B    │
└─────────┬────────┘        └─────────┬────────┘        └─────────┬────────┘
          └─────────────────────────┼─────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                        5. Git & PR Automation                          │
│  [오픈소스 재사용 85%] GitHub/GitLab API + Qodo PR-Agent 자동 리뷰     │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────────┐
│            6. Usage Metering & Contribution Ledger                     │
│  [재사용 30%] OpenMeter 이벤트 수집 + ★ [직접 개발 70%] AI Credit 원장   │
└────────────────────────────────────────────────────────────────────────┘
```

---

### 2. 본 플랫폼의 핵심 질문에 대한 최종 결론

#### Q1. "이 서비스를 0부터 만드는 대신, 2026년 현재 존재하는 오픈소스를 최대한 조합하면 어느 정도까지 만들 수 있는가?"
* **약 75% 수준까지 오픈소스로 즉시 구축 가능합니다.**
  * 에이전트가 코드를 파악하고 수정하여 Git에 커밋하는 기능: `Aider`와 `OpenHands`를 결합하여 해결.
  * 장기 실행 작업의 큐잉, 재시도, 장애 복구: `Temporal`로 해결.
  * 생성된 PR에 대한 자동 코드 리뷰 및 테스트 피드백: `Qodo PR-Agent`로 해결.
  * 공식 API 키 자원의 풀링 및 로드밸런싱: `LiteLLM`으로 해결.
  * 코드 실행 보안 격리: `E2B` 및 `Docker`로 해결.
  * 원시 토큰/이벤트 수집: `OpenMeter`로 해결.
* **결과**: 개발팀이 에이전트 런타임, Git 연동, 큐 인프라, 샌드박스를 바닥부터 개발할 필요가 전혀 없습니다.

#### Q2. "기존 오픈소스와 차별화되는, 우리가 반드시 직접 만들어야 하는 핵심(Core IP)은 무엇인가?"
우리가 반드시 직접 개발해야 하는 영역은 **오픈소스 생태계에 존재하지 않는 다음 3가지 핵심 블록(25%)**입니다.

1. **Self-Hosted AI Worker Daemon & Connection Protocol**:
   * 각 개발자가 자신의 PC에서 개인 구독(Claude Max, Gemini 등) 세션을 안전하게 유지한 채, 플랫폼의 공용 태스크를 수주받아 로컬 Docker 샌드박스에서 수행하고 결과(Commit Diff)만 중앙으로 반환하는 **경량 러너 데몬 및 통신 프로토콜**.
2. **AI Resource Pool & Dynamic Task Router**:
   * "로그인 API에 JWT 추가"라는 이슈가 들어왔을 때, 이를 분석하여 **"현재 온라인 상태인 Worker 중 Claude Max를 보유한 Developer A의 노드"**로 디스패치할지, **"Gemini Pro를 보유한 Developer B의 노드"**로 보낼지 결정하는 **동적 자원 풀 라우팅 엔진**.
3. **AI Credit Exchange & Contribution Ledger**:
   * 서로 다른 AI 모델(Claude의 비싼 고지능 토큰 vs Gemini의 대규모 고속 토큰)의 소모량을 단일 통화 단위인 `AI Credit`으로 정규화(Normalization)하고, PR 머지 성공 여부와 결합하여 프로젝트 기여도 지분으로 환산·기록하는 **기여도 원장 시스템**.

이 3가지 핵심 영역에 개발 역량을 집중하고, 나머지 기반 인프라는 `OpenHands`, `Aider`, `LiteLLM`, `Temporal`, `Qodo PR-Agent`를 조합하는 것이 2026년 현재 가장 빠르고 견고하게 상업적 성공을 달성할 수 있는 최적의 아키텍처 전략입니다.
