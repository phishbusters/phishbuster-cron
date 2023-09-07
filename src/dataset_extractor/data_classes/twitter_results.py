from .twitter_user import TwitterUser
from typing import List, Union
from dataclasses import dataclass

@dataclass
class SearchResultItem:
    pass

@dataclass
class SearchUserItem(SearchResultItem):
    user: TwitterUser

@dataclass
class SearchTweetItem(SearchResultItem):
    tweet_id: str
    # ... otros campos relevantes para un tweet

@dataclass
class SearchResults:
    items: List[Union[SearchUserItem, SearchTweetItem]]
    has_next_page: bool
    cursor_endpoint: str

    @classmethod
    def from_payload(cls, payload):
        items = []
        for item in payload['data']:
            content = item['content']['itemContent']
            if 'user_results' in content:
                user = TwitterUser.from_payload(content['user_results']['result'])
                items.append(SearchUserItem(user))
            elif 'tweet_results' in content:
                # Aquí podrías crear e inicializar un objeto SearchTweetItem
                pass
        return cls(
            items=items,
            has_next_page=payload['has_next_page'],
            cursor_endpoint=payload['cursor_endpoint']
        )
