# 채권 모닝브리핑 · Report 작업 폴더



모든 작업: **`C:\Users\infomax\Documents\Report`**



## 배치 파일 (3개)



| 파일 | 하는 일 |

|------|---------|

| **`fetch_raw.bat`** | 텔레그램 9개 대화 → raw 추출 |

| **`make_pdf.bat`** | raw → CEO 보고용 PDF |

| **`run_all.bat`** | 위 두 개 한번에 |
| **`run_all_and_upload.bat`** | 위 + 대시보드 Report 페이지 업로드 |



```

fetch_raw.bat  →  raw\YYYYMMDD_telegram_raw.txt

make_pdf.bat   →  bond_morning_briefing_YYYYMMDD.pdf  (또는 Cursor prompt 열기)

run_all.bat    →  둘 다

```



## 매일 쓰는 방법



**방법 A — 나눠서 (지금처럼)**

1. `fetch_raw.bat` 더블클릭 → raw 저장

2. `make_pdf.bat` 더블클릭 → PDF 만들기 (또는 Cursor prompt 열림)



**방법 B — 한번에**

- `run_all.bat` 더블클릭

**방법 C — 한번에 + 대시보드 업로드**

- `run_all_and_upload.bat` 더블클릭  
  → PDF 생성 후 `market_db_dashboard/reports/` 로 복사·GitHub 푸시  
  → 대시보드 **Report** 탭에서 당일 PDF 확인



## make_pdf.bat 동작



- **API 키 있음** (`.env`에 GEMINI 등) → PDF 자동 생성

- **API 키 없음** → `telegram_prompt.md` 메모장 열림 → Cursor에 붙여넣고 PDF 요청



## 최초 1회 설정



```powershell

cd C:\Users\infomax\Documents\Report

pip install -r requirements.txt

```



`.env` — 텔레그램 로그인용:

- `TELEGRAM_PHONE` — +8210...

- `TELEGRAM_PASSWORD` — 2단계 인증 비밀번호



## 추출 대상 (9개)



`config.yaml` 참고: SK 채권영업팀 Yoon, 상상인증권 FICC, KB 채권, 관우 박, 키움 한지영, 충 박, MERITZ CMS, 쭈니방, 현지 김


