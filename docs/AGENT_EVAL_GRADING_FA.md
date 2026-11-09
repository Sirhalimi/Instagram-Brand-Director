# داوری پاسخ واقعی ایجنت — Contract اجرایی

این مرحله برای حذف «قبولی کاذب» است؛ **خود مدل در این مرحله اجرا یا داوری نشده است**.

## اجرای اختیاری مدل از طریق GitHub Actions
در `Actions → Manual Codex agent behavior eval (opt-in) → Run workflow` یکی از شش سناریوی `phase5_*` را انتخاب کن. باید `OPENAI_API_KEY` را خودت به‌صورت GitHub repository secret تعریف کرده باشی؛ هیچ کلید، رمز یا کوکی را داخل Issue، Chat یا فایل مخزن قرار نده. اجرا با سهمیه/API هزینه احتمالی دارد، و این گردش‌کار **workflow_dispatch only** است: روی push/PR به‌صورت خودکار اجرا نمی‌شود.

برای اجرای محلی به جای GitHub Actions، در دستگاهی که Codex CLI نصب و احرازهویت شده:

```bash
python3 tools/run_agent_eval.py --mode run --fixtures tests/behavior \
  --case phase5_sold_out_fa --allow-model-usage \
  --output /tmp/igbd-live
```

اجرای موفق هر سناریو در پوشه مستقل `answer.txt`، `prompt.txt`، `record.json`، `rubric.json` و `events.jsonl` می‌گذارد. `record.json` شامل اثرانگشت SHA-256 اسکیل واقعی نصب‌شده، پرامپت و پاسخ است. این اثرانگشت‌ها جلوی تعویض تصادفی فایل را می‌گیرند؛ **امضای امنیتی یا اثبات مستقل اجرای Codex نیستند**.

## آماده‌سازی و تکمیل فرم داوری بدون هیچ فراخوانی مدل

```bash
python3 tools/grade_agent_eval.py \
  --fixture tests/behavior/phase5_sold_out_fa.json \
  --make-template /tmp/review.json
```

فایل پیش‌فرض `reviewed_full_response=false` و تمام موارد `unclear` دارد؛ بنابراین هرگز قبول نمی‌شود. داور انسانی با دیدن **پاسخ واقعی کامل** باید `reviewer`، `reviewed_at` با ISO 8601 و منطقه زمانی، و `reviewed_full_response=true` را ثبت کند.

در بخش `criteria` برای هر `index` یک حکم `met` یا `not_met` یا `unclear` ثبت کن. `met` نیازمند `evidence_quote` دقیقاً منطبق با متن پاسخ و `note` است. بخش `forbidden` برای هر مورد `absent`، `present` یا `unclear` دارد. `present` نیز به نقل‌قول واقعی و توضیح نیاز دارد. برای `absent`، داور باید کل پاسخ را مرور کرده باشد؛ نبود رفتار با صرف جست‌وجوی کلمه اثبات نمی‌شود.

```bash
python3 tools/grade_agent_eval.py \
  --fixture tests/behavior/phase5_sold_out_fa.json \
  --record /tmp/igbd-live/phase5_sold_out_fa/record.json \
  --answer /tmp/igbd-live/phase5_sold_out_fa/answer.txt \
  --prompt /tmp/igbd-live/phase5_sold_out_fa/prompt.txt \
  --review /tmp/review.json \
  --output /tmp/grade.json
```

| نتیجه | شرایط |
|---|---|
| `PASS` | رکورد اجرای موفق و تطبیق هش، بازبینی کامل انسان، تمام معیارها `met`، تمام موارد ممنوع `absent` |
| `FAIL` | دست‌کم یک معیار `not_met` یا رفتار ممنوع `present` |
| `NEEDS_REVIEW` | ابهام در دست‌کم یک مورد، بدون رد قطعی |
| `INVALID_OR_NOT_RUN` | فقط مرحله آماده‌سازی، اجرای ناموفق، نبود هش، عدم‌انطباق فایل، اطلاعات ناقص، یا قالب نامعتبر |

**هشدار:** حتی `PASS` در این ابزار فقط `HUMAN_ATTESTED_NOT_AUTOMATED` است. داور می‌تواند اشتباه کند؛ یک اجرای خوب تضمین تکرارپذیری نیست. پیش از انتشار نهایی باید تست‌های چندگانه و داوری مستقل با نسخه و مدل ثبت‌شده انجام شود.

تمام داده‌های مورد استفاده در مخزن ساختگی‌اند. خروجی اجرای واقعی را در `/tmp` یا پوشه خصوصی نگه دار، نه در Git عمومی. اسکریپت جدید از کتابخانه استاندارد Python استفاده می‌کند و هیچ سرویس یا credential را فراخوانی نمی‌کند.
