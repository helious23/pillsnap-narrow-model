#!/usr/bin/env python
"""
K-CODE와 EDI 매핑 테이블 구축 스크립트
Created: 2024-10-22
Purpose: 현재 보유한 4,523개 K-CODE와 약국 사용량 데이터의 EDI 코드 연결
"""

import json
import pandas as pd
from pathlib import Path
import sys
from typing import Dict, Any
from datetime import datetime

class KCodeEDIMapper:
    def __init__(self):
        self.base_path = Path('/home/max16/pillsnap-narrow-model')
        self.artifacts_path = self.base_path / 'artifacts' / 'datasets'
        self.artifacts_path.mkdir(parents=True, exist_ok=True)

        # 소스 파일 경로
        self.kcode_label_path = Path('/home/max16/pillsnap_inference/mapping/kcode_label_map.json')
        self.drugs_master_path = Path('/home/max16/pillsnap_bff/migrations/drugs_master.csv')

        # 출력 파일 경로
        self.output_mapping_path = self.artifacts_path / 'kcode_edi_mapping.json'
        self.output_stats_path = self.artifacts_path / 'mapping_statistics.json'

    def load_kcode_labels(self) -> Dict[str, str]:
        """K-CODE 라벨 맵 로드"""
        print("📂 K-CODE 라벨 맵 로드 중...")

        if not self.kcode_label_path.exists():
            print(f"❌ K-CODE 라벨 파일을 찾을 수 없습니다: {self.kcode_label_path}")
            sys.exit(1)

        with open(self.kcode_label_path, 'r', encoding='utf-8') as f:
            kcode_map = json.load(f)

        print(f"✅ {len(kcode_map)} 개의 K-CODE 로드 완료")
        return kcode_map

    def load_drugs_master(self) -> pd.DataFrame:
        """drugs_master.csv 로드"""
        print("📂 drugs_master.csv 로드 중...")

        if not self.drugs_master_path.exists():
            print(f"❌ drugs_master 파일을 찾을 수 없습니다: {self.drugs_master_path}")
            sys.exit(1)

        # CSV 파일 로드 (인코딩 처리)
        try:
            drugs_df = pd.read_csv(self.drugs_master_path, encoding='utf-8')
        except UnicodeDecodeError:
            try:
                drugs_df = pd.read_csv(self.drugs_master_path, encoding='cp949')
            except:
                drugs_df = pd.read_csv(self.drugs_master_path, encoding='euc-kr')

        print(f"✅ {len(drugs_df)} 개의 약품 레코드 로드 완료")

        # 컬럼명 정규화
        drugs_df.columns = [col.strip().upper().replace(' ', '_') for col in drugs_df.columns]

        # 필수 컬럼 확인
        required_cols = ['K-CODE', 'EDI_CODE', 'DRUG_NAME']
        available_cols = drugs_df.columns.tolist()

        print(f"📋 사용 가능한 컬럼: {', '.join(available_cols[:10])}...")

        # K-CODE 또는 KCODE 컬럼 찾기
        kcode_col = None
        for col in available_cols:
            if 'CODE' in col and ('K' in col or 'K-' in col):
                kcode_col = col
                break

        if kcode_col and kcode_col != 'K-CODE':
            drugs_df['K-CODE'] = drugs_df[kcode_col]
            print(f"📝 K-CODE 컬럼 매핑: {kcode_col} → K-CODE")

        # EDI 컬럼 찾기
        edi_col = None
        for col in available_cols:
            if 'EDI' in col:
                edi_col = col
                break

        if edi_col and edi_col != 'EDI_CODE':
            drugs_df['EDI_CODE'] = drugs_df[edi_col]
            print(f"📝 EDI_CODE 컬럼 매핑: {edi_col} → EDI_CODE")

        return drugs_df

    def build_mapping(self) -> Dict[str, Any]:
        """K-CODE와 EDI 매핑 테이블 생성"""
        print("\n🔄 K-CODE와 EDI 매핑 시작...")

        # 데이터 로드
        kcode_labels = self.load_kcode_labels()
        drugs_df = self.load_drugs_master()

        # 매핑 결과
        mapping = {}
        stats = {
            'total_kcodes': len(kcode_labels),
            'mapped_count': 0,
            'unmapped_count': 0,
            'unmapped_kcodes': [],
            'duplicate_edi': []
        }

        # K-CODE별로 매핑
        for kcode, drug_name in kcode_labels.items():
            # drugs_master에서 K-CODE 찾기
            matches = drugs_df[drugs_df['K-CODE'] == kcode] if 'K-CODE' in drugs_df.columns else pd.DataFrame()

            if matches.empty:
                # K-CODE 형식 변형 시도 (K-CODE vs KCODE)
                kcode_alt = kcode.replace('-', '') if '-' in kcode else f"K-{kcode[1:]}"
                matches = drugs_df[drugs_df['K-CODE'] == kcode_alt] if 'K-CODE' in drugs_df.columns else pd.DataFrame()

            if not matches.empty:
                # 매핑 성공
                row = matches.iloc[0]

                mapping[kcode] = {
                    'kcode': kcode,
                    'drug_name': drug_name,
                    'edi_code': row.get('EDI_CODE', ''),
                    'manufacturer': row.get('MANUFACTURER', row.get('제조사', '')),
                    'form': row.get('FORM', row.get('제형', '')),
                    'strength': row.get('STRENGTH', row.get('함량', ''))
                }

                stats['mapped_count'] += 1

                # 중복 EDI 확인
                if len(matches) > 1:
                    stats['duplicate_edi'].append({
                        'kcode': kcode,
                        'count': len(matches)
                    })
            else:
                # 매핑 실패
                stats['unmapped_count'] += 1
                stats['unmapped_kcodes'].append(kcode)

        # 매핑률 계산
        stats['mapping_rate'] = (stats['mapped_count'] / stats['total_kcodes']) * 100

        print(f"\n📊 매핑 결과:")
        print(f"  ✅ 매핑 성공: {stats['mapped_count']} / {stats['total_kcodes']}")
        print(f"  ❌ 매핑 실패: {stats['unmapped_count']} / {stats['total_kcodes']}")
        print(f"  📈 매핑률: {stats['mapping_rate']:.2f}%")

        if stats['duplicate_edi']:
            print(f"  ⚠️ 중복 EDI: {len(stats['duplicate_edi'])} 건")

        return mapping, stats

    def save_results(self, mapping: Dict, stats: Dict) -> None:
        """결과 저장"""
        print("\n💾 결과 저장 중...")

        # 매핑 데이터 저장
        with open(self.output_mapping_path, 'w', encoding='utf-8') as f:
            json.dump(mapping, f, ensure_ascii=False, indent=2)

        print(f"✅ 매핑 데이터 저장: {self.output_mapping_path}")

        # 통계 저장
        stats['created_at'] = datetime.now().isoformat()
        with open(self.output_stats_path, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)

        print(f"✅ 통계 저장: {self.output_stats_path}")

        # 매핑되지 않은 K-CODE 리스트 저장 (디버깅용)
        if stats['unmapped_kcodes']:
            unmapped_path = self.artifacts_path / 'unmapped_kcodes.txt'
            with open(unmapped_path, 'w', encoding='utf-8') as f:
                for kcode in sorted(stats['unmapped_kcodes']):
                    f.write(f"{kcode}\n")
            print(f"📝 매핑 실패 K-CODE 리스트: {unmapped_path}")

    def create_summary_csv(self, mapping: Dict) -> None:
        """요약 CSV 파일 생성"""
        print("\n📊 요약 CSV 생성 중...")

        # DataFrame 생성
        data = []
        for kcode, info in mapping.items():
            data.append({
                'K-CODE': kcode,
                'EDI_CODE': info.get('edi_code', ''),
                '약품명': info.get('drug_name', ''),
                '제조사': info.get('manufacturer', ''),
                '제형': info.get('form', ''),
                '함량': info.get('strength', '')
            })

        df = pd.DataFrame(data)

        # CSV 저장
        csv_path = self.artifacts_path / 'kcode_edi_mapping_summary.csv'
        df.to_csv(csv_path, index=False, encoding='utf-8-sig')

        print(f"✅ 요약 CSV 저장: {csv_path}")
        print(f"   총 {len(df)} 개 약품")

        # EDI가 있는 항목만 필터링
        df_with_edi = df[df['EDI_CODE'].notna() & (df['EDI_CODE'] != '')]
        print(f"   EDI 코드 보유: {len(df_with_edi)} 개")

        if len(df_with_edi) > 0:
            csv_with_edi_path = self.artifacts_path / 'kcode_with_edi.csv'
            df_with_edi.to_csv(csv_with_edi_path, index=False, encoding='utf-8-sig')
            print(f"✅ EDI 보유 약품 CSV: {csv_with_edi_path}")

    def run(self) -> None:
        """전체 매핑 프로세스 실행"""
        print("="*60)
        print("K-CODE와 EDI 매핑 테이블 구축")
        print("="*60)

        try:
            # 매핑 실행
            mapping, stats = self.build_mapping()

            # 결과 저장
            self.save_results(mapping, stats)

            # 요약 CSV 생성
            self.create_summary_csv(mapping)

            print("\n✨ 매핑 작업 완료!")
            print(f"📁 결과 파일 위치: {self.artifacts_path}")

            # 다음 단계 안내
            if stats['mapping_rate'] < 80:
                print("\n⚠️ 매핑률이 80% 미만입니다.")
                print("   추가 데이터 소스나 수동 매핑이 필요할 수 있습니다.")

            print("\n📋 다음 단계:")
            print("1. 약국 사용량 CSV 파일 준비")
            print("2. EDI 코드별 사용 빈도 계산")
            print("3. 상위 200개 약품 선정")

        except Exception as e:
            print(f"\n❌ 오류 발생: {str(e)}")
            import traceback
            traceback.print_exc()
            sys.exit(1)


if __name__ == "__main__":
    mapper = KCodeEDIMapper()
    mapper.run()