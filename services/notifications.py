"""
Модуль для отправки уведомлений.
"""

from aiogram import Bot
from data.config import ADMIN_IDS
from database import db
from keyboards.admin_kb import application_actions_keyboard

async def notify_admins_about_new_application(application_id: int, bot: Bot):
    """Отправка уведомлений о новой заявке"""
    application = db.get_application_by_id(application_id)
    
    if application:
        app_id, user_id, service_name, rental_period, app_date, customer_name, phone, status, username, user_full_name = application
        
        notification_text = (
            "🆕 <b>НОВАЯ ЗАЯВКА!</b>\n\n"
            f"<b>№ заявки:</b> #{app_id}\n"
            f"<b>Инструмент:</b> {service_name}\n"
            f"<b>Срок аренды:</b> {rental_period}\n"
            f"<b>Клиент:</b> {customer_name}\n"
            f"<b>Телефон:</b> {phone}\n"
            f"<b>Дата:</b> {app_date}\n"
            f"<b>Username:</b> @{username if username else 'нет'}\n"
            f"<b>User ID:</b> {user_id}"
        )
        
        for admin_id in ADMIN_IDS:
            try:
                await bot.send_message(
                    admin_id,
                    notification_text,
                    reply_markup=application_actions_keyboard(app_id),
                    parse_mode="HTML"
                )
            except Exception:
                print(f"❌ Не удалось отправить уведомление админу {admin_id}")