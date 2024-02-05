# Little Turtle
An AI-powered Telegram bot designed to engage users with stories generated from the perspective of a time-traveling turtle. This innovative bot not only shares tales woven around historical events but also enhances storytelling with generated images, accuracy reviews, and concise summaries. Aimed at merging education with entertainment, Little Turtle offers an interactive way to explore history through storytelling

![Little Turtle](assets/little_turtle_logo.jpeg)

## Features
- **Dynamic Story Generation**: Creates stories based on historical events and date.
- **Image Prompt Creation**: Enhances stories with related images.
- **Channel Scheduling**: Schedules stories and images to be posted on a Telegram channel.

## Installation
### Using Docker Compose
This project can be easily set up using Docker and Docker Compose, which simplifies the deployment and management of the application components

#### Prerequisites
- Docker
- Docker Compose

#### Steps
1. Prepare Environment Variables:
Create a .env file in the project root with the necessary environment variables:

```env
OPENAI_MODEL=<model_name>
OPENAI_API_KEY=<your_openai_api_key>
TELEGRAM_BOT_TOKEN=<your_telegram_bot_token>
TELEGRAM_API_ID=<your_telegram_api_id>
TELEGRAM_API_HASH=<your_telegram_api_hash>
TELEGRAM_PHONE_NUMBER=<your_telegram_phone_number>
TELEGRAM_ALLOWED_USERS=<user_ids_comma_separated>
USER_IDS_TO_SEND_MORNING_MSG=<user_ids_comma_separated>
CHAT_IDS_TO_SEND_STORIES=<chat_ids_comma_separated>
REDIS_URL=redis://story-cache:6379
ERROR_HANDLER_ENABLED=<true_or_false>
ERROR_HANDLER_DNS=<error_handler_dns>
ERROR_HANDLER_ENVIRONMENT=<environment>
ERROR_HANDLER_SERVER_NAME=<server_name>
LANGFUSE_PUBLIC_KEY=<langfuse_public_key>
LANGFUSE_SECRET_KEY=<langfuse_secret_key>
LANGFUSE_URL=<langfuse_url>
```

2. Docker Compose File:
Ensure compose-local.yaml is in the project root. This file defines the services necessary for running Little Turtle, including the bot service and Redis for caching.


3. Launch the Services:
Run the following command to start the services defined in your Docker Compose file:

```bash
docker-compose -f compose-local.yaml up -d
```

## Configuration
The Little Turtle project is configured primarily through environment variables. These variables allow you to customize the application's behavior without changing the code. Below is a list of key environment variables used by the project:

- `OPENAI_API_KEY`: Your OpenAI API key, required for accessing models like GPT-4 for story generation.
- `OPENAI_MODEL`: Specifies the OpenAI model used, defaulting to "gpt-4".
- `REDIS_URL`: Connection string for Redis, used for caching. Default is redis://localhost:6379/0.
- `TELEGRAM_BOT_TOKEN`: Token for your Telegram bot, necessary for bot operation.
- `TELEGRAM_API_ID` and `TELEGRAM_API_HASH`: Required for interacting with the Telegram API.
- `TELEGRAM_PHONE_NUMBER`: Your Telegram account phone number, used for certain API interactions.
- `TELEGRAM_SESSION_NAME`: Session name for the Telegram bot, defaulting to "little_turtle".
- `TELEGRAM_ALLOWED_USERS`: List of user IDs allowed to interact with the bot.
- `CHAT_IDS_TO_SEND_STORIES` and `USER_IDS_TO_SEND_MORNING_MSG`: Lists of chat and user IDs for distributing stories and morning messages.
- `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`, and `LANGFUSE_URL`: Configuration for LangFuse integration.
- `ERROR_HANDLER_ENABLED`: Toggle for enabling a custom error handler.
- `GENERATION_LANGUAGE`: Language used for generating stories, defaulting to "Russian".
- `DEFAULT_TZ`, `DEFAULT_SCHEDULE_HOUR`, `DEFAULT_SCHEDULE_MINUTE`, `DEFAULT_SCHEDULE_SECOND`: Default time zone and scheduling settings for story publication.

## Usage

### Telegram Commands
- `/start` - Welcomes the user and provides an introduction to the bot.
- `/story` - Generates and shares a new story.
- `/get_next_date` - Provides the next story's date based on the list of posts scheduled on the Telegram channel.
- `/suggest_topics` - Suggests a list of potential topics to write about based on the date.
- `/reset_target_topics` - Clears the list of target topics.
- `/set_date` - Save the replied date as the story's date.
- `/set_story` - Saves the replied text as the story.
- `/set_image_prompt` - Saves the replied text as the image prompt.
- `/set_image` - Saves the replied image as the story's image.
- `/add_target_topic` - Adds the replied text as a target topic.
- `/preview` - Previews an upcoming story.
- `/schedule` - Schedules the story to be posted on the Telegram channel.
- `/state` - Print the current status of the story.
- `/cancel` - Cancels the current story.
- `/ping` - Checks if the bot is active.

## License

Little Turtle is released under the MIT License. See the [LICENSE](LICENSE) file for more details.
