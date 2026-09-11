import json
from pypdf import PdfReader

r = PdfReader('map.pdf')
out = []
for pi, page in enumerate(r.pages):
    items = []
    def visitor(text, cm, tm, font_dict, font_size):
        if not text or not text.strip():
            return
        x, y = tm[4], tm[5]
        items.append({"t": text.strip(), "x": round(x,1), "y": round(y,1), "s": round(font_size,1) if font_size else 0})
    page.extract_text(visitor_text=visitor)
    out.append(items)
    print("page", pi, "runs", len(items))

json.dump(out, open('text_pos.json','w'), ensure_ascii=False)
# quick bounds
for pi, items in enumerate(out):
    xs=[i['x'] for i in items]; ys=[i['y'] for i in items]
    print(pi, 'x', min(xs), max(xs), 'y', min(ys), max(ys))
