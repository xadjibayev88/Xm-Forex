# XM hamkor to'plami: o'rnatish yo'riqnomasi (GitHub orqali)

Bu to'plam GitHub'ning o'zida ishlaydi:

- **Sayt** (GitHub Pages): forex asoslari bo'yicha ta'limiy sahifa, hamkorlik havolangiz bilan.
- **Telegram avtopost** (GitHub Actions): har kuni 11:00 (Toshkent) kanalingizga navbatdagi post ketadi.
- **20 ta tayyor post** (`content/posts.json`) va **30 kunlik reja** (`content/content-plan.md`).

> Bu to'plam sizning nomingizdan hech qaerga kirmaydi. Hamma narsa faqat sizning o'z Telegram botingiz va o'z GitHub repozitoriyangiz ichida ishlaydi.

## O'rnatish (taxminan 15 daqiqa)

### 1. Repo yarating
GitHub'da yangi repo oching (masalan `forex-uz`) va shu papkadagi hamma fayllarni yuklang. Bepul tarifda GitHub Pages uchun repo **Public** bo'lishi kerak.

### 2. Telegram bot va kanal
1. Telegram'da `@BotFather` ga yozing, `/newbot` buyrug'i bilan bot yarating va **token**ni oling.
2. O'zingizning yangi kanalingizni oching (bolalar multfilm kanalidan alohida bo'lsin).
3. Botni kanalga **administrator** qiling (xabar yuborish ruxsati bilan).
4. Kanal ochiq bo'lsa, chat ID = `@kanal_nomi`.

### 3. GitHub sozlamalari
Repo: **Settings → Secrets and variables → Actions**

**Secret** (yashirin) — faqat bitta:

| Nom | Qiymat |
|---|---|
| `TELEGRAM_BOT_TOKEN` | BotFather bergan token |

Qolgan sozlamalar (hamkorlik havolasi, kanal manzili, birinchi post sanasi) repo ichidagi `config.json` faylida turadi; ularni shu fayldan o'zgartirasiz. Xohlasangiz, `AFFILIATE_LINK`, `TELEGRAM_URL`, `TELEGRAM_CHAT_ID`, `START_DATE` nomli Secret/Variable yaratib, `config.json` qiymatlarini bekor qilishingiz ham mumkin.

Tokenni hech qachon faylga yozmang va hech kimga bermang.

### 4. Saytni yoqish
**Settings → Pages → Source: GitHub Actions**. Keyin **Actions → "Saytni joylash" → Run workflow**. Tayyor bo'lgach sayt manzili shu yerda ko'rinadi.

### 5. Telegram avtopostni sinash
**Actions → "Telegram kunlik post" → Run workflow**:
1. `dry_run = true` — yubormasdan postni ko'rsatadi.
2. `dry_run = false`, `post_index = 0` — haqiqiy yuboradi.

Shundan so'ng har kuni o'zi ishlaydi. Har postga xavf haqida ogohlantirish avtomatik qo'shiladi.

## Kunlik Reels (avtomatik video: Telegram + Instagram)

Workflow **"Kunlik Reels"** har kuni 13:00 (Toshkent) `content/reels.json` dagi navbatdagi mavzudan 9:16 video yaratadi (Pillow + ffmpeg), uni GitHub Pages'ga joylaydi va:

- **Telegram kanalga** tugma bilan yuboradi (`TELEGRAM_BOT_TOKEN` yetarli);
- **Instagram Reels**'ga joylaydi, agar quyidagi ikkita Secret kiritilgan bo'lsa. Kiritilmasa, Instagram qadami o'tkazib yuboriladi va xato bermaydi.

Video ovozsiz (musiqa yo'q). 10 ta mavzu aylanib turadi; yangi mavzu qo'shish uchun `content/reels.json` ga yozuv qo'shing.

### Instagram'ni ulash (bir marta, rasmiy Meta API)
1. Instagram akkauntingizni **Business** yoki **Creator** turiga o'tkazing va Facebook Page'ga bog'lang.
2. [developers.facebook.com](https://developers.facebook.com) da ilova yarating, **Instagram Graph API** ni qo'shing, `instagram_basic` va `instagram_content_publish` ruxsatlarini bering.
3. Uzoq muddatli **access token** va Instagram akkauntingizning raqamli **ID**sini oling (token taxminan 60 kun amal qiladi, keyin yangilash kerak).
4. Repo → Settings → Secrets and variables → Actions: `IG_ACCESS_TOKEN` va `IG_USER_ID` nomli Secret qo'shing.

Sinash: Actions → "Kunlik Reels" → Run workflow, `dry_run = true` (video yaratadi, joylamaydi).

## Nima avtomatlashtirilmagan (va nega)
- Boshqa kanallarga xabar yozish (o'zaro reklama), guruhlarda izoh qoldirish: ommaviy avtomatik yozish spam hisoblanadi va akkauntni bloklatadi.
- Telegram taklif havolalarini yaratish va kanal tavsifini o'zgartirish: buni kanal egasi o'zi qiladi (matnlar tayyor hujjatda).
- TikTok/YouTube Shorts: ularga joylash uchun alohida akkaunt va API ruxsati kerak. Videoni Actions → Pages manzilidan (`/reels/today.mp4`) yuklab olib qo'lda ham joylash mumkin.

## Postlarni o'zgartirish
`content/posts.json` ni tahrirlang. `{LINK}` joyiga havolangiz avtomatik qo'yiladi. Post 4096 belgidan oshmasin.

## Muhim qoidalar
- **Foyda kafolatlamang**, «tez boyish» va'dasini bermang. Bu XM hamkorlik qoidalariga ham, reklama qonunlariga ham zid.
- Rasmiy logotip va bannerlarni faqat partner panelidagi tayyor materiallardan oling; domen yoki kanal nomida «XM» ishlatmang, sayt mustaqil ekanini ochiq yozing (shablonda yozilgan).
- O'zbekistonda va auditoriyangiz yashaydigan mamlakatlarda xorijiy brokerlar reklamasi bo'yicha qonunchilikni tekshiring.
- Bolalar kontenti kanalingizda (Multiki_Pultiki) bu reklamani yuritmang.
- Faqat o'zingiz bergan Telegram kanalga yuboring; begona guruhlarga spam qilmang.
- GitHub 60 kun faolsiz repo'da rejalashtirilgan ishlarni o'chirib qo'yishi mumkin. Shunda Actions bo'limida qayta yoqing.
