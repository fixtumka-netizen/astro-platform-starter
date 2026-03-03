import logging
import os
import sqlite3
import traceback
from datetime import datetime
from typing import Any

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ID администраторов
ADMIN_IDS = [5327713050, 6552316766]

# Товары и их цены (звезды с 40% скидкой от рубля)
PRODUCTS = {
    'auto_smm': {'name': 'Auto SMM', 'price_rub': 500, 'price_stars': 300},
    'auto_steam': {'name': 'Auto Steam', 'price_rub': 500, 'price_stars': 300},
    'auto_vip_roblox': {'name': 'Auto VIP Roblox', 'price_rub': 300, 'price_stars': 180},
    'auto_stars': {'name': 'Auto Stars', 'price_rub': 1000, 'price_stars': 600},
    'autoticket': {'name': 'AutoTicket', 'price_rub': 300, 'price_stars': 180},
    'autorobux_complete': {'name': 'AutoRobux Complete', 'price_rub': 1000, 'price_stars': 600},
    'auto_discord_boost': {'name': 'Auto Discord Boost', 'price_rub': 1000, 'price_stars': 600},
    'telegram_gift_auto': {'name': 'Telegram Gift Auto', 'price_rub': 1000, 'price_stars': 600},
    'gpt_consultant': {'name': 'GPT Consultant', 'price_rub': 200, 'price_stars': 120},
}

SUPPLIERS = {
    'supplier_smm': {'name': 'Поставщик SMM', 'price_rub': 300, 'price_stars': 180},
    'supplier_steam': {'name': 'Поставщик Steam', 'price_rub': 300, 'price_stars': 180},
    'supplier_roblox': {'name': 'Поставщик Roblox', 'price_rub': 200, 'price_stars': 120},
    'supplier_stars': {'name': 'Поставщик Stars', 'price_rub': 200, 'price_stars': 120},
}

# Имя пользователя для звезд
STARS_USERNAME = 'Koluanich_Play'
DB_PATH = 'payments.db'


def get_product(product_key: str) -> dict[str, Any] | None:
    if product_key.startswith('supplier_'):
        return SUPPLIERS.get(product_key)
    return PRODUCTS.get(product_key)


def init_db() -> None:
    """Создает БД при первом запуске. Существующие данные не удаляются."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute(
                '''CREATE TABLE IF NOT EXISTS payments
                         (id INTEGER PRIMARY KEY AUTOINCREMENT,
                          user_id INTEGER,
                          username TEXT,
                          product TEXT,
                          amount INTEGER,
                          status TEXT,
                          screenshot_file_id TEXT,
                          date TEXT,
                          payment_method TEXT)'''
            )
            conn.commit()
        logger.info('База данных инициализирована')
    except Exception as e:
        logger.error('Ошибка при инициализации БД: %s', e)


def save_payment(user_id: int, username: str, product: str, amount: int, screenshot_file_id: str, payment_method: str = 'card') -> int | None:
    try:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute(
                """INSERT INTO payments
                         (user_id, username, product, amount, status, screenshot_file_id, date, payment_method)
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (user_id, username, product, amount, 'pending', screenshot_file_id, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), payment_method),
            )
            payment_id = c.lastrowid
            conn.commit()
        logger.info('Платеж %s сохранен в БД', payment_id)
        return payment_id
    except Exception as e:
        logger.error('Ошибка при сохранении платежа: %s', e)
        logger.error(traceback.format_exc())
        return None


def get_all_payments() -> list[tuple[Any, ...]]:
    try:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute('SELECT * FROM payments ORDER BY date DESC')
            return c.fetchall()
    except Exception as e:
        logger.error('Ошибка при получении платежей: %s', e)
        return []


def delete_payment(payment_id: int) -> None:
    try:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute('DELETE FROM payments WHERE id=?', (payment_id,))
            conn.commit()
        logger.info('Платеж %s удален', payment_id)
    except Exception as e:
        logger.error('Ошибка при удалении платежа: %s', e)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    del context
    keyboard = [
        [InlineKeyboardButton('🤝 Поставщики', callback_data='suppliers')],
        [InlineKeyboardButton('🔌 Плагины', callback_data='plugins')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        '👋 Добро пожаловать в Funpay Sentinel. Бот для продажи автоматизированных плагинов и поставщиков на платформе FunPay\n\n'
        'Выберите категорию:',
        reply_markup=reply_markup,
    )


async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    del context
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text('⛔ У вас нет доступа к этой команде.')
        return

    keyboard = [
        [InlineKeyboardButton('📦 Управление товарами', callback_data='admin_products')],
        [InlineKeyboardButton('💰 Все оплаты', callback_data='admin_payments')],
        [InlineKeyboardButton('🗑 Удалить платеж', callback_data='admin_delete_payment')],
    ]
    await update.message.reply_text('👨‍💼 Панель администратора:', reply_markup=InlineKeyboardMarkup(keyboard))


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    try:
        if query.data == 'suppliers':
            keyboard = [
                [InlineKeyboardButton('📱 Поставщик SMM - 300₽ / 180⭐', callback_data='buy_supplier_smm')],
                [InlineKeyboardButton('🎮 Поставщик Steam - 300₽ / 180⭐', callback_data='buy_supplier_steam')],
                [InlineKeyboardButton('👑 Поставщик Roblox - 200₽ / 120⭐', callback_data='buy_supplier_roblox')],
                [InlineKeyboardButton('⭐ Поставщик Stars - 200₽ / 120⭐', callback_data='buy_supplier_stars')],
                [InlineKeyboardButton('◀ Назад', callback_data='back_to_main')],
            ]
            await query.edit_message_text('🤝 Выберите поставщика для покупки:', reply_markup=InlineKeyboardMarkup(keyboard))

        elif query.data == 'plugins':
            keyboard = [
                [InlineKeyboardButton('📱 Auto SMM - 500₽ / 300⭐', callback_data='buy_auto_smm')],
                [InlineKeyboardButton('🎮 Auto Steam - 500₽ / 300⭐', callback_data='buy_auto_steam')],
                [InlineKeyboardButton('👑 Auto VIP Roblox - 300₽ / 180⭐', callback_data='buy_auto_vip_roblox')],
                [InlineKeyboardButton('⭐ Auto Stars - 1000₽ / 600⭐', callback_data='buy_auto_stars')],
                [InlineKeyboardButton('🎫 AutoTicket - 300₽ / 180⭐', callback_data='buy_autoticket')],
                [InlineKeyboardButton('💰 AutoRobux Complete - 1000₽ / 600⭐', callback_data='buy_autorobux_complete')],
                [InlineKeyboardButton('🚀 Auto Discord Boost - 1000₽ / 600⭐', callback_data='buy_auto_discord_boost')],
                [InlineKeyboardButton('🎁 Telegram Gift Auto - 1000₽ / 600⭐', callback_data='buy_telegram_gift_auto')],
                [InlineKeyboardButton('🤖 GPT Consultant - 200₽ / 120⭐', callback_data='buy_gpt_consultant')],
                [InlineKeyboardButton('◀ Назад', callback_data='back_to_main')],
            ]
            await query.edit_message_text('🔌 Выберите плагин для покупки:', reply_markup=InlineKeyboardMarkup(keyboard))

        elif query.data.startswith('buy_'):
            product_key = query.data.replace('buy_', '')
            product = get_product(product_key)
            back_callback = 'suppliers' if product_key.startswith('supplier_') else 'plugins'
            if not product:
                await query.edit_message_text('❌ Товар не найден.')
                return

            context.user_data['selected_product'] = product_key
            keyboard = [
                [InlineKeyboardButton('💳 Оплата картой', callback_data=f'pay_card_{product_key}')],
                [InlineKeyboardButton(f"⭐ Оплата звездами ({product['price_stars']}⭐)", callback_data=f'pay_stars_{product_key}')],
                [InlineKeyboardButton('◀ Назад', callback_data=back_callback)],
            ]
            await query.edit_message_text(
                f"🛒 Товар: {product['name']}\n"
                f"💰 Цена: {product['price_rub']} руб. / {product['price_stars']}⭐\n\n"
                'Выберите способ оплаты:',
                reply_markup=InlineKeyboardMarkup(keyboard),
            )

        elif query.data.startswith('pay_card_'):
            product_key = query.data.replace('pay_card_', '')
            product = get_product(product_key)
            if not product:
                await query.edit_message_text('❌ Товар не найден.')
                return

            context.user_data.update({'selected_product': product_key, 'payment_method': 'card', 'amount': product['price_rub']})
            payment_info = (
                f"💳 Оплата товара: {product['name']}\n"
                f"💰 Сумма: {product['price_rub']} руб.\n\n"
                '📋 Реквизиты для оплаты:\n'
                '💳 Номер карты: `2200 7017 9037 7169`\n'
                'Получатель: TINKOFF BANK\n\n'
                '📤 После оплаты отправьте скриншот подтверждения в этот чат.\n'
                'Важно! На скриншоте должен быть виден номер карты получателя.'
            )
            await query.edit_message_text(payment_info, parse_mode=ParseMode.MARKDOWN)

        elif query.data.startswith('pay_stars_'):
            product_key = query.data.replace('pay_stars_', '')
            product = get_product(product_key)
            if not product:
                await query.edit_message_text('❌ Товар не найден.')
                return

            context.user_data.update({'selected_product': product_key, 'payment_method': 'stars', 'amount': product['price_stars']})
            payment_info = (
                f"⭐ Оплата товара: {product['name']}\n"
                f"💰 Сумма: {product['price_stars']} звезд\n\n"
                '📋 Как оплатить звездами Telegram:\n'
                f'1. Откройте диалог с пользователем @{STARS_USERNAME}\n'
                '2. Нажмите на кнопку с звездочкой ⭐ (отправить подарок)\n'
                f"3. Выберите количество звезд: {product['price_stars']}\n"
                '4. Подтвердите отправку\n\n'
                f'👤 Получатель: @{STARS_USERNAME}\n\n'
                '📤 После отправки звезд, отправьте скриншот подтверждения в этот чат.\n'
                'Важно! На скриншоте должен быть виден перевод звезд.'
            )
            await query.edit_message_text(payment_info)

        elif query.data == 'back_to_main':
            keyboard = [
                [InlineKeyboardButton('🤝 Поставщики', callback_data='suppliers')],
                [InlineKeyboardButton('🔌 Плагины', callback_data='plugins')],
            ]
            await query.edit_message_text(
                '👋 Добро пожаловать в Funpay Sentinel. Бот для продажи автоматизированных плагинов и поставщиков на платформе FunPay\n\n'
                'Выберите категорию:',
                reply_markup=InlineKeyboardMarkup(keyboard),
            )

        elif query.data == 'admin_products':
            if query.from_user.id not in ADMIN_IDS:
                await query.edit_message_text('⛔ Доступ запрещен')
                return
            products_list = '📦 Текущие товары:\n\n🔌 ПЛАГИНЫ:\n'
            for product in PRODUCTS.values():
                products_list += f"• {product['name']}\n  💳 Карта: {product['price_rub']}₽\n  ⭐ Звезды: {product['price_stars']}⭐\n\n"
            products_list += '🤝 ПОСТАВЩИКИ:\n'
            for supplier in SUPPLIERS.values():
                products_list += f"• {supplier['name']}\n  💳 Карта: {supplier['price_rub']}₽\n  ⭐ Звезды: {supplier['price_stars']}⭐\n\n"
            await query.edit_message_text(products_list)

        elif query.data == 'admin_payments':
            if query.from_user.id not in ADMIN_IDS:
                await query.edit_message_text('⛔ Доступ запрещен')
                return
            payments = get_all_payments()
            if not payments:
                await query.edit_message_text('💰 Нет платежей для отображения.')
                return

            payments_text = '💰 Все платежи:\n\n'
            for payment in payments:
                payment_method = '💳 Карта' if payment[8] == 'card' else '⭐ Звезды'
                payments_text += (
                    f'ID: {payment[0]}\n'
                    f"Пользователь: @{payment[2] or 'Неизвестно'} (ID: {payment[1]})\n"
                    f'Товар: {payment[3]}\n'
                    f"Сумма: {payment[4]} {'₽' if payment[8] == 'card' else '⭐'}\n"
                    f'Способ оплаты: {payment_method}\n'
                    f'Статус: {payment[5]}\n'
                    f'Дата: {payment[7]}\n'
                    + '-' * 20
                    + '\n'
                )
            if len(payments_text) > 4000:
                for i in range(0, len(payments_text), 4000):
                    await query.message.reply_text(payments_text[i : i + 4000])
            else:
                await query.edit_message_text(payments_text)

        elif query.data == 'admin_delete_payment':
            if query.from_user.id not in ADMIN_IDS:
                await query.edit_message_text('⛔ Доступ запрещен')
                return
            payments = get_all_payments()
            if not payments:
                await query.edit_message_text('Нет платежей для удаления.')
                return

            keyboard = []
            for payment in payments[:10]:
                payment_method = '💳' if payment[8] == 'card' else '⭐'
                amount_text = f"{payment[4]} {'₽' if payment[8] == 'card' else '⭐'}"
                btn_text = f'{payment_method} ID:{payment[0]} - {payment[3]} - {amount_text}'
                keyboard.append([InlineKeyboardButton(btn_text, callback_data=f'delete_{payment[0]}')])
            keyboard.append([InlineKeyboardButton('◀ Назад', callback_data='admin_back')])
            await query.edit_message_text('Выберите платеж для удаления:', reply_markup=InlineKeyboardMarkup(keyboard))

        elif query.data.startswith('delete_'):
            if query.from_user.id not in ADMIN_IDS:
                await query.edit_message_text('⛔ Доступ запрещен')
                return
            payment_id = int(query.data.replace('delete_', ''))
            delete_payment(payment_id)
            await query.edit_message_text(f'✅ Платеж ID {payment_id} успешно удален!')

        elif query.data == 'admin_back':
            if query.from_user.id not in ADMIN_IDS:
                await query.edit_message_text('⛔ Доступ запрещен')
                return
            keyboard = [
                [InlineKeyboardButton('📦 Управление товарами', callback_data='admin_products')],
                [InlineKeyboardButton('💰 Все оплаты', callback_data='admin_payments')],
                [InlineKeyboardButton('🗑 Удалить платеж', callback_data='admin_delete_payment')],
            ]
            await query.edit_message_text('👨‍💼 Панель администратора:', reply_markup=InlineKeyboardMarkup(keyboard))

    except Exception as e:
        logger.error('Ошибка в button_callback: %s', e)
        logger.error(traceback.format_exc())
        try:
            await query.edit_message_text('❌ Произошла ошибка. Попробуйте позже.')
        except Exception:
            await query.message.reply_text('❌ Произошла ошибка. Попробуйте позже.')


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    username = update.effective_user.username or 'Неизвестно'

    try:
        if 'selected_product' not in context.user_data or 'payment_method' not in context.user_data or 'amount' not in context.user_data:
            await update.message.reply_text('❌ Сначала выберите товар и способ оплаты через меню.')
            return

        product_key = context.user_data['selected_product']
        product = get_product(product_key)
        product_name = product['name'] if product else 'Неизвестный товар'
        payment_method = context.user_data['payment_method']
        amount = context.user_data['amount']

        photo_file = await update.message.photo[-1].get_file()
        payment_id = save_payment(user_id, username, product_name, amount, photo_file.file_id, payment_method)
        if not payment_id:
            await update.message.reply_text('❌ Ошибка при сохранении платежа. Попробуйте позже.')
            return

        payment_method_text = 'картой' if payment_method == 'card' else 'звездами'
        amount_symbol = '₽' if payment_method == 'card' else '⭐'

        await update.message.reply_text(
            f'✅ Скриншот получен! Ваш платеж №{payment_id} отправлен на проверку администратору.\n'
            f'Товар: {product_name}\n'
            f'Сумма: {amount}{amount_symbol}\n'
            f'Способ оплаты: {payment_method_text}\n'
            'Ожидайте подтверждения.'
        )

        caption = (
            f'🔔 Новый платеж №{payment_id}\n'
            f'👤 Пользователь: @{username} (ID: {user_id})\n'
            f'🛒 Товар: {product_name}\n'
            f'💰 Сумма: {amount}{amount_symbol}\n'
            f"{'💳' if payment_method == 'card' else '⭐'} Способ оплаты: {'Карта' if payment_method == 'card' else 'Звезды'}\n"
            f"⏰ Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )

        sent_to_admins = False
        for admin_id in ADMIN_IDS:
            try:
                await context.bot.send_photo(chat_id=admin_id, photo=photo_file.file_id, caption=caption)
                sent_to_admins = True
            except Exception as e:
                logger.error('Ошибка отправки админу %s: %s', admin_id, e)

        if not sent_to_admins:
            await update.message.reply_text('⚠️ Уведомление администраторам не доставлено. Но ваш платеж сохранен.')

        context.user_data.pop('selected_product', None)
        context.user_data.pop('payment_method', None)
        context.user_data.pop('amount', None)

    except Exception as e:
        logger.error('Ошибка в handle_photo: %s', e)
        logger.error(traceback.format_exc())
        await update.message.reply_text('❌ Произошла ошибка при обработке фото. Попробуйте позже.')


def main() -> None:
    init_db()

    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        raise RuntimeError('Не задан TELEGRAM_BOT_TOKEN в переменных окружения')

    application = Application.builder().token(token).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('admin', admin))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    logger.info('Бот запущен')
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
