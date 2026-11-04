# XM hamkor to'plami (GitHub orqali)

Bu to'plam GitHub'ning o'zida ishlaydi:

- **Sayt** (GitHub Pages): forex asoslari bo'yicha ta'limiy sahifa, hamkorlik havolangiz bilan.
- **Telegram avtopost** (GitHub Actions): har kuni 10:00 (Toshkent) kanalingizga navbatdagi post ketadi.
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

**Secrets** (yashirin):

| Nom | Qiymat |
|---|---|
| `TELEGRAM_BOT_TOKEN` | BotFather bergan token |
| `TELEGRAM_CHAT_ID` | `@kanal_nomi` |

**Variables** (ochiq):

| Nom | Qiymat |
|---|---|
| `AFFILIATE_LINK` | XM partner panelidan olgan o'zingizning tracking havolangiz (`https://...`) |
| `TELEGRAM_URL` | `https://t.me/kanal_nomi` |
| `START_DATE` | masalan `2026-11-05` (birinchi post sanasi) |

Tokenni hech qachon faylga yozmang va hech kimga bermang.

### 4. Saytni yoqish
**Settings → Pages → Source: GitHub Actions**. Keyin **Actions → "Saytni joylash" → Run workflow**. Tayyor bo'lgach sayt manzili shu yerda ko'rinadi.

### 5. Telegram avtopostni sinash
**Actions → "Telegram kunlik post" → Run workflow**:
1. `dry_run = true` — yubormasdan postni ko'rsatadi.
2. `dry_run = false`, `post_index = 0` — haqiqiy yuboradi.

Shundan so'ng har kuni o'zi ishlaydi. Har postga xavf haqida ogohlantirish avtomatik qo'shiladi.

## Postlarni o'zgartirish
`content/posts.json` ni tahrirlang. `{LINK}` joyiga havolangiz avtomatik qo'yiladi. Post 4096 belgidan oshmasin.

## Muhim qoidalar
- **Foyda kafolatlamang**, «tez boyish» va'dasini bermang. Bu XM hamkorlik qoidalariga ham, reklama qonunlariga ham zid.
- Rasmiy logotip va bannerlarni faqat partner panelidagi tayyor materiallardan oling; domen yoki kanal nomida «XM» ishlatmang, sayt mustaqil ekanini ochiq yozing (shablonda yozilgan).
- O'zbekistonda va auditoriyangiz yashaydigan mamlakatlarda xorijiy brokerlar reklamasi bo'yicha qonunchilikni tekshiring.
- Bolalar kontenti kanalingizda (Multiki_Pultiki) bu reklamani yuritmang.
- Faqat o'zingiz bergan Telegram kanalga yuboring; begona guruhlarga spam qilmang.
- GitHub 60 kun faolsiz repo'da rejalashtirilgan ishlarni o'chirib qo'yishi mumkin. Shunda Actions bo'limida qayta yoqing.
