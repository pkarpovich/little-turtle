from typing import get_type_hints, Union

from dotenv import load_dotenv


class AppConfigError(Exception):
    pass


class AppConfig:
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4"

    MONGODB_URI: str
    MONGODB_USERNAME: str
    MONGODB_PASSWORD: str
    MONGODB_DB_NAME: str = "little_turtle"

    TELEGRAM_BOT_TOKEN: str
    TELEGRAM_API_ID: int
    TELEGRAM_API_HASH: str
    TELEGRAM_PHONE_NUMBER: str
    TELEGRAM_SESSION_NAME: str = "little_turtle"

    TURTLE_CHANNEL_ID: str = "young_turtle_in_hat"

    def __init__(self, env):
        load_dotenv()

        for field in self.__annotations__:
            if not field.isupper():
                continue

            default_value = getattr(self, field, None)
            if default_value is None and env.get(field) is None:
                raise AppConfigError('The {} field is required'.format(field))

            var_type = get_type_hints(AppConfig)[field]
            try:
                if var_type == bool:
                    value = self._parse_bool(env.get(field, default_value))
                else:
                    value = var_type(env.get(field, default_value))

                self.__setattr__(field, value)
            except ValueError:
                err_msg = 'Unable to cast value of "{}" to type "{}" for "{}" field'.format(
                    env[field],
                    var_type,
                    field
                )

                raise AppConfigError(err_msg)

    def __repr__(self):
        return str(self.__dict__)

    @staticmethod
    def _parse_bool(val: Union[str, bool]) -> bool:
        return val if type(val) == bool else val.lower() in ['true', 'yes', '1']
