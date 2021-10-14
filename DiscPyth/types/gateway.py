from ..ext import gopyjson as gpj


class Event(metaclass=gpj.Struct):
    operation = gpj.field("op")
    raw_data = gpj.field("d", raw_json=True)
    type = gpj.field("t", optional=True)
    seq = gpj.field("s", optional=True)


class Hello(metaclass=gpj.Struct):
    heartbeat = gpj.field("heartbeat_interval")
    # Jake said that I can ignore it tho
    # I will still assume its there, gopyjson already
    # assigns None at runtime so I dont have to worry
    # about anything
    # also since it may not exist 
    # we will just get the raw json   
    trace = gpj.field("_trace", raw_json=True)


class IdentifyProperties(metaclass=gpj.Struct):
    os = gpj.field("$os")
    browser = gpj.field("$browser")
    device = gpj.field("$device")


class Identify(metaclass=gpj.Struct):
    token = gpj.field("token")
    properties = gpj.field("properties")
    compress = gpj.field("compress")
    large = gpj.field("large_threshold")
    shard = gpj.field("shard")
    presence = gpj.field("presence", optional=True)
    intents = gpj.field("intents")


class Presence_Update(metaclass=gpj.Struct):
    pass


class Request_Guild_Members(metaclass=gpj.Struct):
    """
    guild_id
    query o
    limit
    presences o
    user_ids o
    nonce o
    """

    pass


class Resume(metaclass=gpj.Struct):
    token = gpj.field("token")
    ses_id = gpj.field("session_id")
    seq = gpj.field("seq")


class Voice_State_Update(metaclass=gpj.Struct):
    guild = gpj.field("guild_id")
    channel = gpj.field("channel_id")
    mute = gpj.field("self_mute")
    deaf = gpj.field("self_deaf")
