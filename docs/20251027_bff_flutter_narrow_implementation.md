# 🔧 BFF & Flutter Narrow Mode 구현 가이드

**작성일**: 2025-10-27
**대상**: Linux PC (BFF 개발) + MacBook (Flutter 개발)
**목적**: 100개 선정 약품 Narrow Mode 구현
**저장소**: `helious23/pillsnap_mobile`

---

## 📋 진행 순서

### 1️⃣ **BFF 서버 Narrow 엔드포인트 개발** (Linux PC)

**위치**: `/home/max16/pillsnap_bff`
**예상 시간**: 1일

#### 구현할 API 스펙

**POST /v1/narrow/analyze**
```http
POST /v1/narrow/analyze
Content-Type: multipart/form-data
X-Api-Key: {api_key}
```

**Request:**
- `image`: 이미지 파일 (multipart)
- `mode`: 'cls_only' (단일) 또는 'detect_cls' (다중) - 기본값 'cls_only'
- `roi`: (선택) ROI 이미지
- `identification_data`: (선택) JSON 문자열

**Response (성공):**
```json
{
  "status": "success",
  "inference": {
    "mode": "cls_only",
    "results": [
      {
        "kcode": "K-030864",
        "item_seq": 200003456,
        "confidence": 0.95,
        "item_name": "모사드린정",
        "entp_name": "동아제약"
      }
    ],
    "narrow_mode": true,
    "candidates_count": 100,
    "inference_time_ms": 250,
    "model_version": "efficientnetv2-l-narrow"
  }
}
```

**Response (실패):**
```json
{
  "status": "error",
  "error": "INFERENCE_ERROR",
  "message": "이미지에서 약품을 인식할 수 없습니다."
}
```

**GET /v1/narrow/kcodes**
```http
GET /v1/narrow/kcodes
X-Api-Key: {api_key}
```

**Response:**
```json
{
  "status": "success",
  "total": 100,
  "kcodes": [
    {
      "kcode": "K-030864",
      "item_seq": 200003456,
      "item_name": "모사드린정",
      "entp_name": "동아제약",
      "chart": "원형",
      "class_name": "전문의약품",
      "form_code_name": "정제"
    }
  ]
}
```

#### 구현 세부사항
- 100개 제한 K-CODE로만 추론
- `allowed_kcodes` 파라미터 사용
- 기존 `/v1/analyze` 로직 재사용
- TTA 비활성화 (속도 우선)
- 응답에 `narrow_mode`, `candidates_count`, `inference_time_ms` 포함

---

### 2️⃣ **Flutter 앱 Narrow 기능 추가** (맥북)

**저장소**: `helious23/pillsnap_mobile`
**예상 시간**: 3-4일

#### 사전 준비

**1. Linux PC에서 확인할 정보**

Linux PC 담당자에게 요청:
- [ ] BFF 서버 로컬 IP 주소 (WiFi 동일 네트워크)
- [ ] **BFF API 키** (보안상 GitHub에 노출 금지)
- [ ] `/v1/narrow/analyze` 엔드포인트 구현 완료 확인
- [ ] `/v1/narrow/kcodes` 엔드포인트 구현 완료 확인
- [ ] 100개 K-CODE 목록 확정

**API 키 확인 방법 (Linux PC):**
```bash
# BFF 설정 파일에서 확인
cat /home/max16/pillsnap_bff/config/runtime.yaml | grep api_key

# 또는 환경 변수 확인
echo $BFF_API_KEY
```

**2. Flutter 프로젝트 구조**

현재 구조 (확인 완료):
```
lib/
├── core/
│   ├── config/
│   │   └── app_config.dart          # Supabase 설정
│   ├── network/
│   │   └── api_client.dart          # PillSnapAPIClient
│   ├── router/                       # go_router 설정
│   └── utils/                        # StructuredLogger 등
├── features/
│   ├── home/                         # 홈 화면 (토글 추가 위치)
│   ├── camera/                       # 카메라 기능
│   ├── drug/                         # 약품 정보
│   └── ...
└── theme.dart                        # AppTheme
```

**3. 환경 변수 설정**

기존 설정 확인 (`lib/core/network/api_client.dart`):
```dart
class PillSnapAPIClient {
  static const String _baseUrl = String.fromEnvironment(
    'API_URL',
    defaultValue: 'https://api.pillsnap.co.kr',
  );
  static const String _apiKey = String.fromEnvironment(
    'API_KEY',
    defaultValue: 'your-default-key-here',  // ⚠️ 프로덕션에서는 제거 필요
  );
}
```

**개발 시 실행 명령어:**
```bash
# 개발 서버 (Linux PC 로컬 IP)
flutter run --dart-define=API_URL=http://192.168.x.x:8000 \
            --dart-define=API_KEY=<Linux PC에서 확인한 실제 키>

# 프로덕션 서버
flutter run --dart-define=API_URL=https://api.pillsnap.co.kr \
            --dart-define=API_KEY=<프로덕션 API 키>
```

**⚠️ 보안 주의사항:**
```dart
// ❌ 잘못된 방법 - 코드에 직접 하드코딩
static const String _apiKey = 'bf3ef0b1655f48fcad98edf61259c6d4';

// ✅ 올바른 방법 - 환경 변수 사용
static const String _apiKey = String.fromEnvironment('API_KEY');

// 개발 중 임시 기본값은 괜찮지만, 프로덕션에서는 제거
static const String _apiKey = String.fromEnvironment(
  'API_KEY',
  defaultValue: '',  // 빈 문자열로 설정
);
```

#### 구현 단계

**Phase 1: API Client 수정 (0.5일)**

기존 파일: `lib/core/network/api_client.dart`

```dart
/// Narrow 모드 이미지 분석 API 추가
Future<Map<String, dynamic>> analyzeNarrowImage(
  File imageFile, {
  String mode = 'cls_only',
  File? roiFile,
  Map<String, dynamic>? identificationData,
}) async {
  try {
    // 기존 analyzeImage와 동일하지만 엔드포인트만 변경
    final uri = Uri.parse('$_baseUrl/v1/narrow/analyze');
    debugPrint('Narrow API Request URL: $uri');

    // 이미지 전처리 (기존 로직 재사용)
    File processedFile;
    if (mode == 'cls_only') {
      processedFile = await ImageProcessor.preprocessForClassification(imageFile);
    } else {
      processedFile = await ImageProcessor.preprocessForDetection(imageFile);
    }

    await ImageProcessor.validateImage(processedFile);

    final fileSize = await processedFile.length();
    debugPrint('[Narrow] Processed file size: ${(fileSize / 1024 / 1024).toStringAsFixed(2)} MB');

    final request = http.MultipartRequest('POST', uri);
    request.headers.addAll(_getHeaders());

    // 파일 추가
    final stream = http.ByteStream(processedFile.openRead());
    final multipartFile = http.MultipartFile(
      'image',
      stream,
      fileSize,
      filename: 'processed_image.jpg',
    );
    request.files.add(multipartFile);

    // ROI 파일 추가 (선택)
    if (roiFile != null && roiFile.existsSync()) {
      final roiFileSize = await roiFile.length();
      final roiStream = http.ByteStream(roiFile.openRead());
      final roiMultipart = http.MultipartFile(
        'roi',
        roiStream,
        roiFileSize,
        filename: 'roi_512.jpg',
      );
      request.files.add(roiMultipart);
    }

    // 필드 추가
    request.fields['mode'] = mode;

    if (identificationData != null) {
      request.fields['identification_data'] = json.encode(identificationData);
    }

    // 요청 전송
    final streamedResponse = await request.send();
    final response = await http.Response.fromStream(streamedResponse);

    debugPrint('[Narrow] API Response Status: ${response.statusCode}');

    if (response.statusCode == 200 || response.statusCode == 201) {
      final data = json.decode(response.body) as Map<String, dynamic>;
      debugPrint('[Narrow] Response contains narrow_mode: ${data['inference']?['narrow_mode']}');
      return data;
    } else {
      debugPrint('[Narrow] API Error: ${response.body}');
      try {
        final error = json.decode(response.body);
        throw Exception(error['message'] ?? 'Narrow 이미지 분석 실패');
      } catch (_) {
        throw Exception('Narrow 분석 실패 (Status: ${response.statusCode})');
      }
    }
  } catch (e) {
    debugPrint('[Narrow] Error: $e');
    rethrow;
  }
}

/// Narrow K-CODE 목록 조회
Future<List<Map<String, dynamic>>> getNarrowKcodes() async {
  try {
    final response = await http.get(
      Uri.parse('$_baseUrl/v1/narrow/kcodes'),
      headers: _getHeaders(),
    );

    debugPrint('[Narrow] K-CODE List Response: ${response.statusCode}');

    if (response.statusCode == 200) {
      final data = json.decode(response.body) as Map<String, dynamic>;
      final kcodes = data['kcodes'] as List;
      debugPrint('[Narrow] Loaded ${kcodes.length} K-CODEs');
      return kcodes.cast<Map<String, dynamic>>();
    } else {
      throw Exception('Narrow K-CODE 목록 조회 실패');
    }
  } catch (e) {
    debugPrint('[Narrow] K-CODE List Error: $e');
    rethrow;
  }
}
```

**Phase 2: Narrow Mode 상태 관리 (0.5일)**

새 파일: `lib/features/home/data/providers/narrow_mode_provider.dart`

```dart
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';

/// Narrow 모드 상태 관리
class NarrowModeNotifier extends StateNotifier<bool> {
  NarrowModeNotifier() : super(false) {
    _loadFromPrefs();
  }

  static const String _key = 'narrow_mode_enabled';

  Future<void> _loadFromPrefs() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      state = prefs.getBool(_key) ?? false;
    } catch (e) {
      debugPrint('[NarrowMode] Load error: $e');
    }
  }

  Future<void> toggle() async {
    try {
      final newState = !state;
      final prefs = await SharedPreferences.getInstance();
      await prefs.setBool(_key, newState);
      state = newState;
      debugPrint('[NarrowMode] Toggled to: $newState');
    } catch (e) {
      debugPrint('[NarrowMode] Toggle error: $e');
    }
  }
}

/// Narrow 모드 Provider
final narrowModeProvider = StateNotifierProvider<NarrowModeNotifier, bool>((ref) {
  return NarrowModeNotifier();
});
```

**Phase 3: Home 화면 UI 수정 (0.5일)**

기존 파일 수정: `lib/features/home/presentation/pages/home_page.dart`

```dart
// import 추가
import 'package:pillsnap/features/home/data/providers/narrow_mode_provider.dart';

// AppBar에 Narrow 토글 추가
class HomePage extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final isNarrowMode = ref.watch(narrowModeProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('PillSnap'),
        actions: [
          // Narrow 모드 토글
          Padding(
            padding: const EdgeInsets.only(right: 8),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Text(
                  'Narrow',
                  style: TextStyle(
                    fontSize: 12,
                    fontWeight: FontWeight.w500,
                    color: isNarrowMode
                      ? AppColors.primary
                      : AppColors.textSecondary,
                  ),
                ),
                const SizedBox(width: 4),
                Switch(
                  value: isNarrowMode,
                  onChanged: (value) {
                    ref.read(narrowModeProvider.notifier).toggle();
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(
                        content: Text(
                          value ? '100개 선정 약품 모드 활성화' : '전체 약품 모드 활성화',
                        ),
                        duration: const Duration(seconds: 2),
                      ),
                    );
                  },
                  activeColor: AppColors.primary,
                ),
              ],
            ),
          ),
        ],
      ),
      body: Column(
        children: [
          // Narrow 모드 안내 배너
          if (isNarrowMode)
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(12),
              color: AppColors.primary.withValues(alpha: 0.1),
              child: Row(
                children: [
                  Icon(Icons.flash_on, size: 20, color: AppColors.primary),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      '100개 선정 약품 빠른 검색 모드',
                      style: TextStyle(
                        color: AppColors.primary,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ),
                  TextButton(
                    onPressed: () => _showNarrowKcodesList(context, ref),
                    child: const Text('목록 보기'),
                  ),
                ],
              ),
            ),

          // 기존 홈 화면 내용
          Expanded(child: _buildHomeContent(context, ref)),
        ],
      ),
    );
  }
}
```

**Phase 4: Narrow K-CODE 목록 다이얼로그 (0.5일)**

새 파일: `lib/features/home/presentation/widgets/narrow_kcodes_list_sheet.dart`

```dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:pillsnap/core/network/api_client.dart';

/// Narrow K-CODE 목록 Provider
final narrowKcodesProvider = FutureProvider<List<Map<String, dynamic>>>((ref) async {
  final apiClient = PillSnapAPIClient();
  return await apiClient.getNarrowKcodes();
});

class NarrowKcodesListSheet extends ConsumerWidget {
  const NarrowKcodesListSheet({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final kcodesAsync = ref.watch(narrowKcodesProvider);

    return DraggableScrollableSheet(
      initialChildSize: 0.7,
      minChildSize: 0.5,
      maxChildSize: 0.95,
      builder: (context, scrollController) {
        return Container(
          decoration: const BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
          ),
          child: Column(
            children: [
              // 헤더
              Padding(
                padding: const EdgeInsets.all(16),
                child: Row(
                  children: [
                    Icon(Icons.list_alt, color: AppColors.primary),
                    const SizedBox(width: 8),
                    Text('Narrow 모드 약품 목록', style: AppTextStyles.titleLarge),
                    const Spacer(),
                    kcodesAsync.when(
                      data: (kcodes) => Chip(label: Text('${kcodes.length}개')),
                      loading: () => const SizedBox.shrink(),
                      error: (_, __) => const SizedBox.shrink(),
                    ),
                  ],
                ),
              ),

              const Divider(height: 1),

              // 목록
              Expanded(
                child: kcodesAsync.when(
                  data: (kcodes) => ListView.builder(
                    controller: scrollController,
                    itemCount: kcodes.length,
                    itemBuilder: (context, index) {
                      final kcode = kcodes[index];
                      return ListTile(
                        leading: CircleAvatar(child: Text('${index + 1}')),
                        title: Text(kcode['item_name'] ?? ''),
                        subtitle: Text('${kcode['kcode']} · ${kcode['entp_name']}'),
                      );
                    },
                  ),
                  loading: () => const Center(child: CircularProgressIndicator()),
                  error: (e, _) => Center(child: Text('오류: $e')),
                ),
              ),
            ],
          ),
        );
      },
    );
  }
}
```

**Phase 5: 카메라 촬영 시 Narrow 모드 적용 (1일)**

기존 카메라 컨트롤러 수정:

```dart
// import 추가
import 'package:pillsnap/features/home/data/providers/narrow_mode_provider.dart';

// 촬영 메서드에서 Narrow 모드 확인
Future<void> takePicture(WidgetRef ref) async {
  final isNarrowMode = ref.read(narrowModeProvider);
  debugPrint('[Camera] Narrow mode: $isNarrowMode');

  final imageFile = await cameraController.takePicture();
  final file = File(imageFile.path);

  final apiClient = PillSnapAPIClient();
  Map<String, dynamic> response;

  if (isNarrowMode) {
    response = await apiClient.analyzeNarrowImage(file, mode: _mode);
  } else {
    response = await apiClient.analyzeImage(file, mode: _mode);
  }

  // 결과 처리
  _handleAnalysisResponse(response);
}
```

**Phase 6: 결과 화면에 Narrow 배지 표시 (0.5일)**

기존 결과 화면 수정:

```dart
// AppBar에 Narrow 배지 추가
if (inference['narrow_mode'] == true)
  Chip(
    avatar: const Icon(Icons.flash_on, size: 16),
    label: const Text('Narrow'),
    backgroundColor: AppColors.primary.withValues(alpha: 0.15),
  ),

// 안내 배너 추가
if (inference['narrow_mode'] == true)
  Container(
    margin: const EdgeInsets.all(16),
    padding: const EdgeInsets.all(12),
    decoration: BoxDecoration(
      color: AppColors.primary.withValues(alpha: 0.1),
      borderRadius: BorderRadius.circular(12),
    ),
    child: Text(
      '100개 선정 약품 모드로 분석됨 · ${inference['inference_time_ms']}ms',
      style: TextStyle(color: AppColors.primary),
    ),
  ),
```

#### 전체 플로우

**일반 모드:**
```
홈 화면 (Narrow OFF)
  ↓
카메라 촬영
  ↓
PillSnapAPIClient.analyzeImage() → POST /v1/analyze
  ↓
결과 화면
```

**Narrow 모드:**
```
홈 화면 (Narrow ON)
  ↓ [선택] "목록 보기" 클릭
  ↓ 100개 약품 목록 표시
카메라 촬영
  ↓
PillSnapAPIClient.analyzeNarrowImage() → POST /v1/narrow/analyze
  ↓
결과 화면 (Narrow 배지, 추론 시간 표시)
```

#### 예상 이슈 및 해결

**1. BFF 서버 연결 실패**
```bash
# 증상: Connection refused

# Linux PC에서 IP 확인
ifconfig | grep inet

# 방화벽 확인
sudo ufw allow 8000

# Flutter 실행
flutter run --dart-define=API_URL=http://192.168.1.100:8000
```

**2. API 키 인증 실패**
```bash
# 증상: 401 Unauthorized

# Linux PC에서 API 키 확인
cat /home/max16/pillsnap_bff/config/runtime.yaml | grep api_key
```

**3. Narrow 엔드포인트 404**
```bash
# BFF 서버에서 확인
curl http://localhost:8000/v1/narrow/kcodes -H "X-Api-Key: {실제키}"
```

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
- [ ] `/v1/narrow/analyze` 엔드포인트 구현
- [ ] `/v1/narrow/kcodes` 엔드포인트 구현
- [ ] 100개 K-CODE 목록 확정
- [ ] 응답에 `narrow_mode`, `candidates_count`, `inference_time_ms` 포함
- [ ] TTA 비활성화 확인
- [ ] 테스트 작성
- [ ] Docker 재빌드

### Flutter 개발 (맥북)
- [ ] Phase 1: API Client에 `analyzeNarrowImage()`, `getNarrowKcodes()` 추가
- [ ] Phase 2: `narrow_mode_provider.dart` 생성
- [ ] Phase 3: Home 화면에 Narrow 토글 추가
- [ ] Phase 4: Narrow K-CODE 목록 다이얼로그 생성
- [ ] Phase 5: 카메라 컨트롤러 Narrow 모드 분기 처리
- [ ] Phase 6: 결과 화면 Narrow 배지 추가
- [ ] **보안**: API 키 하드코딩 제거 (`api_client.dart` 수정)
- [ ] iOS 실기기 테스트
- [ ] GitHub 커밋 & 푸시

### 촬영
- [ ] 장비 세팅
- [ ] 파일럿 테스트 (1약품 × 240장)
- [ ] 본 촬영 (100약품 × 240장)

---

## 🔗 관련 문서
- [20251024_capture_protocol.md](./20251024_capture_protocol.md) - 스튜디오 촬영 프로토콜
- [20251024_storage_structure.md](./20251024_storage_structure.md) - Supabase Storage 구조
- [pillsnap_mobile CLAUDE.md](https://github.com/helious23/pillsnap_mobile/blob/main/CLAUDE.md) - Flutter 아키텍처 가이드
- [pillsnap_mobile README.md](https://github.com/helious23/pillsnap_mobile/blob/main/README.md) - 프로젝트 개요

---

**최종 수정일**: 2025-10-27
**작성자**: Claude Code
**상태**: BFF 개발 대기 중
