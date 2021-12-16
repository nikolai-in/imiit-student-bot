"""Command-line interface."""
import logging
import re
from functools import wraps

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

from imiit_student_bot import __data__

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)


RESPONSE = __data__.RESPONSE
GROUPS = __data__.get_groups()


def check_language(func: callable) -> callable:
    """Sends typing action while processing func command."""

    @wraps(func)
    def command_func(update, context, *args, **kwargs):
        try:
            lang = context.user_data["Language"]
        except KeyError:
            return language_callback(update, context)
        else:
            return func(update, context, lang, *args, **kwargs)

    return command_func


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
        sticker=RESPONSE.get("Sticker").get("Lang"), reply_markup=reply_markup
    )


def set_language(update: Update, context: CallbackContext) -> None:
    """Set language in user data."""
    query = update.callback_query

    query.answer()

    context.user_data["Language"] = query.data
    start_command(update, context)


@check_language
def start_command(update: Update, context: CallbackContext, lang: str) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    context.bot.send_sticker(
        chat_id=update.effective_chat.id,
        sticker=RESPONSE.get("Sticker").get("Start"),
    )
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=RESPONSE.get(lang).get("Start").format(user=user.mention_html()),
        parse_mode=ParseMode.HTML,
        reply_markup=ReplyKeyboardMarkup(RESPONSE.get(lang).get("Keyboard")),
    )


@check_language
def about_callback(update: Update, context: CallbackContext, lang: str) -> None:
    """Send info about the university."""
    about_dict = RESPONSE.get(lang).get("About")
    keyboard = [
        [InlineKeyboardButton(button_text, url=link)]
        for button_text, link in about_dict.items()
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_sticker(
        RESPONSE.get("Sticker").get("About"), reply_markup=reply_markup
    )


@check_language
def map_callback(update: Update, _, lang: str) -> None:
    """Send a map to the university."""
    update.message.reply_sticker(RESPONSE.get("Sticker").get("Map"))
    update.message.reply_html(text=RESPONSE.get(lang).get("Map"))
    update.message.reply_location(
        latitude=55.7878313846929, longitude=37.60799488989068
    )


@check_language
def timetable_callback(update: Update, _, lang: str) -> None:
    """Send a timetable  instruction."""
    update.message.reply_sticker(RESPONSE.get("Sticker").get("Timetable"))
    update.message.reply_html(text=RESPONSE.get(lang).get("Timetable"))


@check_language
def send_timetable(update: Update, context: CallbackContext, lang: str) -> None:
    """Send a map to the university."""
    group = context.match.group(0).lower()

    logger.info(GROUPS, group)

    if group in GROUPS:
        try:
            timetable = __data__.get_timetable(GROUPS[group])
        except KeyError:
            timetable = [{"Ошибка": {"Ошибка": "Ошибка"}}]
        # update.message.reply_text(f"{group}:\n {text}")


@check_language
def unknown_callback(update: Update, _, lang: str) -> None:
    """Send a map to the university."""
    update.message.reply_sticker(RESPONSE.get("Sticker").get("Unknown"))
    update.message.reply_html(text=RESPONSE.get(lang).get("Unknown"))


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
            Filters.regex(re.compile(r"(об )?(иуцт)|(imiit)|(about)", re.IGNORECASE)),
            about_callback,
        )
    )
    dispatcher.add_handler(
        MessageHandler(
            Filters.regex(re.compile(r"(карта)|(map)", re.IGNORECASE)), map_callback
        )
    )
    dispatcher.add_handler(
        MessageHandler(
            Filters.regex(re.compile(r"(расписание)|(timetable)", re.IGNORECASE)),
            timetable_callback,
        )
    )
    updater.dispatcher.add_handler(
        MessageHandler(
            Filters.regex(re.compile(r"([а-я]{3,5}-\d{3})", re.IGNORECASE)),
            send_timetable,
        )
    )
    dispatcher.add_handler(
        MessageHandler(Filters.text & ~Filters.command, unknown_callback)
    )

    dispatcher.add_handler(CallbackQueryHandler(set_language))

    # Start the Bot
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main(prog_name="imiit-student-bot")  # pragma: no cover
