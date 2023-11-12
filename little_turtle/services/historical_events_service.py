from time import strptime

import requests


class HistoricalEventsService:
    url = 'https://api.wikimedia.org/feed/v1/wikipedia/ru/onthisday/events'

    @staticmethod
    def get_by_date(date: str) -> list[str]:
        date_obj = strptime(date, '%d.%m.%Y')

        base_url = f"{HistoricalEventsService.url}/{date_obj.tm_mon}/{date_obj.tm_mday}"
        response = requests.get(base_url)
        if response.status_code != 200:
            return list()

        data = response.json()
        return list(
            map(
                lambda x: f"{x['year']} {x['text']}",
                data['events']
            )
        )
