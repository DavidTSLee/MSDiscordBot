# 갤길용 디스코드 봇 (WIP):
# TODO:
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

# Channels
time_channel = 733246332046802944
text_channel = 733247587473293352
flag_channel = 735257240772149258


# Roles
member_id = 735261202887999548

utc_flags = [11, 18, 20, 21, 22]


@client.event
async def on_ready():
    print("Logged on as {0}.".format(client.user))


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
    await client.wait_until_ready()
    test_channel = client.get_channel(time_channel)
    while not client.is_closed():
        utc = timezone('UTC')
        utc_time = utc.localize(datetime.utcnow())
        wait_sec = 60*(10-(utc_time.minute%10))
        await asyncio.sleep(wait_sec)

        # ping for race if it is 10 minutes prior to race time
        ping_channel = client.get_channel(flag_channel)
        if utc_time.minute == 50 and utc_time.hour in utc_flags:
            message = await ping_channel.send("<@&{}> 10분 뒤 7시 플래그 레이스가 시작 됩니다.".format(member_id)) if utc_time.hour == 18 else await ping_channel.send("<@{}> 10분 뒤 9시 플래그 레이스가 시작 됩니다".format(member_id))
            print("RACE TIME")

        # Edit channel name to show UTC time
        formatted_utc = "{}월{}일ㅣ{}시{}분".format(utc_time.month, utc_time.day, utc_time.hour, utc_time.minute)
        full_string = "🕧{}".format(formatted_utc)
        await test_channel.edit(name=full_string)

async def chat_loop():
    await client.wait_until_ready()
    test_channel = client.get_channel(text_channel)

    while not client.is_closed():
        # Check if there is bot messages. If there is bot message, edit that. If not, send a new message
        bot_msg = await test_channel.history().find(is_bot)

        # Get time in multiple time zone
        utc = timezone('UTC')
        utc_time = utc.localize(datetime.utcnow())
        print(utc_time.weekday())
        time_collection = return_times(utc_time)
        formatted_string = format_time_string(time_collection)
        formatted_string = add_reset_time(formatted_string, utc_time)

        result_msg = await bot_msg.edit(content=formatted_string) if bot_msg else \
            await test_channel.send(formatted_string)
        await asyncio.sleep(300)

def format_time_string(msg_list):
    ret_string = ""
    for msg in msg_list:
        ret_string += "{}\t{}월{}일 \t| \t{}시{}분 \r\n".format(msg[0], msg[1].month,
                                                            msg[1].day, msg[1].hour, msg[1].minute)
    return ret_string

def return_times(utc_time):
    eastern_time = utc_time.astimezone(timezone("America/New_York"))
    pacific_time = utc_time.astimezone(timezone("America/Los_Angeles"))
    kor_time = utc_time.astimezone(timezone('Asia/Seoul'))
    return [("서버     ", utc_time), ("한국    ",kor_time),("미동부", eastern_time), ("미서부",pacific_time)]

def is_bot(message):
    return message.author.bot

def add_reset_time(string, time):
    # Show # of hours remaining until daily reset and weekly reset
    daily_reset_hr = 23 - time.hour
    daily_reset_minute = 60 - time.minute
    daily_reset_str = "{}시간 {}분 뒤".format(daily_reset_hr, daily_reset_minute) if daily_reset_hr != 0 \
        else "{}분 뒤".format(daily_reset_minute)
    weekly_reset_day = (2 - time.weekday()) % 7
    weekly_reset_str = "{}일 {}".format(weekly_reset_day, daily_reset_str) if weekly_reset_day != 0 \
        else "{}".format(daily_reset_str)
    ret_string = "{}\n일간 리셋: {}\n주간 리셋: {}".format(string,daily_reset_str, weekly_reset_str)
    return ret_string


client.loop.create_task(time_loop())
client.loop.create_task(chat_loop())
client.run(sys.argv[1])
