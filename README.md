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
# OpenAI Configuration
OPENAI_API_KEY=<your_openai_api_key>
OPENAI_MODEL=gpt-4  # Optional, defaults to gpt-4

# Anthropic Configuration
ANTHROPIC_API_KEY=<your_anthropic_api_key>
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022  # Optional

# Telegram Configuration
TELEGRAM_BOT_TOKEN=<your_telegram_bot_token>
TELEGRAM_API_ID=<your_telegram_api_id>
TELEGRAM_API_HASH=<your_telegram_api_hash>
TELEGRAM_PHONE_NUMBER=<your_telegram_phone_number>
TELEGRAM_ALLOWED_USERS=<user_ids_comma_separated>
CHAT_IDS_TO_SEND_STORIES=<chat_ids_comma_separated>
USER_IDS_TO_SEND_MORNING_MSG=<user_ids_comma_separated>

# Phoenix Telemetry (Optional)
PHOENIX_COLLECTOR_ENDPOINT=http://phoenix:6006  # Optional
PHOENIX_PROJECT_NAME=little-turtle  # Optional
PHOENIX_ENABLED=true  # Optional, defaults to true

# Redis Configuration (Optional for Docker Compose)
REDIS_URL=redis://story-cache:6379/0
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

### Required Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key, required for story generation and image creation.
- `TELEGRAM_BOT_TOKEN`: Token for your Telegram bot, necessary for bot operation.
- `TELEGRAM_API_ID` and `TELEGRAM_API_HASH`: Required for interacting with the Telegram API.
- `TELEGRAM_PHONE_NUMBER`: Your Telegram account phone number, used for certain API interactions.

### Optional Environment Variables

#### AI Models
- `OPENAI_MODEL`: Specifies the OpenAI model used (default: "gpt-4").
- `ANTHROPIC_API_KEY`: Your Anthropic API key for using Claude models.
- `ANTHROPIC_MODEL`: Specifies the Anthropic model (default: "claude-3-5-sonnet-20241022").

#### Telegram Settings
- `TELEGRAM_SESSION_NAME`: Session name for the Telegram bot (default: "little_turtle").
- `TELEGRAM_ALLOWED_USERS`: Comma-separated list of user IDs allowed to interact with the bot.
- `CHAT_IDS_TO_SEND_STORIES`: Comma-separated list of chat IDs for distributing stories.
- `USER_IDS_TO_SEND_MORNING_MSG`: Comma-separated list of user IDs for morning messages.

#### Phoenix Telemetry
- `PHOENIX_COLLECTOR_ENDPOINT`: Endpoint for Phoenix telemetry collector.
- `PHOENIX_PROJECT_NAME`: Project name for Phoenix telemetry (default: "little-turtle").
- `PHOENIX_ENABLED`: Enable/disable Phoenix telemetry (default: true).

#### Other Settings
- `REDIS_URL`: Connection string for Redis (default: "redis://localhost:6379/0").
- `GENERATION_LANGUAGE`: Language for story generation (default: "Russian").
- `DEFAULT_TZ`: Default timezone offset (default: 3).
- `DEFAULT_SCHEDULE_HOUR`, `DEFAULT_SCHEDULE_MINUTE`, `DEFAULT_SCHEDULE_SECOND`: Default scheduling time.
- `APPLICATION_TZ`: Application timezone (default: "Europe/Warsaw").
- `DEBUG`: Enable debug mode (default: false).
- `LOGS_LEVEL`: Logging level (default: "INFO").

## Usage

### Telegram Commands
- `/start` - Welcomes the user and provides an introduction to the bot.
- `/story` - Generates and shares a new story.
- `/get_next_date` - Provides the next story's date based on the list of posts scheduled on the Telegram channel.
- `/suggest_topics` - Suggests a list of potential topics to write about based on the date.
- `/reset_target_topics` - Clears the list of target topics.
- `/set_date` - Save the replied date as the story's date.
- `/set_story` - Saves the replied text as the story.
- `/set_image` - Saves the replied image as the story's image.
- `/add_target_topic` - Adds the replied text as a target topic.
- `/set_target_topic` - Set the replied text as the target topic.
- `/preview` - Previews an upcoming story.
- `/schedule` - Schedules the story to be posted on the Telegram channel.
- `/state` - Print the current status of the story.
- `/cancel` - Cancels the current story.
- `/ping` - Checks if the bot is active.

## License

Little Turtle is released under the MIT License. See the [LICENSE](LICENSE) file for more details.
