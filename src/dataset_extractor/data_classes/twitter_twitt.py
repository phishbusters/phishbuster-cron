from dataclasses import dataclass


@dataclass
class TwitterTweet:
    rest_id: str
    user_id: str
    full_text: str
    created_at: str
    retweet_count: int
    favorite_count: int
    reply_count: int
    lang: str
    in_reply_to_status_id_str: str
    hashtags: list[str]
    user_mentions: list[str]
    urls: list[str]
    sentiment: str = ''

    @classmethod
    def from_payload(cls, payload):
        legacy_data = payload.get('legacy', {})
        entities_data = legacy_data.get('entities', {})
        return cls(rest_id=payload.get('rest_id', ''),
                   user_id=legacy_data.get('user_id_str', ''),
                   full_text=legacy_data.get('full_text', ''),
                   created_at=legacy_data.get('created_at', ''),
                   retweet_count=legacy_data.get('retweet_count', 0),
                   favorite_count=legacy_data.get('favorite_count', 0),
                   reply_count=legacy_data.get('reply_count', 0),
                   lang=legacy_data.get('lang', ''),
                   in_reply_to_status_id_str=legacy_data.get(
                       'in_reply_to_status_id_str', ''),
                   hashtags=[
                       tag['text']
                       for tag in entities_data.get('hashtags', [])
                   ],
                   user_mentions=[
                       mention['id_str']
                       for mention in entities_data.get('user_mentions', [])
                   ],
                   urls=[
                       url['expanded_url']
                       for url in entities_data.get('urls', [])
                   ])
