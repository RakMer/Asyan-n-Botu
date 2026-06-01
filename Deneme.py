import os
from openai import OpenAI

# 1. OpenRouter istemcisini (client) yapılandırın
# "YOUR_OPENROUTER_API_KEY" yazan yere OpenRouter'dan aldığın anahtarı yapıştır.
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="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", 
)

# 2. Kullanmak istediğin ücretsiz modeli seç
# (OpenRouter'daki tam model adını buraya yazmalısın)
MODEL_NAME = "nvidia/nemotron-3-super-120b-a12b:free"

def chat_with_bot():
    print("🤖 Chatbot Başlatıldı! Çıkmak için 'çıkış' yazabilirsin.\n" + "-"*50)
    
    # Sohbet geçmişini tutmak için bir liste (Botun geçmişi hatırlamasını sağlar)
    messages = [
        {"role": "system", "content": "Sen yardımcı, arkadaş canlısı ve Türkçe konuşan bir yapay zekâ asistanısın."}
    ]

    while True:
        user_input = input("\n👤 Siz: ")
        
        if user_input.lower() in ["çıkış", "exit", "quit"]:
            print("🤖 Bot: Görüşmek üzere!")
            break
            
        if not user_input.strip():
            continue

        # Kullanıcının mesajını geçmişe ekle
        messages.append({"role": "user", "content": user_input})

        try:
            # API'ye istek gönder
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=messages,
                # OpenRouter için zorunlu olmasa da sitenizin adını belirtmek iyi bir pratiktir
                extra_headers={
                    "HTTP-Referer": "http://localhost:3000", # İsteğe bağlı
                    "X-Title": "Mert'in Chatbotu",            # İsteğe bağlı
                }
            )

            # Botun cevabını al
            bot_reply = response.choices[0].message.content
            print(f"\n🤖 Bot: {bot_reply}")

            # Botun cevabını da geçmişe ekle ki sohbet devam edebilsin
            messages.append({"role": "assistant", "content": bot_reply})

        except Exception as e:
            print(f"\n❌ Bir hata oluştu: {e}")

if __name__ == "__main__":
    chat_with_bot()