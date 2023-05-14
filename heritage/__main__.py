import html
import json
import traceback

import httpx

from telegram.constants import ParseMode
from telegram import (
    Update,
    KeyboardButton,
    InputMediaPhoto,
    ReplyKeyboardMarkup,
)
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from heritage.cfg import Settings
from heritage.pkg import PastvuAPI, BusinessLogger
from heritage.dto import SearchState
from heritage.exc import NoPhotos
from heritage.usecase import MediaGroupUseCase
from heritage.entity import (
    UserStep,
    SEND_GEOPOSITION,
    MORE_PHOTO,
    START_MSG,
    INFO_MSG,
    NEED_SEND_GEO_MSG,
    NO_PHOTOS_MSG,
    NO_MORE_PHOTOS_MSG,
    SOME_ERROR_MSG,
)


api = PastvuAPI()
settings = Settings()
use_case = MediaGroupUseCase(api)
logger = BusinessLogger("myheritage")

keyboard = [
    [KeyboardButton(SEND_GEOPOSITION, request_location=True)],
    [KeyboardButton(MORE_PHOTO)],
]
reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log the error and send a telegram message to notify the developer."""
    # Log the error before we do anything else, so we can see it even if something breaks.
    logger.logger.error(
        f'{{"username": "{update.effective_user.username}", "exception": "{context.error}"}}'
    )

    # traceback.format_exception returns the usual python message about an exception, but as a
    # list of strings rather than a single string, so we have to join them together.
    tb_list = traceback.format_exception(
        None, context.error, context.error.__traceback__
    )
    tb_string = "".join(tb_list)

    # Build the message with some markup and additional information about what happened.
    # You might need to add some logic to deal with messages longer than the 4096 character limit.
    update_str = update.to_dict() if isinstance(update, Update) else str(update)
    message = (
        f"An exception was raised while handling an update\n"
        f"<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}"
        "</pre>\n\n"
        f"<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n"
        f"<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n"
        f"<pre>{html.escape(tb_string)}</pre>"
    )

    # Finally, send the message
    await context.bot.send_message(
        chat_id=settings.admin_chat_id, text=message, parse_mode=ParseMode.HTML
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    logger.info(step=UserStep.START, username=update.effective_user.username)
    await update.message.reply_html(
        START_MSG.format(update.effective_user.mention_html()),
        reply_markup=reply_markup,
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    logger.info(step=UserStep.HELP, username=update.effective_user.username)
    await update.message.reply_text(INFO_MSG)


async def hand_text_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Hand text input from user."""
    username = update.effective_user.username
    if update.message.text != MORE_PHOTO:
        await update.message.reply_text(NEED_SEND_GEO_MSG)
        logger.info(
            step=UserStep.GET_MORE,
            case="Incorrect message.text",
            username=update.effective_user.username,
        )
        return

    try:
        state = context.chat_data["state"]
        logger.info(
            step=UserStep.GET_MORE,
            case="Correct message.text",
            username=username,
            state=state.dict(),
        )
        await update.message.reply_media_group(
            media=[
                InputMediaPhoto(photo.file, caption=photo.caption)
                for photo in use_case.get_photos(
                    state.latitude, state.longitude, state.page
                )
            ]
        )
        state.shift()
        logger.info(
            step=UserStep.GET_MORE,
            case="Successfully sent",
            username=username,
            state=state.dict(),
        )
    except NoPhotos:
        await update.message.reply_text(NO_MORE_PHOTOS_MSG)
        logger.info(
            step=UserStep.GET_MORE,
            case="No photos",
            username=username,
            state=state.dict(),
        )
    except KeyError:
        await update.message.reply_text(NEED_SEND_GEO_MSG)
        logger.info(
            step=UserStep.GET_MORE,
            case="No state",
            username=username,
            state=state.dict(),
        )
    except httpx.ReadTimeout:
        await update.message.reply_text(SOME_ERROR_MSG)
        logger.info(
            step=UserStep.GET_MORE,
            case="ReadTimeout",
            username=username,
            state=state.dict(),
        )


async def get_photos(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Get photos by geopoint."""
    latitude = update.message.location.latitude
    longitude = update.message.location.longitude
    username = update.effective_user.username
    logger.info(
        step=UserStep.GET,
        case="Get new location",
        username=username,
        location={"latitude": latitude, "longitude": longitude},
    )
    try:
        context.chat_data["state"] = SearchState(latitude=latitude, longitude=longitude)
        await update.message.reply_media_group(
            media=[
                InputMediaPhoto(photo.file, caption=photo.caption)
                for photo in use_case.get_photos(latitude, longitude)
            ]
        )
        logger.info(
            step=UserStep.GET,
            case="Successfully sent",
            username=username,
            location={"latitude": latitude, "longitude": longitude},
        )
    except NoPhotos:
        await update.message.reply_text(NO_PHOTOS_MSG)
        logger.info(
            step=UserStep.GET,
            case="No photos",
            username=username,
            location={"latitude": latitude, "longitude": longitude},
        )
    except httpx.ReadTimeout:
        await update.message.reply_text(SOME_ERROR_MSG)
        logger.info(
            step=UserStep.GET,
            case="ReadTimeout",
            username=username,
            location={"latitude": latitude, "longitude": longitude},
        )


def main() -> None:
    """Start the bot."""
    application = Application.builder().token(settings.tg_token).build()

    # help logic
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # main logic
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, hand_text_input)
    )

    application.add_handler(
        MessageHandler(filters.LOCATION & ~filters.COMMAND, get_photos)
    )

    # error handler
    application.add_error_handler(error_handler)  # type: ignore

    application.run_polling()


if __name__ == "__main__":
    main()
