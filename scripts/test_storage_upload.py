#!/usr/bin/env python3
"""
Supabase Storage 업로드 테스트 스크립트
- 테스트 이미지 생성
- Storage 업로드
- DB 메타데이터 저장
"""

import os
import sys
from datetime import datetime
from pathlib import Path

# Supabase 클라이언트
try:
    from supabase import create_client, Client
except ImportError:
    print("❌ supabase 패키지가 설치되지 않았습니다.")
    print("설치: pip install supabase")
    sys.exit(1)

# PIL for test image
try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("❌ Pillow 패키지가 설치되지 않았습니다.")
    print("설치: pip install Pillow")
    sys.exit(1)


# Supabase 설정
SUPABASE_URL = "https://dcpuiwszzyoojgikszaa.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRjcHVpd3N6enlvb2pnaWtzemFhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTY5Njg4NzYsImV4cCI6MjA3MjU0NDg3Nn0.opSs4jdj16dIM8_YFnyj86o2JWCl0xNXjFmCmxWgB4o"


def create_test_image(filepath: str) -> None:
    """테스트 이미지 생성"""
    print(f"📸 테스트 이미지 생성 중: {filepath}")

    # 200x200 흰색 배경
    img = Image.new('RGB', (200, 200), color='white')
    draw = ImageDraw.Draw(img)

    # 테두리
    draw.rectangle([10, 10, 190, 190], outline='black', width=2)

    # 텍스트
    draw.text((50, 80), 'TEST', fill='black')
    draw.text((30, 110), 'K-030864', fill='blue')

    # 저장
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    img.save(filepath)
    print(f"✅ 이미지 생성 완료: {filepath}")


def upload_to_storage(supabase: Client, local_path: str, storage_path: str) -> dict:
    """Storage에 파일 업로드"""
    print(f"\n📤 Storage 업로드 시작...")
    print(f"   로컬: {local_path}")
    print(f"   원격: pill-photos/{storage_path}")

    try:
        with open(local_path, 'rb') as f:
            response = supabase.storage.from_('pill-photos').upload(
                storage_path,
                f,
                {
                    'content-type': 'image/jpeg',
                    'cache-control': '3600',
                    'upsert': 'false'
                }
            )

        print(f"✅ Storage 업로드 성공!")
        return response

    except Exception as e:
        print(f"❌ Storage 업로드 실패: {e}")
        raise


def save_metadata(supabase: Client, kcode: str, storage_path: str) -> None:
    """DB에 메타데이터 저장"""
    print(f"\n💾 메타데이터 저장 중...")

    try:
        data = {
            'kcode': kcode,
            'photo_url': storage_path,
            'capture_angle': 'front',
            'turntable_angle': 0,
            'background_color': 'skin_palm',
            'led_brightness': 3,
            'quality_grade': 'A',
            'blur_score': 0.95,
            'exposure_score': 0.88,
            'centering_score': 0.92,
            'capture_date': datetime.now().isoformat()
        }

        response = supabase.table('capture_real_photos').insert(data).execute()

        print(f"✅ 메타데이터 저장 성공!")
        print(f"   레코드 ID: {response.data[0]['id']}")

    except Exception as e:
        print(f"❌ 메타데이터 저장 실패: {e}")
        raise


def verify_upload(supabase: Client, kcode: str) -> None:
    """업로드 확인"""
    print(f"\n🔍 업로드 검증 중...")

    try:
        # DB 확인
        response = supabase.table('capture_real_photos').select('*').eq('kcode', kcode).execute()

        if response.data:
            print(f"✅ DB 레코드 확인: {len(response.data)}개")
            for record in response.data:
                print(f"   - {record['photo_url']} (등급: {record['quality_grade']})")
        else:
            print(f"⚠️  DB에서 레코드를 찾을 수 없습니다.")

        # Storage 공개 URL 생성
        storage_path = f"CS_1_single/{kcode}/K-030864_0_3_front_0_90_000_200.jpg"
        public_url = supabase.storage.from_('pill-photos').get_public_url(storage_path)
        print(f"\n📎 공개 URL (비공개 버킷이므로 인증 필요):")
        print(f"   {public_url}")

    except Exception as e:
        print(f"❌ 검증 실패: {e}")


def main():
    print("=" * 60)
    print("🧪 Supabase Storage 업로드 테스트")
    print("=" * 60)

    # 테스트 파일 경로
    kcode = "K-030864"
    filename = "K-030864_0_3_front_0_90_000_200.jpg"
    local_path = f"/tmp/pill_test/{filename}"
    storage_path = f"CS_1_single/{kcode}/{filename}"

    # 1. 테스트 이미지 생성
    create_test_image(local_path)

    # 2. Supabase 클라이언트 초기화
    print(f"\n🔗 Supabase 연결 중...")
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
    print(f"✅ Supabase 연결 성공!")

    try:
        # 3. Storage 업로드
        upload_to_storage(supabase, local_path, storage_path)

        # 4. 메타데이터 저장
        save_metadata(supabase, kcode, storage_path)

        # 5. 업로드 확인
        verify_upload(supabase, kcode)

        print("\n" + "=" * 60)
        print("✅ 모든 테스트 성공!")
        print("=" * 60)

    except Exception as e:
        print("\n" + "=" * 60)
        print(f"❌ 테스트 실패: {e}")
        print("=" * 60)
        sys.exit(1)


if __name__ == "__main__":
    main()
