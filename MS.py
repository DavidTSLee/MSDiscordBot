# 갤길용 디스코드 봇 (WIP):
# TODO:
#   - process bot commands and allow multiple guild (channels) to have their own prefixes
#   - Carries (Bus driver) can create a scheduled carry which other users can register into
#   - Maintain guild's character info (main/alt/mules)
#   - Allow users to set up instance for party finder for daily quests (muto, spectrum ,CPQ)
#   - Responds to bot-specific queries and allow admin to add their own commands
#   - Allow users to opt-in for reset ping
#   Stretch goal: show when server closes need research on this

from datetime import datetime
from pytz import timezone
import asyncio
import json
from discord.ext import commands
import sys
from discord import channel

client = commands.Bot(command_prefix='$')

# Channels
time_channel = 733246332046802944
text_channel = 733247587473293352
flag_channel = 735257240772149258
party_channel = 739122711627825192


# Roles
member_id = 735261202887999548

utc_flags = [11, 18, 20, 21, 22]
TIME_ZONE_LIST = ['UTC','KST','EST','EDT','PST','PDT']

TIME_ZONE = {
    'KST': timezone('Asia/Seoul'),
    'EST': timezone('America/New_York'),
    'EDT': timezone('America/New_York'),
    'PST': timezone('America/Los_Angeles'),
    'PDT': timezone('America/Los_Angeles')
}

@client.event
async def on_ready():
    print("Logged on as {0}.".format(client.user))

@client.event
async def on_message(message):
    test_channel = client.get_channel(276587544966332417)
    print("message from {0.author}: {0.content}".format(message))
    if client.user != message.author:
        print(message.content)
        if "ㅈㄹ" in message.content:
            await test_channel.send("Logging Off")
            await client.logout()
            await client.close()
            client.clear()
    await client.process_commands(message)

@client.command(name="종료")
async def _close(ctx):
    print("종료")
    await ctx.send("Logging Off")

@client.command(name="보스")
async def _boss(ctx, *args):
    # command for boss related party
    # Syntax:
    #   $보스
    #   - Show description/how to use
    #   $보스 버스 스데미 목 14시 KST
    #   - Create lomien carry party instance at Thursday 2PM KST
    #       - boss carry names are free form, variations may work 스데미/로미엔, 카룻/카루타
    #       - Time zone used to convert to various time zones. (Default: UTC).
    #                              Supported timezone: UTC, KST, EST, PST, AEST
    #       - Time in 24 hr (00:00 to 23:59) 2시30분, 5:40 are both valid input
    #   $보스 트라이 스데미 목 14시 KST
    #   - Create lomien struggle party instance at Thursday 2PM KST
    #       rest are same as above
    # EXCEPTION:
    #   - wrong command:
    #       ex) $보스 버스 스데미
    #              - send "Wrong syntax"
    #       ex2) $보스 트라이 스데미 목 25시
    #               - send "time not in range"
    channel = client.get_channel(party_channel)
    if len(args) == 0:
        await channel.send("```사용법 (괄호없이, []괄호 입력은 선택):\n-\t"
                           "$보스 버스/트라이 (보스이름) (요일) (시간) [시간대]\n\t\t"
                           "- 시간대 입력이 없을경우 기본 UTC로 설정 \n\t\t\t"
                           "예: $보스 버스 스데미 목 00시15분 KST \n\t\t\t"
                           "예2: $보스 트라이 루시드 수 7시```")
    else:
        party_type = args[0]
        boss_name = args[1]
        day = args[2]
        hour, minute = parse_time(args[3])
        time_zone = "UTC" if len(args) < 5 else args[4]
        if time_zone.upper() not in TIME_ZONE_LIST:
            print(time_zone.upper())
            await ctx.send("오류: 알수없는 시간대 입니다.")
        else:
            print(ctx.author)
            party_date = parse_date(time_zone, day, hour, minute)
            # print("{} {} {} {} {}".format(boss_name, day, hour, minute, time_zone))
            # with open('data.json') as json_file:
            #     data = json.load(json_file)
            # if data[str(ctx.guild)]:



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
        utc_time = utc.localize(datetime.utcnow())
        ping_channel = client.get_channel(flag_channel)
        if utc_time.minute == 50 and utc_time.hour in utc_flags:
            message = await ping_channel.send("<@&{}> 10분 뒤 7시 플래그 레이스가 시작 됩니다.".format(member_id)) if utc_time.hour == 18 else await ping_channel.send("<@&{}> 10분 뒤 9시 플래그 레이스가 시작 됩니다".format(member_id))
            print("RACE TIME")
        elif utc_time.minute == 50 and utc_time.hour == 23:
            message = await ping_channel.send("<@&{}> 10분 뒤 리셋입니다".format(member_id))

        # Edit channel name to show UTC time
        formatted_utc = "{}월{}일ㅣ{}시{}분".format(utc_time.month, utc_time.day, utc_time.hour, utc_time.minute)
        full_string = "🕧{}".format(formatted_utc)
        await test_channel.edit(name=full_string)

# background task
async def chat_loop():
    await client.wait_until_ready()
    test_channel = client.get_channel(text_channel)

    while not client.is_closed():
        # Check if there is bot messages. If there is bot message, edit that. If not, send a new message
        bot_msg = await test_channel.history().find(is_bot)

        # Get time in multiple time zone
        utc = timezone('UTC')
        utc_time = utc.localize(datetime.utcnow())
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
    eastern_time = utc_time.astimezone(TIME_ZONE['EST'])
    pacific_time = utc_time.astimezone(TIME_ZONE['PST'])
    kor_time = utc_time.astimezone(TIME_ZONE['KST'])
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

def parse_time(time):
    # check for time and minute and its validity
    hour = time[0:time.index("시")]
    minute = time[time.index("시")+1:len(time) - 1] if "분" in time else 0
    return hour, minute

def parse_date(time_zone, day, hour, minute):
    curr_time = datetime.utcnow()
    if time_zone != "UTC":
        curr_time.astimezone(TIME_ZONE[time_zone])
    new_time = 
    curr_time.hour = hour
    print(curr_time)


client.loop.create_task(time_loop())
client.loop.create_task(chat_loop())

client.run(sys.argv[1])
