#encoding: utf-8

from wxpy import *
import pandas as pd

# initialize chatbot
bot = Bot()
bot.enable_puid('wxpy_puid.pkl')

friends = bot.friends(update=False)
print(friends)

'''
[<Friend: Survey for Harvard-NU study>, <Friend: 10960925>, <Friend: myung kim>, <Friend: 16067600>, <Friend: 19949432>, <Friend: 20975559>, <Friend: 24580797>, <Friend: 22535066>, <Friend: 13330179>, <Friend: 26019115>, <Friend: 17737049>, <Friend: 7771792>, <Friend: 25097422>, <Friend: 33334546109>, <Friend: 31986626>, <Friend: 18845429>, <Friend: 35608716>, <Friend: 35201763>, <Friend: 35120544>, <Friend: 35693276>, <Friend: 35714800>, <Friend: 35658881>, <Friend: 35253418>, <Friend: 35776895>, <Friend: 35675998>, <Friend: 35543981>, <Friend: 35649780>, <Friend: 35134099>, <Friend: 35603078>, <Friend: 35697115>, <Friend: 35271522>, <Friend: 35000658>, <Friend: 35068754>, <Friend: 2884055>, <Friend: 35379473>, <Friend: 3780005>, <Friend: 35724687>, <Friend: 35953541>, <Friend: 35448529>, <Friend: 21853588>, <Friend: 3333336258385>, <Friend: 35106293>, <Friend: 35319372>, <Friend: 35301556>, <Friend: 35038714>, <Friend: 35477518>, <Friend: 33333337530699>, <Friend: 23300203>, <Friend: 6467910>, <Friend: 35947152>, <Friend: 14276185>, <Friend: 35788367>, <Friend: 35861005>, <Friend: 35137663>, <Friend: 35352857>, <Friend: 9331127>, <Friend: 15312225>, <Friend: 11459752>, <Friend: 35339734>, <Friend: 332560850>, <Friend: 5338852>, <Friend: 35043063>, <Friend: 35007460>, <Friend: 35200942>, <Friend: 4125240>, <Friend: 35266497>, <Friend: 333335578856>, <Friend: 3333839517>, <Friend: 1882385>, <Friend: 35002178>, <Friend: 8194629>, <Friend: 35890973>, <Friend: 35395101>]
'''
