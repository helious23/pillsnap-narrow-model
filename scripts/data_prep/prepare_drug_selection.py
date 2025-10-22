#!/usr/bin/env python
"""
약품 선정을 위한 데이터 추출 스크립트
MVP 5개 규칙에 따라 K-CODE와 EDI 매핑 후 Excel 작업용 데이터 생성

Created: 2025-10-22
Purpose: K-CODE와 EDI 매핑하여 Excel 작업용 데이터 준비
Usage: python prepare_drug_selection.py
"""

import json
import pandas as pd
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

def normalize_kcode(kcode):
    """K-CODE를 K-000000 형식으로 정규화"""
    if pd.isna(kcode) or kcode == '':
        return None

    kcode = str(kcode).strip().upper()

    # K- 제거하고 숫자만 추출
    if kcode.startswith('K-'):
        kcode = kcode[2:]
    elif kcode.startswith('K'):
        kcode = kcode[1:]

    # 숫자 부분을 6자리로 패딩
    try:
        num_part = int(kcode)
        return f'K-{num_part:06d}'
    except ValueError:
        print(f"Warning: Invalid K-CODE format: {kcode}")
        return None

def main():
    print("🔄 약품 선정 데이터 준비 시작...")

    # 1. single_list.xlsx에서 K-CODE 추출 (2개 시트)
    print("\n📊 single_list.xlsx 읽기...")
    single_list_path = Path('/home/max16/drug_list/single_list.xlsx')

    # 두 시트를 모두 읽기
    sheet1_df = pd.read_excel(single_list_path, sheet_name=0)
    sheet2_df = pd.read_excel(single_list_path, sheet_name=1)

    print(f"  Sheet 1: {len(sheet1_df)} rows, columns: {list(sheet1_df.columns)}")
    print(f"  Sheet 2: {len(sheet2_df)} rows, columns: {list(sheet2_df.columns)}")

    # K-CODE 컬럼 찾기 및 추출
    all_kcodes = set()

    for df, sheet_name in [(sheet1_df, 'Sheet1'), (sheet2_df, 'Sheet2')]:
        # K-CODE가 포함된 컬럼 찾기
        kcode_cols = [col for col in df.columns if 'K' in str(col).upper() or 'CODE' in str(col).upper()]

        if kcode_cols:
            print(f"  {sheet_name}에서 K-CODE 컬럼 발견: {kcode_cols[0]}")
            for kcode in df[kcode_cols[0]].dropna():
                normalized = normalize_kcode(kcode)
                if normalized:
                    all_kcodes.add(normalized)
        else:
            # 첫 번째 컬럼이 K-CODE일 가능성 확인
            first_col = df.iloc[:, 0].dropna()
            if any('K' in str(val).upper() for val in first_col.head()):
                print(f"  {sheet_name}의 첫 번째 컬럼을 K-CODE로 사용")
                for kcode in first_col:
                    normalized = normalize_kcode(kcode)
                    if normalized:
                        all_kcodes.add(normalized)

    print(f"\n✅ 총 {len(all_kcodes)}개의 고유 K-CODE 추출")

    # 2. K-CODE → EDI 매핑 로드 (우선순위: kcode_label_map.json → drugs_master.csv)
    print("\n📚 매핑 파일 로드...")

    # kcode_label_map.json 로드
    kcode_to_edi = {}
    kcode_label_map_path = Path('/home/max16/pillsnap_inference/mapping/kcode_label_map.json')

    if kcode_label_map_path.exists():
        with open(kcode_label_map_path, 'r', encoding='utf-8') as f:
            label_map = json.load(f)

        # label_map에서 K-CODE와 EDI 정보 추출
        for kcode, info in label_map.items():
            normalized = normalize_kcode(kcode)
            if normalized and isinstance(info, dict):
                # EDI 코드가 있는 경우 (edi_codes 필드는 리스트)
                if 'edi_codes' in info and info['edi_codes']:
                    # 첫 번째 EDI 코드 사용 (실제 사용량 데이터와 매칭 시 사용)
                    edi_code = str(info['edi_codes'][0]).strip() if info['edi_codes'] else ''
                    if edi_code:
                        kcode_to_edi[normalized] = {
                            'edi': edi_code,
                            'source': 'kcode_label_map',
                            'drug_name': (info.get('name_kr') or '').strip(),
                            'manufacturer': (info.get('company') or '').strip()
                        }
        print(f"  kcode_label_map.json: {len(kcode_to_edi)}개 매핑")

    # drugs_master.csv 로드 (보조 매핑) - 문자형으로 읽어 선행 0 보존
    drugs_master_path = Path('/home/max16/pillsnap_bff/migrations/drugs_master.csv')

    if drugs_master_path.exists():
        drugs_master = pd.read_csv(drugs_master_path, dtype=str, keep_default_na=False)

        # drugs_master에서 K-CODE → EDI 매핑 추가 (기존 매핑이 없는 경우만)
        for _, row in drugs_master.iterrows():
            kcode = normalize_kcode(row.get('kcode') or row.get('K-CODE') or row.get('k_code'))
            edi = row.get('edi_code') or row.get('EDI') or row.get('edi')

            if kcode and edi and kcode not in kcode_to_edi:
                kcode_to_edi[kcode] = {
                    'edi': str(edi).strip(),
                    'source': 'drugs_master',
                    'drug_name': (row.get('item_name') or '').strip(),
                    'manufacturer': (row.get('entp_name') or '').strip()
                }

        print(f"  drugs_master.csv 추가: 총 {len(kcode_to_edi)}개 매핑")

    # 3. actual_list.xlsx에서 EDI별 사용량 계산
    print("\n💊 actual_list.xlsx에서 EDI 사용량 분석...")
    actual_list_path = Path('/home/max16/drug_list/actual_list.xlsx')

    # Excel 파일을 읽되, 데이터는 5행부터 시작 (헤더행 제외, 0-indexed로는 4)
    # 헤더를 건너뛰고 읽기
    actual_df = pd.read_excel(actual_list_path, header=None, skiprows=4, dtype=str)
    print(f"  총 {len(actual_df)} 행 로드")

    # 컬럼 설정: 0=약품명, 1=EDI코드, 6=수량
    if len(actual_df.columns) >= 7:
        actual_df = actual_df[[0, 1, 6]]  # 필요한 컬럼만 선택
        actual_df.columns = ['drug_name', 'edi', 'quantity']
    else:
        print("  경고: 예상과 다른 컬럼 구조")
        actual_df.columns = ['drug_name', 'edi'] if len(actual_df.columns) >= 2 else ['drug_name']

    print(f"  컬럼: {list(actual_df.columns)}")

    # 수량을 숫자로 변환
    if 'quantity' in actual_df.columns:
        actual_df['quantity'] = pd.to_numeric(actual_df['quantity'], errors='coerce').fillna(0)

    # EDI별 사용량 집계 (EDI 코드가 있는 행만)
    edi_usage = {}
    if 'quantity' in actual_df.columns:
        # 수량 컬럼이 있으면 합계 계산
        edi_grouped = actual_df[actual_df['edi'].notna()].groupby('edi')['quantity'].sum().sort_values(ascending=False)
    else:
        # 수량 컬럼이 없으면 빈도로 계산
        edi_grouped = actual_df['edi'].dropna().value_counts()

    for edi, count in edi_grouped.items():
        edi_usage[str(edi).strip()] = int(count)

    print(f"  총 {len(edi_usage)}개 EDI의 사용량 계산 완료")

    # 4. 통합 데이터프레임 생성
    print("\n🔄 통합 데이터 생성...")

    rows = []
    for kcode in all_kcodes:
        row = {
            'K-CODE': kcode,
            'EDI': '',
            'Drug_Name': '',
            'Manufacturer': '',
            'Usage_Count': 0,
            'Mapping_Source': 'none',
            'In_Dataset': 'Y'
        }

        # 매핑 정보가 있는 경우
        if kcode in kcode_to_edi:
            mapping = kcode_to_edi[kcode]
            row['EDI'] = mapping['edi']
            row['Drug_Name'] = mapping['drug_name']
            row['Manufacturer'] = mapping['manufacturer']
            row['Mapping_Source'] = mapping['source']

            # EDI 사용량 추가
            if mapping['edi'] in edi_usage:
                row['Usage_Count'] = edi_usage[mapping['edi']]

        rows.append(row)

    # DataFrame 생성 및 정렬
    result_df = pd.DataFrame(rows)
    result_df = result_df.sort_values('Usage_Count', ascending=False)

    # EDI 중복 제거 (동일 EDI가 여러 K-CODE에 매핑된 경우 사용량 높은 것만 유지)
    print("\n🔄 EDI 중복 제거 중...")
    before_dedup = len(result_df)

    # 빈 EDI는 유지, 실제 EDI만 중복 제거
    df_with_edi = result_df[result_df['EDI'] != '']
    df_without_edi = result_df[result_df['EDI'] == '']

    df_dedup = df_with_edi.drop_duplicates(subset=['EDI'], keep='first')
    result_df = pd.concat([df_dedup, df_without_edi]).sort_values('Usage_Count', ascending=False)

    after_dedup = len(result_df)
    print(f"  중복 제거: {before_dedup}개 → {after_dedup}개 (제거된 중복: {before_dedup - after_dedup}개)")

    # 5. 통계 출력
    print("\n📊 매핑 통계:")
    print(f"  총 K-CODE 수: {len(result_df)}")
    print(f"  EDI 매핑된 K-CODE: {len(result_df[result_df['EDI'] != ''])}")
    print(f"  사용량 있는 K-CODE: {len(result_df[result_df['Usage_Count'] > 0])}")
    print(f"  매핑 소스별 분포:")
    print(result_df['Mapping_Source'].value_counts())

    # 상위 10개 미리보기
    print("\n🏆 사용량 상위 10개 약품:")
    top10 = result_df.head(10)[['K-CODE', 'EDI', 'Drug_Name', 'Usage_Count']]
    for idx, row in top10.iterrows():
        print(f"  {row['K-CODE']}: {row['Drug_Name'][:20]} (EDI: {row['EDI']}, 사용량: {row['Usage_Count']:,})")

    # 6. Excel 파일로 저장
    output_path = Path('/home/max16/pillsnap-narrow-model/artifacts/drug_selection_workspace.xlsx')
    output_path.parent.mkdir(exist_ok=True)

    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        # 메인 시트: 전체 데이터
        result_df.to_excel(writer, sheet_name='All_Drugs', index=False)

        # 상위 200개 시트 (데이터만, 헤더 행 제거)
        top200 = result_df.head(200).copy()
        top200['Selected_for_100'] = ''  # 수동 선택용 컬럼
        top200['Shootable'] = ''  # 촬영 가능 여부
        top200['Notes'] = ''  # 메모
        top200.to_excel(writer, sheet_name='Top_200', index=False)

        # 통계 시트 (선정 기준 포함)
        unique_edi = result_df.loc[result_df['EDI'].ne(''), 'EDI'].nunique()
        total_usage = int(result_df['Usage_Count'].sum())

        stats_data = {
            'Metric': [
                '=== 선정 기준 ===',
                'Top 200 선정: Usage_Count 내림차순',
                'EDI 중복 제거: 동일 EDI 중 최고 사용량만 유지',
                '',
                '=== 데이터 통계 ===',
                'Total K-CODEs',
                'K-CODEs with EDI',
                'K-CODEs with Usage',
                'K-CODEs without EDI',
                'Unique EDIs',
                'Total Usage Count',
                'Removed Duplicates'
            ],
            'Value': [
                '',
                '',
                '',
                '',
                '',
                len(result_df),
                len(result_df[result_df['EDI'] != '']),
                len(result_df[result_df['Usage_Count'] > 0]),
                len(result_df[result_df['EDI'] == '']),
                unique_edi,
                total_usage,
                before_dedup - after_dedup
            ]
        }
        stats_df = pd.DataFrame(stats_data)
        stats_df.to_excel(writer, sheet_name='Statistics', index=False)

    print(f"\n✅ Excel 파일 생성 완료: {output_path}")
    print("\n📝 다음 단계:")
    print("  1. Excel 파일 열기: drug_selection_workspace.xlsx")
    print("  2. Top_200 시트에서 촬영 가능한 약품 100개 선택")
    print("  3. Selected_for_100 컬럼에 'Y' 표시")
    print("  4. Shootable 컬럼에 촬영 가능 여부 표시")
    print("  5. 최종 100개 리스트를 top_100_drugs.csv로 저장")

if __name__ == "__main__":
    main()