from game_share_bot.infrastructure.repositories.rental.queue_entry import QueueEntryRepository
from game_share_bot.infrastructure.utils import get_logger
from game_share_bot.scheduler.global_vars import job_container

async def update_queue():
    logger = get_logger(__name__)
    async with job_container.session_maker() as session:
        logger.info("test")

