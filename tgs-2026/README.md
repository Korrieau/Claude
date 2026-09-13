# TGS 2026 회장 지도 (토요일 9/19 일반 관람)

마쿠하리 멧세 홀 1–11 전체를 벡터 SVG로 다시 그린 인터랙티브 지도입니다.
백화점 안내도처럼 부스를 눌러 회사·참여 게임·위치를 확인합니다.

## 파일

| 경로 | 내용 |
|---|---|
| `tgs-map.html` | 지도 본체. 단일 HTML, 외부 의존성 없음(구글 폰트만) |
| `design.md` | 디자인 규칙. 스타일 변경 시 여기부터 고칠 것 |
| `design-schema-reference.md` | 디자인 토큰 스키마 원본 |
| `data/map.json` | 부스 좌표·이름·분류·국기·게임 (370개) |
| `data/games.json` | 부스코드 → 참여 게임 목록. **여기를 채우면 됨** |
| `data/ko.json` | 영문 회사명 → 한글 표기 |
| `data/cflag.json` | 국가 → 국기·한글 국가명 |
| `data/catrules.json` | 부스 분류 키워드 |
| `data/tgs-2026-official-map.pdf` | 공식 회장도 원본 |
| `scripts/rects.py` | PDF 내용스트림에서 채워진 사각형 추출 |
| `scripts/build_all.py` | 부스코드 ↔ 사각형 매칭 → `map.json` 생성 |

## 현재 상태

- 부스 370개 / 이름 있음 352개 / 참여 게임 있음 28개사
- 남은 작업: **참여 게임 채우기**. 대형 부스는 대부분 채웠고, 중소·인디 부스가 남음
- 인디(9–11홀 개별 부스)는 우선순위 낮음

## 게임 정보 채우는 법

1. `data/games.json`에 `"부스코드": ["게임1", "게임2"]` 형태로 추가
2. 아래 스크립트로 `map.json`에 반영

```python
import json
d=json.load(open('data/map.json')); g=json.load(open('data/games.json'))
for b in d['booths']:
    for c in b['codes']:
        if c in g: b['g']=g[c]; break
json.dump(d, open('data/map.json','w'), ensure_ascii=False)
```

3. `tgs-map.html` 203번째 줄 `const MAP={...}` 를 새 `map.json` 내용으로 교체

### 참고 소스

원격 환경에서는 프록시 정책상 아래 사이트가 전부 403이라 웹검색 요약만 썼습니다.
로컬에서는 직접 열립니다.

- https://gamewith.jp/tgs/574121 — 출전 게임 전체 목록 (시연 정보 포함)
- https://gamewith.jp/tgs/573893 — 출전 기업·부스 목록
- https://dengekionline.com/article/202609/86887 — 부스별 배포물·노벨티
- https://akihabara-bc.jp/tgs-exhibitor-guide/ — 출전사·시연 일람
- https://tgs.cesa.or.jp/2026/ — 공식

## 표기 규칙

`design.md` 4절 참조. 요약하면 한글 통용 표기 우선, 영문 브랜드는 영문 유지,
국가관은 「○○관」.
