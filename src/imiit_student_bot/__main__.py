"""Command-line interface."""
import json
import logging

import click
from telegram import InlineKeyboardButton
from telegram import InlineKeyboardMarkup
from telegram import ParseMode
from telegram import ReplyKeyboardMarkup
from telegram import Update
from telegram.ext import CallbackContext
from telegram.ext import CallbackQueryHandler
from telegram.ext import CommandHandler
from telegram.ext import Filters
from telegram.ext import MessageHandler
from telegram.ext import PicklePersistence
from telegram.ext import Updater


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)

with open("src/imiit_student_bot/response.json", "r") as read_file:
    response: dict = json.load(read_file)


def language_callback(update: Update, context: CallbackContext) -> None:
    """Sets the language for the user."""
    languages_list = [{"🇬🇧": "en", "🇷🇺": "ru"}]
    keyboard = [
        [
            InlineKeyboardButton(language_emoji, callback_data=language_code)
            for language_emoji, language_code in language_row.items()
        ]
        for language_row in languages_list
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_sticker(
        sticker=response.get("Sticker").get("Lang"), reply_markup=reply_markup
    )


def set_language(update: Update, context: CallbackContext) -> None:
    """Set language in user data."""
    query = update.callback_query
    query.answer()

    if context.user_data.get("Language-s") == "Start":
        context.user_data["Language"] = query.data
        context.user_data["Language-s"] = "Set"
        start_command(update, context)
    else:
        context.user_data["Language"] = query.data


def start_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    try:
        lang = context.user_data["Language"]
    except KeyError:
        context.user_data["Language-s"] = "Start"
        language_callback(update, context)
    else:
        context.bot.send_sticker(
            chat_id=update.effective_chat.id,
            sticker=response.get("Sticker").get("Start"),
        )
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=response.get(lang).get("Start").format(user=user.mention_html()),
            parse_mode=ParseMode.HTML,
            reply_markup=ReplyKeyboardMarkup(response.get(lang).get("Keyboard")),
        )


def about_callback(update: Update, context: CallbackContext) -> None:
    """Send info about the university."""
    try:
        lang = context.user_data["Language"]
    except KeyError:
        update.message.reply_html(response.get("Error"))
    else:
        about_dict = response.get(lang).get("About")
        keyboard = [
            [InlineKeyboardButton(button_text, url=link)]
            for button_text, link in about_dict.items()
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_sticker(
            response.get("Sticker").get("About"), reply_markup=reply_markup
        )


def map_callback(update: Update, context: CallbackContext) -> None:
    """Send a map to the university."""
    try:
        lang = context.user_data["Language"]
    except KeyError:
        update.message.reply_html(response.get("Error"))
    else:
        update.message.reply_sticker(response.get("Sticker").get("Map"))
        update.message.reply_html(text=response.get(lang).get("Map"))
        update.message.reply_location(
            latitude=55.7878313846929, longitude=37.60799488989068
        )


def timetable_callback(update: Update, context: CallbackContext) -> None:
    """Send a map to the university."""
    try:
        lang = context.user_data["Language"]
    except KeyError:
        update.message.reply_html(response.get("Error"))
    else:
        update.message.reply_sticker(response.get("Sticker").get("Timetable"))
        update.message.reply_html(text=response.get(lang).get("Timetable"))


def send_timetable(update: Update, context: CallbackContext) -> None:
    """Send a map to the university."""
    try:
        lang = context.user_data["Language"]
    except KeyError:
        update.message.reply_html(response.get("Error"))
    else:
        group = context.match.group(0)
        logger.info(response.get(lang).get("send_timetable").format(group=group))
        update.message.reply_html(
            response.get(lang).get("send_timetable").format(group=group)
        )


@click.command()
@click.argument(
    "token",
    type=str,
)
@click.version_option()
def main(token: str) -> None:
    """Imiit Student Bot.

    Starts the bot.

    Args:
        token: Bot authentication token.
    """
    updater = Updater(
        token,
        persistence=PicklePersistence(filename="user_data.pickle"),
        use_context=True,
    )

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start_command))
    dispatcher.add_handler(CommandHandler("lang", language_callback))

    dispatcher.add_handler(
        MessageHandler(
            Filters.regex(r"/(Об ИУЦТ)|(ИУЦТ)|(IMIIT)|(imiit)/i"), about_callback
        )
    )
    dispatcher.add_handler(
        MessageHandler(Filters.regex(r"(Карта)|(map)|(Map)"), map_callback)
    )
    dispatcher.add_handler(
        MessageHandler(Filters.regex(r"(Расписание)|(Timetable)"), timetable_callback)
    )
    updater.dispatcher.add_handler(
        MessageHandler(Filters.regex(r"^([а-яА-Я]{3}-\d{3})"), send_timetable)
    )

    dispatcher.add_handler(CallbackQueryHandler(set_language))

    # Start the Bot
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main(prog_name="imiit-student-bot")  # pragma: no cover
