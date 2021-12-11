# Source https://github.com/bwmarrin/discordgo/blob/master/endpoints.go

API_VERSION = 9

ENDPOINT_DISCORD = "https://discord.com/"
ENDPOINT_API = f"{ENDPOINT_DISCORD}api/{API_VERSION}/"

ENDPOINT_GUILDS = f"{ENDPOINT_API}guilds/"
ENDPOINT_CHANNELS = f"{ENDPOINT_API}channels/"
ENDPOINT_USERS = f"{ENDPOINT_API}users/"

ENDPOINT_GATEWAY = f"{ENDPOINT_API}gateway"
ENDPOINT_GATEWAY_BOT = f"{ENDPOINT_GATEWAY}/bot"
