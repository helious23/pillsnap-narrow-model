-- Supabase 데이터베이스 스키마 설정 (최종판 v2)
-- 실제 약품 사진 메타데이터 관리
-- 촬영 환경: LED 스튜디오 박스 + 360도 회전판 + Galaxy S21 수직 촬영

-- 0. 필수 확장 기능 활성화
CREATE EXTENSION IF NOT EXISTS "pgcrypto";  -- UUID 생성용

-- 1. 약품 마스터 테이블 (100개 선정 약품)
CREATE TABLE IF NOT EXISTS drugs_master (
    id SERIAL PRIMARY KEY,
    kcode VARCHAR(20) UNIQUE NOT NULL,
    edi_code VARCHAR(20),
    drug_name VARCHAR(200) NOT NULL,
    manufacturer VARCHAR(200),
    usage_count INTEGER,
    shootable VARCHAR(1) CHECK (shootable IN ('Y', 'M', 'N')),

    -- 촬영 진행 상태
    photos_taken INTEGER DEFAULT 0,
    photos_required INTEGER DEFAULT 2,  -- front/back 2장
    is_complete BOOLEAN DEFAULT false,

    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. 실제 사진 메타데이터 (수직 촬영 특화)
CREATE TABLE IF NOT EXISTS real_photos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    kcode VARCHAR(20),
    photo_url TEXT NOT NULL,

    -- 촬영 정보 (front/back만)
    capture_date TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    capture_device VARCHAR(100) DEFAULT 'Galaxy S21',
    capture_angle VARCHAR(10) NOT NULL,

    -- 스튜디오 박스 환경 정보
    studio_settings JSONB DEFAULT '{}',  -- LED 밝기, 색온도 등
    background_color VARCHAR(20),  -- 12가지 배경색 중 선택
    turntable_angle INTEGER CHECK (turntable_angle BETWEEN 0 AND 360),

    -- 품질 정보
    quality_grade VARCHAR(1),
    blur_score FLOAT CHECK (blur_score >= 0 AND blur_score <= 1),
    exposure_score FLOAT CHECK (exposure_score >= 0 AND exposure_score <= 1),
    centering_score FLOAT CHECK (centering_score >= 0 AND centering_score <= 1),

    -- 촬영 조건 (LED 스튜디오 박스 - 96개 LED, CRI 97+)
    lighting_mode VARCHAR(20) DEFAULT 'white',  -- 'white', 'warm', 'mixed'
    led_brightness INTEGER,
    color_temperature INTEGER CHECK (color_temperature IN (3200, 5500, 6000)),

    -- 검증 상태
    is_verified BOOLEAN DEFAULT false,
    verified_by VARCHAR(100),
    verified_at TIMESTAMPTZ,
    rejection_reason TEXT,

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- FK with CASCADE
    CONSTRAINT real_photos_kcode_fkey
    FOREIGN KEY (kcode) REFERENCES drugs_master(kcode)
    ON UPDATE CASCADE ON DELETE SET NULL,

    -- 제약조건 추가
    CONSTRAINT chk_capture_angle_fb CHECK (capture_angle IN ('front','back')),
    CONSTRAINT chk_quality_grade_abc CHECK (quality_grade IN ('A','B','C') OR quality_grade IS NULL),
    CONSTRAINT chk_led_brightness_1_10 CHECK (led_brightness BETWEEN 1 AND 10)
);

-- 3. 촬영 세션 관리
CREATE TABLE IF NOT EXISTS capture_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_date DATE NOT NULL,
    photographer VARCHAR(100),

    -- 촬영 장비 정보
    device_info VARCHAR(200) DEFAULT 'Galaxy S21',
    studio_box_model VARCHAR(100) DEFAULT 'LED Light Box 200mm',

    -- 세션 통계
    total_photos INTEGER DEFAULT 0,
    grade_a_count INTEGER DEFAULT 0,
    grade_b_count INTEGER DEFAULT 0,
    grade_c_count INTEGER DEFAULT 0,

    -- 약품 커버리지
    drugs_captured INTEGER DEFAULT 0,
    target_drugs INTEGER DEFAULT 100,
    drugs_completed INTEGER DEFAULT 0,  -- front/back 모두 촬영 완료

    -- 환경 설정
    default_background VARCHAR(20) DEFAULT 'white',
    default_led_brightness INTEGER,

    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),

    -- 제약조건
    CONSTRAINT chk_default_led_brightness_1_10 CHECK (default_led_brightness BETWEEN 1 AND 10)
);

-- 4. 배경색 마스터 (12가지 - 스튜디오 박스 제공)
CREATE TABLE IF NOT EXISTS background_colors (
    id SERIAL PRIMARY KEY,
    color_name VARCHAR(20) UNIQUE NOT NULL,
    hex_code VARCHAR(7),
    paper_side VARCHAR(20),  -- 'side_a' or 'side_b'
    is_recommended BOOLEAN DEFAULT false,  -- 알약 촬영에 적합한 색상
    usage_count INTEGER DEFAULT 0
);

-- 배경색 초기 데이터 삽입 (6장 양면 = 12색)
INSERT INTO background_colors (color_name, hex_code, paper_side, is_recommended) VALUES
    ('black', '#000000', 'paper1_side_a', true),
    ('white', '#FFFFFF', 'paper1_side_b', true),
    ('gray', '#808080', 'paper2_side_a', false),
    ('gold', '#FFD700', 'paper2_side_b', false),
    ('yellow', '#FFFF00', 'paper3_side_a', false),
    ('orange', '#FFA500', 'paper3_side_b', false),
    ('red', '#FF0000', 'paper4_side_a', false),
    ('pink', '#FFC0CB', 'paper4_side_b', false),
    ('blue', '#0000FF', 'paper5_side_a', false),
    ('purple', '#800080', 'paper5_side_b', false),
    ('green', '#008000', 'paper6_side_a', false),
    ('brown', '#A52A2A', 'paper6_side_b', false)
ON CONFLICT (color_name) DO NOTHING;

-- 5. 품질 통계 뷰 (수정됨)
CREATE OR REPLACE VIEW photo_quality_stats AS
SELECT
    dm.kcode,
    dm.drug_name,
    COUNT(rp.id) as total_photos,
    COUNT(CASE WHEN rp.capture_angle = 'front' THEN 1 END) as front_photos,
    COUNT(CASE WHEN rp.capture_angle = 'back' THEN 1 END) as back_photos,
    COUNT(CASE WHEN rp.quality_grade = 'A' THEN 1 END) as grade_a,
    COUNT(CASE WHEN rp.quality_grade = 'B' THEN 1 END) as grade_b,
    COUNT(CASE WHEN rp.quality_grade = 'C' THEN 1 END) as grade_c,
    AVG(rp.blur_score) as avg_blur,
    AVG(rp.exposure_score) as avg_exposure,
    AVG(rp.centering_score) as avg_centering,
    CASE
        WHEN COUNT(CASE WHEN rp.capture_angle = 'front' AND rp.quality_grade = 'A' THEN 1 END) > 0
         AND COUNT(CASE WHEN rp.capture_angle = 'back' AND rp.quality_grade = 'A' THEN 1 END) > 0
        THEN true
        ELSE false
    END as is_complete
FROM drugs_master dm
LEFT JOIN real_photos rp ON dm.kcode = rp.kcode
GROUP BY dm.kcode, dm.drug_name;

-- 6. updated_at 자동 갱신 트리거
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
  NEW.updated_at := NOW();
  RETURN NEW;
END$$;

DROP TRIGGER IF EXISTS trg_real_photos_updated ON real_photos;
CREATE TRIGGER trg_real_photos_updated
BEFORE UPDATE ON real_photos
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- 7. 인덱스 생성 (성능 최적화)
CREATE INDEX IF NOT EXISTS idx_drugs_kcode ON drugs_master(kcode);
CREATE INDEX IF NOT EXISTS idx_photos_kcode ON real_photos(kcode);
CREATE INDEX IF NOT EXISTS idx_photos_date ON real_photos(capture_date);
CREATE INDEX IF NOT EXISTS idx_photos_quality ON real_photos(quality_grade);
CREATE INDEX IF NOT EXISTS idx_photos_angle ON real_photos(capture_angle);
CREATE INDEX IF NOT EXISTS idx_photos_kcode_angle ON real_photos(kcode, capture_angle);  -- 합성 인덱스

-- 8. RLS (Row Level Security) 활성화
ALTER TABLE drugs_master ENABLE ROW LEVEL SECURITY;
ALTER TABLE real_photos ENABLE ROW LEVEL SECURITY;
ALTER TABLE capture_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE background_colors ENABLE ROW LEVEL SECURITY;

-- 9. RLS 정책 - drugs_master
CREATE POLICY "drugs_read_all" ON drugs_master
FOR SELECT TO authenticated USING (true);

CREATE POLICY "drugs_write_all" ON drugs_master
FOR INSERT TO authenticated WITH CHECK (true);

CREATE POLICY "drugs_update_all" ON drugs_master
FOR UPDATE TO authenticated USING (true) WITH CHECK (true);

-- 10. RLS 정책 - real_photos
CREATE POLICY "photos_read_all" ON real_photos
FOR SELECT TO authenticated USING (true);

CREATE POLICY "photos_write_all" ON real_photos
FOR INSERT TO authenticated WITH CHECK (true);

CREATE POLICY "photos_update_all" ON real_photos
FOR UPDATE TO authenticated USING (true) WITH CHECK (true);

-- 11. RLS 정책 - capture_sessions
CREATE POLICY "sessions_read_all" ON capture_sessions
FOR SELECT TO authenticated USING (true);

CREATE POLICY "sessions_write_all" ON capture_sessions
FOR INSERT TO authenticated WITH CHECK (true);

-- 12. RLS 정책 - background_colors (읽기 전용)
CREATE POLICY "colors_read_all" ON background_colors
FOR SELECT TO authenticated USING (true);

-- 13. Storage 버킷 생성 (SQL)
INSERT INTO storage.buckets (id, name, public, avif_autodetection, file_size_limit, allowed_mime_types)
VALUES (
    'pill-photos',
    'pill-photos',
    false,  -- 비공개
    false,
    10485760,  -- 10MB
    ARRAY['image/jpeg', 'image/png', 'image/webp']
)
ON CONFLICT (id) DO NOTHING;

-- 14. Storage RLS 정책
CREATE POLICY "storage_read_auth" ON storage.objects
FOR SELECT TO authenticated
USING (bucket_id = 'pill-photos');

CREATE POLICY "storage_write_auth" ON storage.objects
FOR INSERT TO authenticated
WITH CHECK (bucket_id = 'pill-photos');

CREATE POLICY "storage_update_auth" ON storage.objects
FOR UPDATE TO authenticated
USING (bucket_id = 'pill-photos')
WITH CHECK (bucket_id = 'pill-photos');

CREATE POLICY "storage_delete_auth" ON storage.objects
FOR DELETE TO authenticated
USING (bucket_id = 'pill-photos');

-- 15. 100개 약품 데이터 로드용 함수 (타입 안전 버전)
CREATE OR REPLACE FUNCTION load_selected_drugs(drugs_json JSONB)
RETURNS VOID AS $$
DECLARE
    drug_record JSONB;
BEGIN
    FOR drug_record IN SELECT * FROM jsonb_array_elements(drugs_json)
    LOOP
        INSERT INTO drugs_master (
            kcode,
            edi_code,
            drug_name,
            manufacturer,
            usage_count,
            shootable
        ) VALUES (
            drug_record->>'kcode',
            drug_record->>'edi_code',
            drug_record->>'drug_name',
            drug_record->>'manufacturer',
            NULLIF(drug_record->>'usage_count','')::INTEGER,  -- 안전 캐스팅
            NULLIF(drug_record->>'shootable','')  -- Y/M/N 문자열 그대로
        )
        ON CONFLICT (kcode) DO UPDATE SET
            edi_code = EXCLUDED.edi_code,
            drug_name = EXCLUDED.drug_name,
            manufacturer = EXCLUDED.manufacturer,
            usage_count = EXCLUDED.usage_count;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- 16. 촬영 진행 상황 업데이트 함수
CREATE OR REPLACE FUNCTION update_drug_photo_count()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE drugs_master
        SET photos_taken = (
            SELECT COUNT(DISTINCT capture_angle)
            FROM real_photos
            WHERE kcode = NEW.kcode AND quality_grade = 'A'
        ),
        is_complete = (
            SELECT COUNT(DISTINCT capture_angle) = 2
            FROM real_photos
            WHERE kcode = NEW.kcode AND quality_grade = 'A'
        )
        WHERE kcode = NEW.kcode;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_update_drug_photo_count
AFTER INSERT ON real_photos
FOR EACH ROW EXECUTE FUNCTION update_drug_photo_count();

-- 17. 촬영 진행률 대시보드 뷰
CREATE OR REPLACE VIEW capture_progress AS
SELECT
    COUNT(*) as total_drugs,
    COUNT(CASE WHEN photos_taken > 0 THEN 1 END) as started_drugs,
    COUNT(CASE WHEN is_complete THEN 1 END) as completed_drugs,
    ROUND(100.0 * COUNT(CASE WHEN is_complete THEN 1 END) / COUNT(*), 2) as completion_rate,
    100 - COUNT(CASE WHEN is_complete THEN 1 END) as remaining_drugs
FROM drugs_master
WHERE is_active = true;

-- 사용 예시:
-- 100개 약품 데이터 로드
-- SELECT load_selected_drugs('[{"kcode":"K-030864","edi_code":"698001940","drug_name":"모사드린정","manufacturer":"(주)제뉴파마","usage_count":120848,"shootable":"Y"}]'::jsonb);