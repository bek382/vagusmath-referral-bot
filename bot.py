from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.utils import executor
import json
import os
from config import bot_token, channel_username, owner_id

bot = Bot(token=bot_token)
dp = Dispatcher(bot)

DATA_FILE = "db.json"
REQUIRED_REFERRALS = 5  # necha kishi taklif qilishi kerak

# Ma'lumotlar bazasini yuklash/saqlash
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

@dp.message_handler(commands=["start"])
async def start_cmd(message: Message):
    user_id = str(message.from_user.id)
    data = load_data()

    # Referal tracking
    ref_id = message.get_args()
    if ref_id and ref_id != user_id:
        if ref_id not in data:
            data[ref_id] = {"referrals": [], "link_sent": False}
        if user_id not in data[ref_id]["referrals"]:
            data[ref_id]["referrals"].append(user_id)

    # Foydalanuvchini ro'yxatdan o'tkazish
    if user_id not in data:
        data[user_id] = {"referrals": [], "link_sent": False}

    save_data(data)

    referral_link = f"https://t.me/{(await bot.get_me()).username}?start={user_id}"
    await message.answer(
        f"👋 Salom! Bu sizning referal ssilkangiz:\n\n{referral_link}\n\n"
        f"Do‘stlaringizni taklif qiling! 5 ta odam qo‘shilgach, sizga kanal ssilkasi yuboriladi."
    )

@dp.message_handler(commands=["progress"])
async def progress_cmd(message: Message):
    user_id = str(message.from_user.id)
    data = load_data()

    user_data = data.get(user_id)
    if not user_data:
        await message.answer("Siz hali boshlamadingiz. /start buyrug‘ini bosing.")
        return

    count = len(user_data["referrals"])
    await message.answer(f"📊 Siz hozirgacha {count} ta odam taklif qildingiz.")

    if count >= REQUIRED_REFERRALS and not user_data["link_sent"]:
        invite_link = f"https://t.me/{channel_username}"
        await message.answer(f"🎉 Tabriklaymiz! Mana yopiq kanalga ssilkalaringiz:\n\n{invite_link}")
        user_data["link_sent"] = True
        save_data(data)

@dp.message_handler(commands=["users"])
async def list_users(message: Message):
    if message.from_user.id != owner_id:
        return
    data = load_data()
    await message.answer(f"📈 Jami foydalanuvchilar soni: {len(data)}")

if __name__ == "__main__":
    print("Bot is running...")
    executor.start_polling(dp)
