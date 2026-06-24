import os
from pypdf import PdfReader

folder = r"C:\Users\infomax\Documents\카카오톡 받은 파일\6월 FOMC Review 리포트"
out_dir = r"C:\Users\infomax\Documents\Cursor\scripts\fomc_extracted"
os.makedirs(out_dir, exist_ok=True)

for f in sorted(os.listdir(folder)):
    if not f.endswith(".pdf"):
        continue
    path = os.path.join(folder, f)
    reader = PdfReader(path)
    parts = []
    for i, page in enumerate(reader.pages):
        parts.append(f"--- Page {i+1} ---\n{page.extract_text() or ''}")
    text = "\n".join(parts)
    safe_name = f.replace(".pdf", ".txt")
    out_path = os.path.join(out_dir, safe_name)
    with open(out_path, "w", encoding="utf-8") as fp:
        fp.write(text)
    print(f"Wrote {safe_name} ({len(reader.pages)} pages, {len(text)} chars)")
