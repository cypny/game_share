from game_share_bot.scheduler.jobs.check_pending_subscriptions import check_pending_subscriptions
from game_share_bot.scheduler.jobs.notify_subscription_end import notify_subscription_end
from game_share_bot.scheduler.jobs.queue import update_queue_to_rental
from game_share_bot.scheduler.jobs.rental.cancel_pending_take import cancel_pending_take
from game_share_bot.scheduler.jobs.rental.notify_overdue_rentals import notify_overdue_rentals
from game_share_bot.scheduler.jobs.rental.notify_rental_end import notify_rental_end
from game_share_bot.scheduler.jobs.rental.update_to_overdue import update_to_overdue

JOBS = [
    {
        "func": update_queue_to_rental,
        "trigger": "interval",
        "minutes": 10,
        # "seconds": 5,
        "id": "update_queue_to_rental"
    },
    {
        "func": check_pending_subscriptions,
        "trigger": "interval",
        "minutes": 10,
        # "seconds": 5,
        "id": "check_pending_subscriptions"
    },
    {
        "func": notify_rental_end,
        "trigger": "cron",
        "hour": 9,
        "minute": 0,
        "id": "notify_rental_end"
    },
    {
        "func": update_to_overdue,
        "trigger": "cron",
        "hour": 8,
        "minute": 30,
        "id": "update_to_overdue"
    },
    {
        "func": notify_overdue_rentals,
        "trigger": "cron",
        "hour": 10,
        "minute": 0,
        "id": "notify_overdue_rentals"
    },
    {
        "func": notify_subscription_end,
        "trigger": "cron",
        "hour": 10,
        "minute": 0,
        "id": "notify_subscription_end"
    },
    {
        "func": cancel_pending_take,
        "trigger": "cron",
        "hour": 20,
        "minute": 0,
        "id": "notify_subscription_end"
    }

]