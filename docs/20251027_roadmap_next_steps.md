# 🗺️ PillSnap Narrow Model - 다음 단계 로드맵

**작성일**: 2025-10-27

---

## 📋 진행 순서 (우선순위별)

### 1️⃣ **BFF 서버 Narrow 엔드포인트 개발** (Linux PC)

**위치**: `/home/max16/pillsnap_bff`

**구현할 API:**

```python
POST /v1/narrow/analyze
- 100개 제한 K-CODE로만 추론
- allowed_kcodes 파라미터 사용
- 기존 /v1/analyze 로직 재사용

GET /v1/narrow/kcodes
- 100개 K-CODE 목록 반환
- 약품명, 제조사 포함
```

**예상 시간**: 1일

---

### 2️⃣ **Flutter 앱 Narrow 기능 추가** (맥북)

**위치**: 기존 pillsnap 프로젝트 (로컬, GitHub 미등록)

**추가할 기능:**
- 홈 화면에 Narrow 모드 토글 버튼
- Narrow 모드 활성화 시 100개 제한 추론
- BFF `/v1/narrow/analyze` 호출
- 결과 화면에 "Narrow 모드" 표시

**기존 코드 활용:**
- 카메라 촬영 로직 재사용
- 기존 UI 컴포넌트 재사용
- API 서비스만 분기 처리

**예상 시간**: 2-3일

**GitHub 등록:**
- Narrow 기능 완성 후 첫 커밋
- 저장소: `pillsnap` (앱 전체)

---

### 3️⃣ **실제 스튜디오 촬영** (최종)

**조건:**
- 장비 도착 대기 중
- Flutter 앱 Narrow 기능 완성
- 주말 외 시간

**촬영:**
- 100개 약품 × 240장 = 24,000장
- 예상 소요: 16일

---

## ✅ 체크리스트

### BFF 개발 (Linux PC)
- [ ] `/v1/narrow/analyze` 엔드포인트
- [ ] `/v1/narrow/kcodes` 엔드포인트
- [ ] 테스트 작성
- [ ] Docker 재빌드

### Flutter 개발 (맥북)
- [ ] Narrow 모드 토글 UI
- [ ] API 호출 분기 처리
- [ ] 결과 화면 Narrow 표시
- [ ] iOS/Android 테스트
- [ ] GitHub 첫 커밋

### 촬영
- [ ] 장비 세팅
- [ ] 파일럿 테스트
- [ ] 본 촬영

---

## 🔗 관련 문서
- [20251024_capture_protocol.md](./20251024_capture_protocol.md)
- [20251024_storage_structure.md](./20251024_storage_structure.md)
