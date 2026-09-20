<div dir="rtl">

# راهنمای نصب

> English: [SETUP.md](SETUP.md)

این ریپازیتوری هم **README پروفایل گیت‌هاب** شماست (`Parsa-Emami/Parsa-Emami`) و هم یک **وب‌سایت** هم‌طرح با آن
(الهام‌گرفته از [chanhdai.com](https://chanhdai.com)). همه‌چیز از **یک فایل** ساخته می‌شود: [`data/profile.json`](data/profile.json).

</div>

```
data/profile.json ──► scripts/build.py ──► README.md          (چیزی که در github.com/Parsa-Emami دیده می‌شود)
                                       ├─► assets/cards/*.svg  (کارت‌های روشن/تاریک README)
                                       └─► site/               (وب‌سایت استاتیک؛ قابل انتشار روی GitHub Pages)
```

<div dir="rtl">

README گیت‌هاب اجازه‌ی اجرای CSS و JavaScript نمی‌دهد؛ برای همین README از کارت‌های SVG ساخته شده که ظاهر سایت را تقلید می‌کنند،
و **وب‌سایت** نسخه‌ی کاملاً تعاملی است (جست‌وجوی ⌘K / Ctrl+K، تغییر تم، «Show more»، جمله‌های چرخان).

## ۱. انتشار (حدود ۵ دقیقه)

1. ریپازیتوری باید **Public** باشد و دقیقاً `Parsa-Emami` نام داشته باشد (هم‌نام یوزرنیم).
2. محتوای ریپو را با محتوای این پوشه جایگزین کنید و روی `main` پوش کنید:

</div>

```bash
git clone https://github.com/Parsa-Emami/Parsa-Emami.git
cd Parsa-Emami
# فایل‌های قدیمی را پاک کنید، فایل‌های جدید را کپی کنید، سپس:
git add -A && git commit -m "feat: chanhdai-style profile" && git push
```

<div dir="rtl">

3. **Settings ← Actions ← General ← Workflow permissions** را روی **Read and write permissions** بگذارید و Save کنید.
4. **Actions ← Update profile ← Run workflow** را بزنید. این Workflow هیت‌مپ فعالیت را به‌روز می‌کند، همه‌چیز را دوباره می‌سازد و نتیجه را کامیت می‌کند.
   از آن به بعد هر روز و هر بار که `data/profile.json` را عوض کنید خودکار اجرا می‌شود.

### اختیاری: وب‌سایت

**Settings ← Pages ← Build and deployment ← Source: GitHub Actions** و بعد **Actions ← Deploy site** را اجرا کنید.
سایت روی `https://parsa-emami.github.io/Parsa-Emami/` می‌آید (دکمه‌ی «Interactive site» در README به همین آدرس می‌رود؛
اگر آدرس دیگری دارید `site.url` را در `profile.json` عوض کنید).

## ۲. ویرایش محتوا

فایل `data/profile.json` را باز کنید، متن‌ها را عوض کنید و کامیت کنید؛ Workflow خودش README و سایت را دوباره می‌سازد.

| کلید | کنترل می‌کند |
| --- | --- |
| `person` | نام، عنوان، جمله‌های چرخان (`flip`)، مختصات «Fig. 1»، مکان. فیلدهای اختیاری `email` و `phone` و `pronouns` تا وقتی خالی‌اند نمایش داده نمی‌شوند |
| `overview` و `links` و `cta` | لیست آیکون‌دار، دکمه‌های شبکه‌های اجتماعی، جمله‌ی پایانی |
| `about` و `principles` و `focus` | بخش‌های متنی (با `[متن](آدرس)` لینک بسازید) |
| `stack` و `experience` و `education` و `projects` و `lab` و `research` | بخش‌های ساخت‌یافته |
| `awards` و `certifications` | به‌صورت پیش‌فرض خالی‌اند. مثلاً `{ "title": "...", "issuer": "...", "year": 2026, "url": "..." }` اضافه کنید تا بخشش ظاهر شود |
| `contributions` | اکانت‌هایی که هیت‌مپ از آن‌ها ساخته می‌شود (پایین‌تر توضیح داده شده) |

تاریخ‌ها به‌شکل `YYYY-MM` هستند؛ برای نقش فعلی `"end": null` بگذارید. مدت‌ها («1y 1m») خودکار محاسبه می‌شوند.

## ۳. عوض کردن عکس

</div>

```bash
pip install -r scripts/requirements-local.txt
python scripts/prep_avatar.py assets/source/source-photo.jpg --cx 1015 --cy 1215 --size 1500
python scripts/make_og.py        # اختیاری: تصویر پیش‌نمایش لینک (نیاز به playwright install chromium)
python scripts/build.py
```

<div dir="rtl">

مقدارهای `--cx/--cy/--size` برش مربعی هستند (مرکز و ضلع، بر حسب پیکسل عکس اصلی). حالت روشن نسخه‌ی طرح مدادی و حالت تاریک عکس اصلیِ رنگ‌تنظیم‌شده را می‌گیرد.

## ۴. پیش‌نمایش محلی

</div>

```bash
pip install -r scripts/requirements.txt
python scripts/build.py
python -m http.server -d site 8000     # http://localhost:8000
```

<div dir="rtl">

تست‌ها: `python -m unittest discover -s tests -v`

## ۵. چرا هیت‌مپ قبلی خالی بود؟

تقویم رسمی گیت‌هاب فقط کامیت‌هایی را می‌شمارد که ایمیلشان به همان اکانت وصل باشد. تقویم عمومی `Parsa-Emami` الان **۰ مشارکت** را نشان می‌دهد
(و `parsaemm` فقط ۱)، در حالی که کامیت‌های ریپوهایتان با اکانت `parsaemm` ثبت شده‌اند. برای همین اسکریپت `fetch_contributions.py` هر روز را از دو منبع
می‌سازد (مقدار **بزرگ‌تر** را برمی‌دارد، جمع نمی‌زند): تقویم اکانت‌های `contributions.accounts` **و** کامیت‌های ریپوهای عمومی خودتان، صرف‌نظر از نویسنده‌ی کامیت.
اگر فقط تقویم رسمی را می‌خواهید `"include_repo_commits": false` بگذارید.

برای اینکه خودِ گیت‌هاب هم کارهایتان را بشمارد: **Settings ← Emails** و ایمیلی را که در `git config user.email` دارید به اکانت اضافه کنید
(یا با آدرس `@users.noreply.github.com` کامیت کنید).

## ۶. ساختار

| مسیر | کاربرد |
| --- | --- |
| `README.md` | تولیدشده؛ دستی ویرایش نکنید |
| `data/profile.json` | **همه‌ی محتوا** |
| `data/contributions.json` | داده‌ی فعالیت (تولیدشده) |
| `assets/cards/` | کارت‌های SVG روشن/تاریک (تولیدشده) |
| `assets/avatar/` و `assets/source/` | نسخه‌های آواتار و عکس اصلی |
| `site/` | وب‌سایت تولیدشده (`assets/css` و `assets/js` دستی نوشته شده‌اند) |
| `scripts/` | خط لوله‌ی ساخت (`build.py` همه‌چیز را اجرا می‌کند) |
| `tests/` | تست‌های واحد جمع‌آوری فعالیت |
| `.github/workflows/` | `update-profile.yml` (بازسازی روزانه)، `pages.yml` (انتشار سایت) |

## عیب‌یابی

* **Workflow نمی‌تواند پوش کند** ← مرحله‌ی ۳ بالا (Workflow permissions).
* **Deploy site خطای «Pages not enabled» می‌دهد** ← Settings ← Pages ← Source: GitHub Actions.
* **README به‌روز نشد** ← گیت‌هاب تصاویر را چند دقیقه کش می‌کند؛ صفحه را Hard-refresh کنید.

</div>
