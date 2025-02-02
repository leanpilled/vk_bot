from vk import VKBotService
import asyncio
from settings import settings
import signal
import sys
import logging

if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    bot = VKBotService(settings)

    signals = (signal.SIGTERM, signal.SIGINT)
    for s in signals:
        loop.add_signal_handler(
            s, bot.stop_gracefully
        )

    loop.create_task(bot.run())
    loop.run_forever()
