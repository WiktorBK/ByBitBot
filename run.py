from bot import Bot

from apscheduler.schedulers.background import BlockingScheduler

'''
Run main function every 3 seconds using apscheduler
'''

bot = Bot()
scheduler = BlockingScheduler(daemon=True)
scheduler.add_job(bot.run, 'interval', seconds=3)
scheduler.start()
