from apscheduler.schedulers.background import BackgroundScheduler
scheduler = BackgroundScheduler(daemon=True)
scheduler.start()
