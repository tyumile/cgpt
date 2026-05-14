import asyncio
import logging

from app.modules.worker_poller.main import worker_loop

logging.basicConfig(level=logging.INFO)


async def main() -> None:
    await worker_loop()


if __name__ == "__main__":
    asyncio.run(main())
