# job-radar 데이터 갱신 방법

- 앱 주소: https://claude.ai/artifact/7BgqVVRH6AbAXK7dsHK8Vg (본인만 열람·수정 가능)
- 데이터 위치: 앱 안의 데이터베이스 (컬렉션 5개)
- 갱신 방법 (지금): Claude에게 "공고 채워줘", "이 링크 공고 추가해줘"라고 요청 → Claude가 검색하고 정리해서 바로 넣음
- 갱신 방법 (나중, A 단계): n8n → 구글 시트. 열 이름은 아래 표와 같게 맞춤
- 시트로 옮기기: 공고 탭 오른쪽 위 **CSV** 버튼 → 구글 시트에서 가져오기

---

## 컬렉션 구조

### jobs (공고 1개 = 문서 1개)
| 필드 | 뜻 | 예시 |
|---|---|---|
| company_id / company | 회사 키 / 회사 이름 | epid / 에피드게임즈 |
| game | 대표 게임 | 트릭컬 리바이브 |
| title | 공고 제목 | [트릭컬 리바이브] 글로벌 사업PM 추가 모집 |
| job_type | 공고 종류 (색이 바뀜) | bizpm, publish, service, design, local, mkt, ip |
| country | 국가 | KR, JP, CN, US |
| tags | 태그 목록 | 서브컬처, 정규직 |
| career_req / min_years_months | 경력 조건 글 / 최소 경력(개월) | 무관 / 0 |
| deadline / deadline_date | 마감 글 / 마감일 | 채용시 마감 / null |
| posted, added, checked | 등록일, 앱에 넣은 날, 확인한 날 | 2026-10-27 |
| url / apply_url | 원문 / 회사 지원 페이지 | |
| summary | 카드에 보이는 2줄 요약 | |
| duties, quals, prefs, conditions | 담당 업무, 지원 자격, 우대 사항, 근무 조건 (외국어 공고는 한글 번역) | |
| reqs | 적합도 계산용 조건 목록 (아래) | |
| needs | 지원에 필요한 스탯 (title, detail) | |

**reqs 한 줄**: `kind`(must 필수 / plus 우대), `text`, `status`(ok / part / no / ask), `reason`.
내 스펙과 연결되는 조건은 `rule`을 붙이면 앱이 바로 다시 계산함:
- 언어: `{"type":"lang","any":["ja","zh"],"min":"원어민"}`
- 해외 출장: `{"type":"travel"}` / 해외 근무: `{"type":"overseas"}`

### companies (회사 1개 = 문서 1개)
name, address, size, titles, work, benefits_posting, benefits_other, sources, checked

### tests (CBT·베타테스트 1개 = 문서 1개)
game, company, kind(CBT/베타), platform, start, end(모집 마감일), test_period, region, url, note, tone(색: job_type 값 중 하나)

### profile/me (내 스펙)
lang(en, ko, ja, zh: 못 함 / 학습 중 / 기초 / 일상 회화 / 비즈니스 / 원어민), learn, travel, overseas, place, career, notes
앱의 "내 스펙" 탭에서 바꾸면 여기에 저장됨

### status (공고별 지원 상태)
문서 이름 = 공고 id. status(관심 / 지원함 / 결과 대기 / 종료), updated

---

## 적합도 계산
필수 조건 60점 + 우대 조건 30점 + 경력 조건 10점. 충족은 만점, 일부는 절반, 부족과 확인 필요는 0점.
"확인 필요"가 모두 충족될 때의 최대 점수를 같이 표시.

### news (홈 화면 "주요 소식" 1건 = 문서 1개)
| 필드 | 뜻 |
|---|---|
| kind | job(신규 공고), deadline(마감 임박), industry(업계 소식), hiring(채용 동향), test(테스트), update |
| date | 소식 날짜 |
| title / body | 제목 / 2~3줄 요약 |
| job_id 또는 url | 앱 안 공고로 연결하거나, 외부 원문(https) 또는 앱 화면(#tests 등)으로 연결 |
| source | 출처 |
| pin | true면 맨 앞에 고정 |

마감 14일 이내 공고는 앱이 자동으로 "마감 임박" 소식을 만듦 (따로 저장하지 않음).

### watch (추적 회사 1곳 = 문서 1개, 문서 id = companies·jobs의 company_id와 같음)
| 필드 | 뜻 |
|---|---|
| name, category(game·vtuber·ip·goods·webtoon·platform), category_label, country | 기본 정보 |
| careers_url / candidate_urls | 확인된 채용 페이지 / 확인 못 한 후보 주소 |
| method | api(채용 시스템 데이터), page(채용 페이지 확인), page+gamejob, gamejob(게임잡으로 추적), manual(자동 접속 불가) |
| ip_focus | IP 사업 관련 회사 (우선 표시) |
| open_count | 마지막 확인 때 채용 페이지의 관련 공고 수 (모르면 null) |
| new_count / closed_count | 마지막 확인에서 새로 생긴 / 내려간 공고 수 |
| last_checked, history | 마지막 확인일, [{date, open, new, closed}] 기록 (최근 30개) |

### jobs 추적 필드
- `closed: true` + `deadline: "공고 내려감 (확인 날짜)"`: 공고가 내려감. 삭제하지 않음
- `added`: 처음 발견한 날 (3일 이내면 앱에 NEW 표시)
