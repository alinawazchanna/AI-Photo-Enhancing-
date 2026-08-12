# 📸 Photo Enhancement Telegram Bot (100% GitHub par Free)

Yeh bot user ki bheji hui photo ko automatically enhance karta hai
(sharpness, contrast, color, brightness) aur wapas send kar deta hai.
Deployment **GitHub Actions** ke zariye hoti hai — koi third-party
hosting service (Render/Railway) nahi chahiye.

⚠️ **Important note**: GitHub Actions "always-on server" ke liye nahi
bana hai. Har run max ~5 hr 40 min chalta hai, phir automatically restart
hota hai. Restart ke beech 1-2 minute ka chhota gap aa sakta hai jisme bot
offline rahega. Agar zero-downtime chahiye to Render/Railway jaisi free
hosting behtar rahegi — lekin agar sirf GitHub chahiye, to yeh setup
achhe se kaam karega.

---

## Step 1: Telegram Bot Banayein

1. Telegram par [@BotFather](https://t.me/BotFather) open karein.
2. `/newbot` bhejein, naam aur username set karein.
3. Jo **TOKEN** milega (jaisे `123456789:AAExxxxxxxxxxxxxxxxxxxxxxxxxx`),
   use safe rakhein.

> ⚠️ Agar aapne pehle koi token kahin (chat, screenshot, public jagah)
> share kiya hai, to BotFather me `/mybots` → apna bot → **API Token**
> → **Revoke current token** karke naya token generate kar lein.

---

## Step 2: Repo GitHub par Banayein

1. [github.com](https://github.com) par **New repository** banayein
   (naam jo chahe rakhein, e.g. `photo-enhance-bot`). Public rakhein
   (public repos ke liye GitHub Actions minutes unlimited/free hain).
2. Neeche di gayi saari files/folders repo me upload karein
   (structure exactly waisa hi rakhein):

```
photo-enhance-bot/
├── .github/
│   └── workflows/
│       └── bot.yml
├── bot.py
├── requirements.txt
└── .gitignore
```

   Website se upload karte waqt `.github/workflows/bot.yml` ka poora
   folder structure banaye rakhna zaroori hai — GitHub isse automatically
   detect karta hai.

---

## Step 3: Token ko GitHub Secret me Daalein (File me NAHI)

1. Apne repo me jaayein → **Settings** tab.
2. Left sidebar me **Secrets and variables** → **Actions**.
3. **New repository secret** click karein.
4. Naam: `BOT_TOKEN`
   Value: (aapka naya token, Step 1 wala)
5. **Add secret** dabayein.

Ye token kabhi code/file me nahi jaata, sirf GitHub ke secure secrets
store me rehta hai.

---

## Step 4: Workflow ko Start Karein

1. Repo me **Actions** tab par jaayein.
2. Left side me **"Run Telegram Bot"** workflow dikhega, use click karein.
3. **Run workflow** button dabayein (green button, right side).
4. Kuch second me run shuru ho jayega — click karke live logs dekh sakte hain.

Bas! Ab har baar jab aap `main` branch me push karenge, ya har ~5 ghante
40 min me automatically, bot naye run ke sath restart hota rahega.

---

## Step 5: Bot Test Karein

Telegram par apne bot ko open karein, `/start` bhejein, phir koi photo
bhejein — bot use enhance karke wapas bhej dega.

---

## Files ka Overview

| File | Kaam |
|---|---|
| `bot.py` | Bot logic + photo enhancement + auto-timeout (5h40m pe khud stop) |
| `requirements.txt` | Python dependencies |
| `.github/workflows/bot.yml` | GitHub Actions workflow — bot ko schedule pe (re)start karta hai |

---

## Customize Karna Chahein To

`bot.py` me `enhance_image()` function ke andar values change karke
enhancement ki strength adjust kar sakte hain:

```python
img = ImageEnhance.Contrast(img).enhance(1.15)   # 1.0 = no change, 1.5 = strong
img = ImageEnhance.Color(img).enhance(1.2)
img = ImageEnhance.Sharpness(img).enhance(1.5)
```

## Local Testing (Optional)

```bash
pip install -r requirements.txt
export BOT_TOKEN="your-token-here"
python bot.py
```

## Troubleshooting

- **Workflow "Run workflow" button nahi dikh raha?** — Pehli baar file
  push karne ke baad Actions tab refresh karein; kabhi kabhi 1-2 min lag
  jate hain detect hone me.
- **Bot respond nahi kar raha?** — Actions tab me jaake latest run ke
  logs check karein, error wahan dikhega.
- **"BOT_TOKEN environment variable set nahi hai" error** — Secret ka
  naam exactly `BOT_TOKEN` hi hona chahiye (case-sensitive).
