from typing import get_type_hints, Union


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
    TELEGRAM_ALLOWED_USERS: list[int]

    TURTLE_CHANNEL_ID: str = "young_turtle_in_hat"

    TNL_API_KEY: str

    DEBUG: bool = False

    def __init__(self, env):
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
                elif var_type == list[int]:
                    value = list(map(lambda item: int(item), self._parse_list(env.get(field, default_value))))
                elif var_type == list[str]:
                    value = self._parse_list(env.get(field, default_value))
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

    @staticmethod
    def _parse_list(val: Union[str, list]) -> list:
        match val:
            case str():
                if ',' not in val:
                    return [val]

                return val.split(',')

            case _:
                return val
