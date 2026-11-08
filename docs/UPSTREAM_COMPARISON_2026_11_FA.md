# ممیزی مقایسه و انتقال مستقیم اسکیل‌های آماده — ۲۰۲۶-۱۱-۰۹

## نتیجه تصمیم

**فایل‌های آماده بهتر را برای وظایف تخصصی نگه داریم؛ موتور اختصاصی را برای تصمیم نهایی و کنترل تجاری حفظ کنیم.** هیچ ابزار ارزیابی Hook نباید تصمیم نهایی فروش یا انتشار را جایگزین کند.

| بخش موجود | ابزار مرجع بررسی‌شده | نتیجه | دلیل |
|---|---|---|---|
| `scripts/campaign_decision.py` | S: `reels-script`; D: `instagram-organic` | **حفظ هسته اختصاصی** | ابزارهای خارجی مسیر کامل تصمیم با موجودی، ظرفیت تولید، Trial و تأیید انسان ندارند |
| `scripts/trial_review.py` | J: `ig-reel`, `ig-audit`; S: `reels-script` | **حفظ هسته اختصاصی** | رفرنس‌ها سناریونویسی/تحلیل محتوا دارند؛ این ابزار بر خط مبنای پیج، زمان و سیاست برند تصمیم می‌گیرد |
| `scripts/catalog_guard.py` | S: `brand-profile`; M: اسکیل‌های product marketing | **حفظ هسته اختصاصی** | کاتالوگ/موجودی/تأمین و اعتبار قیمت نیازمند کنترل عملیاتی جداگانه است |
| ریلز، Hook و زمان‌بندی | J: `hookscore.py`, `beats.py`, `hooks.json` | **کپی مستقیم مجاز، تست مستقل** | ابزارهای اجرایی و الگوهای کامل‌تری نسبت به صرفاً پرامپت ارائه می‌دهند |
| کپشن و کنترل کیفیت | J: `caption.py`; I: `ig-caption-writer` | **کپی مستقیم به‌عنوان مرجع/ابزار** | ابزار J هشتگ، CTA، لینک غیرقابل‌کلیک و طول را بررسی می‌کند؛ I فرمول‌های نوشتاری ارائه می‌دهد |
| رصد ریلز رقبا | J: `swipe.py` | **کپی مستقیم، نیازمند داده واردشده** | عملکرد ریلز را نسبت به میانه همان حساب می‌سنجد؛ خودکار داده جمع نمی‌کند |
| شناخت برند | S: `brand-profile` و الگوی پرونده | **کپی مرجع و توسعه اختصاصی** | مدل اولیه برند مناسب است، اما باید محدودیت تولید، موجودی، قیمت و اعتبار داده را اضافه کنیم |
| رشد ارگانیک | D: `instagram-organic` | **کپی مرجع، نه کپی قانون به هسته** | جریان ممیزی خوب است؛ هر عدد/وزن الگوریتم باید مستقل و تاریخ‌دار تأیید شود |
| سناریوی Instagram Reels | S: `reels-script` | **کپی مرجع، نه تصمیم‌گیرنده** | تولید محتوای بدون صدا، Cover و نماها را پوشش می‌دهد؛ بعضی ادعاهای وزن‌دهی غیرقابل‌تأیید است |

## انتقال‌های مستقیم (source-exact)

### J — Jakeschincariol/instagram-agent-skill
- `third_party/jake-instagram-agent-skill/LICENSE`
- `skills/ig-reel/{SKILL.md,hooks.json,hookscore.py,beats.py}`
- `skills/ig-caption/{SKILL.md,caption.py}`
- `skills/ig-viral/{SKILL.md,swipe.py}`
- GitHub: https://github.com/Jakeschincariol/instagram-agent-skill
- مجوز اصلی در همان پوشه نگهداری می‌شود؛ فایل‌های upstream دست‌نخورده‌اند.

### S — social-media-skills/skills
- `third_party/social-media-skills/LICENSE`
- `skills/brand-profile/SKILL.md`
- `skills/brand-profile/references/brand-profile-template.md`
- `skills/reels-script/SKILL.md`
- GitHub: https://github.com/social-media-skills/skills

### I — sergebulaev/instagram-skills
- `third_party/sergebulaev-instagram-skills/LICENSE`
- `skills/ig-caption-writer/SKILL.md`
- GitHub: https://github.com/sergebulaev/instagram-skills

### D — vidual-labs/digital-marketing-skills
- `third_party/vidual-digital-marketing-skills/LICENSE`
- `skills/marketing/instagram-organic/SKILL.md`
- GitHub: https://github.com/vidual-labs/digital-marketing-skills

**نکته:** بعضی `SKILL.md`‌های منبع به فایل‌های reference یا سایر Skillها ارجاع می‌دهند که هنوز منتقل نشده‌اند. پس وجودشان به معنی فعال بودن کامل آن مهارت نیست. ابزارهای Python انتقال‌یافته با تست مستقل بررسی می‌شوند.

## محدودیت‌های علمی، زبان و پلتفرم

- خود `hookscore.py` اذعان می‌کند در تمایز ریلز موفق و ناموفق یک سازنده تقریباً نزدیک به تصادفی است (AUC گزارش‌شده 0.56). این امتیاز **فقط ویرایش ساختاری** است، نه پیش‌بینی بازدید.
- `hookscore.py`, `beats.py`, `caption.py` و طبقه‌بندی Hook در `swipe.py` به واژگان و regex انگلیسی متکی هستند. **برای فارسی هنوز تأیید نشده‌اند**؛ امتیاز آن‌ها نباید به‌عنوان ارزیابی معتبر متن فارسی نمایش داده شود.
- ادعای وزن «۳ تا ۵ برابر» برای Sends نسبت به Likes در `S: reels-script` را به‌عنوان واقعیت رسمی قبول نمی‌کنیم؛ وزن دقیق الگوریتم عمومی نیست.
- زمان ثابت ۳ ثانیه، طول ریلز، و تعداد/سقف هشتگ در فایل‌های شخص ثالث باید هنگام توصیه با منابع رسمی و تاریخ بررسی شوند؛ توصیه‌های تاریخی ممکن است تغییر کرده باشند.
- متن‌های منبعی که به یک ابزار انتشار وابسته‌اند اجازه انتشار خودکار بدون رضایت مشخص کاربر را نمی‌دهند.
- اسکیل‌های ثالث فقط در `third_party` هستند؛ موتور اصلی با قواعد سختگیرانه‌تر حریم خصوصی، کنترل تجاری و تأیید انسان کار می‌کند.

## اولویت‌های مرحله بعد

1. تکمیل فایل‌های وابسته `brand-profile`، `reels-script` و `ig-caption-writer` با بازبینی مجوز.
2. ساخت **آداپتور فارسی** برای Hook، تقسیم واژگان و تخمین زمان گفتار؛ همراه داده آزمون فارسی و در صورت نیاز کالیبراسیون با صوت واقعی.
3. اتصال خروجی ابزارهای J به یک `creative_quality_report` مستقل؛ خروجی صرفاً توصیه و رفع اشکال است.
4. اضافه‌کردن مدل اولیه برند با موجودی، محدودیت تولید و ورودی Insights؛ بدون داده واقعی خروجی ساختگی ندهیم.
5. ممیزی ابزارهای دیگر از M و A با هدف یافتن ماژول‌های اجرایی واقعاً بهتر، نه کپی حجیم توضیحات.
6. تکمیل انتقال بسته ۰.۴ قدیمی و مقایسه تست‌های آن با نسخه GitHub.
