class StateSession:
    def __init__(self) -> None:
        max_message_count: int
        track_channels: bool = True
        track_emojis: bool = True
        track_members: bool = True
        track_roles: bool = True
        track_voice: bool = True
        track_presences: bool = True

        guild_map: dict = {}
        channel_map: dict = {}
        member_map: dict = {}