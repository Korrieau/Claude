// Browser collectors. Usage: node pw.js <mode> [args...] > out.json
//   gamejob                      full GameJob list (all pages)
//   jobkorea <query...>          JobKorea search results (3 pages each)
//   moka <url#/jobs> <kw...>     Moka board keyword search (links)
//   feishu <host> <kw...>        Feishu board keyword search (links)
//   page <url...>                body text of pages (for details)
const { chromium } = require('playwright');
const [mode, ...args] = process.argv.slice(2);
(async () => {
  const b = await chromium.launch(); const p = await b.newPage(); const out = [];
  const wait = ms => p.waitForTimeout(ms);
  try {
    if (mode === 'gamejob') {
      await p.goto('https://www.gamejob.co.kr/Recruit/joblist?menucode=duty&duty=24', { waitUntil: 'domcontentloaded', timeout: 45000 }); await wait(2000);
      const seen = new Set();
      for (let page = 1; page <= 80; page++) {
        const rows = await p.evaluate(async page => {
          const r = await fetch('/Recruit/_GI_Job_List/', { method: 'POST', headers: { 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8', 'X-Requested-With': 'XMLHttpRequest' }, body: `page=${page}&condition%5Bmenucode%5D=&condition%5Btabcode%5D=1&direct=0&order=1&pagesize=40&tabcode=1` });
          const d = document.createElement('div'); d.innerHTML = await r.text();
          return [...d.querySelectorAll('a[href*="GI_No="]')].map(a => { const tr = a.closest('tr,li'); return { t: a.innerText.trim().replace(/\s+/g, ' '), id: (a.getAttribute('href').match(/GI_No=(\d+)/) || [])[1], ctx: (tr ? tr.innerText : '').replace(/\s+/g, ' ').slice(0, 320) }; });
        }, page);
        let n = 0; for (const r of rows) if (r.id && !seen.has(r.id)) { seen.add(r.id); n++; out.push({ src: 'GameJob', title_original: r.t, url: `https://www.gamejob.co.kr/Recruit/GI_Read/View?GI_No=${r.id}`, key: 'gj-' + r.id, ctx: r.ctx, country: 'KR' }); }
        if (!n) break;
      }
    } else if (mode === 'jobkorea') {
      const seen = new Set();
      for (const q of args) for (let pg = 1; pg <= 3; pg++) {
        await p.goto(`https://www.jobkorea.co.kr/Search/?stext=${encodeURIComponent(q)}&tabType=recruit&Page_No=${pg}`, { waitUntil: 'domcontentloaded', timeout: 30000 }).catch(() => { }); await wait(3000);
        const r = await p.evaluate(() => [...document.querySelectorAll('a[href*="/Recruit/GI_Read/"]')].map(a => { const c = a.closest('article,li,div[class*=item],div[class*=list]'); return [a.innerText.replace(/\s+/g, ' ').trim(), a.href.split('?')[0], c ? c.innerText.replace(/\s+/g, ' ').slice(0, 260) : ''] }).filter(x => x[0].length > 5));
        let n = 0; for (const [t, h, c] of r) { const id = h.split('/').pop(); if (!seen.has(id)) { seen.add(id); n++; out.push({ src: 'JobKorea', q, title_original: t, url: h, key: 'jk-' + id, ctx: c, country: 'KR' }); } }
        if (!n) break;
      }
    } else if (mode === 'moka' || mode === 'feishu') {
      const [base, ...kws] = args;
      for (const kw of kws) {
        const u = mode === 'moka' ? `${base}?keyword=${encodeURIComponent(kw)}` : `https://${base}/index/position/list?keywords=${encodeURIComponent(kw)}`;
        await p.goto(u, { waitUntil: 'domcontentloaded', timeout: 40000 }).catch(() => { }); await wait(6000);
        const r = await p.evaluate(() => [...document.querySelectorAll('a')].map(a => [a.href, a.innerText.replace(/\s+/g, ' ').trim().slice(0, 160)]).filter(x => /#\/job\/|position\/\d+/.test(x[0])));
        for (const [h, t] of r) out.push({ src: mode, kw, url: h, title_original: t.split(' ')[0], ctx: t });
      }
    } else if (mode === 'page') {
      for (const u of args) { await p.goto(u, { waitUntil: 'networkidle', timeout: 45000 }).catch(() => { }); await wait(2500); out.push({ url: u, text: await p.evaluate(() => document.body.innerText) }); }
    }
  } finally { process.stdout.write(JSON.stringify(out)); await b.close(); }
})();
