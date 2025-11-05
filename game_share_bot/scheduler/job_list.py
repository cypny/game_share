from game_share_bot.scheduler.jobs.queue import update_queue_to_rental

JOBS = [
    {
        "func": update_queue_to_rental,
        "trigger": "interval",
        "seconds": 3,
        "id": "update_queue"
    }
]