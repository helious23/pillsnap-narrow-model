# 📅 PillSnap Narrow Model - 일일 진행 로그

## 2025-10-22 (화요일)

### ✅ 완료된 작업

#### 14:00-17:00 | Phase별 상세 계획서 작성 완료
- [x] Phase 1: 데이터 준비 계획서 (`planning/phase1_data_prep.md`)
  - K-CODE와 EDI 매핑 워크플로우 설계
  - 약국 사용량 기반 선정 프로세스
  - 100개 약품 선정 기준 및 검증 방법

- [x] Phase 2: 수집 시스템 구축 계획서 (`planning/phase2_collection.md`)
  - DIY 촬영 Kit 사양 (예산: 50,000원)
  - Flutter 앱 아키텍처 및 기능 명세
  - Supabase 백엔드 스키마 설계

- [x] Phase 3: 실제 약품 사진 수집 계획서 (`planning/phase3_photo_collection.md`)
  - 파일럿 테스트 프로토콜 (30개 약품)
  - 5일간 집중 촬영 일정 (일일 20개)
  - 품질 관리 및 A등급 70% 달성 전략

- [x] Phase 4: 모델 학습 계획서 (`planning/phase4_training.md`)
  - UnifiedPreprocessor 표준화 설계
  - 스튜디오:실사진 = 3:7 통합 전략
  - EfficientNetV2-S 학습 파이프라인

- [x] Phase 5: 모델 배포 계획서 (`planning/phase5_deployment.md`)
  - ONNX 변환 및 최적화 (양자화)
  - 추론서버 100개 클래스 전용 엔드포인트
  - 약국 현장 테스트 프로토콜

#### 17:00 | GitHub 프로젝트 구조 완성
- 프로젝트 디렉토리 구조 생성
- 57개 상세 작업 TODO 리스트 문서화
- 진행 상황 추적 시스템 구축

### 🔄 진행중인 작업

#### K-CODE와 EDI 매핑 테이블 구축
- 파일 위치 확인 완료:
  - `/home/max16/pillsnap_inference/mapping/kcode_label_map.json`
  - `/home/max16/pillsnap_bff/migrations/drugs_master.csv`
- 다음 단계: 매핑 스크립트 작성 및 실행

### 📝 내일 계획 (2024-10-23)

1. **오전 (09:00-12:00)**
   - [ ] K-CODE-EDI 매핑 스크립트 작성 및 실행
   - [ ] 약국 사용량 데이터 확보 (사용자 제공 필요)
   - [ ] 4,523개 중 EDI 매핑된 항목 필터링

2. **오후 (13:00-18:00)**
   - [ ] 사용량 기준 상위 200개 추출
   - [ ] Excel 검토 파일 생성
   - [ ] 촬영 Kit 구매 리스트 작성

### 📊 진행 통계

| Phase | 진행률 | 완료 작업 | 전체 작업 |
|-------|--------|-----------|-----------|
| **전체** | 8.8% | 5/57 | 57 |
| **Phase 1** | 0% | 0/7 | 7 |
| **Phase 2** | 0% | 0/16 | 16 |
| **Phase 3** | 0% | 0/8 | 8 |
| **Phase 4** | 0% | 0/14 | 14 |
| **Phase 5** | 0% | 0/12 | 12 |
| **문서화** | 100% | 5/5 | 5 |

### 💡 이슈 및 메모

- **데이터 필요**: 약국 사용량 CSV 파일이 필요함 (EDI 코드별 처방 데이터)
- **Galaxy S21**: 촬영용 스마트폰 주문 상태 확인 필요
- **협력 요청**: 약사회 또는 약국 협조 요청 준비 필요

### 🔗 참고 링크

- GitHub Repository: https://github.com/helious23/pillsnap-narrow-model
- 프로젝트 문서: `/home/max16/pillsnap-narrow-model/planning/`

---

## 2025-10-22 (화요일) - 실제 작업

### ✅ 완료된 작업

#### 18:00-20:30 | Phase 1 데이터 준비 작업
- [x] Python 3.11 가상환경 설정 (`.venv`)
- [x] 데이터 추출 스크립트 구현 (`scripts/data_prep/prepare_drug_selection.py`)
  - K-CODE와 EDI 매핑 기능: 4,397개 매핑 성공
  - actual_list.xlsx 사용량 데이터 추출: 1,746개 EDI 처리
  - 562개 약품의 실제 사용량 데이터 매칭
  - EDI 중복 제거 로직 구현

- [x] Excel 작업 파일 생성 (`drug_selection_workspace.xlsx`)
  - All_Drugs 시트: 전체 4,998개 K-CODE
  - Top_200 시트: 사용량 상위 200개 약품
  - Statistics 시트: 매핑 통계 정보

#### 상위 10개 약품 (사용량 기준)
1. K-030864: 모사드린정 (120,848)
2. K-044579: 일성레바미피드정 (97,690)
3. K-000231: 인데놀정 10mg (97,193)
4. K-003544: 무코스타정(레바미피드) (93,410)
5. K-015867: 무코란정 (80,781)

### 📊 진행 통계

| Phase | 진행률 | 완료 작업 | 전체 작업 |
|-------|--------|-----------|-----------|
| **전체** | 7% | 4/57 | 57 |
| **Phase 1** | 57% | 4/7 | 7 |
| **Phase 2** | 0% | 0/16 | 16 |
| **Phase 3** | 0% | 0/8 | 8 |
| **Phase 4** | 0% | 0/14 | 14 |
| **Phase 5** | 0% | 0/12 | 12 |

### 📝 내일 계획 (2025-10-23)

1. **오전 (09:00-12:00)**
   - [ ] Excel 파일에서 촬영 가능한 100개 약품 수동 선정
   - [ ] PTP/연질캡슐/소형약품 표시 작업

2. **오후 (13:00-18:00)**
   - [ ] 최종 100개 약품 메타데이터 JSON 생성
   - [ ] Phase 2 준비: Flutter 앱 개발 환경 설정
   - [ ] 촬영 장비 구매 리스트 작성

### 💡 이슈 및 메모

- **매칭 성공률**: 562개 약품만 사용량 매칭 (예상보다 낮음)
- **데이터 품질**: EDI 코드 매핑이 완벽하지 않음 (추가 보완 필요)
- **다음 단계**: Excel 작업 후 실제 촬영 가능성 검토 필수

---

## 2025-10-23 (수요일)

### ✅ 완료된 작업

#### 09:00-14:00 | Phase 1 완료 - 100개 약품 최종 선정
- [x] Excel 검토 및 수동 선정 작업
  - 상위 200개 중 shootable 기준 필터링
  - Y (촬영 용이): 92개, M (중간 난이도): 8개
  - PTP 블리스터 포장, 소형 약품 제외

- [x] 최종 메타데이터 생성
  - `artifacts/top_100_metadata_final.json` 생성
  - K-CODE, EDI, 약품명, 제조사, 사용량, 촬영난이도 포함
  - 총 사용량: 1,784,622건, 평균: 17,846건

- [x] 촬영 체크리스트 생성
  - `scripts/capture_checklist.csv` 생성
  - Front/Back 촬영 진행 상황 추적

#### 14:00-18:00 | Phase 2 시작 - Supabase 백엔드 구축
- [x] Supabase 스키마 설계
  - `scripts/setup_supabase_final.sql` 작성
  - capture_drugs_master: 100개 약품 마스터 데이터
  - capture_real_photos: 촬영 사진 메타데이터
  - capture_sessions: 촬영 세션 추적
  - capture_background_colors: 배경색 정의

- [x] MCP Supabase로 스키마 적용
  - 테이블 생성 및 제약조건 설정
  - RLS (Row Level Security) 정책 적용
  - Storage bucket 설정

- [x] 100개 약품 데이터 로드
  - `scripts/load_drugs_to_supabase.py` 구현
  - INSERT ON CONFLICT 로직으로 안전한 로드
  - 100개 약품 데이터 Supabase 업로드 완료

#### 15:00-20:00 | 실제 촬영 전략 수립
- [x] 기존 데이터셋 구조 상세 분석
  - 파일명 컨벤션: K-CODE_배경_조명_면_형태_앙각_회전각_크기.png
  - 18단계 회전 (20도 간격), 4단계 앙각
  - 약품당 1,296장 (3 조명 × 2 면 × 3 형태 × 4 앙각 × 18 회전)

- [x] 촬영 조건 설계
  - 배경: 5종 (손바닥, 나무, 흰색, 검은색, 패턴)
  - 조명: 3단계 (LED 3, 5, 8)
  - 앙각: 90도 고정 (수직)
  - 회전: 8단계 (45도 간격)
  - **약품당: 240장 (5×3×8×2)**
  - **총: 24,000장 (100개 약품)**

- [x] 배경 타입 추가
  - Supabase에 5가지 실제 배경 추가
  - skin_palm, wood_table, white, black, pattern_check

- [x] 촬영 프로토콜 문서 작성
  - `docs/capture_protocol.md` 작성 (448줄)
  - 파일명 컨벤션, 폴더 구조
  - 품질 검증 기준 (A/B/C 등급)
  - 회전판 타이밍 자동화 로직
  - 예상 소요 시간: 16일 (하루 8시간)

### 📊 진행 통계

| Phase | 진행률 | 완료 작업 | 전체 작업 |
|-------|--------|-----------|-----------|
| **전체** | 12% | 7/57 | 57 |
| **Phase 1** | 100% | 7/7 | 7 ✅ |
| **Phase 2** | 19% | 3/16 | 16 |
| **Phase 3** | 0% | 0/8 | 8 |
| **Phase 4** | 0% | 0/14 | 14 |
| **Phase 5** | 0% | 0/12 | 12 |

### 🎯 Phase 1 완료 요약

**목표:** 100개 약품 선정 ✅
**달성:**
- 4,397개 K-CODE EDI 매핑
- 562개 약품 사용량 매칭
- 상위 200개 후보 추출
- **최종 100개 선정 완료**
- Supabase에 데이터 로드

**선정 기준:**
- 사용량 상위 200개 중 선별
- 촬영 용이성 (Y: 92개, M: 8개)
- 정제/경질캡슐 형태만 (PTP 블리스터 제외)

### 📝 내일 계획 (2025-10-24)

1. **오전 (09:00-12:00)**
   - [ ] Flutter 프로젝트 생성 및 기본 구조
   - [ ] Camera2 API 패키지 통합
   - [ ] 권한 설정 (카메라, 저장소)

2. **오후 (13:00-18:00)**
   - [ ] 약품 선택 UI 구현
   - [ ] Supabase 연동 (인증, 데이터 로드)
   - [ ] 촬영 가이드 UI 프로토타입

3. **저녁 (19:00-21:00)**
   - [ ] 촬영 장비 구매 리스트 작성
   - [ ] LED 스튜디오 박스, 회전판 검색

### 💡 이슈 및 메모

**Phase 1 완료 성과:**
- ✅ 100개 약품 선정 완료
- ✅ Supabase 백엔드 80% 완료
- ✅ 촬영 전략 및 프로토콜 수립

**Phase 2 진행 상황:**
- Supabase: 3/4 완료 (75%)
- Flutter 앱: 0/7 (시작 전)
- 촬영 환경: 0/5 (시작 전)

**다음 우선순위:**
1. Flutter 앱 개발 시작
2. 파일럿 테스트용 장비 구매
3. 1개 약품으로 240장 테스트 촬영

### 🔗 산출물

**Phase 1:**
- `artifacts/top_100_metadata_final.json` - 100개 약품 메타데이터
- `scripts/capture_checklist.csv` - 촬영 진행 체크리스트

**Phase 2:**
- `scripts/setup_supabase_final.sql` - Supabase 스키마
- `scripts/load_drugs_to_supabase.py` - 약품 데이터 로드
- `scripts/supabase_load_drugs.sql` - SQL 로드 스크립트
- `docs/capture_protocol.md` - 촬영 프로토콜 문서 (448줄)

---

*Last updated: 2025-10-23 20:15 KST*
