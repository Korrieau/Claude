"""Shared helpers for Job Radar collectors.

Every collector writes candidates as a list of dicts:
  {src, company_id, company, title_original, url, country, raw, deadline_date?, extra?}
run.py filters (scope), dedupes against the DB export and writes cand.json.
Only cand.json needs to be read by the agent -> keeps token use low.
"""
import json, re, os, glob, subprocess, html, difflib

UA = "Mozilla/5.0"
TODAY = os.environ.get("JR_TODAY") or subprocess.run(["date", "+%F"], capture_output=True, text=True).stdout.strip()

# --- scope filters (titles only, bracket tags removed) ---
IN_RE = re.compile(
    r"사업|PM\b|프로듀서|매니저|마케팅|마케터|운영|퍼블리싱|서비스|커뮤니티|\bCM\b|\bGM\b|CS\b|고객|현지화|로컬|로컬라이|IP|라이선|굿즈|MD\b|콜라보|제휴|BD\b|이벤트|PR\b|홍보|브랜드|데이터 ?분석|UX ?분석|리서치|인턴|신입|"
    r"事業|プロデュー|プロジェクトマネ|プロダクトマネ|運営|運用|マーケ|宣伝|プロモーション|広報|コミュニティ|カスタマー|サポート|ローカライズ|ライセンス|版権|グッズ|商品|コラボ|アライアンス|パートナー|営業|パブリッシング|海外|グローバル|アナリスト|イベント|タレント|マネージャー|インターン|"
    r"运营|市场|营销|发行|商务|本地化|社区|品牌|产品经理|项目经理|PM|授权|周边|衍生品|用户研究|数据分析|实习|海外|"
    r"Producer|Marketing|Business|Localization|Community|Publishing|Operations|Partnership|Licens|Merch|Brand|Analyst|Intern|Player Support|Customer",
    re.I)
OUT_RE = re.compile(
    r"프로그래머|엔지니어|개발자|원화|모델러|애니메이터|디자이너|아티스트|\bTA\b|리거|사운드|성우|보이스|서버|클라이언트|시나리오|레벨 ?디자|전투|밸런스|퀘스트|총무|회계|재무|인사담당|채용담당|법무|세무|보안|인프라|DBA|\bQA\b|테스터|"
    r"プログラマ|エンジニア|デザイナー|アニメーター|イラスト|モデラ|エフェクト|サウンド|声優|デバッグ|テスター|シナリオ|レベル|バトル|ゲームプランナー|アルバイト|経理|人事|採用|法務|総務|情報システム|インフラ|セキュリティ|アート|背景|作画|CG|ライター|"
    r"程序|工程师|开发|美术|原画|动画|特效|音效|语音|配音|声优|测试|策划|关卡|数值|战斗|系统策划|交互|财务|会计|法务|人力|HR\b|招聘|行政|安全|算法|"
    r"Engineer|Scientist|Developer|Programmer|Designer|Artist|Animator|Sound|Audio|Voice|QA\b|Tester|Recruiter|Legal|Finance|Accountant|Security|Payroll",
    re.I)
WEBTOON_RE = re.compile(r"웹툰|웹소설|webtoon|web ?novel", re.I)
EXCL_CO = {"lilith", "devsisters", "c-8c3156ff"}  # + profile hidden_cos at runtime
KO_RE = re.compile(r"韩语|韩国|韓国|韓国語|Korean|Korea|한국어|한국 ?시장")


def strip_tags(t):
    return re.sub(r"【[^】]*】|\[[^\]]*\]|\([^)]*\)|（[^）]*）|<[^>]*>", " ", t or "")


def in_scope(title):
    t = strip_tags(title)
    return bool(IN_RE.search(t)) and not OUT_RE.search(t) and not WEBTOON_RE.search(t)


def norm(t):
    t = re.sub(r"【[^】]*】|\[[^\]]*\]|\([^)]*\)|（[^）]*）|_求人No.*|추가\s*(모집|채용)|모집|채용|공고|담당자|\s", "", t or "")
    return t.lower()[:40]


def curl(url, data=None, headers=None, timeout=30):
    cmd = ["curl", "-sL", "-m", str(timeout), "-A", UA, url]
    for k, v in (headers or {}).items():
        cmd += ["-H", f"{k}: {v}"]
    if data is not None:
        cmd += ["-X", "POST", "-H", "Content-Type: application/json", "--data-binary", json.dumps(data)]
    return subprocess.run(cmd, capture_output=True, text=True).stdout


def html_text(h):
    h = re.sub(r"<script.*?</script>|<style.*?</style>", "", h, flags=re.S)
    t = html.unescape(re.sub(r"<br\s*/?>|</p>|</li>|</div>|</tr>|</h\d>", "\n", h))
    t = re.sub(r"<[^>]+>", "", t)
    return re.sub(r"\n\s*\n+", "\n", t).strip()


class Index:
    """Existing-job index built from a DB export dir (ArtifactData list out_dir)
    plus local backups in job-radar/data."""

    def __init__(self, export_dir=None, repo="job-radar/data"):
        self.jobs = {}
        for f in sorted(glob.glob(f"{repo}/jobpacks/*.json")):
            for k, v in json.load(open(f)).get("items", {}).items():
                self.jobs[k] = v
        dirs = [f"{repo}/jobs"] + ([f"{export_dir}/jobpacks", f"{export_dir}/jobs"] if export_dir else [])
        for d in dirs:
            for f in glob.glob(f"{d}/*.json"):
                v = json.load(open(f))
                v = v.get("data", v)
                if "items" in v:
                    self.jobs.update(v["items"])
                else:
                    self.jobs[os.path.basename(f)[:-5]] = v
        self.urls = {(v.get("url") or "").rstrip("/") for v in self.jobs.values()}
        self.blob = " ".join(self.urls)
        self.by_co = {}
        for v in self.jobs.values():
            self.by_co.setdefault(v.get("company_id"), []).append(norm(v.get("title_original") or v.get("title")))
        self.hidden_cos, self.hidden_jobs = set(), set()
        pf = f"{export_dir}/profile/me.json" if export_dir else None
        if pf and os.path.exists(pf):
            p = json.load(open(pf)); p = p.get("data", p)
            self.hidden_cos = set(p.get("hidden_cos") or []); self.hidden_jobs = set(p.get("hidden_jobs") or [])

    def known(self, c):
        u = (c.get("url") or "").rstrip("/")
        if u and (u in self.urls or (c.get("key") and c["key"] in self.blob)):
            return True
        n = norm(c.get("title_original"))
        return any(e and difflib.SequenceMatcher(None, n, e).ratio() > 0.8 for e in self.by_co.get(c.get("company_id"), []))
