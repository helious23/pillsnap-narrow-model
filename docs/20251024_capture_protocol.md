# PillSnap Narrow Model 실제 촬영 프로토콜

## 🎯 촬영 목표

**목적:** 도메인 갭 해소를 위한 Head Fine-tuning 데이터 수집
- 기존 230만장 스튜디오 데이터로 학습된 모델
- 실사용 환경(손으로 들고 촬영) 데이터 부족
- 100개 선정 약품 × 240장 = **24,000장** 촬영

## 📊 촬영 조건 상세

### 고정 조건
- **약품 수**: 100개
- **앙각**: 90도 (수직 고정)
- **회전각**: 8개 (0, 45, 90, 135, 180, 225, 270, 315도)
- **촬영 면**: Front, Back (2개)

### 가변 조건
- **배경**: 5종류
  1. `skin_palm` - 손바닥 (#F5D5C5)
  2. `wood_table` - 나무 테이블 (#8B4513)
  3. `white` - 흰색 종이/천 (#FFFFFF)
  4. `black` - 검은색 천 (#000000)
  5. `pattern_check` - 체크무늬/패턴 (#CCCCCC)

- **조명**: 3단계
  - LED 3 (어두움)
  - LED 5 (정상)
  - LED 8 (밝음)

### 촬영량 계산
```
5 배경 × 3 조명 × 8 회전 × 2 면 = 240장/약품
100 약품 × 240장 = 24,000장
```

## 📁 파일명 컨벤션

### 기존 데이터셋 형식 준수
```
K-CODE_배경_조명_면_형태_앙각_회전각_크기.jpg
```

### 필드 상세
| 필드 | 값 | 설명 |
|------|-----|------|
| K-CODE | K-030864 | 약품 코드 |
| 배경 | 0-4 | 0=손바닥, 1=나무, 2=흰색, 3=검은색, 4=패턴 |
| 조명 | 0-2 | 0=LED3, 1=LED5, 2=LED8 |
| 면 | 0-1 | 0=front, 1=back |
| 형태 | 0 | 고정 (기울임 없음) |
| 앙각 | 90 | 수직 촬영 |
| 회전각 | 000-315 | 45도 간격 (000, 045, 090, 135, 180, 225, 270, 315) |
| 크기 | 200 | 고정값 |

### 파일명 예시
```
K-030864_0_0_0_0_90_000_200.jpg  # 손바닥, LED3, Front, 0도
K-030864_0_0_0_0_90_045_200.jpg  # 손바닥, LED3, Front, 45도
K-030864_0_1_0_0_90_000_200.jpg  # 손바닥, LED5, Front, 0도
K-030864_0_0_1_0_90_000_200.jpg  # 손바닥, LED3, Back, 0도
K-030864_1_0_0_0_90_000_200.jpg  # 나무, LED3, Front, 0도
```

## 📂 폴더 구조

### 로컬 저장 구조 (기존 데이터셋 형식)
```
/capture_photos/
└── single/
    └── CS_1_single/           # Capture Setup 1
        ├── K-030864/          # 약품별 폴더
        │   ├── K-030864_0_0_0_0_90_000_200.jpg
        │   ├── K-030864_0_0_0_0_90_045_200.jpg
        │   ├── ... (240장)
        ├── K-044579/
        └── ... (100개 약품)
```

### Supabase Storage 구조
```
pill-photos/
└── CS_1_single/
    ├── K-030864/
    │   └── K-030864_0_0_0_0_90_000_200.jpg
    ├── K-044579/
    └── ...
```

## 🛠️ 하드웨어 세팅

### LED 스튜디오 박스
- 크기: 200mm × 200mm × 200mm
- LED: 96개 비드, CRI 97+
- 색온도: 5500K 고정

### 360도 회전판 (흰색)
- 직경: 13.8cm
- 속도: 4 RPM 권장
- 각도 설정: 45도

### Galaxy S21
- 수직 고정 (삼각대 사용)
- 카메라 높이: 박스 상단 10-15cm
- 해상도: 4000×3000 (12MP)
- ISO: 100 고정
- 셔터 스피드: 1/100초

### 배경 재료
1. **손바닥**: 손바닥 사진 출력물 (A4)
2. **나무 테이블**: 나무 무늬 사진/원목 보드
3. **흰색**: 흰색 A4 용지
4. **검은색**: 검은색 천/종이
5. **패턴**: 체크무늬 천/신문지

## 📸 촬영 프로세스

### 1단계: 환경 초기 설정 (1회만)
```
1. LED 스튜디오 박스 조립
2. 회전판을 박스 중앙 배치
3. Galaxy S21 수직 고정 (삼각대)
4. Flutter 앱 설치 및 로그인
5. 배경 재료 5종 준비
```

### 2단계: 약품 선택
```
1. Flutter 앱 실행
2. 100개 약품 목록에서 선택
3. 촬영 모드 진입
```

### 3단계: 배경별 촬영 (48장/배경)

#### 배경 1: 손바닥 (48장, 15분)
```
LED 3 설정
├─ Front: 0→45→90→135→180→225→270→315 (8장)
│   - 회전 버튼 누름 → 2.5초 대기 → 자동 촬영
└─ Back: 알약 뒤집기 → 8장 동일 촬영

LED 5 설정 → Front 8장 + Back 8장 (16장)
LED 8 설정 → Front 8장 + Back 8장 (16장)

총 48장 촬영 완료
품질 확인 (자동)
```

#### 배경 2-5: 동일 프로세스 반복
```
배경 교체 (1분)
↓
나무 테이블: 48장 (15분)
↓
배경 교체 (1분)
↓
흰색 종이: 48장 (15분)
↓
배경 교체 (1분)
↓
검은색 천: 48장 (15분)
↓
배경 교체 (1분)
↓
패턴 배경: 48장 (15분)
```

### 4단계: 품질 검증
```
촬영 완료 후 자동 검증:
- 선명도 (라플라시안 분산 > 100)
- 노출 (히스토그램 평균 50-200)
- 중앙 정렬 (프레임 중앙 20% 이내)
- 반사광 (밝은 스팟 < 10%)

등급 판정:
- A등급: 모든 지표 80% 이상
- B등급: 모든 지표 60% 이상
- C등급: 재촬영 필요
```

### 5단계: Supabase 업로드
```
WiFi 환경에서 자동 업로드
- 배치 단위: 240장 (1약품 완료 시)
- 메타데이터 동시 저장
```

## ⏱️ 소요 시간

### 약품당
- 배경 1 (손바닥): 15분
- 배경 교체: 1분
- 배경 2 (나무): 15분
- 배경 교체: 1분
- 배경 3 (흰색): 15분
- 배경 교체: 1분
- 배경 4 (검은색): 15분
- 배경 교체: 1분
- 배경 5 (패턴): 15분
- **총: 80분 (1.3시간)/약품**

### 전체 100개
- 100 × 1.3시간 = 130시간
- 하루 8시간 작업 시 **16일 소요**

## 📊 Supabase 데이터 구조

### capture_real_photos 테이블
```sql
{
  "id": "uuid",
  "kcode": "K-030864",
  "photo_url": "https://...pill-photos/CS_1_single/K-030864/...",
  "capture_date": "2025-10-23T14:30:00Z",
  "capture_device": "Galaxy S21",
  "capture_angle": "front",           -- 'front' or 'back'
  "turntable_angle": 45,               -- 0, 45, 90, 135, 180, 225, 270, 315
  "background_color": "skin_palm",     -- 5종류
  "led_brightness": 5,                 -- 3, 5, 8
  "color_temperature": 5500,           -- 고정
  "quality_grade": "A",                -- A, B, C
  "blur_score": 0.95,                  -- 0-1
  "exposure_score": 0.88,              -- 0-1
  "centering_score": 0.92,             -- 0-1
  "lighting_mode": "white",            -- 고정
  "studio_settings": {
    "box_model": "LED Light Box 200mm",
    "rpm": 4,
    "angle_interval": 45
  }
}
```

### 배경색 매핑 (capture_background_colors)
| ID | color_name | hex_code | is_recommended |
|----|------------|----------|----------------|
| 13 | skin_palm | #F5D5C5 | true |
| 14 | wood_table | #8B4513 | true |
| 2 | white | #FFFFFF | true |
| 1 | black | #000000 | true |
| 15 | pattern_check | #CCCCCC | true |

## ✅ 품질 검증 상세

### 자동 검증 알고리즘

#### 1. 선명도 (Sharpness)
```python
# 라플라시안 분산 계산
laplacian = cv2.Laplacian(image, cv2.CV_64F)
variance = laplacian.var()

score = min(1.0, variance / 200)  # 정규화
threshold = 0.5  # 최소 기준
```

#### 2. 노출 (Exposure)
```python
# 히스토그램 분석
histogram = cv2.calcHist([image], [0], None, [256], [0,256])
mean_brightness = histogram.mean()

# 과노출/부족노출 체크
overexposed = (image > 240).sum() / image.size
underexposed = (image < 15).sum() / image.size

score = 1.0 - max(overexposed, underexposed)
threshold = 0.6
```

#### 3. 중앙 정렬 (Centering)
```python
# 윤곽선 검출
contours = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
pill_contour = max(contours, key=cv2.contourArea)

# 중심점 계산
M = cv2.moments(pill_contour)
cx = int(M['m10'] / M['m00'])
cy = int(M['m01'] / M['m00'])

# 프레임 중심과 거리
distance = sqrt((cx - width/2)**2 + (cy - height/2)**2)
max_distance = sqrt((width/2)**2 + (height/2)**2)

score = 1.0 - (distance / max_distance)
threshold = 0.7
```

#### 4. 반사광 (Reflection)
```python
# 밝은 스팟 영역 감지
bright_spots = (image > 250).sum() / image.size

score = 1.0 - bright_spots
threshold = 0.9  # 10% 미만이어야 함
```

### 등급 판정 로직
```python
def calculate_grade(scores):
    min_score = min(scores.values())
    avg_score = sum(scores.values()) / len(scores)

    if avg_score >= 0.85 and min_score >= 0.7:
        return 'A'
    elif avg_score >= 0.65 and min_score >= 0.5:
        return 'B'
    else:
        return 'C'  # 재촬영
```

## 🔄 회전 타이밍 자동화

### 4 RPM 기준 시간 계산
```dart
// 회전판 속도: 4 RPM = 1회전/15초
final rotationTimes = {
  45: 1.875,    // 초 (45/360 × 15)
  90: 3.75,     // 초
  135: 5.625,   // 초
  180: 7.5,     // 초
  225: 9.375,   // 초
  270: 11.25,   // 초
  315: 13.125,  // 초
  360: 15.0,    // 초 (원위치)
};

// 안전 버퍼 추가 (정지 시간)
final captureDelay = 0.5;  // 초
```

### 촬영 시퀀스
```
1. 사용자가 회전 버튼 누름
2. 타이머 시작 (예: 1.875초 for 45도)
3. 회전 완료 대기
4. 0.5초 안정화 대기
5. 자동 촬영
6. 품질 즉시 검증
7. 결과 표시 + 다음 각도 가이드
```

## 📝 체크리스트

### 촬영 전 준비
- [ ] LED 스튜디오 박스 조립 완료
- [ ] 회전판 작동 테스트 (4 RPM, 45도)
- [ ] Galaxy S21 충전 100%
- [ ] 배경 재료 5종 준비
- [ ] Flutter 앱 설치 및 Supabase 연동 확인
- [ ] WiFi 연결 확인

### 약품별 촬영 체크
- [ ] 알약 중앙 배치 확인
- [ ] 배경 1 (손바닥): 48장 완료
- [ ] 배경 2 (나무): 48장 완료
- [ ] 배경 3 (흰색): 48장 완료
- [ ] 배경 4 (검은색): 48장 완료
- [ ] 배경 5 (패턴): 48장 완료
- [ ] 총 240장 품질 확인 (A/B 등급)
- [ ] Supabase 업로드 확인

### 일일 작업 종료
- [ ] 촬영 완료 약품 수 기록
- [ ] 실패한 약품 목록 (C등급)
- [ ] 로컬 백업 확인
- [ ] 다음 날 촬영 약품 준비

## 🚨 주의사항

### 1. 회전판 조작
- 회전 중 촬영 절대 금지
- 완전 정지 확인 후 촬영
- 일정한 속도 유지 (4 RPM)
- 각도 설정 정확히 확인 (45도)

### 2. 품질 관리
- C등급 발생 시 해당 배경 전체 재촬영
- Front/Back 구분 명확히
- 조명 변경 시 LED 안정화 대기 (5초)
- 배경 교체 시 중앙 정렬 재확인

### 3. 데이터 관리
- 로컬 백업 유지 (업로드 전까지)
- WiFi 환경에서만 대량 업로드
- 파일명 컨벤션 엄격히 준수
- 약품별 폴더 구조 유지

### 4. 하드웨어 관리
- Galaxy S21 과열 방지 (1시간마다 10분 휴식)
- LED 박스 환기 (2시간마다 10분)
- 회전판 배터리 충전 확인
- 삼각대 고정 상태 수시 확인

## 📈 진행 상황 모니터링

### Flutter 앱 대시보드
```
총 진행률: 42/100 약품 (42%)
오늘 촬영: 5약품 (1,200장)
평균 속도: 1.2시간/약품
남은 시간: 약 70시간 (9일)

품질 분포:
- A등급: 850장 (70%)
- B등급: 320장 (27%)
- C등급: 30장 (3%, 재촬영 완료)
```

### Supabase 쿼리
```sql
-- 전체 진행률
SELECT
  COUNT(DISTINCT kcode) as completed_drugs,
  COUNT(*) as total_photos
FROM capture_real_photos;

-- 약품별 진행 상황
SELECT
  kcode,
  COUNT(*) as photos_taken,
  COUNT(DISTINCT background_color) as backgrounds,
  COUNT(DISTINCT led_brightness) as lightings,
  ROUND(AVG(CASE
    WHEN quality_grade = 'A' THEN 100
    WHEN quality_grade = 'B' THEN 70
    ELSE 30
  END), 2) as avg_quality
FROM capture_real_photos
GROUP BY kcode
ORDER BY photos_taken DESC;
```

## 🎓 예상 결과

### 데이터셋 특성
- **총량**: 24,000장
- **다양성**: 5배경 × 3조명 = 15가지 환경
- **각도**: 8방향 × 2면 = 16각도
- **품질**: A/B 등급 90% 이상 목표

### Fine-tuning 효과 예상
- **Before**: 실사용 정확도 60-70%
- **After**: 실사용 정확도 85-90% 목표
- **개선**: 배경/조명 변화에 강건한 모델