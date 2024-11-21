from datetime import date
from aiogram import Bot, Dispatcher, executor, types
from aiogram.utils.exceptions import MessageNotModified

from buttons import *
from config import *
from utils import (profile_text, ref_text, pay_text, get_all_mamonts, add_mamont)

bot = Bot(token=API_TOKEN)
dispatcher = Dispatcher(bot)


@dispatcher.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    """
    Handles the /start command and welcomes the user.

    If a referral ID is provided in the command, it adds the user to the system
    as a new participant under the referrer, unless the user is already registered.

    Args:
        message (types.Message): The incoming message containing the command.
    """
    user_id = message.from_user.id
    if " " in message.text:
        referrer_id = message.text.split()[1]
        try:
            referrer_id = int(referrer_id)
            if user_id != referrer_id and user_id not in get_all_mamonts():
                add_mamont(referrer_id, user_id, date.today())
        except ValueError:
            pass
    await bot.send_photo(chat_id=message.chat.id,
                         photo=open("images/start.png", "rb"),
                         caption=main_text,
                         reply_markup=markup_start)


@dispatcher.message_handler(commands=['воркер'])
async def send_worker(message: types.Message):
    """
    Handles the /воркер command and sends information about the worker.

    This function responds with details regarding the worker when the user requests it.

    Args:
        message (types.Message): The incoming message containing the command.
    """
    await message.answer(worker_text, reply_markup=markup_worker)


@dispatcher.callback_query_handler(lambda call: call.data == 'worker_ref')
async def worker_ref(call: types.CallbackQuery):
    """
    Handles the request for referral information about the worker.

    This function edits the message to provide the user with their referral information.

    Args:
        call (types.CallbackQuery): The callback query containing the request data.
    """
    await bot.answer_callback_query(call.id)
    try:
        await bot.edit_message_text(ref_text(call.from_user.id),
                                    reply_markup=markup_worker,
                                    inline_message_id=call.inline_message_id,
                                    message_id=call.message.message_id,
                                    chat_id=call.message.chat.id)
    except MessageNotModified:
        pass


@dispatcher.callback_query_handler(lambda call: call.data == 'worker_buy')
async def worker_buy(call: types.CallbackQuery):
    """
    Handles the request to buy services from the worker.

    This function sends a message with the purchase options available for the worker's services.

    Args:
        call (types.CallbackQuery): The callback query containing the request data.
    """
    await bot.answer_callback_query(call.id)
    await bot.send_message(text=worker_buy_text,
                           chat_id=call.message.chat.id)


@dispatcher.message_handler(content_types=['text'])
async def worker_add_orders(message: types.Message):
    """
    Handles text messages to add orders for boosting services.

    If the message contains the word 'накрутить', it attempts to process the order
    and sends confirmation to the user.

    Args:
        message (types.Message): The incoming text message containing the order request.
    """
    if 'накрутить' in message.text.lower():
        try:
            count = message.text.split(' ')[1]
            await bot.send_message(text=profile_text(message.from_user.id,
                                                     count),
                                   chat_id=message.chat.id)
        except IndexError:
            pass


@dispatcher.message_handler(commands=['help'])
async def send_help(message: types.Message):
    """
    Handles the /help command and sends a list of available commands.

    This function provides the user with a guide on how to interact with the bot.

    Args:
        message (types.Message): The incoming message containing the command.
    """
    help_text = (
        "Available commands:\n"
        "/start - Start interacting with the bot\n"
        "/воркер - Get information about the worker\n"
        "/help - Show this message\n"
        "Click the buttons in the menu to access other "
        "functions."
    )
    await message.answer(help_text, reply_markup=markup_main)


@dispatcher.callback_query_handler(lambda call: call.data == 'back_main')
async def main_layout(call: types.CallbackQuery):
    """
    Handles requests to return to the main menu.

    This function edits the current message to display the main menu options again.

    Args:
        call (types.CallbackQuery): The callback query containing the request data.
    """
    await bot.answer_callback_query(call.id)
    await bot.edit_message_text(back_main,
                                reply_markup=markup_main,
                                inline_message_id=call.inline_message_id,
                                message_id=call.message.message_id,
                                chat_id=call.message.chat.id)


@dispatcher.callback_query_handler(lambda call: 'links' in call.data)
async def links(call: types.CallbackQuery):
    """
    Handles requests for obtaining links.

    Depending on the state indicated in the callback data, it either sends a message
    with links or edits the existing message to update the links.

    Args:
        call (types.CallbackQuery): The callback query containing the request data.
    """
    await bot.answer_callback_query(call.id)
    if int(call.data[-1]) == 0:
        await bot.send_message(chat_id=call.message.chat.id,
                               text=links_text,
                               reply_markup=markup_feedback)
    else:
        try:
            await bot.edit_message_text(links_text,
                                        reply_markup=markup_feedback,
                                        inline_message_id=call.inline_message_id,
                                        message_id=call.message.message_id,
                                        chat_id=call.message.chat.id)
        except MessageNotModified:
            pass


@dispatcher.callback_query_handler(lambda call: 'feedback' in call.data)
async def feedback(call: types.CallbackQuery):
    """
    Handles requests for obtaining feedback.

    This function edits the message to show the feedback based on the user's selection.

    Args:
        call (types.CallbackQuery): The callback query containing the request data.
    """
    await bot.answer_callback_query(call.id)
    try:
        await bot.edit_message_text(feedback_list[int(call.data[-1])],
                                    reply_markup=markup_feedback,
                                    inline_message_id=call.inline_message_id,
                                    message_id=call.message.message_id,
                                    chat_id=call.message.chat.id)
    except MessageNotModified:
        pass


@dispatcher.callback_query_handler(lambda call: 'buy_stuff' in call.data)
async def buy_process(call: types.CallbackQuery):
    """
    Handles requests to purchase items.

    Depending on the state indicated in the callback data, it either sends a message
    with the purchase options or edits the existing message to update the options.

    Args:
        call (types.CallbackQuery): The callback query containing the request data.
    """
    await bot.answer_callback_query(call.id)
    if int(call.data[-1]) == 0:
        await bot.send_message(chat_id=call.message.chat.id,
                               text=buy_text,
                               reply_markup=markup_city)
    else:
        await bot.edit_message_text(buy_text,
                                    reply_markup=markup_city,
                                    inline_message_id=call.inline_message_id,
                                    message_id=call.message.message_id,
                                    chat_id=call.message.chat.id)


@dispatcher.callback_query_handler(lambda call: 'vacancies' in call.data)
async def vacancies(call: types.CallbackQuery):
    """
    Handles requests for obtaining vacancies.

    This function either sends a message with available vacancies or edits the existing
    message to show the updated information.

    Args:
        call (types.CallbackQuery): The callback query containing the request data.
    """
    await bot.answer_callback_query(call.id)
    if int(call.data[-1]) == 0:
        await bot.send_message(chat_id=call.message.chat.id,
                               text=vacancies_text,
                               reply_markup=markup_main)
    else:
        try:
            await bot.edit_message_text(vacancies_text,
                                        reply_markup=markup_main,
                                        inline_message_id=call.inline_message_id,
                                        message_id=call.message.message_id,
                                        chat_id=call.message.chat.id)
        except MessageNotModified:
            pass


@dispatcher.callback_query_handler(lambda call: 'promo' in call.data)
async def promo(call: types.CallbackQuery):
    """
    Handles requests for obtaining a promo code.

    This function sends or edits a message to provide the user with their promo code
    based on the callback data.

    Args:
        call (types.CallbackQuery): The callback query containing the request data.
    """
    await bot.answer_callback_query(call.id)
    if int(call.data[-1]) == 0:
        await bot.send_message(chat_id=call.message.chat.id,
                               text=ref_text(call.from_user.id),
                               reply_markup=markup_main)
    else:
        try:
            await bot.edit_message_text(ref_text(call.from_user.id),
                                        reply_markup=markup_main,
                                        inline_message_id=call.inline_message_id,
                                        message_id=call.message.message_id,
                                        chat_id=call.message.chat.id)
        except MessageNotModified:
            pass


@dispatcher.callback_query_handler(lambda call: 'important' in call.data)
async def important(call: types.CallbackQuery):
    """
    Handles requests for obtaining important information.

    This function sends or edits a message to provide the user with important updates
    based on the callback data.

    Args:
        call (types.CallbackQuery): The callback query containing the request data.
    """
    await bot.answer_callback_query(call.id)
    if int(call.data[-1]) == 0:
        await bot.send_message(chat_id=call.message.chat.id,
                               text=important_text,
                               reply_markup=markup_main)
    else:
        try:
            await bot.edit_message_text(important_text,
                                        reply_markup=markup_main,
                                        inline_message_id=call.inline_message_id,
                                        message_id=call.message.message_id,
                                        chat_id=call.message.chat.id)
        except MessageNotModified:
            pass


@dispatcher.callback_query_handler(lambda call: 'profile' in call.data)
async def profile(call: types.CallbackQuery):
    """
    Handles requests for obtaining the user's profile information.

    This function sends or edits a message to provide the user with their profile details
    based on the callback data.

    Args:
        call (types.CallbackQuery): The callback query containing the request data.
    """
    await bot.answer_callback_query(call.id)
    if int(call.data[-1]) == 0:
        await bot.send_message(chat_id=call.message.chat.id,
                               text=profile_text(call.from_user.id),
                               reply_markup=markup_main)
    else:
        try:
            await bot.edit_message_text(profile_text(call.from_user.id),
                                        reply_markup=markup_main,
                                        inline_message_id=call.inline_message_id,
                                        message_id=call.message.message_id,
                                        chat_id=call.message.chat.id)
        except MessageNotModified:
            pass


@dispatcher.callback_query_handler(lambda call: call.data == 'city_moscow')
async def moscow_layout(call: types.CallbackQuery):
    """
    Handles requests to select a district in Moscow.

    This function prompts the user to choose a district within Moscow.

    Args:
        call (types.CallbackQuery): The callback query containing the request data.
    """
    await bot.answer_callback_query(call.id)
    await bot.edit_message_text("Choose a district in Moscow:",
                                reply_markup=markup_moscow,
                                inline_message_id=call.inline_message_id,
                                message_id=call.message.message_id,
                                chat_id=call.message.chat.id)


@dispatcher.callback_query_handler(lambda call: call.data == 'city_saintP')
async def saint_p_layout(call: types.CallbackQuery):
    """
    Handles requests to select a district in Saint Petersburg.

    This function prompts the user to choose a district within Saint Petersburg.

    Args:
        call (types.CallbackQuery): The callback query containing the request data.
    """
    await bot.answer_callback_query(call.id)
    await bot.edit_message_text("Choose a district in Saint Petersburg:",
                                reply_markup=markup_saintP,
                                inline_message_id=call.inline_message_id,
                                message_id=call.message.message_id,
                                chat_id=call.message.chat.id)


@dispatcher.callback_query_handler(lambda call: 'city_default' in call.data)
async def city_default_layout(call: types.CallbackQuery):
    """
    Handles requests to select a default location.

    This function prompts the user to choose a default location.

    Args:
        call (types.CallbackQuery): The callback query containing the request data.
    """
    await bot.answer_callback_query(call.id)
    await bot.edit_message_text("Choose a location",
                                reply_markup=markup_city_default,
                                inline_message_id=call.inline_message_id,
                                message_id=call.message.message_id,
                                chat_id=call.message.chat.id)


@dispatcher.callback_query_handler(lambda call: 'price_list' in call.data)
async def price_list(call: types.CallbackQuery):
    """
    Handles requests for obtaining the price list.

    This function edits the message to show the current price list to the user.

    Args:
        call (types.CallbackQuery): The callback query containing the request data.
    """
    await bot.answer_callback_query(call.id)
    await bot.edit_message_text(price_list_text,
                                reply_markup=markup_price,
                                inline_message_id=call.inline_message_id,
                                message_id=call.message.message_id,
                                chat_id=call.message.chat.id)


@dispatcher.callback_query_handler(lambda call: call.data == 'price_back')
async def price_list1(call: types.CallbackQuery):
    """
    Handles requests to return to the price list.

    This function sends a message with the price list to the user.

    Args:
        call (types.CallbackQuery): The callback query containing the request data.
    """
    await bot.answer_callback_query(call.id)
    await bot.send_message(chat_id=call.message.chat.id,
                           text=price_list_text,
                           reply_markup=markup_price)


@dispatcher.callback_query_handler(lambda call: call.data == 's1')
async def s1(call: types.CallbackQuery):
    """
    Handles requests to send the image s1.

    This function sends the specified image along with a caption to the user.

    Args:
        call (types.CallbackQuery): The callback query containing the request data.
    """
    await bot.answer_callback_query(call.id)
    image = open("images/s1.jpg", "rb")
    await bot.send_photo(chat_id=call.message.chat.id,
                         photo=image, caption=s1_text,
                         reply_markup=markup_s1)


@dispatcher.callback_query_handler(lambda call: call.data == 's2')
async def s2(call: types.CallbackQuery):
    """
    Handles requests to send the image s2.

    This function sends the specified image along with a caption to the user.

    Args:
        call (types.CallbackQuery): The callback query containing the request data.
    """
    await bot.answer_callback_query(call.id)
    image = open("images/s2.jpg", "rb")
    await bot.send_photo(chat_id=call.message.chat.id,
                         photo=image, caption=s2_text,
                         reply_markup=markup_s2)


@dispatcher.callback_query_handler(lambda call: call.data == 's3')
async def s3(call: types.CallbackQuery):
    """
    Handles requests to send the image s3.

    This function sends the specified image along with a caption to the user.

    Args:
        call (types.CallbackQuery): The callback query containing the request data.
    """
    await bot.answer_callback_query(call.id)
    image = open("images/s3.jpg", "rb")
    await bot.send_photo(chat_id=call.message.chat.id,
                         photo=image, caption=s3_text,
                         reply_markup=markup_s3)


@dispatcher.callback_query_handler(lambda call: call.data == 's4')
async def s4(call: types.CallbackQuery):
    """
    Handles requests to send the image s4.

    This function sends the specified image along with a caption to the user.

    Args:
        call (types.CallbackQuery): The callback query containing the request data.
    """
    await bot.answer_callback_query(call.id)
    image = open("images/s4.jpg", "rb")
    await bot.send_photo(chat_id=call.message.chat.id,
                         photo=image, caption=s4_text,
                         reply_markup=markup_s4)


@dispatcher.callback_query_handler(lambda call: call.data == 's5')
async def s5(call: types.CallbackQuery):
    """
    Handles requests to send the image s5.

    This function sends the specified image along with a caption to the user.

    Args:
        call (types.CallbackQuery): The callback query containing the request data.
    """
    await bot.answer_callback_query(call.id)
    image = open("images/s5.jpg", "rb")
    await bot.send_photo(chat_id=call.message.chat.id,
                         photo=image, caption=s5_text,
                         reply_markup=markup_s5)


@dispatcher.callback_query_handler(lambda call: call.data == 's6')
async def s6(call: types.CallbackQuery):
    """
    Handles requests to send the image s6.

    This function sends the specified image along with a caption to the user.

    Args:
        call (types.CallbackQuery): The callback query containing the request data.
    """
    await bot.answer_callback_query(call.id)
    image = open("images/s6.jpg", "rb")
    await bot.send_photo(chat_id=call.message.chat.id,
                         photo=image, caption=s6_text,
                         reply_markup=markup_s6)


@dispatcher.callback_query_handler(lambda call: call.data == 's7')
async def s7(call: types.CallbackQuery):
    """
    Handles requests to send the image s7.

    This function sends the specified image along with a caption to the user.

    Args:
        call (types.CallbackQuery): The callback query containing the request data.
    """
    await bot.answer_callback_query(call.id)
    image = open("images/s7.jpg", "rb")
    await bot.send_photo(chat_id=call.message.chat.id,
                         photo=image, caption=s7_text,
                         reply_markup=markup_s7)


@dispatcher.callback_query_handler(lambda call: call.data == 's8')
async def s8(call: types.CallbackQuery):
    """
    Handles requests to send the image s8.

    This function sends the specified image along with a caption to the user.

    Args:
        call (types.CallbackQuery): The callback query containing the request data.
    """
    await bot.answer_callback_query(call.id)
    image = open("images/s8.jpg", "rb")
    await bot.send_photo(chat_id=call.message.chat.id,
                         photo=image, caption=s8_text,
                         reply_markup=markup_s8)


@dispatcher.callback_query_handler(lambda call: 'pay' in call.data)
async def pay(call: types.CallbackQuery):
    """
        Handles callback queries related to payment actions.

        This function is triggered when a callback query is received that contains
        the substring 'pay' in the callback data. It acknowledges the callback
        query and sends a message to the user with payment information.

        Args:
    - call: The callback query object containing:
        - data (str): The data associated with the callback query, which
          includes details necessary to determine the payment amount and type.
        - message (types.Message): The message object from which the callback
          originated, containing the chat ID.
    """
    await bot.answer_callback_query(call.id)
    await bot.send_message(chat_id=call.message.chat.id,
                           text=pay_text(prices[call.data[-2]][int(call.data[-1])]),
                           reply_markup=markup_pay)


if __name__ == '__main__':
    executor.start_polling(dispatcher, skip_updates=True)
