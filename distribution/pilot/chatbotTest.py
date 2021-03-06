#encoding: utf-8

import csv
from wxpy import *
from datetime import datetime, timedelta
import time
import pandas as pd
import requests
from bs4 import BeautifulSoup
from io import StringIO
from hashids import Hashids
import numpy as np
from math import floor
from random import randint, uniform

# Get date
now = datetime.now() + timedelta(hours = 4) # Convert to GMT

# Test? (YES / NO)
test = input("\nAre you testing (YES / NO) ?\n")

# What to do? (6PM / 10PM / pre-walkathon / post-walkathon)
todo = input("\nWhat to do (6PM / 10PM / pre-walkathon / post-walkathon) ?\n")
if todo == "pre-walkathon" or todo == "post-walkathon" :
    walkathon_cohort = input("\nSend walkathon messsages to which cohort (1 ... ∞) ?\n")

# Which cohort?
cohort = input("\nAdd new users to which cohort (1 ... ∞) ?\n")

# If to send out day 7 and day 8
cohort_to_send = 2
todo_day7 = (now.strftime("%m/%d/%Y") == "05/26/2019")
todo_day8 = (now.strftime("%m/%d/%Y") == "06/08/2019")
cohort_day7 = datetime(2019, 5, 26)
cohort_day8 = datetime(2019, 6, 8)

# If to send out before walkathon on day 8 8am - 9am TODO change time
# send_before_walkathon =  (now.strftime("%m/%d/%Y %H") == "06/08/2019 08")

# Assign probability for each treament group, sum to 1
treat_no = [1, 2, 3, 4, 5]
treat_prob = [0.2, 0.2, 0.2, 0.2, 0.2]

# Message content
if cohort == "1":
    date_range = u'2019年5月13-19日'
elif cohort == "2":
    date_range = u'2019年6月3-9日'

# Canned WeChat scripts
default = u'我们会尽快回复您的消息。此账号不具备实时交流的功能，预计回复您的时间会有延迟。 这是一条自动消息。'
intro = u'  此次调研总共维持8天时间。\
我们将在接下来的6天（包括今天）每天提供一些将在 '+ date_range +' 举办的户外活动信息，\
并询问一些简短的问题（约5分钟）。第7天和第8天的调研将在 2周和4周 后进行。\n\n\
  我们也将会询问您一些关于各类话题的问题。 如果您想参加这项学术调研，请点击以下链接开始。\
您的回答仅被用于学术研究，我们将对您的个人信息及回答进行严格保密。\
调研结束后我们将进行抽奖，所有参与并完成调研的同学将有机会赢得800元人民币作为奖励。\
这是一条自动消息。'
title = u'  请点击下面的链接。'
same_day_reminder = u'  看上去您还没有完成今天的调研。 请您点击链接，参与不到五分钟的调研。\
如果您在每天晚上12点前完成调研，您将有机会参与赢得800元人民币的抽奖，并收到来自哈佛大学研究员出具的参与证明。'
next_day_reminder = u'  您没有完成昨天的调查。我们理解您可能有别的事在忙。我们将再给您一整天的时间来完成昨天的调研。\
如您所知，只有在完成所有8天 的调研后，您才有机会参与赢得800元人民币的抽奖，并收到来自哈佛大学研究员的参与证明。这里是链接！'
reminder = u'  看上去您还没有完成今天的调研。 请您点击链接，参与不到五分钟的调研。'
installWeRun = u'在您的手机上开启微信运动：请您点击开启。\n\
- 您可以打开“进入我的主页”选项查看自己的当前步数\n\
- 每晚十点，微信运动将发送您当天的步数排行和您微信好友的步数。您可以看到所有开启微信运动好友的每日步数\n\
- 我们将以您微信运动上的步数作为活动当天您的步行结果。'
URLmessage = [u'',u'']
URLmessage.append(u'  今天是调研第二天。 请点击下面的链接开始，同时了解另一个精彩的本地活动。 这是一条自动消息。')
URLmessage.append(u'  今天是调研第三天。 请点击下面的链接开始，同时了解另一个精彩的本地活动。 这是一条自动消息。')
URLmessage.append(u'  今天是调研第四天。 请点击下面的链接开始，同时了解另一个精彩的本地活动。 这是一条自动消息。')
URLmessage.append(u'  今天是调研第五天。 请点击下面的链接开始，同时了解另一个精彩的本地活动。 这是一条自动消息。')
URLmessage.append(u'  今天是调研第六天，今天的调研问卷会比平时稍长一些。 但我们将涵盖更多精彩的活动，其中包括我们自己举办的活动！ 我们非常重视今天的调研，所以请您花些时间仔细回答每个问题。')
URLmessage.append(u'  好久不见！今天是调研的第7天。我们就快要完成所有调研了！')
URLmessage.append(u'  今天是调研的最后一天。 如果您完成今天的简短问卷，您将有赢得800元人民币的机会。我们还将向您提供哈佛大学研究员出具的参与证明。')

# Get current list of activities, as pandas dataframe
def get_activities():
    page = requests.get("https://dailyeventinfo.com/allActivities").text
    soup = BeautifulSoup(page, "html.parser")
    divList = soup.findAll('div', attrs={"class" : "list"})
    data=','.join(['user_id','day','day_complete','survey_page','day_started','curr_time'])
    for div in divList:
        data = data + '\n' + ' '.join(div.text.split())
    csv_data = StringIO(data)
    df = pd.read_csv(csv_data)
    df = df[pd.notnull(df['user_id'])]
    df['user_id']=df['user_id'].astype(int)
    return df

def get_results():
    page = requests.get("https://dailyeventinfo.com/allResults").text
    soup = BeautifulSoup(page, "html.parser")
    divList = soup.findAll('div', attrs={"class" : "about"})
    data=','.join(['user_id', 'day', 'question_id', 'result', 'created'])
    for div in divList:
        data = data + '\n' + ' '.join(div.text.split())
    csv_data = StringIO(data)
    df = pd.read_csv(csv_data)
    df = df[pd.notnull(df['user_id'])]
    df['user_id']=df['user_id'].astype(int)
    return df

def duration_till_now(then):
    then = datetime.strptime(then, '%Y-%m-%d %H:%M:%S.%f')
    duration = now - then
    return duration

def exclude_dropout(all_users):
    # dropout after 6 reminders (including 6PM and 10PM)
    # i.e., now - last survey result timestamp > 3 days or,
    #       now - activity timestamp > 10 hours
    results = get_results()
    last_results = results.drop_duplicates(subset='user_id', keep='last')
    last_results = last_results.assign(duration=last_results['created'].apply(duration_till_now))
    # for day 1-5 & 8, drop if > 3 days
    dropout_day = last_results.loc[np.logical_and(last_results.day.isin([1,2,3,4,5,8]), last_results.duration > timedelta(days=3))]
    valid_users = all_users[~all_users.user_id.isin(dropout_day['user_id'].tolist())]
    # for day 6 and 7, drop if > 14 + 3 = 17 days
    # dropout_2wks = last_results.loc[np.logical_and(last_results.day.isin([6,7]), last_results.duration > timedelta(days=17))] # TODO enable later
    # valid_users = valid_users[~valid_users.user_id.isin(dropout_2wks['user_id'].tolist())]
    # still drop user if attemp after 6pm (day after 6th reminder is sent)
    activities = get_activities()
    last_acitivites = activities.assign(duration=activities['curr_time'].apply(duration_till_now))
    # for day 1-5 & 8, drop if > 10 hours
    dropout_overdue = last_acitivites.loc[np.logical_and(last_acitivites.day.isin([1,2,3,4,5,8]), last_acitivites.duration > timedelta(hours=10))]
    valid_users = valid_users[~valid_users.user_id.isin(dropout_overdue['user_id'].tolist())]
    return valid_users

def exclude_completed(all_users):
    activities = get_activities()
    completed = activities.loc[(activities['day_complete'] == 1) & (activities['day'] == 8)]
    completed_user_list = completed['user_id'].tolist()
    non_completed = all_users[~all_users.user_id.isin(completed_user_list)]
    return non_completed

def get_users():
    page = requests.get("https://dailyeventinfo.com/allUsers").text
    soup = BeautifulSoup(page, "html.parser")
    divList = soup.findAll('div', attrs={"class" : "list"})
    data=','.join(['user_id','day','wechat_id','cohort','treatment','user_id_hashid','day_hashid'])
    for div in divList:
        data = data + '\n' + ' '.join(div.text.split())
    csv_data = StringIO(data)
    df = pd.read_csv(csv_data)
    df = df[pd.notnull(df['user_id'])]
    df['user_id']=df['user_id'].astype(int)
    # exclude dropouts
    df = exclude_dropout(df)
    # exclude completed
    df = exclude_completed(df)
    return df

# # initialize chatbot
# bot = Bot()
# bot.enable_puid('wxpy_puid.pkl')


# ##############################################################################################
# # auto accept friend request
# @bot.register(msg_types=FRIENDS)
# def auto_accept_friends(msg):
#
#     ## Accept request
#     new_friend = msg.card.accept()
#     nextUserID = int((floor(get_activities()['user_id'].dropna().max()/1e6)+1)*1e6+randint(1,999999)) # Next user's ID
#     print(nextUserID)
#
#     ## Deal with too many users in a cohort
#     users = get_users()
#     cohortCount = int(len(users.loc[users.cohort == cohort])/9)
#     if cohortCount > 120:
#         new_friend.send("Current round of recruitment is finished. We will message you as soon as the next round begins!") ## Please write this in Chinese?
#         new_friend.set_remark_name("WL_"+str(nextUserID))
#     else:
#         ## Get wxid (assuming that this is the unique ID we can use)
#         userName = new_friend.user_name[1:]
#
#     # Check whether existing user TODO
#
#     # Create hashes for the new user, save in user db, create new activity
#     nextUserID = int((floor(get_activities()['user_id'].dropna().max()/1e6)+1)*1e6+randint(1,999999)) # Next user's ID
#     treatment = "T"+str(choices(treat_no, treat_prob)[0])
#     print("adding new user", nextUserID, "assigning treatment", treatment, "...")
#     for day in range(9):
#         user_id_hashids = Hashids(salt=str(10 * nextUserID + day) + "user_id", min_length=16)
#         day_hashids = Hashids(salt=str(10 * nextUserID + day) + "day", min_length=10)
#         hashed_user_id = user_id_hashids.encrypt(nextUserID)
#         hashed_day = day_hashids.encrypt(day)
#         requests.post("https://dailyeventinfo.com/userInsert/"+str(nextUserID)+"/"+
#             str(day)+"/"+str(userName)+"/"+ str(cohort) + "/" + str(treatment) +"/"+hashed_user_id+"/"+hashed_day)
#     requests.post("https://dailyeventinfo.com/activityUpdate/"+str(nextUserID)+"/0/0/0/0/0")
#
#     # Send intro message
#     day = 0
#     user_id_hashids = Hashids(salt=str(10 * nextUserID + day) + "user_id", min_length=16)
#     day_hashids = Hashids(salt=str(10 * nextUserID + day) + "day", min_length=10)
#     hashed_user_id = user_id_hashids.encrypt(nextUserID)
#     hashed_day = day_hashids.encrypt(day)
#     sendURL = "https://dailyeventinfo.com/" + hashed_user_id.strip() + "/" + hashed_day.strip() + "/info"
#     new_friend.send(intro)
#     new_friend.send(sendURL)
#
#     # Set remark_name to use for reminder messages
#     new_friend.set_remark_name(str(nextUserID))
##############################################################################################

##############################################################################################
# for sending day 7 and day 8
def sendDaySeven():
    # send out day 7, update activity
    if todo_day7:
        print("\n------------------------------------ Sending day 7 urls ------------------------------------")
        cohort_users = users.loc[users['cohort'] == cohort_to_send]
        send_list_day7_n = pd.merge(sorted_acts_day7_n, cohort_users, on=['user_id','day'])
        send_list_day7_n['url'] = "https://dailyeventinfo.com/" + send_list_day7_n['user_id_hashid'].str.strip() + "/" + send_list_day7_n['day_hashid'].str.strip() + "/survey"
        print("" if send_list_day7_n.empty else send_list_day7_n)
        # for i in range(send_list_day7_n.shape[0]):
        #     wechat_id = send_list_day7_n.iloc[i]['user_id']
        #     try:
        #         my_friend = bot.friends().search(remark_name=str(wechat_id))[0]
        #         print('sending 6PM day7 message to',wechat_id,'...')
        #         my_friend.send(URLmessage[7])
        #         my_friend.send(send_list_day7_n.iloc[i]['url'])
        #         time.sleep(2)
        #         #Update activity for new day URL
        #         requests.post("https://dailyeventinfo.com/activityUpdate/"+str(int(send_list_day7_n['user_id'].iloc[i]))+"/"+str(7)+"/0/0/0/0")
        #     except IndexError:
        #         print('cannot find user',wechat_id,'...')

def sendDayEight():
    # send out day 8, update activity
    if todo_day8:
        print("\n------------------------------------ Sending day 8 urls ------------------------------------")
        cohort_users = users.loc[users['cohort'] == cohort_to_send]
        send_list_day8_n = pd.merge(sorted_acts_day8_n, cohort_users, on=['user_id','day'])
        send_list_day8_n['url'] = "https://dailyeventinfo.com/" + send_list_day8_n['user_id_hashid'].str.strip() + "/" + send_list_day8_n['day_hashid'].str.strip() + "/survey"
        print("" if send_list_day8_n.empty else send_list_day8_n)
        # for i in range(send_list_day8_n.shape[0]):
        #     wechat_id = send_list_day8_n.iloc[i]['user_id']
        #     try:
        #         my_friend = bot.friends().search(remark_name=str(wechat_id))[0]
        #         print('sending 6PM day8 message to',wechat_id,'...')
        #         my_friend.send(URLmessage[8])
        #         my_friend.send(send_list_day8_n.iloc[i]['url'])
        #         time.sleep(2)
        #         #Update activity for new day URL
        #         requests.post("https://dailyeventinfo.com/activityUpdate/"+str(int(send_list_day8_n['user_id'].iloc[i]))+"/"+str(8)+"/0/0/0/0")
        #     except IndexError:
        #         print('cannot find user',wechat_id,'...')
##############################################################################################

##############################################################################################
# for walkathon
def get_walkathon_list():
    # get users with walkathonSteps > 0 from day 7
    results = get_results()
    results_day7 = results.loc[results['day'] == 7]
    walkathon_steps = results_day7.loc[results_day7['question_id'] == 'walkathonSteps']
    walkathon_list = walkathon_steps.loc[walkathon_steps['result'].astype(int) > 0]
    users = get_users()
    cohort_users = users.loc[users['cohort'] == int(walkathon_cohort)]
    cohort_walkathon_list = pd.merge(walkathon_list, cohort_users, on=['user_id','day'])
    return cohort_walkathon_list

if todo == "pre-walkathon":
    print("\n\n==================== Now it's day 8! Sending pre-walkathon instructions ====================\n")
    walkathon_list = get_walkathon_list()
    print(walkathon_list)

    for i in range(walkathon_list.shape[0]):
        wechat_id = walkathon_list.iloc[i]['user_id']
        step = walkathon_list.iloc[i]['result']
        donation = float(step) * 0.002

        try:
            # my_friend = bot.friends().search(remark_name=str(wechat_id))[0]
            # step = walkathon_list.iloc[i]['result']
            # donation = step * 0.002
            print('sending pre-walkathon message to',wechat_id,':', step, 'steps, ￥', donation)
#             beforeWalkathon = u'明天将是“儿童慈善徒步活动”的一天！ 您曾经承诺走 {0} 步。\
# 如果您步行超过 {0} 步，我们将捐赠 {1} 元人民币给上海联合基金会，这笔钱将用于支持贫困儿童成长。\
# 以下是关于如何参加活动的指引链接。 如果您还没有开启微信运动，您需要在手机上进行开启——别担心，这很容易！'.format(step, donation)
#             my_friend.send(beforeWalkathon)
#
#             # send WeRun-WeChat name card
#             my_friend.send_raw_msg(
#             raw_type=42,
#             # bot must be friend with WeRun-WeChat
#             raw_content='<msg username="WeRun-WeChat" nickname="微信运动"/>'
#             )
#             time.sleep(2)
#             my_friend.send(installWeRun)
        except IndexError:
            print('cannot find user',wechat_id,'...')

if todo == "post-walkathon":
    print("\n\n========================= Now it's day 8! Sending post-walkathon message ===================\n")
    walkathon_list = get_walkathon_list()
    print(walkathon_list)

    for i in range(walkathon_list.shape[0]):
        wechat_id = walkathon_list.iloc[i]['user_id']
        step = walkathon_list.iloc[i]['result']
        donation = float(step) * 0.002
        wechat_id = walkathon_list.iloc[i]['user_id']
        actual_step = input("{0} number of steps?  ".format(wechat_id))
        if int(actual_step) >= int(step):
            try:
                # my_friend = bot.friends().search(remark_name=str(wechat_id))[0]
                step = walkathon_list.iloc[i]['result']
                donation = step * 0.002
                print('--> reached', step, 'sending msg to',wechat_id,':', step, 'steps, ￥', donation)
                # afterWalkathhon = u'感谢您的参与——您走了 {0} 步，超过您的承诺步数。 感谢您，我们将捐赠 {1} 人民币给上海联合基金会。'.format(step, donation)
                # my_friend.send(afterWalkathon)
            except IndexError:
                print('cannot find user',wechat_id,'...')
##############################################################################################

##############################################################################################
# 10PM SAME-DAY REMINDER
if todo == "10PM":
    print("\n\n====================== Now it's 10PM! Sending 10PM same-day reminders ======================\n")
    # Get list of (user_id, day) to send reminders
    activities = get_activities()
    # activities['day_started'] = pd.to_datetime(activities['day_started'], format="%Y-%m-%d %H:%M:%S.%f") # Currently not using in the selection logic
    activities['curr_time'] = pd.to_datetime(activities['curr_time'], format="%Y-%m-%d %H:%M:%S.%f")
    activities['time_since_last_activity'] = (now - activities['curr_time']) / np.timedelta64(1, 'h')
    sorted_acts = activities.loc[activities['day_complete'] == 0]
    if test == "YES":
        sorted_acts = sorted_acts.loc[sorted_acts['user_id'] == 1882385] # Turn this off for test with Eliza's ID
    else:
        sorted_acts = sorted_acts.loc[sorted_acts['user_id'] >= 1882385] # Turn this on for test with Eliza's ID
        # Note: 104=Zixin, 105=Jie
    sorted_acts = sorted_acts.loc[sorted_acts['time_since_last_activity'] < 48].iloc[:,0:2]
    # drop all users who have not completed day 6 after day 7 is sent
    if now >= cohort_day7:
        sorted_acts = sorted_acts.loc[sorted_acts['day'] >= 7]
    # Search user list using (user_id, day), get wechat_id
    users = get_users()
    send_list = pd.merge(sorted_acts, users, on=['user_id','day'])
    send_list['url'] = "https://dailyeventinfo.com/" + send_list['user_id_hashid'].str.strip() + "/" + send_list['day_hashid'].str.strip() + "/info"
    print("" if send_list.empty else send_list)
    # # Send reminders
    # for i in range(send_list.shape[0]):
    #     wechat_id = send_list.iloc[i]['user_id']
    #     try:
    #         my_friend = bot.friends().search(remark_name=str(wechat_id))[0]
    #         print('sending 10PM reminder message to',wechat_id,'...')
    #         my_friend.send(reminder)
    #         my_friend.send(send_list['url'].iloc[i])
    #         time.sleep(2)
    #     except IndexError:
    #         print('cannot find user',wechat_id,'...')

##############################################################################################

##############################################################################################
# 6PM NEXT DAY URL + REMINDER IF NOT COMPLETED
if todo == "6PM":
    print("\n\n========== Now it's 6PM! Sending 6PM next-day urls + reminders if not completed: ===========")

    # Prep
    activities = get_activities()
    activities['day_started'] = pd.to_datetime(activities['day_started'], format="%Y-%m-%d %H:%M:%S.%f")
    activities['curr_time'] = pd.to_datetime(activities['curr_time'], format="%Y-%m-%d %H:%M:%S.%f")
    activities['time_since_last_activity'] = (now - activities['curr_time']) / np.timedelta64(1, 'h')
    users = get_users()

    # New day URL prep
    sorted_acts_n = activities.loc[activities['day_complete'] == 1]

    # only send to Eliza if test
    if test == "YES":
        sorted_acts_n = sorted_acts_n.loc[sorted_acts_n['user_id'] == 1882385] # Turn this on for test with Eliza's ID
    else:
        sorted_acts_n = sorted_acts_n.loc[sorted_acts_n['user_id'] >= 1882385] # Turn this off for test with Eliza's ID

    # if Day > 6: wait till time
    sorted_acts_n['day'] = sorted_acts_n['day'] + 1
    sorted_acts_day7_n = sorted_acts_n.loc[sorted_acts_n['day'] == 7]
    sorted_acts_day8_n = sorted_acts_n.loc[sorted_acts_n['day'] == 8]
    sorted_acts_n = sorted_acts_n.loc[sorted_acts_n['day'] <= 6]

    if now >= cohort_day7:
        sorted_acts_n = sorted_acts_n.loc[sorted_acts_n['day'] > 7]
    send_list_n = pd.merge(sorted_acts_n, users, on=['user_id','day'])
    send_list_n['url'] = "https://dailyeventinfo.com/" + send_list_n['user_id_hashid'].str.strip() + "/" + send_list_n['day_hashid'].str.strip() + "/info"
    print("" if send_list_n.empty else send_list_n)

    # # Send new day URL, update activity
    # for i in range(send_list_n.shape[0]):
    #     wechat_id = send_list_n.iloc[i]['user_id']
    #     try:
    #         my_friend = bot.friends().search(remark_name=str(wechat_id))[0]
    #         print('sending 6PM new day message to',wechat_id,'...')
    #         my_friend.send(URLmessage[send_list_n.iloc[i]['day']])
    #         my_friend.send(send_list_n.iloc[i]['url'])
    #         time.sleep(2)
    #         #Update activity for new day URL
    #         requests.post("https://dailyeventinfo.com/activityUpdate/"+str(int(send_list_n['user_id'].iloc[i]))+"/"+str(int(send_list_n['day'].iloc[i]))+"/0/0/0/0")
    #     except IndexError:
    #         print('cannot find user',wechat_id,'...')

    # if todo_day7 is YES send out day 7, update activity
    sendDaySeven()

    # if todo_day8 is YES send out day 8, update activity
    sendDayEight()

    # Next day reminder prep
    sorted_acts_r = activities.loc[activities['day_complete'] == 0]
    sorted_acts_r = sorted_acts_r.loc[sorted_acts_r['time_since_last_activity'] < 48].iloc[:,0:2]
    if test == "YES":
        sorted_acts_r = sorted_acts_r.loc[sorted_acts_r['user_id'] == 1882385] # Turn this off for test with Zixin
    else:
        sorted_acts_r = sorted_acts_r.loc[sorted_acts_r['user_id'] >= 1882385] # Turn this on For test with Zixin

    # drop all users who have not completed day 6 after day 7 is sent
    if now == cohort_day7:
        sorted_acts_r = sorted_acts_r.loc[sorted_acts_r['day'] > 7]
    if now > cohort_day7:
        sorted_acts_r = sorted_acts_r.loc[sorted_acts_r['day'] >= 7]

    send_list_r = pd.merge(sorted_acts_r, users, on=['user_id','day'])
    send_list_r['url'] = "https://dailyeventinfo.com/" + send_list_r['user_id_hashid'].str.strip() + "/" + send_list_r['day_hashid'].str.strip() + "/info"
    print("" if send_list_r.empty else "\n------------------------------ Sending 6PM next-day reminders ------------------------------")
    print("" if send_list_r.empty else send_list_r)

    # # Send new day URL, update activity
    # for i in range(send_list_r.shape[0]):
    #     wechat_id = send_list_r.iloc[i]['user_id']
    #     try:
    #         my_friend = bot.friends().search(remark_name=str(wechat_id))[0]
    #         print('sending 6PM reminder message to',wechat_id,'...')
    #         my_friend.send(next_day_reminder)
    #         my_friend.send(send_list_r['url'].iloc[i])
    #         time.sleep(2)
    #     except IndexError:
    #         print('cannot find user',wechat_id,'...')
##############################################################################################

# # Keep logged in
# embed()
