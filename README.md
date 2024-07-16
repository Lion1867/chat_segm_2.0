## Chat Segm 2.0 - Intelligent Image Segmentation Chatbot
# Overview

Chat Segm 2.0 is an intelligent chatbot developed in Python that operates within the Telegram platform. It provides users with the functionality to segment images sent to it using various pre-trained AI segmentation models. The project leverages FastAPI to wrap the developed program into a microservice and Docker for containerizing the solution.

# Installation

# Clone the repository:

Open your terminal and run the following command to clone the repository:

git clone https://github.com/yourusername/chat_segm_2.0.git

# Navigate to the project directory:

Change your current working directory to the project directory:

cd chat_segm_2.0

# Add your Telegram Bot API Token to the .env file:

Open the .env file in a text editor and add your Telegram Bot API Token:

TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here

Save the .env file.

# Build the Docker image and start the services:

Run the following commands to build the Docker image and start the services:

sudo docker-compose build
sudo docker-compose up

This will build the Docker image and start the FastAPI server and the Telegram bot.

# Access the chatbot on Telegram:

Now that the chatbot is running, you can access it on Telegram using your bot's token. Open Telegram and search for your bot using its username or its token. Start a conversation with the bot and send it an image to segment.
