from sqlalchemy.ext.asyncio import async_sessionmaker


class JobContainer:
    def __init__(self):
        self._session_maker = None
        self._bot = None

    def init(self, session_maker, bot):
        self._session_maker = session_maker
        self._bot = bot

    @property
    def session_maker(self):
        if self._session_maker is None:
            raise RuntimeError("JobContainer not initialized")
        return self._session_maker
    @property
    def bot(self):
        if self._bot is None:
            raise RuntimeError("JobContainer not initialized")
        return self._bot

job_container = JobContainer()