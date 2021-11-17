class Endpoints:
    API_VERSION = "9"

    ENDPOINT_DISCORD = "https://discord.com/"
    ENDPOINT_API = ENDPOINT_DISCORD + "api/v" + API_VERSION + "/"

    ENDPOINT_GATEWAY = ENDPOINT_API + "gateway"
    ENDPOINT_GATEWAY_BOT = ENDPOINT_GATEWAY + "/bot"