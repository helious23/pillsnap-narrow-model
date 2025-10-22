# 📅 PillSnap Narrow Model - 일일 진행 로그

## 2024-10-22 (화요일)

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

*Last updated: 2024-10-22 17:30 KST*