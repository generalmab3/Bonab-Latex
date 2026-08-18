# دفترچه راهنمای قالب پروژه کارشناسی دانشگاه بناب

## ۱. هدف قالب

این قالب برای گزارش پروژه کارشناسی رشته علوم کامپیوتر تنظیم شده و از دستورالعمل ارسالی دانشگاه بناب برای صفحه‌آرایی، ترتیب صفحات، شماره‌گذاری، شکل‌ها، جدول‌ها، روابط و بخش انگلیسی پیروی می‌کند. چون دستورالعمل اصلی برای تحصیلات تکمیلی نوشته شده است، فرم‌های اداری مخصوص دفاع کارشناسی ارشد و دکتری در خروجی پیش‌فرض پروژه کارشناسی قرار نگرفته‌اند.

## ۲. اجرای صحیح

### Overleaf

1. ZIP پروژه را بارگذاری کنید.
2. Compiler را روی XeLaTeX قرار دهید.
3. Main document را `main.tex` انتخاب کنید.
4. از Recompile from scratch استفاده کنید.

### اجرای محلی

در ویندوز `build.bat` و در لینوکس یا macOS فایل `build.sh` را اجرا کنید. این اسکریپت‌ها به‌ترتیب XeLaTeX، Biber و دو بار XeLaTeX را اجرا می‌کنند.

روش جایگزین:

```bash
latexmk -C
latexmk -xelatex main.tex
```

اگر فقط یک بار XeLaTeX اجرا شود، فهرست‌ها خالی، منابع ناقص و ارجاع‌ها `؟؟` خواهند بود.

## ۳. ساختار پوشه

| مسیر | کاربرد |
|---|---|
| `main.tex` | ترتیب اجزای سند؛ معمولاً نیاز به تغییر ندارد |
| `config/metadata.tex` | همه مشخصات پروژه و کلیدهای فعال/غیرفعال |
| `config/fonts.tex` | انتخاب قلم‌های رسمی و جایگزین |
| `config/style.tex` | حاشیه، فاصله، عنوان‌ها و شماره‌گذاری |
| `config/packages.tex` | بسته‌های LaTeX |
| `frontmatter/` | صفحات آغازین و انگلیسی |
| `chapters/` | متن فصل‌ها |
| `appendices/` | پیوست‌های اختیاری |
| `assets/` | لوگو و تصاویر |
| `references.bib` | اطلاعات کتاب‌شناختی منابع |

## ۴. تغییر مشخصات

فقط متن داخل آکولادها را در `config/metadata.tex` تغییر دهید:

```latex
\newcommand{\ProjectTitleFa}{عنوان فارسی}
\newcommand{\ProjectTitleEn}{English Title}
\newcommand{\StudentNameFa}{نام دانشجو}
\newcommand{\StudentNumber}{شماره دانشجویی}
\newcommand{\SupervisorNameFa}{نام استاد}
```

نام فرمان‌ها و آکولادها را حذف نکنید.

## ۵. بخش‌های اختیاری

در انتهای `config/metadata.tex` مقدار `true` یا `false` را تغییر دهید:

```latex
\IncludeDedicationtrue
\IncludeAcknowledgementstrue
\IncludeSymbolstrue
\IncludeListOfFigurestrue
\IncludeListOfTablestrue
\IncludeListOfListingstrue
\IncludeAppendixfalse
\IncludeEnglishPagestrue
```

اگر یک فهرست هیچ مدخلی ندارد، کلید آن را `false` کنید تا صفحه خالی تولید نشود.

## ۶. افزودن فصل

فایل جدیدی مانند `chapters/chapter6.tex` بسازید:

```latex
\chapter{عنوان فصل}
\label{chap:new}

\section{عنوان بخش}
متن بخش.
```

سپس در `main.tex` اضافه کنید:

```latex
\include{chapters/chapter6}
```

## ۷. فارسی و انگلیسی در یک سطر

فونت‌های قدیمی B Mitra و B Titr همه حروف لاتین را ندارند. بنابراین اصطلاح لاتین در متن فارسی باید جهت و قلم مستقل داشته باشد:

```latex
شبکه عصبی \lr{PINN} با کتابخانه \lr{PyTorch} پیاده‌سازی شد.
```

یک پاراگراف کاملاً انگلیسی را داخل محیط `latin` قرار دهید:

```latex
\begin{latin}
This paragraph is written in English.
\end{latin}
```

## ۸. منابع و ارجاع

منبع را در `references.bib` ثبت کنید. در متن فارسی از فرمان زیر استفاده کنید:

```latex
\pcite{raissi2019pinns}
```

فرمان `\pcite` شماره و براکت ارجاع را با قلم لاتین کامل می‌سازد تا B Mitra مربع تولید نکند. در متن کاملاً انگلیسی می‌توان از `\cite` استفاده کرد.

نمونه BibTeX:

```bibtex
@article{key,
  author  = {First Author and Second Author},
  title   = {Article Title},
  journal = {Journal Name},
  year    = {2026}
}
```

## ۹. شکل

تصویر را در `assets` قرار دهید:

```latex
\begin{figure}[H]
  \centering
  \includegraphics[width=0.75\textwidth]{figure-name.pdf}
  \caption{عنوان فارسی شکل}
  \label{fig:sample}
\end{figure}
```

ارجاع:

```latex
شکل~\ref{fig:sample}
```

عنوان شکل پایین آن قرار می‌گیرد و شماره به‌صورت فصل-شماره ساخته می‌شود.

## ۱۰. جدول

```latex
\begin{table}[H]
  \centering
  \caption{عنوان فارسی جدول}
  \label{tab:sample}
  \begin{tabular}{lc}
    \toprule
    روش & خطا \\
    \midrule
    روش پیشنهادی & 0.01 \\
    \bottomrule
  \end{tabular}
\end{table}
```

عنوان جدول باید بالای آن باشد.

## ۱۱. رابطه ریاضی

```latex
\begin{equation}
  E = mc^2
  \label{eq:energy}
\end{equation}
```

ارجاع:

```latex
رابطه~\eqref{eq:energy}
```

قالب رابطه را از حاشیه چپ و شماره را در سمت راست قرار می‌دهد.

## ۱۲. کد برنامه‌نویسی

```latex
\begin{latin}
\begin{lstlisting}[caption={\protect\lr{Python example}},label={lst:python}]
print("Hello")
\end{lstlisting}
\end{latin}
```

عنوان انگلیسی باید با `\lr` محافظت شود تا در فهرست کدها وارونه نشود.

## ۱۳. قلم‌ها

ترتیب انتخاب در `config/fonts.tex`:

- متن فارسی: B Mitra، سپس Amiri، سپس FreeSerif
- عنوان بخش: B Nazanin، سپس Amiri
- عنوان فصل: B Titr، سپس Amiri
- انگلیسی: Times New Roman، سپس TeX Gyre Termes
- اعداد و نمادهای ریاضی: Amiri یا قلم کامل جایگزین

B Mitra نباید `digitfont` باشد، زیرا بعضی نمادهای موردنیاز `unicode-persianmath` را ندارد.

## ۱۴. قواعد اصلی اعمال‌شده

- کاغذ A4
- حاشیه ۲٫۵ سانتی‌متر از چهار طرف
- متن ۱۴ پوینت و فاصله خط ۱٫۵
- تورفتگی پاراگراف ۱٫۲۵ سانتی‌متر
- عنوان فصل ۱۶ پوینت، پررنگ و وسط‌چین
- عنوان بخش ۱۴ پوینت، پررنگ و مایل
- عنوان شکل و جدول ۱۰ پوینت
- شماره صفحه وسط پایین با فاصله استاندارد
- صفحات مقدماتی با حروف فارسی
- متن اصلی از صفحه ۱
- عنوان جدول بالا و عنوان شکل پایین
- شماره‌گذاری فصل‌محور با خط تیره
- چکیده فارسی و انگلیسی و ۵ تا ۱۰ کلیدواژه

رنگ جلد، صحافی و صفحه سفید پس از جلد از الزامات نسخه چاپی‌اند و باید هنگام تحویل فیزیکی با آموزش دانشکده هماهنگ شوند.

## ۱۵. خطاهای رایج

### `unicode-persianmath` و `B Mitra`

نسخه قدیمی قالب یا فایل کمکی قدیمی استفاده شده است. پروژه جدید را در پوشه تازه باز کنید و از `config/fonts.tex` جدید استفاده کنید.

### مربع به‌جای واژه انگلیسی

عبارت لاتین خارج از `\lr` نوشته شده یا عنوان انگلیسی با فونت فارسی ساخته شده است.

### مربع به‌جای ارجاع منبع

Biber اجرا نشده یا از `\cite` در متن فارسی استفاده شده است. از `\pcite` و اسکریپت build استفاده کنید.

### فهرست خالی یا `؟؟`

کامپایل چندمرحله‌ای کامل نشده است. `latexmk -C` و سپس `latexmk -xelatex main.tex` اجرا شود.

### فونت پیدا نمی‌شود

TeX Live کامل نصب شود یا فونت‌های رسمی به‌صورت قانونی نصب شوند. قالب در نبود فونت رسمی باید به قلم آزاد برگردد.

## ۱۶. کنترل نهایی پیش از تحویل

- هیچ `؟؟`، مربع یا کلید خام منبع در PDF نباشد.
- فهرست‌ها و شماره صفحات به‌روز باشند.
- همه شکل‌ها و جدول‌ها در متن ارجاع داده شده باشند.
- اعداد و نتایج واقعی باشند.
- چکیده فارسی و انگلیسی هم‌معنا باشند.
- فایل PDF با XeLaTeX و Biber از ابتدا بازسازی شده باشد.
- نسخه چاپی از نظر رنگ جلد و فرم‌های اداری با گروه آموزشی کنترل شود.
