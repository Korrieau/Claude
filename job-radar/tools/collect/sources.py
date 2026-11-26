"""curl-based collectors (no browser). Each returns a list of candidate dicts."""
import json, re
from common import curl, html_text, KO_RE

HRMOS = {  # org slug -> company_id
    "capcom": "capcom", "pokemon": "c-pokemon", "hal": "hallab", "aiming": "c-aiming", "klab": "klab", "gree": "gree",
    "cover-corp": "cover", "cygames": "cygames", "sega": "sega", "square-enix": "squareenix", "yostar": "yostarjp",
    "bandainamcoent": "bandainamcoent", "nexon": "nexonjp", "gamefreak": "gamefreak", "enish": "c-enish",
    "bravegroup": "brave", "bushiroad": "bushiroad", "animate-group": "animate", "colopl": "colopl",
    "pokemoncenter": "pokemoncenter", "lasengle": "lasengle", "bandainamcostudios": "c-bnstudios", "iriam": "c-iriam",
    "sumzap": "sumzap",
}


def hrmos(orgs=None, max_pages=15):
    out = []
    for org in orgs or HRMOS:
        seen = set()
        for pg in range(1, max_pages + 1):
            h = curl(f"https://hrmos.co/pages/{org}/jobs?page={pg}")
            got = 0
            for m in re.finditer(r'href="(https://hrmos\.co/pages/%s/jobs/[^"?#]+)"(.*?)</a>' % re.escape(org), h, re.S):
                u = m.group(1)
                if u in seen:
                    continue
                seen.add(u); got += 1
                t = html_text(m.group(2)).split("\n")[0][:120]
                out.append({"src": "HRMOS", "company_id": HRMOS.get(org, "c-" + org), "company": org, "title_original": t,
                            "url": u, "country": "JP"})
            if not got:
                break
    return out


def hrmos_detail(url):
    return html_text(curl(url))[:6000]


def netease(keywords=("韩语", "韩国"), page_size=100):
    out, seen = [], set()
    for k in keywords:
        d = json.loads(curl("https://hr.163.com/api/hr163/position/queryPage",
                            data={"currentPage": 1, "pageSize": page_size, "keyword": k}) or "{}")
        for x in (d.get("data") or {}).get("list") or []:
            i = str(x["id"])
            if i in seen or "游戏" not in (x.get("productName") or ""):
                continue
            seen.add(i)
            raw = f"{x['name']}\n岗位职责\n{x.get('description','')}\n任职要求\n{x.get('requirement','')}"
            out.append({"src": "NetEase", "company_id": "netease", "company": "넷이즈 게임즈 (NetEase)",
                        "title_original": x["name"], "url": f"https://hr.163.com/job-detail.html?id={i}&lang=zh",
                        "key": f"id={i}&", "country": "CN", "raw": raw[:4000], "ko": bool(KO_RE.search(raw)),
                        "extra": {"product": x.get("productName"), "years": x.get("reqWorkYearsName"),
                                  "place": x.get("workPlaceNameList")}})
    return out


def tencent(keywords=("韩语", "韩国")):
    out, seen = [], set()
    for k in keywords:
        d = json.loads(curl(f"https://careers.tencent.com/tencentcareer/api/post/Query?keyword={k}&pageIndex=1&pageSize=100&language=zh-cn&area=cn") or "{}")
        for x in (d.get("Data") or {}).get("Posts") or []:
            if x["PostId"] in seen:
                continue
            seen.add(x["PostId"])
            out.append({"src": "Tencent", "company_id": "tencent", "company": "텐센트 (Tencent)",
                        "title_original": x["RecruitPostName"], "key": x["PostId"],
                        "url": f"https://careers.tencent.com/jobdesc.html?postId={x['PostId']}", "country": "CN",
                        "raw": x.get("Responsibility", "")[:3000], "extra": {"bg": x.get("BGName"), "loc": x.get("LocationName")}})
    return out


def famitsu(ko_only=True):
    out = []
    for pg in range(1, 40):
        try:
            L = json.loads(curl(f"https://syscareer.famitsu.com/api/job_search?page_number={pg}&count=100"))["jobs"]
        except Exception:
            break
        if not L:
            break
        for x in L:
            txt = x["name"] + " " + (x.get("description") or "")
            if ko_only and not re.search(r"韓国|Korea|ハングル", txt):
                continue
            out.append({"src": "Famitsu", "company_id": None, "company": x["company_name"], "title_original": x["name"],
                        "key": x["id"], "url": f"https://career.famitsu.com/job-detail/{x['id']}", "country": "JP",
                        "raw": (x.get("description") or "")[:3000]})
    return out


def ashby_hoyoverse():
    d = json.loads(curl("https://api.ashbyhq.com/posting-api/job-board/hoyoverse") or "{}")
    return [{"src": "Ashby", "company_id": "hoyoverse", "company": "HoYoverse", "title_original": j["title"],
             "url": j["jobUrl"], "key": j["id"], "country": j.get("location"), "raw": (j.get("descriptionPlain") or "")[:3000],
             "ko": bool(KO_RE.search(j["title"] + (j.get("descriptionPlain") or "")))} for j in d.get("jobs", [])]


def jobkorea_detail(gno):
    return html_text(curl(f"https://www.jobkorea.co.kr/Recruit/GI_Read_Comt_Ifrm?Gno={gno}"))[:6000]
