# قالب پروژه کارشناسی دانشگاه بناب

این پوشه شامل قالب XeLaTeX، متن نمونه پروژه، لوگوی دانشگاه و دفترچه راهنمای فارسی است.

## شروع سریع

### Overleaf

1. فایل ZIP را با **New Project → Upload Project** بارگذاری کنید.
2. از **Menu → Compiler** گزینه **XeLaTeX** را انتخاب کنید.
3. فایل اصلی را `main.tex` قرار دهید.
4. گزینه **Recompile from scratch** را اجرا کنید.

### ویندوز

پس از نصب TeX Live یا MiKTeX، روی فایل زیر دوبار کلیک کنید:

```text
build.bat
```

### لینوکس و macOS

```bash
chmod +x build.sh
./build.sh
```

یا در همه سیستم‌ها:

```bash
latexmk -C
latexmk -xelatex main.tex
```

فقط یک بار اجرای XeLaTeX کافی نیست؛ فهرست‌ها، منابع و ارجاع‌ها به Biber و چند اجرای XeLaTeX نیاز دارند. اسکریپت‌های همراه، همه مراحل را خودکار انجام می‌دهند.

## فایل‌هایی که معمولاً ویرایش می‌شوند

```text
config/metadata.tex       اطلاعات دانشجو، عنوان، استاد و کلیدهای اختیاری
chapters/chapter1.tex     فصل اول
chapters/chapter2.tex     فصل دوم
chapters/chapter3.tex     فصل سوم
chapters/chapter4.tex     فصل چهارم
chapters/chapter5.tex     فصل پنجم
frontmatter/abstract-fa.tex
frontmatter/abstract-en.tex
references.bib            منابع
```

برای تغییر فونت‌ها فقط `config/fonts.tex` و برای تغییر صفحه‌آرایی فقط `config/style.tex` را ویرایش کنید.

## دفترچه راهنما

- نسخه آماده مطالعه: `USER-GUIDE.pdf`
- متن قابل‌جست‌وجو: `docs/USER-GUIDE.md`
- سورس LaTeX راهنما: `manual/guide.tex`
- جدول تطبیق با دستورالعمل دانشگاه: `docs/COMPLIANCE.md`
- گزارش آزمون فنی: `VALIDATION.md`

## نکات ضروری

- موتور کامپایل باید **XeLaTeX** باشد.
- برای ارجاع در متن فارسی از `\pcite{key}` استفاده کنید.
- عبارت لاتین در پاراگراف فارسی را داخل `\lr{...}` بنویسید.
- نتایج عددی نمونه در قالب قرار نگرفته‌اند؛ فقط نتایج واقعی پروژه را اضافه کنید.
- قلم B Mitra فقط برای متن است و برای نمادهای ریاضی استفاده نمی‌شود.
