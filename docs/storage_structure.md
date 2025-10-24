# 📦 Supabase Storage 구조 및 규칙

## 📋 목차
1. [Storage Bucket 설정](#storage-bucket-설정)
2. [폴더 구조](#폴더-구조)
3. [파일명 규칙](#파일명-규칙)
4. [메타데이터 관리](#메타데이터-관리)
5. [업로드 플로우](#업로드-플로우)

---

## 🪣 Storage Bucket 설정

### Bucket 정보
```yaml
Bucket ID: pill-photos
공개 여부: false (비공개)
파일 크기 제한: 10MB
허용 MIME 타입:
  - image/jpeg
  - image/png
  - image/webp
```

### RLS (Row Level Security) 정책
```sql
-- 인증된 사용자만 접근 가능
storage_read_auth:   SELECT (authenticated)
storage_write_auth:  INSERT (authenticated)
storage_update_auth: UPDATE (authenticated)
storage_delete_auth: DELETE (authenticated)
```

---

## 📂 폴더 구조

### 전체 구조
```
pill-photos/                        # Root bucket
└── CS_{N}_single/                  # 촬영 세션 폴더
    ├── K-030864/                   # 약품별 폴더 (K-CODE)
    │   ├── K-030864_0_3_front_0_90_000_200.jpg
    │   ├── K-030864_0_3_front_0_90_045_200.jpg
    │   ├── ...
    │   └── K-030864_4_8_back_0_90_315_200.jpg
    ├── K-044579/
    └── ...
```

### 세션 폴더 명명 규칙
```
CS_{N}_single
```
- `CS`: Capture Session
- `{N}`: 세션 번호 (1부터 시작)
- `single`: 단일 약품 모드 (vs combo)

**예시:**
- `CS_1_single`: 첫 번째 촬영 세션
- `CS_2_single`: 두 번째 촬영 세션

### 약품 폴더 명명 규칙
```
K-{6자리숫자}
```
- K-CODE 그대로 사용
- 하이픈(-) 포함

**예시:**
- `K-030864`: 모사드린정
- `K-044579`: 일성레바미피드정

---

## 📝 파일명 규칙

### 파일명 형식
```
K-{KCODE}_{BG}_{LED}_{SIDE}_{FORM}_{ANGLE}_{ROT}_{SIZE}.jpg
```

### 각 필드 설명

#### 1. K-CODE (약품 코드)
- 형식: `K-{6자리숫자}`
- 예시: `K-030864`

#### 2. BG (배경)
| 코드 | 의미 | 비고 |
|------|------|------|
| 0 | 손바닥 | skin_palm |
| 1 | 나무 테이블 | wood_table |
| 2 | 흰색 | white |
| 3 | 검은색 | black |
| 4 | 패턴 | pattern_check |

#### 3. LED (조명 밝기)
| 코드 | 의미 |
|------|------|
| 3 | LED 레벨 3 (낮음) |
| 5 | LED 레벨 5 (중간) |
| 8 | LED 레벨 8 (높음) |

#### 4. SIDE (약품 면)
| 코드 | 의미 |
|------|------|
| front | 앞면 |
| back | 뒷면 |

#### 5. FORM (제형)
| 코드 | 의미 | 비고 |
|------|------|------|
| 0 | 정제 | tablet |
| 1 | 캡슐 | capsule |

#### 6. ANGLE (앙각)
| 코드 | 의미 |
|------|------|
| 90 | 수직 (90도) |

**현재 프로젝트는 90도 고정**

#### 7. ROT (회전각)
| 코드 | 의미 |
|------|------|
| 000 | 0도 (정면) |
| 045 | 45도 |
| 090 | 90도 |
| 135 | 135도 |
| 180 | 180도 |
| 225 | 225도 |
| 270 | 270도 |
| 315 | 315도 |

**8단계 회전 (45도 간격)**

#### 8. SIZE (이미지 크기)
| 코드 | 의미 |
|------|------|
| 200 | 200x200 (정사각형) |

### 파일명 예시

```bash
# 손바닥 배경, LED 3, 앞면, 정제, 90도 앙각, 0도 회전
K-030864_0_3_front_0_90_000_200.jpg

# 나무 배경, LED 5, 뒷면, 정제, 90도 앙각, 180도 회전
K-030864_1_5_back_0_90_180_200.jpg

# 흰색 배경, LED 8, 앞면, 캡슐, 90도 앙각, 45도 회전
K-044579_2_8_front_1_90_045_200.jpg
```

### 파일명 생성 로직 (Pseudo Code)

```python
def generate_filename(kcode, bg, led, side, form, angle, rotation):
    """
    촬영 파라미터로부터 파일명 생성
    """
    return f"{kcode}_{bg}_{led}_{side}_{form}_{angle}_{rotation:03d}_200.jpg"

# 사용 예시
filename = generate_filename(
    kcode="K-030864",
    bg=0,              # 손바닥
    led=3,             # LED 레벨 3
    side="front",      # 앞면
    form=0,            # 정제
    angle=90,          # 90도 앙각
    rotation=45        # 45도 회전
)
# 결과: K-030864_0_3_front_0_90_045_200.jpg
```

---

## 🗄️ 메타데이터 관리

### capture_real_photos 테이블

파일 업로드 시 메타데이터를 DB에 저장합니다:

```sql
INSERT INTO capture_real_photos (
    kcode,
    photo_url,
    capture_angle,
    turntable_angle,
    background_color,
    led_brightness,
    quality_grade,
    blur_score,
    exposure_score,
    centering_score
) VALUES (
    'K-030864',
    'pill-photos/CS_1_single/K-030864/K-030864_0_3_front_0_90_000_200.jpg',
    'front',
    0,
    'skin_palm',
    3,
    'A',
    0.95,
    0.88,
    0.92
);
```

### 메타데이터 필드

| 필드 | 타입 | 설명 | 예시 |
|------|------|------|------|
| kcode | VARCHAR(20) | 약품 코드 | K-030864 |
| photo_url | TEXT | Storage 경로 | pill-photos/CS_1_single/... |
| capture_angle | VARCHAR(10) | 촬영 면 | front, back |
| turntable_angle | INTEGER | 회전각 (0-360) | 0, 45, 90, ... |
| background_color | VARCHAR(20) | 배경 타입 | skin_palm, wood_table |
| led_brightness | INTEGER | LED 밝기 (1-10) | 3, 5, 8 |
| quality_grade | VARCHAR(1) | 품질 등급 | A, B, C |
| blur_score | FLOAT | 선명도 점수 (0-1) | 0.95 |
| exposure_score | FLOAT | 노출 점수 (0-1) | 0.88 |
| centering_score | FLOAT | 중앙 정렬 점수 (0-1) | 0.92 |

---

## 📤 업로드 플로우

### 1. Flutter 앱에서 촬영
```dart
// 1. 카메라로 촬영
final XFile photo = await camera.takePicture();

// 2. 파일명 생성
final filename = generateFilename(
  kcode: 'K-030864',
  bg: 0,
  led: 3,
  side: 'front',
  form: 0,
  angle: 90,
  rotation: 0,
);

// 3. Storage 경로 생성
final storagePath = 'CS_1_single/K-030864/$filename';
```

### 2. Supabase Storage 업로드
```dart
// 4. Storage에 업로드
final response = await supabase.storage
  .from('pill-photos')
  .upload(
    storagePath,
    photo,
    fileOptions: FileOptions(
      contentType: 'image/jpeg',
      upsert: false,  // 중복 방지
    ),
  );

final publicUrl = supabase.storage
  .from('pill-photos')
  .getPublicUrl(storagePath);
```

### 3. 메타데이터 저장
```dart
// 5. DB에 메타데이터 저장
await supabase.from('capture_real_photos').insert({
  'kcode': 'K-030864',
  'photo_url': storagePath,
  'capture_angle': 'front',
  'turntable_angle': 0,
  'background_color': 'skin_palm',
  'led_brightness': 3,
  'quality_grade': qualityGrade,  // 품질 검증 결과
  'blur_score': blurScore,
  'exposure_score': exposureScore,
  'centering_score': centeringScore,
});
```

### 4. 진행 상황 업데이트
```dart
// 6. 약품별 촬영 진행 상황 자동 업데이트 (트리거 작동)
// capture_drugs_master 테이블의 photos_taken, is_complete 자동 갱신
```

---

## 📊 통계 및 쿼리

### 전체 진행 상황 확인
```sql
SELECT * FROM capture_progress;
-- total_drugs: 100
-- completed_drugs: 5
-- completion_rate: 5.0%
```

### 약품별 촬영 현황
```sql
SELECT
    kcode,
    drug_name,
    photos_taken,
    photos_required,
    is_complete
FROM capture_drugs_master
WHERE is_active = true
ORDER BY photos_taken DESC;
```

### Storage 사용량 확인
```sql
SELECT
    COUNT(*) as total_files,
    pg_size_pretty(SUM(metadata->>'size')::bigint) as total_size
FROM storage.objects
WHERE bucket_id = 'pill-photos';
```

### 품질 등급별 분포
```sql
SELECT
    quality_grade,
    COUNT(*) as count,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER(), 2) as percentage
FROM capture_real_photos
GROUP BY quality_grade
ORDER BY quality_grade;
```

---

## ⚠️ 주의사항

### 파일명 제약
1. **영문/숫자/언더스코어(_)/하이픈(-)만** 사용
2. **공백, 한글, 특수문자 금지**
3. **확장자는 소문자 `.jpg`로 통일**
4. **파일명 중복 방지** (upsert: false)

### Storage 제약
1. **10MB 이하 파일만** 업로드 가능
2. **JPEG/PNG/WebP만** 허용
3. **인증된 사용자만** 접근 가능

### 데이터 무결성
1. **DB와 Storage 동기화** 필수
2. **파일 삭제 시 DB 레코드도 삭제**
3. **orphaned 파일 주기적 정리**

---

## 🔄 마이그레이션 (향후)

기존 스튜디오 데이터셋 구조와 호환성:
```
기존: K-030864_0_0_0_0_90_000_200.png
신규: K-030864_0_3_front_0_90_000_200.jpg
```

차이점:
1. LED 밝기 추가 (0 → 3/5/8)
2. 면 구분 명시 (없음 → front/back)
3. 확장자 변경 (png → jpg)

**기존 데이터셋 매핑 필요 시:**
```python
def convert_old_to_new(old_filename):
    parts = old_filename.split('_')
    kcode = parts[0]
    bg = parts[1]
    # LED는 기본값 5로 설정
    led = 5
    # 면은 기본값 front로 설정
    side = 'front'
    form = parts[4]
    angle = parts[5]
    rotation = parts[6].split('.')[0]

    return f"{kcode}_{bg}_{led}_{side}_{form}_{angle}_{rotation}_200.jpg"
```

---

**최종 수정일**: 2025-10-24
**작성자**: Claude Code
**프로젝트**: PillSnap Narrow Model - Phase 2
