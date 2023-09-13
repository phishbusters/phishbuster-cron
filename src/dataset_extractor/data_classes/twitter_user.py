from dataclasses import dataclass


@dataclass
class TwitterUser:
    id: str
    name: str
    screen_name: str
    statuses_count: int
    followers_count: int
    friends_count: int
    favourites_count: int
    listed_count: int
    default_profile: bool
    default_profile_image: bool
    location: str
    description: str
    description_has_url: bool
    description_url: str
    followers_to_following_ratio: float
    verified_type: str
    verified: bool
    is_blue_verified: bool
    has_graduated_access: bool
    can_dm: bool
    media_count: int
    has_custom_timelines: bool
    has_verification_info: bool
    possibly_sensitive: bool
    profile_banner_https: str
    profile_image_url_https: str
    created_at: str

    @classmethod
    def from_payload(cls, payload):
        legacy_data = payload.get('legacy', {})
        urls = [
            url['expanded_url'] for url in legacy_data.get('entities', {}).get(
                'description', {}).get('urls', [])
        ]
        followers_count = legacy_data.get('followers_count', 0)
        friends_count = legacy_data.get('friends_count', 0)

        return cls(
            id=payload.get('rest_id', ''),
            name=legacy_data.get('name', ''),
            screen_name=legacy_data.get('screen_name', ''),
            statuses_count=legacy_data.get('statuses_count', 0),
            followers_count=followers_count,
            friends_count=friends_count,
            favourites_count=legacy_data.get('favourites_count', 0),
            listed_count=legacy_data.get('listed_count', 0),
            default_profile=legacy_data.get('default_profile', False),
            default_profile_image=legacy_data.get('default_profile_image',
                                                  False),
            location=legacy_data.get('location', ''),
            description=legacy_data.get('description', ''),
            description_has_url=bool(urls),
            description_url=','.join(urls) if urls else '',
            followers_to_following_ratio=followers_count /
            friends_count if friends_count != 0 else 0,
            verified_type=legacy_data.get('verified_type', ''),
            verified=legacy_data.get('verified', False),
            is_blue_verified=payload.get('is_blue_verified', False),
            has_graduated_access=payload.get('has_graduated_access', False),
            can_dm=legacy_data.get('can_dm', False),
            media_count=legacy_data.get('media_count', 0),
            has_custom_timelines=legacy_data.get('has_custom_timelines',
                                                 False),
            has_verification_info=payload.get('verification_info', ''),
            possibly_sensitive=legacy_data.get('possibly_sensitive', False),
            profile_banner_https=legacy_data.get('profile_banner_url', ''),
            profile_image_url_https=legacy_data.get('profile_image_url_https',
                                                    ''),
            created_at=legacy_data.get('created_at', '')
        )
