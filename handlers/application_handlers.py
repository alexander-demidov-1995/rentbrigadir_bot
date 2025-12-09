"""
Модуль обработчиков для системы заявок на аренду.

Содержит обработчики для многошагового процесса оформления заявок
с использованием Finite State Machine (FSM).
"""

from aiogram import types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database import db
from keyboards.user_kb import (main_keyboard, cancel_application_keyboard, 
                              confirmation_keyboard)
from services.notifications import notify_admins_about_new_application


# ОПРЕДЕЛЕНИЕ СОСТОЯНИЙ FSM

class ApplicationStates(StatesGroup):
    """
    Класс-контейнер для состояний процесса оформления заявки на аренду.
    
    States:
        waiting_for_tool_name: Ожидание ввода названия инструмента
        waiting_for_rental_period: Ожидание ввода срока аренды  
        waiting_for_customer_name: Ожидание ввода ФИО клиента
        waiting_for_phone: Ожидание ввода телефона
        confirmation: Ожидание подтверждения заявки
    """
    waiting_for_tool_name = State()
    waiting_for_rental_period = State()
    waiting_for_customer_name = State()
    waiting_for_phone = State()
    confirmation = State()


# НАЧАЛО ПРОЦЕССА ОФОРМЛЕНИЯ ЗАЯВКИ

async def start_application(message: types.Message, state: FSMContext):
    """
    Начинает процесс оформления заявки, запрашивая название инструмента.
    
    Args:
        message: Объект сообщения от пользователя
        state: Контекст состояния FSM
    """
    await message.answer(
        "📝 <b>Начнем оформление заявки!</b>\n\n"
        "Введите название инструмента или оборудования, которое хотите арендовать:",
        reply_markup=cancel_application_keyboard(),
        parse_mode="HTML"
    )
    await state.set_state(ApplicationStates.waiting_for_tool_name)

async def rent_tool(callback: types.CallbackQuery, state: FSMContext):
    """
    Начинает процесс аренды конкретного инструмента, предзаполняя его название.
    
    Args:
        callback: Callback запрос от inline кнопки
        state: Контекст состояния FSM
    """
    tool_id = int(callback.data.split("_")[1])
    tool = db.get_tool_by_id(tool_id)
    
    if tool:
        tool_name = tool[1]  # Название инструмента
        await state.update_data(tool_name=tool_name)
        await callback.message.edit_text(
            f"📝 <b>Оформляем аренду:</b>\n🔧 {tool_name}\n\n"
            f"Введите срок аренды (например: '2 дня', '1 неделя', '1 месяц'):",
            reply_markup=cancel_application_keyboard(),
            parse_mode="HTML"
        )
        await state.set_state(ApplicationStates.waiting_for_rental_period)
    else:
        await callback.message.edit_text("❌ Инструмент не найден")
    
    await callback.answer()


# ОБРАБОТЧИКИ СОСТОЯНИЙ FSM

async def process_tool_name(message: types.Message, state: FSMContext):
    """
    Обрабатывает ввод названия инструмента и переводит к следующему шагу.
    
    Args:
        message: Сообщение с названием инструмента
        state: Контекст состояния FSM
    """
    await state.update_data(tool_name=message.text)
    await message.answer(
        "📅 Теперь введите срок аренды (например: '2 дня', '1 неделя', '1 месяц'):",
        reply_markup=cancel_application_keyboard()
    )
    await state.set_state(ApplicationStates.waiting_for_rental_period)

async def process_rental_period(message: types.Message, state: FSMContext):
    """
    Обрабатывает ввод срока аренды и запрашивает ФИО.
    
    Args:
        message: Сообщение со сроком аренды
        state: Контекст состояния FSM
    """
    await state.update_data(rental_period=message.text)
    await message.answer(
        "👤 Введите ваше ФИО:",
        reply_markup=cancel_application_keyboard()
    )
    await state.set_state(ApplicationStates.waiting_for_customer_name)

async def process_customer_name(message: types.Message, state: FSMContext):
    """
    Обрабатывает ввод ФИО и запрашивает телефон.
    
    Args:
        message: Сообщение с ФИО клиента
        state: Контекст состояния FSM
    """
    await state.update_data(customer_name=message.text)
    await message.answer(
        "📞 Введите ваш номер телефона:",
        reply_markup=cancel_application_keyboard()
    )
    await state.set_state(ApplicationStates.waiting_for_phone)

async def process_phone(message: types.Message, state: FSMContext):
    """
    Обрабатывает ввод телефона, показывает сводку и запрашивает подтверждение.
    
    Args:
        message: Сообщение с номером телефона
        state: Контекст состояния FSM
    """
    await state.update_data(phone=message.text)
    data = await state.get_data()
    
    # Формирование текста заявки для подтверждения
    application_text = (
        "📋 <b>Проверьте вашу заявку:</b>\n\n"
        f"🔧 <b>Инструмент:</b> {data['tool_name']}\n"
        f"📅 <b>Срок аренды:</b> {data['rental_period']}\n"
        f"👤 <b>ФИО:</b> {data['customer_name']}\n"
        f"📞 <b>Телефон:</b> {data['phone']}\n\n"
        "<i>Всё верно?</i>"
    )
    
    await message.answer(application_text, reply_markup=confirmation_keyboard(), parse_mode="HTML")
    await state.set_state(ApplicationStates.confirmation)


# ПОДТВЕРЖДЕНИЕ И ОТМЕНА ЗАЯВКИ

async def confirm_application(callback: types.CallbackQuery, state: FSMContext, bot):
    """
    Подтверждает заявку, сохраняет в БД, уведомляет админов и очищает состояние.
    
    Args:
        callback: Callback запрос от кнопки подтверждения
        state: Контекст состояния FSM
        bot: Экземпляр бота для отправки уведомлений
    """
    data = await state.get_data()
    
    # Сохранение заявки в базу данных
    application_id = db.add_application(
        user_id=callback.from_user.id,
        service_name=data['tool_name'],
        customer_name=data['customer_name'],
        phone=data['phone'],
        rental_period=data['rental_period']
    )
    
    await state.clear()  # Важно: очистка состояния после успешного сохранения
    
    if application_id:
        # Уведомление администраторов о новой заявке
        await notify_admins_about_new_application(application_id, bot)
        
        # Подтверждение пользователю
        await callback.message.edit_text(
            f"✅ <b>Заявка #{application_id} успешно отправлена!</b>\n\n"
            f"🔧 <b>Инструмент:</b> {data['tool_name']}\n"
            f"📅 <b>Срок аренды:</b> {data['rental_period']}\n"
            f"👤 <b>ФИО:</b> {data['customer_name']}\n"
            f"📞 <b>Телефон:</b> {data['phone']}\n\n"
            "<i>Наш менеджер свяжется с вами в ближайшее время для уточнения деталей.</i>",
            parse_mode="HTML"
        )
    else:
        await callback.message.edit_text(
            "❌ <b>Произошла ошибка при сохранении заявки.</b>\n\n"
            "Пожалуйста, попробуйте еще раз или свяжитесь с нами по телефону.",
            parse_mode="HTML"
        )
    
    await callback.answer()

async def edit_application(callback: types.CallbackQuery, state: FSMContext):
    """
    Отменяет текущую заявку и возвращает пользователя в главное меню.
    
    Args:
        callback: Callback запрос от кнопки редактирования
        state: Контекст состояния FSM
    """
    await state.clear()
    await callback.message.edit_text("❌ Заявка отменена. Начните заново, если нужно.")
    await callback.message.answer("Выберите действие:", reply_markup=main_keyboard())
    await callback.answer()

async def cancel_application(message: types.Message, state: FSMContext):
    """
    Обработчик команды /cancel для отмены процесса оформления заявки.
    
    Args:
        message: Сообщение с командой /cancel
        state: Контекст состояния FSM
    """
    current_state = await state.get_state()
    if current_state is None:
        await message.answer("❌ Нет активной заявки для отмены.")
        return
        
    await state.clear()
    await message.answer(
        "❌ Заполнение заявки отменено.",
        reply_markup=main_keyboard()
    )