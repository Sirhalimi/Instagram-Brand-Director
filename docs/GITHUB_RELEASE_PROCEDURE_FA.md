# روش انتقال کامل نسخه ۰.۴ به GitHub

## وضعیت فعلی
مخزن GitHub ایجاد شده و هسته و مستندات اولیه منتشر شده‌اند. بسته محلی نسخه ۰.۴ حاوی ۷۸ فایل (از جمله تست‌ها) است، اما تا زمان انتقال، این ۷۸ فایل در GitHub موجود نیستند. گردش‌کار CI در این مخزن پس از انتقال تست‌ها را اجرا خواهد کرد.

## انتقال بسته محلی
فایل `instagram-brand-director-v0.4.zip` را در سیستم خود ذخیره کن. Git و Python 3 لازم است.

```bash
git clone https://github.com/Sirhalimi/Instagram-Brand-Director.git
cd Instagram-Brand-Director
python3 tools/import_local_release.py /path/to/instagram-brand-director-v0.4.zip
python3 -m unittest discover -s tests -v
git status
git diff --stat
git diff --check
git add -A
git commit -m "feat: import complete v0.4 release"
git push origin main
```

پیش از `git add` و `git push`، فایل‌ها را برای اطلاعات شخصی، کلید API، توکن، داده مشتری یا اطلاعات واقعی خصوصی برند بررسی کن. اسکریپت فایل‌های کلیدی حساس و پوشه‌های شخصی را حذف می‌کند، اما جایگزین بررسی امنیتی نیست. از `git add -A` فقط پس از بررسی تغییرات استفاده کن.

## راستی‌آزمایی
- شاخه `main` باید پوشه‌های `scripts`، `tests`، `templates`، `modules`، `references` و `docs` را داشته باشد.
- اجرای `python3 -m unittest discover -s tests -v` باید موفق باشد.
- در GitHub Actions، workflow به نام `Skill checks` باید سبز شود.
- قابلیت‌های وابسته به OAuth، Meta API، انتشار و همگام‌سازی فروشگاه تا زمان توسعه و تست واقعی، فعال معرفی نشوند.
