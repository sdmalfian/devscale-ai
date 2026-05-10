import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(base_url=OPENAI_BASE_URL, api_key=OPENAI_API_KEY)

def load_local_database():
    """Helper to load the static JSON database using robust absolute paths."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    database_path = os.path.join(current_dir, "database.json")
    
    try:
        with open(database_path, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: File tidak ditemukan di {database_path}")
        return {"products": [], "store_info": {}}

# --- PIPELINE START ---
def generate_raw_info(topic):
    """
    Step 1: Detecting intents for Catalog, Stock, Shipping, or Specific Products.
    """
    db = load_local_database()
    query = topic.lower()
    
    # Define Keyword Groups
    catalog_triggers = ["jual apa", "barang", "katalog", "apa saja", "list", "produk", "ready"]
    stock_triggers = ["stok", "masih ada", "habis", "tersisa"]
    shipping_triggers = ["kirim", "ongkir", "kurir", "ekspedisi", "pakai apa"]
    store_triggers = ["jam buka", "jadwal", "lokasi", "alamat", "toko dimana", "bayar"]

    # Result container
    context_data = {
        "store": db["store_info"],
        "products": [],
        "context_type": "general"
    }

    # 1. Check for Catalog or Stock requests
    if any(word in query for word in catalog_triggers + stock_triggers):
        context_data["products"] = db["products"]
        context_data["context_type"] = "catalog_and_stock"
        return context_data

    # 2. Check for Shipping or Store Info requests
    if any(word in query for word in shipping_triggers + store_triggers):
        context_data["context_type"] = "store_policy"
        return context_data

    # 3. Check for specific product names
    matched_products = [
        p for p in db["products"]
        if query in p["name"].lower() or query in p["category"].lower()
    ]
    
    if matched_products:
        context_data["products"] = matched_products
        context_data["context_type"] = "specific_product"
        return context_data

    # Fallback to general store info if something is asked but not matched
    return context_data

def summarize(raw_info):
    """
    Step 2: Formatting the injected context based on the detected intent.
    """
    store = raw_info["store"]
    products = raw_info["products"]
    context_type = raw_info["context_type"]
    
    # Basic Store Info (Always Included)
    summary = f"INFO TOKO: {store['name']}, Lokasi: {store['location']}, Jam Buka: {store['working_hours']}.\n"
    summary += f"PENGIRIMAN: {', '.join(store['shipping_methods'])}.\n"
    summary += f"PEMBAYARAN: {', '.join(store['payment_methods'])}.\n\n"

    # Product & Stock Info
    if products:
        summary += "DATA STOK PRODUK:\n"
        for p in products:
            status = "READY" if p["stock"] > 0 else "HABIS/SOLD OUT"
            summary += f"- {p['name']} | Harga: {p['price']} | Stok: {p['stock']} ({status}) | Warna: {', '.join(p['available_colors'])}\n"
    elif context_type == "specific_product":
        return "TIDAK_ADA_DATA"

    return summary


def extract_and_respond(summarized_content, user_query):
    """
    Step 3: Final extraction to user-friendly chat format.
    """
    system_prompt = f"""
    Anda adalah Customer Service chatbot untuk toko busana muslim 'Zahra Hijab & Wear'.
    
    TUGAS ANDA:
    1. Jawab pertanyaan user HANYA berdasarkan konteks informasi di bawah ini.
    2. Jika informasi berisi 'TIDAK_ADA_DATA', katakan maaf karena produk atau info tidak tersedia.
    3. Selalu gunakan Bahasa Indonesia yang ramah, sopan, dan gunakan emoji yang sesuai.
    4. JANGAN memberikan informasi di luar data yang diberikan.

    KONTEKS INFORMASI:
    {summarized_content}
    """

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_query}
    ]

    completion = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=messages,
    )

    return completion.choices[0].message.content or ""

# --- EXECUTION LOOP ---

if __name__ == "__main__":
    print("✨ Assalamu'alaikum! Selamat datang di Zahra Hijab & Wear. ✨")
    print("Nama saya Zahra, asisten virtual Anda. Ada yang bisa saya bantu hari ini, Kak?")
    print("(Ketik 'x atau X' jika sudah selesai berkonsultasi)\n")
    
    while True:
        user_input = input("Silakan jawab disini: ")
        
        if user_input.lower() in ["x", "X", "keluar", "exit", "quit", "stop"]:
            print("\nTerima kasih sudah menghubungi Zahra Hijab & Wear. Sukses selalu dan sampai jumpa lagi, Kak! 😊")
            break
            
        # Run the Pipeline
        raw_data = generate_raw_info(user_input)
        context_summary = summarize(raw_data)
        final_answer = extract_and_respond(context_summary, user_input)
        
        print(f"\n{final_answer}\n")