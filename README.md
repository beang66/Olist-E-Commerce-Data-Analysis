# Olist 이커머스 데이터 분석 및 대시보드

> **README 구조 개편:** 2026-11-16 · 기존 설명·명령·이미지·원저작자 표기를 보존하고 제품·의사결정·검증 기준으로 재배열했습니다. **이번 작업에서 앱과 테스트를 재실행하지 않았습니다.** 기재된 성과는 원본 README의 기록입니다.

**읽는 순서:** 0~2 제품 설명 → 3~4 설계 판단 → 5~8 실행·검증·권리 → 9 다음 단계.

## 0. 30초 요약·실행 상태

브라질 온라인 마켓플레이스 **Olist** 의 실제 주문 데이터(약 10만 건)를 pandas · plotly 로 탐색적 데이터 분석(EDA)하고,
분석 결과를 **Streamlit 대시보드**로 만들어 배포한 프로젝트입니다.

- **대시보드 바로 가기**: https://olist-ecommerce-sinaboro.streamlit.app
  (Streamlit Community Cloud 무료 배포 — 한동안 접속이 없으면 잠들어 있다가, 접속 후 버튼을 누르면 1분 안에 다시 켜집니다)

- **학습 교안 (PDF, 53쪽)**: [docs/Olist_이커머스_분석과_서비스배포_학습교안.pdf](docs/Olist_이커머스_분석과_서비스배포_학습교안.pdf)
  — 노트북 3개 보충 설명, 주요 인사이트 10가지, GitHub · Streamlit Cloud 배포 따라 하기(실제 화면), 내 도메인으로 확장하는 방법

## 1. 사용자 문제·프로젝트 목표

**데이터 분석 목적(원문 근거):** 공개된 Olist 주문 데이터를 pandas·plotly로 탐색하고, 확인된 인사이트를 Streamlit 대시보드에서 재사용할 수 있도록 시각화한다.

**대상 자료:** Kaggle 공개 이커머스 데이터 약 10만 주문. 실제 고객 인터뷰나 분석 결과의 운영 의사결정 반영 여부는 별도 확인해야 한다.

## 2. 핵심 사용 흐름·기능

**분석·서비스 흐름(원문 근거):** 공개 Olist CSV → Jupyter/Colab 분석 노트북 → 대시보드용 가공 데이터 → Streamlit 화면 탐색. 실행 명령과 데이터 산출 방식은 아래 5번과 3번 구조를 참고한다.

> **추가 확인:** 특정 사용자 과업의 성공률·대시보드 이용 결과는 미측정.

## 3. 시스템 구조·데이터·기술

### 구성

```
├── app.py                  ← Streamlit 대시보드 (배포되는 앱)
├── requirements.txt        ← 배포 서버가 설치할 패키지
├── .streamlit/config.toml  ← 대시보드 테마
├── data/
│   ├── olist_….csv.gz (8개) · product_category_name_translation.csv.gz
│   │                       ← Kaggle 원본 9개를 압축한 것 (126MB → 44MB) — 노트북 실습용
│   ├── orders.csv.gz       ← 대시보드용 가공 데이터 (필요한 열만 추려 압축, 약 2.4MB)
│   └── items.csv.gz
├── docs/                   ← 학습 교안 PDF
└── notebooks/              ← 분석 노트북 (실행 결과 포함)
    ├── 01_데이터이해_고객_매출.ipynb
    ├── 02_시간패턴_카테고리_배송리뷰.ipynb
    └── 03_대시보드_만들기와_GitHub_배포.ipynb
```

| 노트북 | 내용 |
|---|---|
| 01 | 9개 테이블의 연결 구조(키), 분석 대상 정의, 고객 수 · 재구매율, 지역, 결제 수단, 객단가, 월별 매출 |
| 02 | 일 · 요일 · 시간 패턴, 공정한 기간 비교, 카테고리 판매량 vs 매출, 파레토, 배송 기간 · 지연율, 배송 지연과 리뷰 점수, 지역별 배송 |
| 03 | 배포용 데이터 가공 → `app.py` 작성 → 자동 테스트 → GitHub push → Streamlit Community Cloud 배포 |

## 4. 핵심 의사결정·대안

> **확인 필요:** 채택안/대안/선택 이유와 근거가 있는 설계 변경을 기록.

## 5. 설치·실행·배포

### 실행 방법

#### 대시보드
```bash
pip install -r requirements.txt
streamlit run app.py
```

#### 분석 노트북
1. 저장소를 받습니다 (`git clone` 또는 Code → Download ZIP). 원본 데이터는 `data/` 에 압축본(`.csv.gz`)으로 이미 들어 있어 따로 내려받을 필요가 없습니다.
   (노트북은 `PATH = "../data/"` 에서 `.csv.gz` 를 그대로 읽습니다. 엑셀로 보고 싶으면 반디집 · 7-Zip 으로 압축을 푸세요. 압축을 푼 `.csv` 는 `.gitignore` 의 `data/*.csv` 규칙으로 저장소에 올라가지 않습니다.)
2. `pip install pandas plotly jupyter` 후 `notebooks/` 의 노트북을 01 → 02 → 03 순서로 실행합니다.
   (03 노트북은 `notebooks/olist_dashboard/` 에 대시보드 파일을 만듭니다. 저장소 최상위의 `app.py` · `data/` 가 그 결과물입니다.)

## 6. 검증·측정 결과

### 주요 인사이트

| 영역 | 발견 |
|---|---|
| 고객 | 실제 고객 96,096명 중 **재구매율 약 3%**, 고객의 42% 가 상파울루(SP) |
| 매출 | 같은 1~8월 기준 1년 새 매출 **+143%**, 성장은 객단가가 아니라 **주문 수** 증가 덕분 |
| 시간 | 2017-11-24 블랙프라이데이 하루 1,100건+, 평일 낮 시간대에 주문 집중 |
| 카테고리 | 판매 수량 1위 bed_bath_table, 매출 1위 health_beauty, 상위 10개 카테고리가 매출의 62% |
| 배송 · 리뷰 | 배송 지연 시 평균 리뷰 **4.28 → 2.55점**, 성수기 지연율 14~21%, 북부 지역 배송 약 25일 |

## 7. 담당 역할·협업

> **확인 필요:** 실제 개인·팀·원저자·AI 도구의 기여와 증거를 구분.

## 8. 한계·보안·라이선스

### 데이터 출처 · 라이선스

Olist, *Brazilian E-Commerce Public Dataset by Olist* (Kaggle), **CC BY-NC-SA 4.0** (비영리 · 출처 표시 · 동일 조건 공유).
`data/` 의 `olist_….csv.gz` · `product_category_name_translation.csv.gz` 는 원본 CSV 를 내용 변경 없이 압축만 한 것이고, `orders.csv.gz` · `items.csv.gz` 는 대시보드에 필요한 열만 가공 · 압축한 것입니다. 교육용 프로젝트입니다.

## 9. 다음 단계·참고 문서

---

> 공통 작성 가이드: [Vault README 표준](https://github.com/beang66/Vault/blob/main/wiki/concepts/GitHub%20README%20%EA%B0%80%EC%9D%B4%EB%93%9C%20%E2%80%94%20%EC%A0%9C%ED%92%88%C2%B7%EC%9D%98%EC%82%AC%EA%B2%B0%EC%A0%95%C2%B7%EA%B2%80%EC%A6%9D.md). '확인 필요'는 구현 완료가 아닙니다.
