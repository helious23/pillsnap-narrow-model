#!/usr/bin/env python
"""
100개 선정 약품을 Supabase에 로드하는 스크립트
"""

import json
from pathlib import Path

# 경로 설정 (실행 위치 상관없이 동작)
BASE = Path(__file__).resolve().parent
json_path = BASE.parent / 'artifacts' / 'top_100_metadata_final.json'
output_path = BASE / 'supabase_load_drugs.sql'
checklist_path = BASE / 'capture_checklist.csv'

def sql_str(s):
    """SQL 문자열 처리 - NULL 또는 escape된 문자열 반환"""
    if s is None or s == '':
        return 'NULL'
    return "'" + str(s).replace("'", "''") + "'"

def generate_supabase_load_script():
    """top_100_metadata_final.json을 읽어서 Supabase 로드용 SQL 생성"""

    # JSON 파일 읽기
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"📊 총 {data['total_drugs']}개 약품 로드 준비")
    print(f"📈 통계:")
    print(f"  - 총 사용량: {data['statistics']['total_usage']:,}")
    print(f"  - 평균 사용량: {data['statistics']['average_usage']:,}")
    print(f"  - 촬영 용이(Y): {data['statistics']['shootable_Y']}개")
    print(f"  - 중간 난이도(M): {data['statistics']['shootable_M']}개")

    # 1. 직접 INSERT 방식 (개발용)
    print("\n" + "="*80)
    print("-- 방법 1: 직접 INSERT (Supabase SQL Editor에서 실행)")
    print("="*80)
    print("\n-- 약품 마스터 데이터 삽입")
    print("INSERT INTO drugs_master (kcode, edi_code, drug_name, manufacturer, usage_count, shootable)")
    print("VALUES")

    values = []
    for drug in data['drugs']:
        # 안전한 값 추출
        kcode = drug.get('kcode', '')
        edi_code = drug.get('edi_code')  # None 가능
        drug_name = drug.get('drug_name') or ''  # None 방지
        manufacturer = drug.get('manufacturer') or ''  # None 방지
        usage_count = drug.get('usage_count')  # int 또는 None
        shootable = drug.get('shootable') or 'Y'

        # NULL/문자열 안전 처리
        kcode_sql = sql_str(kcode)
        edi_sql = sql_str(edi_code)
        name_sql = sql_str(drug_name)
        manu_sql = sql_str(manufacturer)
        usage_sql = 'NULL' if usage_count in (None, '') else str(int(usage_count))
        shootable_sql = sql_str(shootable)

        value = f"  ({kcode_sql}, {edi_sql}, {name_sql}, {manu_sql}, {usage_sql}, {shootable_sql})"
        values.append(value)

    # 처음 5개만 출력 (안전하게)
    print(",\n".join(values[:min(5, len(values))]))
    if len(values) > 5:
        print(f"  -- ... 나머지 {len(values)-5}개 약품")
    print("ON CONFLICT (kcode) DO UPDATE SET")
    print("  edi_code = EXCLUDED.edi_code,")
    print("  drug_name = EXCLUDED.drug_name,")
    print("  manufacturer = EXCLUDED.manufacturer,")
    print("  usage_count = EXCLUDED.usage_count;")

    # 2. 함수 호출 방식 (권장)
    print("\n" + "="*80)
    print("-- 방법 2: load_selected_drugs 함수 사용 (권장)")
    print("="*80)

    # JSON 배열 생성 (None 값 처리)
    drugs_json = []
    for drug in data['drugs']:
        drugs_json.append({
            'kcode': drug.get('kcode', ''),
            'edi_code': drug.get('edi_code', ''),
            'drug_name': drug.get('drug_name', ''),
            'manufacturer': drug.get('manufacturer', ''),
            'usage_count': drug.get('usage_count', 0),
            'shootable': drug.get('shootable', 'Y')
        })

    print("\n-- Supabase SQL Editor에서 실행:")
    print("SELECT load_selected_drugs('")
    print(json.dumps(drugs_json[:min(3, len(drugs_json))], ensure_ascii=False, indent=2))  # 처음 3개만 예시
    if len(drugs_json) > 3:
        print("-- ... 나머지 약품 데이터")
    print("'::jsonb);")

    # 3. 전체 SQL 파일 생성
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("-- 100개 선정 약품 Supabase 로드 스크립트\n")
        f.write(f"-- 생성일: 2025-10-23\n")
        f.write(f"-- 총 약품 수: {data['total_drugs']}개\n\n")

        # 직접 INSERT 방식
        f.write("-- 직접 INSERT 방식\n")
        f.write("INSERT INTO drugs_master (kcode, edi_code, drug_name, manufacturer, usage_count, shootable)\n")
        f.write("VALUES\n")
        f.write(",\n".join(values))
        f.write("\nON CONFLICT (kcode) DO UPDATE SET\n")
        f.write("  edi_code = EXCLUDED.edi_code,\n")
        f.write("  drug_name = EXCLUDED.drug_name,\n")
        f.write("  manufacturer = EXCLUDED.manufacturer,\n")
        f.write("  usage_count = EXCLUDED.usage_count;\n\n")

        # 함수 호출 방식
        f.write("-- 또는 함수 사용 방식 (권장)\n")
        f.write("/*\n")
        f.write("SELECT load_selected_drugs('")
        f.write(json.dumps(drugs_json, ensure_ascii=False))
        f.write("'::jsonb);\n")
        f.write("*/\n")

    print(f"\n✅ SQL 파일 생성 완료: {output_path}")

    # 4. 촬영 진행 체크리스트 생성
    with open(checklist_path, 'w', encoding='utf-8-sig') as f:
        f.write("K-CODE,약품명,촬영난이도,Front,Back,완료\n")
        for drug in data['drugs'][:min(20, len(data['drugs']))]:  # 상위 20개만 (안전하게)
            drug_name = (drug.get('drug_name', '') or '').replace(',', '/')  # CSV 안전
            shootable = drug.get('shootable', 'Y') or 'Y'
            f.write(f"{drug.get('kcode', '')},{drug_name},{shootable},[],[],[]\n")

    print(f"📋 촬영 체크리스트 생성: {checklist_path}")

    # 5. Supabase 연동 정보
    print("\n" + "="*80)
    print("📌 Supabase 설정 안내")
    print("="*80)
    print("""
1. Supabase 프로젝트 생성
   - https://supabase.com 접속
   - New Project 생성
   - Region: Singapore (ap-southeast-1) 권장

2. SQL Editor에서 실행 순서:
   1) setup_supabase_final.sql (스키마 생성)
   2) supabase_load_drugs.sql (약품 데이터 로드)

3. API 정보 확인:
   - Settings > API
   - Project URL 복사
   - anon public key 복사
   - service_role key 복사 (서버용)

4. Storage 설정:
   - Storage > New Bucket
   - Name: pill-photos (자동 생성됨)
   - Public: False

5. Flutter 앱 환경변수:
   SUPABASE_URL=your-project-url
   SUPABASE_ANON_KEY=your-anon-key
    """)

    # 6. 통계 출력
    print("\n📊 약품 데이터 요약:")
    print(f"  - 총 약품 수: {len(drugs_json)}개")
    edi_count = sum(1 for d in drugs_json if d['edi_code'])
    print(f"  - EDI 코드 있음: {edi_count}개")
    print(f"  - EDI 코드 없음: {len(drugs_json) - edi_count}개")

if __name__ == "__main__":
    generate_supabase_load_script()