from game_share_bot.scheduler.jobs.check_pending_subscriptions import check_pending_subscriptions
from game_share_bot.scheduler.jobs.queue import update_queue_to_rental

JOBS = [
    {
        "func": update_queue_to_rental,
        "trigger": "interval",
        "minutes": 10,
        "id": "update_queue"
    },
    {
        "func": check_pending_subscriptions,
        "trigger": "interval",
        "minutes": 10,
        "id": "check_pending_subscriptions"
    }
]