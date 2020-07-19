# 갤길용 디스코드 봇 (WIP):
# TODO:
#   1) Show Time (UTC, update every 5 ~10 minutes)
#   2) Alert for flag
#   3) Show days/hours remaining until reset (daily/weekly)
#   Stretch goal: show when server closes need research on this

# from time import gmtime, strftime
from datetime import datetime
from pytz import timezone
import asyncio
from discord.ext import commands
import sys
from discord import channel

client = commands.Bot(command_prefix='.')


@client.event
async def on_ready():
    print("Logged on as {0}.".format(client.user))
#
#     test_channel = client.get_channel(276587544966332417)
#
#     timer_channel = client.get_channel(733246332046802944)
#     utc = timezone('UTC')
    # formatted_utc = "{}월{}일 | {}시{}분".format(utc_time.month, utc_time.day, utc_time.hour, utc_time.minute)
    # await client.wait_until_ready()
    # await timer_channel.edit(name="🕧{}".format(formatted_utc))

    # for c in client.get_all_channels():
    #     print(c)
    # await test_channel.send("Currect time: {0}".format(time.gmtime()))


@client.event
async def on_message(message):
    test_channel = client.get_channel(276587544966332417)
    print("message from {0.author}: {0.content}".format(message))
    if client.user != message.author:
        # await test_channel.send("{0} No Thanks".format(message.author.mention))
        await test_channel.send("Logging Off")
        await client.logout()
        await client.close()
        client.clear()


# background task
async def time_loop():
    rest_time = 600
    await client.wait_until_ready()
    test_channel = client.get_channel(733246332046802944)
    while not client.is_closed():
        print("LOOPING")
        utc = timezone('UTC')
        utc_time = utc.localize(datetime.utcnow())
        # eastern_time, pacific_time, kor_time = return_times(utc_time)
        formatted_utc = "{}월{}일 ㅣ {}시{}분".format(utc_time.month, utc_time.day, utc_time.hour, utc_time.minute)
        full_string = "🕧{}".format(formatted_utc)
        await test_channel.edit(name=full_string)
        await asyncio.sleep(600)

async def chat_loop():
    await client.wait_until_ready()
    test_channel = client.get_channel(733247587473293352)

    while not client.is_closed():
        # Check if there is bot messages. If there is bot message, edit that. If not, send a new message
        bot_msg = await test_channel.history().find(is_bot)

        # Get time in multiple time zone
        utc = timezone('UTC')
        utc_time = utc.localize(datetime.utcnow())

        time_collection = return_times(utc_time)
        formatted_string = format_time_string(time_collection)
        # print("formatted string: {}".format(formatted_string))

        # formatted_utc = "{}월{}일 | {}시{}분".format(utc_time.month, utc_time.day, utc_time.hour, utc_time.minute)
        # full_string = "🕧{}".format(formatted_utc)
        result_msg = await bot_msg.edit(content=formatted_string) if bot_msg else await test_channel.send(formatted_string)
        print("Result message: {}".format(result_msg))
        await asyncio.sleep(30)

def format_time_string(msg_list):
    ret_string = ""
    for msg in msg_list:
        ret_string += "{}\t{}월{}일 \t| \t{}시{}분 \r\n".format(msg[0], msg[1].month, msg[1].day, msg[1].hour, msg[1].minute)
    return ret_string

def return_times(utc_time):
    eastern_time = utc_time.astimezone(timezone("America/New_York"))
    pacific_time = utc_time.astimezone(timezone("America/Los_Angeles"))
    kor_time = utc_time.astimezone(timezone('Asia/Seoul'))
    return [("서버     ", utc_time), ("한국    ",kor_time),("미동부", eastern_time), ("미서부",pacific_time)]

def is_bot(message):
    return message.author.bot


# client.loop.create_task(time_loop())
client.loop.create_task(chat_loop())
client.run(sys.argv[1])