import asyncio
from ewelink import EWeLink
from ewelink.types import AppCredentials, EmailUserCredentials

APP_CREDENTIALS = AppCredentials(
    id="APP_ID",        # app id из eWeLink Open Platform
    secret="APP_SECRET" # app secret оттуда же
)

USER_CREDENTIALS = EmailUserCredentials(
    email="b.oris.ka@ukr.net",
    password="k0r0stel"
)

async def main():
    api = EWeLink(app=APP_CREDENTIALS, user=USER_CREDENTIALS)
    await api.login()

    devices = await api.get_devices()
    print(devices)

    # допустим, у розетки deviceid = "1000abcd1234"
    plug = await api.get_device("1000abcd1234")

    # включить
    await plug.on()

    # выключить
    await plug.off()

asyncio.run(main())
