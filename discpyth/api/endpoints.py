API_VERSION = 10

# I mean,
# The gatewway url is literally hardcoded into the client
# so its no harm to save on an extra request just to get the url
#
# from the client (canary):
#
# window.GLOBAL_ENV = {
#         API_ENDPOINT: '//canary.discord.com/api',
#         API_VERSION: 9,
#         GATEWAY_ENDPOINT: 'wss://gateway.discord.gg',
#         WEBAPP_ENDPOINT: '//canary.discord.com',
#         CDN_HOST: 'cdn.discordapp.com',
#         ASSET_ENDPOINT: '//canary.discord.com',
#         MEDIA_PROXY_ENDPOINT: '//media.discordapp.net',
#         WIDGET_ENDPOINT: '//canary.discord.com/widget',
#         INVITE_HOST: 'discord.gg',
#         GUILD_TEMPLATE_HOST: 'discord.new',
#         GIFT_CODE_HOST: 'discord.gift',
#         RELEASE_CHANNEL: 'canary',
#         MARKETING_ENDPOINT: '//canary.discord.com',
#         BRAINTREE_KEY: 'production_5st77rrc_49pp2rp4phym7387',
#         STRIPE_KEY: 'pk_live_CUQtlpQUF0vufWpnpUmQvcdi',
#         NETWORKING_ENDPOINT: '//router.discordapp.net',
#         RTC_LATENCY_ENDPOINT: '//latency.discord.media/rtc',
#         ACTIVITY_APPLICATION_HOST: 'discordsays.com',
#         PROJECT_ENV: 'production',
#         REMOTE_AUTH_ENDPOINT: '//remote-auth-gateway.discord.gg',
#         SENTRY_TAGS: {"buildId":"228ea0b3a6f77c4d7d3623c9a095290601eb7997","buildType":"normal"},
#         MIGRATION_SOURCE_ORIGIN: 'https://canary.discordapp.com',
#         MIGRATION_DESTINATION_ORIGIN: 'https://canary.discord.com',
#         HTML_TIMESTAMP: Date.now(),
#         ALGOLIA_KEY: 'aca0d7082e4e63af5ba5917d5e96bed0',
#       };

GATEWAY_URL = (
    f"wss://gateway.discord.gg/?v={API_VERSION}&encoding=json&compress=zlib-stream"
)

API_BASE_URL = f"https://discord.com/api/v{API_VERSION}"

GATEWAY = f"{API_BASE_URL}/gateway"
GATEWAY_BOT = f"{API_BASE_URL}/gateway/bot"
