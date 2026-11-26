"""Job Radar candidate finder.

Usage (from repo root):
  python3 job-radar/tools/collect/run.py --export <db-export-dir> [--only hrmos,netease,...] [--out cand.json]

<db-export-dir>: folder written by ArtifactData list ... out_dir (jobs/, jobpacks/, profile/).
Runs every source, keeps in-scope titles, drops known/hidden/excluded ones, and writes a SHORT
candidate list (one line per posting) for the agent to review, translate and pack.
Korean-language hits (ko=true) are kept even when the title filter is unsure.
"""
import argparse, json, os, subprocess, sys
sys.path.insert(0, os.path.dirname(__file__))
from common import Index, in_scope, EXCL_CO, KO_RE, OUT_RE, strip_tags
import sources

HERE = os.path.dirname(os.path.abspath(__file__))
JK_QUERIES = ["넥슨", "넥슨게임즈", "네오플", "서브컬처 게임", "게임 사업PM", "게임 마케팅 인턴", "게임 운영 신입", "일본어 게임 사업",
              "중국어 게임 사업", "스마일게이트", "시프트업", "카카오게임즈", "쿠로게임즈", "호요버스", "요스타", "빌리빌리", "하이퍼그리프",
              "레벨인피니트", "에피드게임즈", "디나미스원", "컨트롤나인", "빅게임스튜디오", "슈퍼크리에이티브", "라이온하트"]
MOKA = {"pwrd": "https://app.mokahr.com/social-recruitment/pwrd/142341#/jobs",
        "yostar": "https://app.mokahr.com/social-recruitment/yostar/145292#/jobs",
        "hypergryph": "https://jobs.hypergryph.com/apply/hypergryph/26325/#/jobs"}
FEISHU = {"kuro": "kurogame.jobs.feishu.cn", "papergames": "career.papegames.com", "xd": "xd-legacy.jobs.feishu.cn"}
KW = ["韩语", "韩国"]
# reviewed-and-rejected postings (url or key) so later runs don't show them again
SKIP_FILE = os.path.join(HERE, "..", "..", "data", "skip.json")
SKIP = set(json.load(open(SKIP_FILE))) if os.path.exists(SKIP_FILE) else set()


def pw(*a):
    r = subprocess.run(["node", os.path.join(HERE, "pw.js"), *a], capture_output=True, text=True, timeout=900)
    try:
        return json.loads(r.stdout or "[]")
    except Exception:
        print("pw failed", a[:2], r.stderr[-300:], file=sys.stderr); return []


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--export"); ap.add_argument("--only"); ap.add_argument("--out", default="cand.json")
    a = ap.parse_args()
    only = set(a.only.split(",")) if a.only else None
    want = lambda k: not only or k in only
    idx = Index(a.export)
    C = []
    steps = [("hrmos", lambda: sources.hrmos()), ("netease", sources.netease), ("tencent", sources.tencent),
             ("famitsu", sources.famitsu), ("hoyoverse", sources.ashby_hoyoverse),
             ("gamejob", lambda: pw("gamejob")), ("jobkorea", lambda: pw("jobkorea", *JK_QUERIES))]
    steps += [(f"moka:{k}", (lambda u: lambda: pw("moka", u, *KW))(u)) for k, u in MOKA.items()]
    steps += [(f"feishu:{k}", (lambda h: lambda: pw("feishu", h, *KW))(h)) for k, h in FEISHU.items()]
    for name, fn in steps:
        if not want(name.split(":")[0]):
            continue
        try:
            got = fn()
        except Exception as e:
            print(name, "ERR", e, file=sys.stderr); got = []
        print(f"{name}: {len(got)} raw", file=sys.stderr)
        for c in got:
            c.setdefault("src", name)
            C.append(c)
    keep, seen = [], set()
    for c in C:
        cid = c.get("company_id")
        if cid in EXCL_CO or cid in idx.hidden_cos or c.get("key") in idx.hidden_jobs:
            continue
        ko = c.get("ko") or bool(KO_RE.search(c.get("title_original", "")))
        t = c.get("title_original", "")
        if OUT_RE.search(strip_tags(t)) or not (in_scope(t) or ko):
            continue
        if c.get("url") in SKIP or c.get("key") in SKIP:
            continue
        if idx.known(c):
            continue
        k = c.get("url")
        if k in seen:
            continue
        seen.add(k); c["ko"] = ko; keep.append(c)
    json.dump(keep, open(a.out, "w"), ensure_ascii=False, indent=0)
    for c in keep:  # compact listing for the agent
        print(f"{'KO ' if c['ko'] else ''}{c['src']} | {c.get('company') or ''} | {c['title_original'][:70]} | {c['url']}")
    print(f"{len(keep)} candidates -> {a.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
