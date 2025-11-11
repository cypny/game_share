from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.ext.asyncio import async_sessionmaker

from game_share_bot.scheduler.job_container import job_container
from game_share_bot.scheduler.job_list import JOBS


def get_scheduler(
        db_conn_string_sync: str,
        bot,
        session_maker: async_sessionmaker) -> AsyncIOScheduler:
    job_container.init(session_maker, bot)

    # пока убрал, так как они в бд сохраняются, и чтобы удалить или поменять название надо туда лезть
    # jobstores = {"default": SQLAlchemyJobStore(url=db_conn_string_sync)}
    jobstores = {}
    scheduler = AsyncIOScheduler(jobstores=jobstores)

    for job in JOBS:
        func = job["func"]
        scheduler.add_job(func, replace_existing=True, **{k: v for k, v in job.items() if k != "func"})

    return scheduler
