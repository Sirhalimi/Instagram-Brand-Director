# موتور تصمیم کمپین — Campaign Decision

نسخه اولیه اجرایی، مستقل و آفلاین است و به اینستاگرام یا فروشگاه متصل نیست. این موتور از اطلاعاتی که واقعاً در فایل ورودی وجود دارد استفاده می‌کند.

## اجرای نمونه

```bash
python3 -m scripts.campaign_decision examples/campaign-brief.sample.json
python3 -m unittest discover -s tests -v
```

## جریان تصمیم

1. هدف کمپین را بررسی می‌کند: `discovery`، `community`، `education` یا `conversion`.
2. حقوق محتوا و صحت ادعاها را کنترل می‌کند؛ اگر تأیید نشده، `HOLD_CREATIVE`.
3. محدودیت تولید را ارزیابی می‌کند و در صورت ممنوعیت حضور جلوی دوربین، پیشنهاد `REWORK_FACELESS` می‌دهد.
4. برای کمپین فروش، با `catalog_guard.py` موجودی، قیمت، تاریخ اعتبار داده، تأمین، تحویل و حاشیه سود را بررسی می‌کند.
5. اجرای تبلیغات پولی به‌صورت پیش‌فرض غیرفعال است.
6. فرمت محتوای قابل تولید را انتخاب می‌کند.
7. در صورت هدف کشف مخاطب جدید، تازگی ایده، نبود فوریت زمانی و فعال بودن قابلیت Trial در همان اکانت، `TRIAL_REEL` را انتخاب می‌کند؛ در غیر این صورت یک تصمیم دیگر می‌دهد.
8. هر تصمیم همراه دلیل، اقدام بعدی و الزام تأیید انسانی ارائه می‌شود.

## خروجی و محدودیت

این موتور کد محتوا تولید نمی‌کند و انتشار، خرج بودجه، اتصال حساب یا پیش‌بینی دقیق بازدید انجام نمی‌دهد. معیار Trial یک سیاست تصمیم‌گیری داخلی است، نه قانون پنهان اینستاگرام. باید اطلاعات واقعی برند و Insights جایگزین مثال‌ها شود. تمام داده‌های خصوصی برند خارج از مخزن عمومی نگهداری شوند.

## توسعه بعدی

- امتیازدهی و اولویت‌بندی چند ایده و چند محصول قابل‌عرضه
- دریافت داده تازه از فروشگاه با adapter
- تطبیق آمار تاریخی محتوا
- اتصال خروجی تصمیم به برنامه زمان‌بندی و گردش‌کار تأیید
- ثبت تاریخچه تصمیم و نتیجه واقعی


## Phase 4 — New source_content and availability types
- For each asset in `source_content`, specify `origin` (owned/licensed/permission/third_party), `has_visible_watermark` and `documented_permission` as actual booleans. `usage="research"` never authorizes publication.
- `subtitles_only_repost=true` blocks a publishable asset even with documented permission: translating on top of somebody else's clip does not make new original production.
- The rights result is attached under `source_content_review`. `HOLD_CREATIVE` is distinct from `DO_NOT_PROMOTE`: one blocks the media, the other a commercial offer. An unavailable item is rejected immediately.
- `availability_type`: physical_stock (legacy), digital_product, cohort_seats, consult_slots. Full field contracts and CLI examples: [CONTENT_RIGHTS_AND_AVAILABILITY.md](CONTENT_RIGHTS_AND_AVAILABILITY.md).
- All results are offline, owner-provided evidence; no Meta/source API, license registry, slot booking or sales execution.
