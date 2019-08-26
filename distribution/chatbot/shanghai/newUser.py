###########################
## This file handles new users
## Search for XXX to make final changes before deployment
###########################

from bs4 import BeautifulSoup
import requests
from io import StringIO
import pandas as pd
import random
from math import floor
from random import randint
from hashids import Hashids

## Toggle test vs. deployment (XXX for deployment activate first line, de-activate the second line)
#URL = "https://dailyeventinfo.com/"
URL = "http://127.0.0.1:5000/"

## Scripts (XXX check these before deployment)
msg_ineligible = "Sorry, you are ineligible to participate in this survey this time. Thank you very much for your interest."  ## XXX Chinese translation needed
msg_maxnum_cohort = "次轮招募已完成，我们将在下轮开始时尽快联系您！" ## XXX Google translate says "the second round of recuitment has been completed". If this is correct translation, can we say "this round" instead of "the second round"?
msg_initial = "此次调研总共维持6天时间。我们将在接下来的8天（包括今天）每天提供一些上海本地及周边的户外活动及场所的信息。根据参与者的意向，我们或将于 [Sep 30 - Oct 4 2019] 组团结伴前往。<br><br>\
接下来的4天里，我们将向您询问一些简短的问题（约5分钟） 。第5天和第6天的调研将在2周和4周后进行。<br><br>\
我们也将会询问您一些关于各类话题的问题。 如果您想参加这项学术调研，请点击以下链接开始。 您的回答仅被用于学术研究，我们将对您的个人信息及回答进行严格保密。 调研结束后我们将进行抽奖，所有参与并完成调研的同学将有机会赢得800元人民币作为奖励。 <br><br>"

## Parameters (XXX check these before deployment)
cohort = "4"
maxnum_cohort = 200 ## Maximum number of cohorts in this trial
maxday = 8
seq = [3, 0, 2, 3, 0, 0, 3, 0, 0, 2, 0, 2, 1, 0, 2, 3, 3, 3, 2, 3, 3, 2, 0, 2, 2, 1, 1, 1, 1, 3, 1, 0, 0, 1, 0, 2, 0, 3, 2, 1, 3, 0, 3, 3, 2, 1, 0, 3, 0, 0, 0, 2, 2, 3, 2, 1, 2, 2, 1, 1, 2, 1, 1, 2, 0, 1, 3, 2, 2, 0, 2, 3, 0, 1, 3, 3, 3, 1, 0, 1, 2, 0, 2, 1, 1, 0, 2, 3, 1, 3, 1, 3, 2, 0, 1, 1, 0, 3, 2, 1, 1, 2, 0, 2, 3, 1, 3, 3, 2, 3, 1, 0, 2, 2, 3, 0, 2, 0, 3, 0, 2, 0, 0, 3, 1, 0, 3, 3, 2, 0, 1, 2, 3, 0, 2, 1, 1, 1, 2, 3, 1, 0, 3, 2, 2, 3, 3, 1, 1, 1, 1, 1, 0, 2, 1, 0, 3, 2, 2, 3, 1, 1, 3, 0, 0, 2, 1, 0, 1, 0, 1, 3, 3, 0, 0, 2, 1, 3, 2, 3, 3, 0, 3, 0, 1, 2, 2, 2, 2, 0, 2, 3, 0, 3, 2, 0, 1, 1, 0, 1]
# Note: the sequence is created randomly from "treatSequence.py"

## Get list of users (XXX allUsers page should be updated with actual WeChat IDs of former users in Shanghai)
def get_users():
    page = requests.get(URL+"allUsers").text
    soup = BeautifulSoup(page, "html.parser")
    divList = soup.findAll('div', attrs={"class" : "list"})
    data=','.join(['user_id','day','wechat_id','cohort','treatment','user_id_hashid','day_hashid'])
    for div in divList:
        data = data + '\n' + ' '.join(div.text.split())
    csv_data = StringIO(data)
    df = pd.read_csv(csv_data)
    df = df[pd.notnull(df['user_id'])]
    return df

## Using the input, create user profile in DB, and produce output
def new_user_process(input_ID):
    users = get_users()
    cohort_users = users.loc[users.cohort == int(cohort)].drop_duplicates(subset=['user_id'])
    curr_cohort_user_count = int(len(set(cohort_users['user_id'])))
    if input_ID in list(set(users['wechat_id'])): # Already existing user
        return ["EXISTING USER",msg_ineligible]
    elif curr_cohort_user_count >= maxnum_cohort: # Max cohort size reached
        requests.post(URL+"userInsert/WAITLIST/TBD"+"/"+str(input_ID)+"/"+ str(int(cohort)+1)+"/TBD/TBD/TBD")
        return ["MAX SIZE REACHED: SAVED IN WAITLIST",msg_maxnum_cohort]
    else:
        # Create nickname #
        if len(cohort_users) == 0: previousMax = 0
        else: previousMax = int((max(pd.to_numeric(cohort_users['user_id'])) % 1e6) / 1e3)
        nextUserID = int(int(cohort)*1e6 + (previousMax+1)*1e3 + randint(1,999))
        # Assign treatment group #
        treatment = "T"+str(seq[previousMax]+1)
        # Save user profile in allUsers #
        for day in range(maxday+1):
            user_id_hashids = Hashids(salt=str(10 * nextUserID + day) + "user_id", min_length=16)
            day_hashids = Hashids(salt=str(10 * nextUserID + day) + "day", min_length=10)
            hashed_user_id = user_id_hashids.encrypt(nextUserID)
            hashed_day = day_hashids.encrypt(day)
            requests.post(URL+"userInsert/"+str(nextUserID)+"/"+
                str(day)+"/"+str(input_ID)+"/"+ str(cohort) + "/" + str(treatment) +"/"+hashed_user_id+"/"+hashed_day)
            if day == 0: msg_URL = URL+"s/"+hashed_user_id+"/"+hashed_day + "/info" ## XXX Change URL accordingly
        # Set up initial allActivities #
        requests.post(URL+"activityUpdate/"+str(nextUserID)+"/0/0/0/0/0") ## XXX I put day 0 here for new user. Is this going to be a problem? (I need this so that we send correct reminder for people who didn't even finish consent form)
        # Return output for surveyors #
        return ["SAVE USER AS: "+str(nextUserID),msg_initial+msg_URL]

## Test
input_ID = "idididid" # Get input from surveyor (XXX in reality this comes from HTML form input)
for k in range(1):
    print(new_user_process("h"+str(k)))