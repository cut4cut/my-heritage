import logging

import httpx

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
from heritage.pkg import PastvuAPI
from heritage.dto import SearchState
from heritage.exc import NoMorePhotos
from heritage.usecase import MediaGroupUseCase
from heritage.entity import (
    SEND_GEOPOSITION,
    MORE_PHOTO,
    START_MSG,
    INFO_MSG,
    NEED_SEND_GEO_MSG,
    NO_MORE_PHOTOS_MSG,
    SOME_ERROR_MSG,
)


api = PastvuAPI()
settings = Settings()
use_case = MediaGroupUseCase(api)

keyboard = [
    [KeyboardButton(SEND_GEOPOSITION, request_location=True)],
    [KeyboardButton(MORE_PHOTO)],
]
reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    await update.message.reply_html(
        START_MSG.format(update.effective_user.mention_html()),
        reply_markup=reply_markup,
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text(INFO_MSG)


async def hand_text_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Hand text input from user."""
    username = update.effective_user.username
    if update.message.text != MORE_PHOTO:
        await update.message.reply_text(NEED_SEND_GEO_MSG)

    try:
        state = context.chat_data["state"]
        logger.info(f"Current state={state} from user={username}")
        await update.message.reply_media_group(
            media=[
                InputMediaPhoto(photo.file, caption=photo.caption)
                for photo in use_case.get_photos(
                    state.latitude, state.longitude, state.page
                )
            ]
        )
        state.shift()
    except NoMorePhotos:
        await update.message.reply_text(NO_MORE_PHOTOS_MSG)
    except KeyError:
        await update.message.reply_text(NEED_SEND_GEO_MSG)
    except httpx.ReadTimeout:
        await update.message.reply_text(SOME_ERROR_MSG)


async def get_photos(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Get photos by geopoint."""
    latitude = update.message.location.latitude
    longitude = update.message.location.longitude
    username = update.effective_user.username
    logger.info(f"Get location=({latitude}, {longitude}) from user={username}")
    try:
        context.chat_data["state"] = SearchState(latitude=latitude, longitude=longitude)
        await update.message.reply_media_group(
            media=[
                InputMediaPhoto(photo.file, caption=photo.caption)
                for photo in use_case.get_photos(latitude, longitude)
            ]
        )
    except NoMorePhotos:
        await update.message.reply_text(NO_MORE_PHOTOS_MSG)
    except httpx.ReadTimeout:
        await update.message.reply_text(SOME_ERROR_MSG)


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

    application.run_polling()


if __name__ == "__main__":
    main()
