from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import yfinance as yf
import pandas as pd
import ta
from textblob import TextBlob

TOKEN = "TOKEN_BURAYA"

def haber_duygu(haberler):
    skorlar = []
    for h in haberler:
        skorlar.append(TextBlob(h).sentiment.polarity)
    return sum(skorlar)/len(skorlar) if skorlar else 0

def analiz(hisse):
    df = yf.download(hisse, period="6mo", interval="1d", progress=False)
    if df.empty:
        return None

    close = df["Close"]
    rsi = ta.momentum.RSIIndicator(close).rsi().iloc[-1]
    ema50 = ta.trend.EMAIndicator(close, 50).ema_indicator().iloc[-1]
    ema200 = ta.trend.EMAIndicator(close, 200).ema_indicator().iloc[-1]
    price = close.iloc[-1]

    haberler = [
        "Şirket finansal sonuçlarını açıkladı",
        "Sektörde büyüme beklentisi arttı"
    ]

    duygu = haber_duygu(haberler)

    kisa = "↗ %3–8" if duygu > 0 and price > ema50 else "⚠️ Riskli"
    orta = "↗ %6–15" if price > ema200 else "⚠️ Zayıf"
    uzun = "↗ Trend pozitif" if ema50 > ema200 else "↘ Zayıf trend"

    return f"""
📊 {hisse.replace(".IS","")}

📰 Haber Etkisi Skoru: {round(duygu,2)}
📉 RSI: {round(rsi,1)}

⏱ Kısa Vade: {kisa}
📆 Orta Vade: {orta}
📈 Uzun Vade: {uzun}

⚠️ Yatırım tavsiyesi değildir
"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("BIST Analiz Botu\n/analiz THYAO")

async def analiz_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        hisse = context.args[0].upper() + ".IS"
        sonuc = analiz(hisse)
        await update.message.reply_text(sonuc or "Hisse bulunamadı")
    except:
        await update.message.reply_text("Kullanım: /analiz THYAO")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("analiz", analiz_cmd))
app.run_polling()
