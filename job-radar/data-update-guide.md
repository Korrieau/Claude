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

| lite / raw / title_original | 자동 수집 공고 표시 / 원문 전체(번역 전) / 원래 제목. lite 공고는 duties가 비어 있고 앱이 원문을 펼쳐 보여줌 | |

**reqs 한 줄**: `kind`(must 필수 / plus 우대), `text`, `status`(ok / part / no / ask), `reason`.
내 스펙과 연결되는 조건은 `rule`을 붙이면 앱이 바로 다시 계산함:
- 언어: `{"type":"lang","any":["ja","zh"],"min":"원어민"}`
- 해외 출장: `{"type":"travel"}` / 해외 근무: `{"type":"overseas"}`
- 그 외 `status:"ask"` 조건은 앱에서 "있음 / 조금 있음 / 없음" 버튼으로 답함 → `profile.answers["q:조건 텍스트"]`에 저장, 같은 텍스트 조건 전체에 반영
- 홈 "답할 질문"에 답이 없는 조건이 공고 수 많은 순으로 뜸

### companies (회사 1개 = 문서 1개)
name, address, size, titles, work, benefits_posting, benefits_other, sources, checked

### tests (CBT·베타테스트 1개 = 문서 1개)
game, company, kind(CBT/베타), platform, start, end(모집 마감일), test_period, region, url, note, tone(색: job_type 값 중 하나)

### profile/me (내 스펙)
lang(en, ko, ja, zh: 못 함 / 학습 중 / 기초 / 일상 회화 / 비즈니스 / 원어민), learn, travel, overseas, place, career, notes, answers
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
| method | api(채용 시스템 데이터), page(채용 페이지 확인), page+gamejob, gamejob(게임잡으로 추적), wanted(원티드로 추적), manual(자동 접속 불가) |
| logo / minor | 로고 이미지(240x120 PNG data URI) / 중소 회사 표시 |
| ip_focus | IP 사업 관련 회사 (우선 표시) |
| open_count | 마지막 확인 때 채용 페이지의 관련 공고 수 (모르면 null) |
| new_count / closed_count | 마지막 확인에서 새로 생긴 / 내려간 공고 수 |
| last_checked, history | 마지막 확인일, [{date, open, new, closed}] 기록 (최근 30개) |

### jobs 추적 필드
- `closed: true` + `deadline: "공고 내려감 (확인 날짜)"`: 공고가 내려감. 삭제하지 않음
- `added`: 처음 발견한 날 (3일 이내면 앱에 NEW 표시)

---

## 묶음(pack) 컬렉션
- `jobpacks/pNNN` = `{items:{<job id>: <jobs 문서>}, updated}` (문서 1개당 170KB 이하). `watchpacks/wNNN`도 같은 형식.
- 앱은 jobs + jobpacks, watch + watchpacks를 합쳐서 보여줌. 같은 id가 단독 문서에도 있으면 단독 문서가 우선 → 공고 1건을 고칠 때는 `jobs/<id>`에 전체 문서를 쓰면 됨 (pack은 그대로 둬도 됨).
- 대량 추가는 새 pack 문서로 (쓰기 횟수 절약).
- lite 공고 중 지원 자격 목록이 없고 필수 조건도 없으면 앱이 점수를 70점으로 제한함.

## 수집 경로 (자동 추적용)
| 경로 | 방법 |
|---|---|
| miHoYo | jobs.mihoyo.com을 브라우저로 연 뒤 페이지 안에서 `ats.openout.mihoyo.com/ats-portal/v1/job/list`·`/job/info` POST |
| HoYoverse | `api.ashbyhq.com/posting-api/job-board/hoyoverse` |
| Crunchyroll·NC America·크래프톤 | `boards-api.greenhouse.io/v1/boards/{crunchyroll,ncamerica,krafton}/jobs?content=true` |
| 텐센트 | `careers.tencent.com/tencentcareer/api/post/Query?keyword=...` / `ByPostId` (키워드: 二次元, 发行, 海外运营, IP, 周边 등) |
| 게임잡 (전체) | 브라우저로 게임잡 목록 페이지를 연 뒤 페이지 안에서 `POST /Recruit/_GI_Job_List/` body `page=N&condition%5Bmenucode%5D=&condition%5Btabcode%5D=1&direct=0&order=1&pagesize=100&tabcode=1` (N=1.. 빈 페이지까지, 전체 약 1,300건). 상세 meta description(경력·고용형태·마감), 로고 `//file.gamejob.co.kr/net/Corp/CoImage/LogoView?FN=` |
| 사람인 (국내 중소 회사) | `https://www.saramin.co.kr/zf_user/search/recruit?searchword=KW&recruitPageCount=100` curl 가능. `.item_recruit` 안 `.job_tit a`(rec_idx), `.corp_name a`, `.job_condition span`, `.job_date .date`, `.job_sector` |
| Green (일본 중소 회사) | Playwright로 `https://www.green-japan.com/search?keyword=KW&page=N`, 공고 링크 `/company/ID/job/JID`, 상세 페이지 본문 "仕事内容" 구간 (지원 자격은 로그인 필요) |
| 해외 중견 Greenhouse | riotgames, epicgames, scopely, 2k, roblox, twitch, neteasegames, hasbro, vizmedia, bungie / Lever: neowiz |
| 잡코리아 | `https://www.jobkorea.co.kr/Search/?stext=KW&tabType=recruit&Page_No=N` curl 가능. 카드 `[data-sentry-component=CardJob]`, 본문 `/Recruit/GI_Read_Comt_Ifrm?Gno=ID`, 로고 `imgs.jobkorea.co.kr` (Referer 필요) |
| GreetingHR 회사 페이지 | Playwright로 사이트를 열고 응답·`__NEXT_DATA__` 안의 `openingId`·`title`·`dueDate` 수집. 상세 `https://{사이트}/ko/o/{openingId}` 본문 텍스트. 사이트: careers.hybecorp.com, recruit.kakaogames.com, supercent / 111percent / antstudio / kstd-lezhin / epidgames `.career.greetinghr.com` |
| 스마일게이트 | careers.smilegate.com/apply/announce를 연 뒤 페이지 안에서 `POST /api/apply/announce/guest` (pageIndex, pageSize 50). 상세 `/apply/announce/view?seq=ID` |
| 쿠로게임즈 · 릴리스 (Feishu) | `https://kurogame.jobs.feishu.cn/index/position/list?current=N&limit=100`을 페이지마다 열고 `/api/v1/search/job/posts` 응답 수집 (요청 서명 때문에 직접 호출 불가). 상세 `/index/position/{id}/detail`. lilithgames도 같은 방식 |
| 하이퍼그리프 (Moka) | `https://jobs.hypergryph.com/apply/hypergryph/26325/#/jobs`를 Playwright로 열고 `button[data-page=N]`을 눌러 페이지마다 `a[href*="#/job/"]` 수집 (약 330건, API 응답은 암호화돼서 화면에서 읽음). 상세 `#/job/{id}` 본문의 "职位描述" ~ "申请职位" 구간 |
| HRMOS (일본) | `https://hrmos.co/pages/{회사}/jobs?page=N` curl로 목록 (`<a href=".../jobs/ID"> ... <h2>제목</h2>`), 상세도 curl. 회사: cover-corp, bravegroup, cygames, sega, square-enix, colopl, klab, gungho, sumzap, yostar, nexon(재팬), gree. ANYCOLOR는 recruit.anycolor.co.jp/career/ 에 있는 hrmos 링크로 수집 |
| axol (일본) | 목록 `job.axol.jp/{x}/c/{회사}/job/list` (도호는 `/public/job/list`), 상세 `/job/detail/ID`. 회사: toho(bx), sonymusic(hy, 애니플렉스 모회사), kadokawa(jn). "【社員紹介】" 붙은 공고는 중복이라 제외 |
| HERP / jobcan (일본) | 굿스마일 `herp.careers/v1/goodsmile`, Donuts `recruit.jobcan.jp/donuts/list/all/all/N` (게임사업부·ANYLAND만) |
| 페이퍼게임즈·빌리빌리·요스타(상하이) | 페이퍼게임즈 Feishu `papergames.jobs.feishu.cn/social/position/list?current=N&limit=100` (응답 수집), 빌리빌리 jobs.bilibili.com 페이지 안에서 `POST /api/srs/position/positionList` (pageSize 100, workTypeList ["3"]), 요스타 Moka `app.mokahr.com/social-recruitment/yostar/145292#/jobs` |
| NHN·SOOP·넥슨 아메리카·반다이남코 미국 | NHN `careers.nhn.com/v1/job-postings?page=0&size=200`, SOOP `recruit.sooplive.com/recruit_list.php`, 넥슨 아메리카 `careers.jobscore.com/careers/nexonamericainc`, 반다이남코 미국 Greenhouse `bandainamco` |
| 산바오 (Moka) | `jobs.sunborngame.com/social-recruitment/micateam/142158/#/` 홈에서 직무 분류(市场运营类·商务类·项目管理类·本地化类·产品策划类·质量管理类)를 하나씩 눌러 목록 수집 (페이지 넘김만으로는 일부 누락) |
| MIXI / DeNA | MIXI HERP `herp.careers/v1/mixigroup`, DeNA Green `green-japan.com/company/1324`, DeNA Games Tokyo HERP `herp.careers/v1/dgtrecruit` |
| KAMITSUBAKI (THINKR) | Wantedly `wantedly.com/companies/thinkr/projects` |
| 레벨 인피니트 | `levelinfinite.com/careers/` 목록(`a.career-item[data-index]`, 66건 전부 DOM에 있음)을 JS로 클릭해 팝업 본문 수집 |
| 스퀘어 에닉스 유럽 | Workable `POST apply.workable.com/api/v3/accounts/square-enix/jobs` |
| 넷이즈 게임즈 | `hr.163.com/job-list.html`을 열고 페이지 안에서 `POST /api/hr163/position/queryPage` {currentPage,pageSize:100} (전체 약 2,600건). productName이 网易游戏（互娱）·网易游戏（雷火）·网易元气·星间/烈酷工作室, firstPostTypeName이 市场·运营·产品·内容·项目管理·客服인 것만 |
| 엔씨소프트 | careers.ncsoft.com/apply/list 를 열어 첫 `/interface/apply/list` 요청의 헤더·본문을 잡은 뒤 page=2,3..로 같은 요청 반복 (pagesize 20 고정, 50으로 바꾸면 거부). 상세 `/apply/view/{jopenId}?companyId={regOpId}` (자주 빈 화면 → 재시도) |
| 만쥬 (벽람항로) | Feishu `ooia5293gn.jobs.feishu.cn/index/position/list` (career.manjuu.com 연결) |
| 넥슨 그룹 | careers.nexon.com은 Cloudflare 봇 차단 → 게임잡 전체 목록의 넥슨·넥슨게임즈·네오플·민트로켓·엔엑스쓰리 공고로 수집. "라이브(서비스) 기획자", "UX 분석가"는 포함 |
| 원티드 | 브라우저로 wanted.co.kr을 연 뒤 페이지 안에서 `/api/chaos/search/v1/position?query=...` 검색, `/api/v4/jobs/{id}` 상세 (curl은 차단됨) |

제외: 넷마블 계열, 디자인·아트·개발·QA·재무·인사 직군. 언어 때문에 거르지 않음.

## 로고 수집 순서
1. 게임잡 공고 페이지의 회사 로고 (LogoView)
2. 사람인 회사 페이지 `company-info/view?csn=` 의 og:image (주소에 logo가 있을 때만. 사람인 기본 이미지는 버림)
3. Green 회사 페이지 `alt="企業メインロゴ"` 이미지
4. 공식 사이트 apple-touch-icon / Google favicon (128px)
- 240x120 흰 바탕 PNG로 맞춰 `logo`에 저장. 앱은 watch 로고 → companies 로고 → 회사 이름 글자 순으로 표시.

## 중복 정리
- 같은 공고가 게임잡·사람인·원티드에 동시에 올라오는 경우가 많음. 회사명 앞 4글자 + 제목(공백·괄호·"모집/채용" 제거)이 같으면 하나만 남김 (게임잡 > 원티드 > 잡코리아 > 사람인 순).

## 공고 원문 (bodypacks)
- `bodypacks/bNNN` = `{items:{<job id>:{raw, duties?, quals?, prefs?, ocr?}}}` (문서 1개당 200KB 이하).
- 본문 주소: 게임잡·잡코리아 `/Recruit/GI_Read_Comt_Ifrm?gno=ID`, 사람인 `/zf_user/jobs/relay/view-detail?rec_idx=ID&rec_seq=0`, 해외 ATS는 상세 API의 본문.
- 본문 글자가 400자 미만이고 이미지가 있으면 `tesseract -l kor+eng --psm 4`로 이미지 글자를 읽어 `ocr:true`로 저장 (오타 가능).
- 제목 패턴(담당업무/자격요건/우대사항)으로 나눠 duties·quals·prefs에 넣음. 앱은 "공고 원문 전체"를 펼친 상태로 보여줌.
- 새 공고만 기존 pack 뒤에 새 pack으로 추가.

## 번역 (tr)
- `tr/<job id>` = `{summary, duties, quals, prefs, at}`. 앱의 번역 버튼이 만들어 저장. 미리 채워둬도 됨.

## 회사 정보
- watch 문서 `info` = `{summary, size, founded, address, site}`. 사람인 `company-info/view?csn=` 의 `.company_summary`·`.company_details`에서 수집.

## 마감일
- 날짜가 보이면 항상 `deadline_date`(YYYY-MM-DD)를 채움. 게임잡·사람인 목록 날짜, 잡코리아 페이지 meta "마감일 : YYYY.MM.DD", 원티드 due_time, 해외 ATS 필드.
- "오늘마감/내일마감/D-3/~12/05" 같은 상대 표현은 수집한 날 기준으로 실제 날짜로 바꿔 저장.
- 날짜가 정말 없을 때만 `deadline`에 "상시채용" 또는 "채용시 마감".
- 앱은 `deadline_date`가 지난 공고를 자동으로 "마감됨" 처리해서 지원 가능 목록에서 뺌. 매일 추적 때는 마감·내려간 공고를 `closed:true`로 기록하고, 마감일이 바뀐 공고는 새 날짜로 고침.

## 회사별 점검 원칙
- 관심 회사(watch)마다 실제 채용 사이트(ATS)를 찾아 직접 수집. 채용 사이트를 모르면 홈페이지의 recruit/career/採用/招聘 링크를 따라가 ATS 주소를 찾음 (HRMOS, axol, HERP, jobcan, GreetingHR, Moka, Feishu, Greenhouse, Lever, Ashby, JobScore 등).
- 회사 공고가 0~2건이면 수집이 빠졌을 가능성부터 의심하고 회사 사이트를 확인.
- 카카오엔터테인먼트·데브시스터즈: GreetingHR 사이트 확인 결과 2026-11-24 기준 공개 공고 없음.

## 확인 못 하는 곳 (회사 사이트에서 직접 확인)
- 엔씨소프트 careers.ncsoft.com: 목록이 불안정하게 뜸 (게임잡 등으로 수집).
- 넥슨 careers.nexon.com·CareerCross(만쥬 재팬): Cloudflare 봇 차단. 서산쥐: 공식 채용 사이트 없음(위챗). 774 inc.·코단샤 USA·Aniplex USA·스튜디오비사이드·스텔라이브: 공개 공고 목록 없음.
- 애니메이트·코토부키야·무빅·세가 아메리카·Square Enix US(Workable): 사이트가 막혀 있거나 오류. 넥슨 career.nexon.com, 세가, KADOKAWA: 프록시에서 접속 차단. Cygames, 반다이남코: 403.

## 숨긴 회사·공고
- `profile/me`의 `hidden_cos`(회사 id 목록), `hidden_jobs`(공고 id 목록). 앱에서 사용자가 "이 회사 숨기기/이 공고 숨기기"로 저장.
- 매일 추적 때 `hidden_cos` 회사는 새 공고를 수집·추가하지 않고, 보고와 소식(news)에도 넣지 않음. `hidden_jobs`는 소식·보고에서 제외.

## 번역 묶음 (trpacks) — 매주
- `trpacks/tNNN` = `{items:{<job id>:{summary,duties,quals,prefs,at,by}}}`. 앱은 trpacks + tr(앱 번역 버튼 결과)를 합쳐 공고 화면에 한국어로 보여줌 (tr가 우선).
- 매주: `python3 tools/trprep.py IN.json` → 우선순위 순 최대 60건(한국 관련 → IP·굿즈 → 최근 8일 사업 직군)의 업무·자격·우대 줄만 뽑은 압축 입력.
- 번역 결과는 `{"id":{"s":요약,"d":[업무],"q":[자격],"p":[우대]}}` 형식, 줄당 짧게 (업무 ≤5, 자격 ≤4). → `python3 tools/trpack.py OUT.json` → 새 `data/trpacks/tNNN.json` → ArtifactData set (trpacks).
- 이미 번역된 id는 trprep가 자동으로 건너뜀. 나머지 공고는 앱의 "한국어로 번역하기" 버튼으로 필요할 때 번역.

## 키아트 (카드 배경 이미지)

- 파일: `art/<key>.webp` (960x540, webp q68). 앱과 함께 Artifact `files`로 게시 (`{"art/x.webp":"art/x.webp"}`).
- 연결: 앱 HTML의 `ART_GAME`(공고 game·제목에 들어간 게임 이름 → key)과 `ART_CO`(company_id → 회사 대표 게임 key).
- 우선순위: 공고의 게임 → 회사 대표 게임 → 없으면 다크 패널 + 로고.
- 출처: Steam `IStoreBrowseService/GetItems` 의 `library_hero` (글자 없는 키아트) → 없으면 공식 사이트 og:image.
- 로고만 있는 이미지·이벤트 배너·다른 게임 콜라보 이미지는 쓰지 않음. 새로 넣을 땐 시트로 한 번 눈으로 확인.

### 관련 이미지 (키아트가 없는 회사·공고)

- 순서: 공고의 게임 키아트(`ART_GAME`) → 회사 대표작(`ART_CO`, 여러 개면 공고마다 돌아가며) → 공고/회사 관련 이미지(`ART_X`) → 장르 참고 이미지(`ART_KW`/`ART_POOL`, 카드에 "참고 이미지" 표시).
- `ART_X` 채우기 (새 회사·새 공고가 생길 때):
  1. 키아트 없는 열린 공고를 JSON 목록(missing_jobs.json: id,url,company_id)으로 만든다.
  2. `python3 tools/art_fill.py missing_jobs.json cand.json` — 사람인 상세 이미지, 게임잡 회사 사진, 그린 재팬 사진, 원티드 회사 이미지, 그 밖은 og:image 후보를 모은다.
  3. `python3 tools/art_pick.py cand.json missing_jobs.json art/c <tmpdir>` 후 `--relax`로 한 번 더 — 로고·글자뿐인 이미지를 거르고 회사별(헤드헌팅은 공고별 `j-<id>`) 1장을 `art/c/<key>.webp`(640x360)로 저장, `art/c/_map.json` 갱신.
  4. 앱 HTML의 `const ART_X=` 를 `_map.json` 내용으로 바꾸고, 새 이미지 파일을 Artifact publish `files`(root `job-radar`, 한 번에 255개 이하)로 같이 올린다.
  5. 그래도 없는 회사: 네이버 이미지 검색 "<회사명> 사옥"(해외는 "<name> headquarters office") 상위 3장 중 회사 건물·사무실·회사 활동 사진을 눈으로 골라 쓴다. 다른 회사 건물이거나 무관하면 쓰지 않는다. 헤드헌팅(회사명 없음)은 참고 이미지 유지.

## 범위 밖 공고·중복 (앱에서 자동 처리)

- 앱의 `OUT_RE`에 걸리는 공고는 화면에 안 나온다: UA·퍼포먼스 마케터, 컨셉·배경·시네마틱 아티스트, 디자이너, 엔지니어·개발자·QA, 급여, 시스템·전투 기획, 레벨 디자인. (엔터 업계 "아티스트"=가수는 범위 안이라 걸지 않음)
- 인턴(`INTERN_RE`)은 기본으로 숨기고, 공고 탭 "인턴 포함" 버튼으로 볼 수 있다.
- 같은 회사의 같은 공고(괄호·대괄호 태그 제거 후 제목 일치)가 다른 채용 사이트에 또 있으면 하나만 남긴다: 공식 채용 사이트 > 게임잡·잡코리아·사람인. 같은 사이트 안의 같은 제목은 다른 공고로 보고 둔다. 헤드헌팅은 헤드헌팅 회사 이름 단위.
- 수집 단계에서도 위 직군은 넣지 않는다. 앱 필터는 안전망이다.

## 관심 회사 채용 주소 점검

- watch의 careers_url이 회사 홈페이지(채용 시스템이 아님)이거나 method가 manual이면 실제로는 수집이 안 된다. 예: Lilith는 lilith.com으로 되어 있어 0건이었음 → lilithgames.jobs.feishu.cn 으로 수정.
- 매일 실행 때 공고 0~2건 회사는 실제 ATS(GreetingHR, Feishu, Moka, HRMOS, Greenhouse, Workday 등)를 찾아 careers_url·method를 고친다.

## 추가 수집 경로 (2026-11-25)

| 회사 | 경로 | 비고 |
|---|---|---|
| 반다이남코 엔터테인먼트 (일본 본사) | https://hrmos.co/pages/bandainamcoent/jobs | 게임 프로듀스·마케팅·현지화·IP 브랜딩·홍보. 페이지의 JSON-LD(application/ld+json)에 제목·본문 있음 |
| 사이버에이전트 그룹 (QualiArts, 아프리봇, CA Soa, 넬케 플래닝 등) | https://hrmos.co/pages/cyberagent-group/jobs | 그룹 전체라 게임·애니·IP 계열사 공고만 고른다 |
| 애니메이트 그룹 (무빅, 프론티어웍스, 게이머즈 등) | https://hrmos.co/pages/animate-group/jobs | 굿즈 기획·이벤트·게임 프로듀스 |
| 릴리스 게임즈 | https://lilithgames.jobs.feishu.cn/ | `/api/v1/search/job/posts` 응답 캡처. 대부분 개발·아트라 범위 내는 소수 |
| 반다이남코코리아 | https://careerbandainamco.ninehire.site/ | 나인하이어 |
| DeNA | https://career.dena.com/ | Green 1324와 함께 |
| 라인게임즈 | https://recruit.line.games/ | |
| 슈퍼크리에이티브 | https://recruit.supercreative.kr/ | |
| SEGA of America | careers.sega.com → Paycom | |
| 부시로드 | https://hrmos.co/pages/bushiroad/jobs | TCG·굿즈·출판·음악·애니. 아르바이트(PART_TIME)·법무·경리·SE·디자이너 제외 |
| 포켓몬센터 | https://hrmos.co/pages/pokemoncenter/jobs | 해외 사업·EC 마케팅·글로벌 종합직. 매장 계약직·점장 제외 |
| Cygames 전체 | https://recruit.cygames.co.jp/career/ (→ hrmos cygames) | 프로모션·현지화(일영·일한 코디네이터)·GM 등이 빠져 있었음. 목록 전체를 범위 기준으로 다시 확인 |
| 프로젝트문 | 사람인·게임잡·잡코리아 검색 "프로젝트문" | 자체 채용 페이지 없음 |
| 일본 게임업계 구인 (파미통 커리어) | API `https://syscareer.famitsu.com/api/job_search?page_number=N&count=100` (Referer career.famitsu.com/job-search), 상세 `https://career.famitsu.com/job-detail/<id>` | 약 1,800건. 제목 기준으로 범위 내만. 캡콤·코나미·코에이테크모·EXNOA·플래티넘·TMS 등 |
| XD (심동) | https://xd-legacy.jobs.feishu.cn/ | Feishu |
| 히어로게임즈 | https://careers.hero.com/ | |


## 수집 우선순위

- 서브컬처 게임·IP 회사가 우선이다. 서브컬처가 아닌 캐주얼·전략·SLG 위주 회사(Century Games, FunPlus, Moonton 등)는 새로 찾지 않는다.

## 서브컬처 필터 (앱)

- `SUB_CO`(서브컬처 핵심 회사)는 공고 전체를 보여준다. 그 밖의 회사는 공고 제목·게임·요약·본문 앞부분에 `SUB_RE` 단서(애니, 미소녀, 수집형, IP, 굿즈, 버튜버, 웹툰, 二次元, アニメ, 작품명 등)가 있을 때만 보인다.
- 캐릭터·IP 공고는 항상 포함: 직군이 ip이거나 제목·요약·본문에 IP·캐릭터·라이선스·굿즈·MD·상품화·licensing·merchandise·character 등이 있으면 서브컬처가 아니어도 보인다.
- 숨긴 공고는 공고 탭 "서브컬처 외 포함" 버튼으로 볼 수 있다. 회사 탭도 서브컬처 공고가 없는 회사는 숨긴다.
- 새 서브컬처 회사를 넣으면 `SUB_CO`에 id를 추가한다.
