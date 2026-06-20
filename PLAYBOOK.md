# Playbook — פרסום סושיאל אוטומטי (Composio → Facebook + Instagram)

תהליך מלא לפרסום פוסט לפייסבוק + קרוסלה לאינסטגרם לאתרי הטיולים, דרך Composio MCP.
נכתב אחרי הפרסום הראשון: **אירועי גאורגיה יולי–אוגוסט 2026** (20.6.2026).

> 🔒 **אבטחה:** הריפו הזה ציבורי. אין לשמור כאן מפתחות/טוקנים. כל הסודות נמצאים מקומית
> ב-`d:\CLAUDE\.mcp.json` ובזיכרון הפרטי של Claude.

---

## 1. תשתית — Composio MCP

- מוגדר ב-`d:\CLAUDE\.mcp.json` בשם `composio`:
  - `type: http`, `url: https://connect.composio.dev/mcp`
  - אימות: `Authorization: Bearer <ck_...>` ← **מפתח שמתחיל ב-`ck_`** (לא `ak_` — הוא נדחה).
- דפוס Tool Router (לא כלים סטטיים). הזרימה תמיד:
  1. `COMPOSIO_SEARCH_TOOLS` — לגלות כלים + תוכנית מומלצת
  2. `COMPOSIO_GET_TOOL_SCHEMAS` — לקבל סכמת פרמטרים מדויקת
  3. `COMPOSIO_MULTI_EXECUTE_TOOL` — להריץ (אפשר כמה כלים במקביל אם הם עצמאיים)
  4. `COMPOSIO_MANAGE_CONNECTIONS` — לחבר/לבדוק חשבונות (action: list/add/remove)

---

## 2. חשבונות מחוברים (נכון ל-20.6.2026)

| פלטפורמה | חשבון | מזהה |
|---|---|---|
| Facebook | פרופיל Michael Benor | `10163901206687702` |
| FB Page | יפן שלנו למטיילים | `937994292731264` |
| FB Page | ארמניה שלנו למטיילים | `943092128888857` |
| FB Page | גאורגיה שלנו למטיילים | `947115751809312` |
| Instagram | georgia.travel.il (default) | ig_user_id `26974287245601419`, alias `instagram_dail-jumble` |

> יש עוד 4 חשבונות IG תקועים ב-"initializing" — לא שמישים עד שיושלם החיבור.

---

## 3. אחסון תמונות — GitHub raw (קריטי לאינסטגרם)

אינסטגרם דורש **URL ציבורי ישיר ל-JPEG**. PNG וקישורי Google Drive נכשלים.

- ריפו ציבורי: **`b-mish/social-assets`**
- מבנה: `<יעד>/<קמפיין>/slideN.jpg` (למשל `georgia/2026-07-events/`)
- URL לשימוש: `https://raw.githubusercontent.com/b-mish/social-assets/main/<path>/slideN.jpg`
- אימות שעובד: `curl -sI <url>` → צריך `HTTP 200` + `content-type: image/jpeg`

**דרישות תמונה של אינסטגרם:** JPEG · יחס 0.8–1.91 (1:1 מושלם) · רוחב 320–1440px · עד 8MB.

---

## 4. ייצור שקופיות עם טקסט עברי מדויק (HTML → screenshot)

לא משתמשים ב-AI image-gen לטקסט (שובר עברית/RTL). במקום זה:

1. תמונת רקע מ-**Pexels API** (מפתח שמור מקומית). מורידים `src.large2x`.
2. `gen.py` בונה קובץ HTML לכל שקופית: תמונת רקע (`object-fit:cover`) + שכבת טקסט
   RTL בפונט **Rubik** (Google Fonts) + שכבת הצללה לקריאוּת + מיתוג `georgia-travel.co.il`.
3. צילום מסך עם Chrome headless ל-1080×1080:
   ```bash
   CHROME="/c/Program Files/Google/Chrome/Application/chrome.exe"
   "$CHROME" --headless=new --disable-gpu --hide-scrollbars --no-sandbox \
     --force-device-scale-factor=1 --window-size=1080,1080 \
     --virtual-time-budget=5000 \
     --screenshot="D:/path/slide1.png" "file:///D:/path/slide1.html"
   ```
   ⚠️ **לתת ל-Chrome נתיב Windows** (`D:/...`) ולא נתיב MSYS (`/d/...`) — אחרת `ERR_FILE_NOT_FOUND`.
4. המרה ל-JPEG (Pillow): `Image.open(png).convert("RGB").save(jpg,"JPEG",quality=90)`.

קבצים: `gen.py` + `img/` בתיקייה המקומית `d:\CLAUDE\social-georgia-2026`.

---

## 5. כללי תוכן (מסקיל `social`)

- **לינק לא בגוף הפוסט** — האלגוריתם של מטא מדכא פוסטים עם לינק יוצא.
  - פייסבוק: לינק ב**תגובה הראשונה**.
  - אינסטגרם: לינקים לא לחיצים ב-caption → "**לינק בביו**".
- **Hook בשורה הראשונה** + **CTA לשמירה/תיוג** (שמירות = אות חזק באינסטגרם).
- האשטגים ממוקדים (לא 30). פייסבוק — 1–3 בלבד.
- **בלי סימני AI** (סקיל `stop-slop`): בלי קו מפריד ארוך (—), בלי קלישאות
  ("שאסור לפספס", "נופים אינסופיים"), אימוג'ים במידה. עברית מדויקת — לבדוק כתיב,
  בלי אותיות לטיניות בתוך מילה עברית (טעות שקרתה: "טושֶטoba" → "טושטובה").

---

## 6. שלבי הפרסום (סלאגים מדויקים)

**פייסבוק:**
1. `FACEBOOK_CREATE_PHOTO_POST` — `{ page_id, url (raw jpg), message }` → מחזיר `post_id` מורכב `pageId_postId`.
2. `FACEBOOK_CREATE_COMMENT` — `{ object_id: <post_id המורכב>, message: "... 👉 https://georgia-travel.co.il" }`.

**אינסטגרם (קרוסלה):**
1. `INSTAGRAM_CREATE_CAROUSEL_CONTAINER` — `{ ig_user_id, child_image_urls: [5 raw jpg], caption }` → `creation_id`.
   (אפשר גם ליצור קונטיינר נפרד לכל תמונה, אבל `child_image_urls` חוסך שלב.)
2. `INSTAGRAM_POST_IG_USER_MEDIA_PUBLISH` — `{ ig_user_id, creation_id, max_wait_seconds: 90 }`.
- ב-`COMPOSIO_MULTI_EXECUTE_TOOL` להעביר `account: "instagram_dail-jumble"` כדי לכוון לחשבון הנכון.
- קונטיינר קרוסלה תקף פחות מ-24 שעות — לפרסם מיד.

> ⚠️ תגובות Composio מדליפות **page access tokens** — לא להציג ולא לשמור אותם.

---

## 7. צ'קליסט לפרסום הבא

- [ ] לאמת תוכן/תאריכים (חיפוש אם צריך)
- [ ] לכתוב קופי (FB + IG) לפי כללי §5
- [ ] להוריד תמונות Pexels → `gen.py` → screenshot → JPG
- [ ] לדחוף JPG ל-`b-mish/social-assets` ולוודא 200 + image/jpeg
- [ ] `FACEBOOK_LIST_MANAGED_PAGES` לאמת page_id
- [ ] לפרסם FB (פוסט + תגובת לינק)
- [ ] לפרסם IG (קונטיינר → publish)
- [ ] לוודא בלייב + להוסיף תובנות חדשות ל-playbook הזה

---

## 8. היסטוריית פרסומים

| תאריך | יעד | תוכן | נכסים |
|---|---|---|---|
| 2026-06-20 | FB גאורגיה + IG georgia.travel.il | 3 אירועי קיץ בגאורגיה (ג'אז בטומי, ארט-ג'ין, טושטובה) | `georgia/2026-07-events/slide1-5.jpg` |
