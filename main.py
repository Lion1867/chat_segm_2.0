from decouple import config
import requests
from telegram.ext import Application, ContextTypes, CommandHandler, MessageHandler, filters
from telegram import Update

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler

import os
os.makedirs("/tmp", exist_ok=True)

# Define a function to handle the /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Привет! Я бот для сегментации изображений")
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Загрузите ваше изображение")

async def media_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.document:
        # Handle documents
        file_id = update.message.document.file_id
        file_name = update.message.document.file_name
    elif update.message.photo:
        # Handle images
        file_id = update.message.photo[-1].file_id
        file_name = f"{file_id}.png"
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Unsupported media type")
        return

    # Get the file object of the media
    file = await context.bot.get_file(file_id)

    # Download the media to a temporary file
    media_path = f"/tmp/{file_name}"
    await file.download_to_drive(media_path)

    # Save the media path in the context for later use
    context.user_data["file_path"] = media_path

    # Show the menu with buttons for the user to choose which model to use
    keyboard = [
        [InlineKeyboardButton("SAM (Base)", callback_data="sam_b")],
        [InlineKeyboardButton("Mobile SAM", callback_data="mobile_sam")],
        [InlineKeyboardButton("FastSAM (Small)", callback_data="fast_sam_s")],
        [InlineKeyboardButton("YOLOv8 (Extra Large)", callback_data="yolov8x_seg")],
        [InlineKeyboardButton("YOLOv8 (Nano)", callback_data="yolov8n_seg")],
        [InlineKeyboardButton("All Models", callback_data="all_models")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Привет! Я бот для сегментации изображений. Пожалуйста, выберите модель для сегментации:", reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    # Send a message to the user that their image is being processed
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Пожалуйста, подождите, ваше изображение обрабатывается...")

    # Determine the URL based on the user's choice
    if query.data == "all_models":
        url = "http://api:8080/segment_image/all_models/"
    else:
        url = f"http://api:8080/segment_image/{query.data}/"

    # Check if the file_path key is present in the context
    if "file_path" in context.user_data:
        file_path = context.user_data["file_path"]
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Извините, произошла ошибка при сегментации изображения")
        return

    files = {"file": open(file_path, "rb")}
    response = requests.post(url, files=files)

    # Check the response status code
    if response.status_code == 200:
        image_info = response.json()

        # If the user selected "All Models"
        if query.data == "all_models":
            segmented_images = image_info["segmented_images"]
            for image_info in segmented_images:
                model_name = image_info["model_name"]
                image_path = image_info["image_path"]

                # Send the segmented image
                with open(image_path, "rb") as f:
                    await context.bot.send_photo(chat_id=update.effective_chat.id, photo=f)

                # Send a message containing the model name
                await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Model: {model_name}")
        else:
            # Check if the image_path key is present in the image_info dictionary
            if "image_path" in image_info:
                # Send the segmented image back to the user
                image_path = image_info["image_path"]
                with open(image_path, "rb") as f:
                    await context.bot.send_photo(chat_id=update.effective_chat.id, photo=f)

                # Send a message containing the model name
                model_name = image_info["model_name"]
                await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Модель: {model_name}")
            else:
                # Send a message indicating that no objects were detected in the image
                await context.bot.send_message(chat_id=update.effective_chat.id, text="Объектов для детектирования на изображении не обнаружено")
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Извините, произошла ошибка при сегментации изображения")

    # Show the menu with buttons again for the user to choose which model to use
    keyboard = [
        [InlineKeyboardButton("SAM (Base)", callback_data="sam_b")],
        [InlineKeyboardButton("Mobile SAM", callback_data="mobile_sam")],
        [InlineKeyboardButton("FastSAM (Small)", callback_data="fast_sam_s")],
        [InlineKeyboardButton("YOLOv8 (Extra Large)", callback_data="yolov8x_seg")],
        [InlineKeyboardButton("YOLOv8 (Nano)", callback_data="yolov8n_seg")],
        [InlineKeyboardButton("All Models", callback_data="all_models")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Попробуйте использовать другие модели для сегментации:", reply_markup=reply_markup)

    await context.bot.send_message(chat_id=update.effective_chat.id, text="Или загрузите новое изображение")

# Define the main function to run the bot
def main():
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(config('TOKEN')).build()

    # Add command handler for the /start command
    application.add_handler(CommandHandler("start", start))

    # Add message handler for images and documents
    application.add_handler(MessageHandler(filters.Document.ALL | filters.PHOTO, media_handler))

    # Add callback query handler for button clicks
    application.add_handler(CallbackQueryHandler(button_handler))

    # Run the bot until you press Ctrl-C
    application.run_polling()

if __name__ == '__main__':
    main()

