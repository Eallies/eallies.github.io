import pandas as pd
import numpy as np
import math
import datetime
import pytz
import tzlocal
import collections
import itertools
from tabulate import tabulate
import sys
import matplotlib.pyplot as plt
import japanize_matplotlib

def sekki(year,month): #当該年月の節分の日を求める関数
  basetime = datetime.datetime(2000,3,20,16,35) #基準時として２０００年の春分の日を利用
  baseyear = 365.2422 #地球の公転周期
  year -= 2000
  syunbun_of_the_year = basetime + datetime.timedelta(minutes= math.ceil(baseyear * year * 24 * 60)) #その年の春分の日
  month -= 3
  if month < 0: #春分以前
    sekki_of_the_month = syunbun_of_the_year + datetime.timedelta(minutes = (-1 + month * 2) * (baseyear-186.5)* 24 * 60 // 12)
  elif month < 7: #春分から秋分
    sekki_of_the_month = syunbun_of_the_year + datetime.timedelta(minutes = (-1 + month * 2) * 186.5 * 24 * 60 // 12)
  else: #秋分以後
    month -= 6
    sekki_of_the_month = syunbun_of_the_year + datetime.timedelta(minutes = ((((-1 + month * 2) * (baseyear-186.5) // 12) + 186.5) * 24 * 60))
  return(sekki_of_the_month)

def jikkan(num):  #十干番号から十干を返す関数
  num %= 10
  a = (("甲", 0,   0, 4),#十干のタプルコンテンツ：十干名、十干番号、五行角度、干合後の干支番号
       ("乙", 1,   0, 7),
       ("丙", 2,  72, 8),
       ("丁", 3,  72, 1),
       ("戊", 4, 144, 2),
       ("己", 5, 144, 5),
       ("庚", 6, 216, 6),
       ("辛", 7, 216, 9),
       ("壬", 8, 288, 0),
       ("癸", 9, 288, 3))
  return(a[num])

def junishi(num):  #番号から十二支を返す関数
  num %= 12
  a = (#十二支のタプルコンテンツ：十二支名、十二支番号(五行と合わせるため寅始まり)、十二支角度（度）、五行角度、蔵干余気十干番号、同中気(なければ-1)、同本気
       ("子", 10, 15,  288, 8, -1, 9),
       ("丑", 11, 45,  144, 9,  7, 5),
       ("寅",  0, 75,    0, 4,  2, 0),
       ("卯",  1, 105,   0, 0, -1, 1),
       ("辰",  2, 135, 144, 1,  9, 4),
       ("巳",  3, 165,  72, 4,  6, 2),
       ("午",  4, 195,  72, 5, -1, 3),
       ("未",  5, 225, 144, 3,  1, 5),
       ("申",  6, 255, 216, 4,  8, 6),
       ("酉",  7, 285, 216, 6, -1, 7),
       ("戌",  8, 315, 144, 7,  3, 4),
       ("亥",  9, 345, 288, 0, -1, 8))
  return(a[num])

tuhenseilib = (#通変星のタプルコンテンツ：通変星名、神名、神角度
("比肩", "比劫",   0),
("劫財", "比劫",   0),
("食神", "食傷",  72),
("傷官", "食傷",  72),
("偏財",   "財", 144),
("正財",   "財", 144),
("偏官", "官殺", 216),
("正官", "官殺", 216),
("偏印",   "印", 288),
("印綬",   "印", 288) )

fivepower = {0:"木" ,72:"火", 144:"土", 216:"金" ,288:"水"} #五行の数値を変換するdict

def tuhensei(day_jikkan,jikkannum): #通変星を求める関数（念のため日干も引数にする）
  a = ((jikkannum[2] - day_jikkan[2] + 360) % 360) // 72
  if day_jikkan[1] % 2 == jikkannum[1] % 2:
    b = 0
  else:
    b = 1
  return(tuhenseilib[a * 2 + b])

#干合を出す関数
def kango(tenkan, chishi, loglist):
  kangoFlags = [1,1,1,1] #干合をフラグ管理するリスト(１は干合せず、‐1が干合)
  for i in range(3):
    if abs(tenkan[i][1] - tenkan[i+1][1]) == 5:
      kangoFlags[i] *= -1 #妬合したら反転して元に戻る
      kangoFlags[i+1] *= -1
  for i in range(4):
    if kangoFlags[i] == -1:
      kango5 = [i[2] for i in tenkan] + [i[3] for i in chishi] #命式全体の5行を集計するリスト
      if tenkan[i][1] == 0 or 5:
        if chishi[1][0] in ["丑辰未戌巳午"] and kango5.count(144) > 3 and kango5.count(288) ==1:
          tenkan[i] = jikkan(tenkan[i][3]) #合化土
          loglist.append(f"{tenkan[i][0]}合化土")
      if tenkan[i][1] == 1 or 6:
        if chishi[1][0] in ["申酉丑辰未戌"] and kango5.count(216) > 3 and kango5.count(72) ==0:
          tenkan[i] = jikkan(tenkan[i][3]) #合化金
          loglist.append(f"{tenkan[i][0]}合化金")
      if tenkan[i][1] == 2 or 7:
        if chishi[1][0] in ["子亥申酉"] and kango5.count(288) > 3 and (kango5.count(144) == 0 or (chishi[1][0] in ["丑辰"] and kango5.count(144) ==1)):
          tenkan[i] = jikkan(tenkan[i][3]) #合化水
          loglist.append(f"{tenkan[i][0]}合化水")
      if tenkan[i][1] == 3 or 8:
        if chishi[1][0] in ["寅卯子亥辰未"] and kango5.count(0) > 3 and kango5.count(216) == 0:
          tenkan[i] = jikkan(tenkan[i][3]) #合化木
          loglist.append(f"{tenkan[i][0]}合化木")
      if tenkan[i][1] == 4 or 9:
        if chishi[1][0] in ["巳午寅卯未戌"] and kango5.count(72) > 3 and kango5.count(288) == 1 :
          tenkan[i] = jikkan(tenkan[i][3]) #合化水
          loglist.append(f"{tenkan[i][0]}合化水")
  return([tenkan, kangoFlags, loglist])
#干合ここまで

def yojin(kakkyoku, kyojaku, tuhensei): #吉凶神を出す関数
  if kakkyoku == "従旺":
    return([tuhenseilib[0],tuhenseilib[8],tuhenseilib[6],tuhenseilib[4]])
  elif kakkyoku == "従強":
    return([tuhenseilib[8],tuhenseilib[0],tuhenseilib[4],tuhenseilib[2]])
  elif kakkyoku == "従児":
    return([tuhenseilib[2],tuhenseilib[4],tuhenseilib[8],tuhenseilib[0]])
  elif kakkyoku == "従財":
    return([tuhenseilib[4],tuhenseilib[2],tuhenseilib[0],tuhenseilib[8]])
  elif kakkyoku == "従殺":
    return([tuhenseilib[6],tuhenseilib[4],tuhenseilib[8],tuhenseilib[0]])
  elif kakkyoku == "従勢":
    return([tuhenseilib[4],tuhenseilib[6],tuhenseilib[0],tuhenseilib[8],tuhenseilib[2]])
  elif kyojaku == "身弱":
    if tuhensei == "官殺":
      return([tuhenseilib[8],tuhenseilib[0],tuhenseilib[4],tuhenseilib[2]])
    elif tuhensei == "財":
      return([tuhenseilib[0],tuhenseilib[8],tuhenseilib[6],tuhenseilib[4]])
    else:#食傷の場合
      return([tuhenseilib[8],tuhenseilib[0],tuhenseilib[4],tuhenseilib[2]])
  else:
    if kakkyoku == "食神" or kakkyoku == "傷官" or kakkyoku == "偏財" or kakkyoku == "正財":
      if tuhensei == "比劫":
        return([tuhenseilib[2],tuhenseilib[4],tuhenseilib[8],tuhenseilib[0]])
      elif tuhensei == "印":
        return([tuhenseilib[4],tuhenseilib[2],tuhenseilib[0],tuhenseilib[8]])
      elif tuhensei == "食傷":
        return([tuhenseilib[4],tuhenseilib[6],tuhenseilib[0],tuhenseilib[8]])
      elif tuhensei == "財":
        return([tuhenseilib[6],tuhenseilib[4],tuhenseilib[8],tuhenseilib[0]])
      else:#官殺の場合
        return([tuhenseilib[2],tuhenseilib[4],tuhenseilib[8],tuhenseilib[0]])
    else:
      if tuhensei == "比劫":
        return([tuhenseilib[6],tuhenseilib[4],tuhenseilib[0],tuhenseilib[8]])
      elif tuhensei == "印":
        return([tuhenseilib[4],tuhenseilib[2],tuhenseilib[0],tuhenseilib[8]])
      elif tuhensei == "食傷":
        return([tuhenseilib[4],tuhenseilib[6],tuhenseilib[0],tuhenseilib[8]])
      elif tuhensei == "財":
        return([tuhenseilib[6],tuhenseilib[4],tuhenseilib[8],tuhenseilib[0]])
      else:
        return([tuhenseilib[2],tuhenseilib[4],tuhenseilib[8],tuhenseilib[0]])

def zokan(gesshi, nissu):#蔵干深浅を図る関数
  if gesshi[0] == "寅":
    if nissu <= 7:
      return(jikkan(4))
    elif nissu <= 14:
      return(jikkan(2))
    else:
      return(jikkan(0))
  elif gesshi[0] == "卯":
    if nissu <= 10:
      return(jikkan(0))
    else:
      return(jikkan(1))
  elif gesshi[0] == "辰":
    if nissu <= 9:
      return(jikkan(1))
    elif nissu <= 12:
      return(jikkan(9))
    else:
      return(jikkan(4))
  elif gesshi[0] == "巳":
    if nissu <= 7:
      return(jikkan(4))
    elif nissu <= 16:
      return(jikkan(6))
    else:
      return(jikkan(2))
  elif gesshi[0] == "午":
    if nissu <= 9:
      return(jikkan(5))
    else:
      return(jikkan(3))
  elif gesshi[0] == "未":
    if nissu <= 9:
      return(jikkan(3))
    elif nissu <= 12:
      return(jikkan(1))
    else:
      return(jikkan(5))
  elif gesshi[0] == "申":
    if nissu <= 7:
      return(jikkan(4))
    elif nissu <= 14:
      return(jikkan(8))
    else:
      return(jikkan(6))
  elif gesshi[0] == "酉":
    if nissu <= 10:
      return(jikkan(6))
    else:
      return(jikkan(7))
  elif gesshi[0] == "戌":
    if nissu <= 9:
      return(jikkan(7))
    elif nissu <= 12:
      return(jikkan(3))
    else:
      return(jikkan(4))
  elif gesshi[0] == "亥":
    if nissu <= 10:
      return(jikkan(0))
    else:
      return(jikkan(8))
  elif gesshi[0] == "子":
    if nissu <= 10:
      return(jikkan(8))
    else:
      return(jikkan(9))
  elif gesshi[0] == "丑":
    if nissu <= 9:
      return(jikkan(9))
    elif nissu <= 12:
      return(jikkan(7))
    else:
      return(jikkan(5))

#会局の有無を調べる
kaikyokulib = (#会局のタプルコンテンツ：会局名、五行角度、構成十二支
    ("三方木局",   0, junishi(2),  junishi(3), junishi(4)),
    ("三方火局",  72, junishi(5),  junishi(6), junishi(7)),
    ("三方金局", 216, junishi(8),  junishi(9), junishi(10)),
    ("三方水局", 288, junishi(11), junishi(0), junishi(1)),
    ("三合木局",   0, junishi(3),  junishi(7), junishi(11)),
    ("三合火局",  72, junishi(2),  junishi(6), junishi(10)),
    ("三合金局", 216, junishi(1),  junishi(5), junishi(9)),
    ("三合水局", 288, junishi(0),  junishi(4), junishi(8)),
    ("四墓土局", 144, junishi(1),  junishi(4), junishi(7), junishi(10)))

def kikkyo(tenkan_jikkan, chishi_jikkan, kamilist): #吉凶判定の数値を出す関数
  kikkyo_tuhensei = [tuhensei(tenkan[2], tenkan_jikkan), tuhensei(tenkan[2], chishi_jikkan)]
  for i in kamilist: #神が二つの時は少ない方を消す
    if len(i) == 2:
      del(i[1])
  a = 0 #吉凶の数値を入れる
  for i in range(2):
    b = kikkyo_tuhensei[i][2]
    if b == kamilist[0][0][2]:
      a += 2 * (i + 1)
    elif b == kamilist[1][0][2]:
      a += 1 * (i + 1)
    elif b == kamilist[2][0][2]:
      a += -2 * (i + 1)
    elif b == kamilist[3][0][2]:
      a += -1 * (i + 1)
    else:
      a += 0
  if a == 6:
    b = "大吉"
  elif a == -6:
    b ="大凶"
  elif a == 0:
    b ="和"
  elif a >= 4:
    b ="中吉"
  elif a <= -4:
    b ="末凶"
  elif a == 3:
    b ="小吉"
  elif a == -3:
    b ="半凶"
  elif a == 2:
    b ="吉"
  elif a == -2:
    b ="小凶"
  elif a == 1:
    b ="末吉"
  else:
    b ="凶"
  return([b,a])

loglist = []#パロメーター等を格納するリスト


def indicate():
  date = Element("birthdate") #HTMLからデータを受け取り
  time = Element("birthtime")
  sex = Element("sex")
  
  year = int(date.split("-")[0])
  month = int(date.split("-")[1])
  day = int(date.split("-")[2])
  hour = int(time.split(":")[0])
  minute = int(time.split(":")[1])
  
  birthday = ja.localize(datetime.datetime(year,month,day,hour,minute))

  #ここから年干支を求める
  if birthday.date() - sekki(year,2).date() < datetime.timedelta(days = 0 ):
    year -= 1
  a = year - 1924
  tenkan[0] = jikkan(a)
  chishi[0] = junishi(a)
  #年干支ここまで

  #ここから月干支を求める
  if birthday.date() - sekki(year,month).date() < datetime.timedelta(days = 0):
    month -= 1
  monthnum = (year - 1924) * 12 + month
  tenkan[1] = jikkan(monthnum)
  chishi[1] = junishi(monthnum)
  #月干支ここまで
  
  #ここから日干支を求める
  a = birthday.date() - datetime.date(1924,2,15)
  nikkanNum = a.days
  tenkan[2] = jikkan(nikkanNum)
  chishi[2] = junishi(nikkanNum)
  #日干支ここまで

  #ここから時干支を求める
  b = datetime.timedelta(hours = birthday.hour, minutes = birthday.minute, seconds = birthday.second)
  b = ((b.total_seconds()// 60) + ((nikkanNum % 5) * 12 * 120 + 60)) // 120
  b = math.ceil(b)
  tenkan[3] = jikkan(b)
  chishi[3] = junishi(b)
  #時干支ここまで

  tenkan, kangoFlags, loglist = kango(tenkan, chishi, loglist) #干合を計算

  tenkan = tuple(tenkan)
  chsihi = tuple(chishi)

  #ここから各通変星を求める
  tuhensei_list = [tenkan[i] for i in range(len(tenkan)) if i != 2]

  for i in range(4,len(chishi[0])):
    for e in chishi:
      if e[i] == -1:
        tuhensei_list.append(0)
      else:
        tuhensei_list.append(jikkan(e[i]))
  a = tenkan[2]
  #通変星ここまで

  #命式と通変星を出力
  outputlist = [] #出力を格納するリスト
  for i in range(4):
    a = []
    if i == 2:
      a.append("")
    else:
      if i < 2:
        a.append(f"{tuhensei(tenkan[2],tuhensei_list[i])[0]}")
      else:
        a.append(f"{tuhensei(tenkan[2],tuhensei_list[i - 1])[0]}")
    a.append(f"{tenkan[i][0]}")
    a.append(f"{chishi[i][0]}")
    a.append(f"{jikkan(chishi[i][6])[0]}")
    a.append(f"{tuhensei(tenkan[2],tuhensei_list[i+11])[0]}")
    if chishi[i][5] == -1:
      a.append("‐")
      a.append("")
    else:
      a.append(f"{jikkan(chishi[i][5])[0]} ")
      a.append(f"{tuhensei(tenkan[2],tuhensei_list[i+7])[0]} ")
    a.append(f"{jikkan(chishi[i][4])[0]} ")
    a.append(tuhensei(tenkan[2],tuhensei_list[i+3])[0])
    outputlist.append(a)
  df = pd.DataFrame(outputlist, index = pd.Index(["年柱","月柱","日柱","時柱"], name="命式"),
                  columns = pd.Index(["通変星","天干","地支","蔵干本気","通変星","蔵干中気","通変星","蔵干余気","通変星"]))
  if nameUse == True:
    print(f"{name_of_person} の命式")
  else:
    print("命　式")
  print(tabulate(df,headers = df.columns,tablefmt='simple', showindex=True))
  print()
  #出力ここまで


  #ここから身強弱判定
  score = 0 #ここに身強弱数値入れる
  a = tenkan[2][2]
  if a == chishi[1][3]: #当旺
    score += 7
  if a == chishi[1][3] + 72: #次旺
    score += 6
  scorelist1 = chishi #地支
  for i in scorelist1:
    if i[3] == a:
      score += 3
    elif i[3] + 72 == a:
      score += 2
    else:
      score -= 2
  scorelist2 = list(tenkan) #天干
  del scorelist2[2]
  for i in scorelist2:
    if i[2] == a:
      score += 2
    elif i[2] + 72 == a:
      score += 1
    else:
      score -= -1

  for i in kaikyokulib: #会局を調べる
    if i[2:] in chishi and i[1] == tenkan[3][2]:
      score += 2
      if chishi[1] in i[2:]:#月支と一致していれば追加
        score += 1

  if (a - chishi[1][3] + 360) % 360 == 144: #失令
    score -= 4
  loglist.append(f"日干強弱値：{score}")
  if score > 10:
    kyojaku = "極身強"
  elif score < -10:
    kyojaku = "極身弱"
  elif score > 0:
    kyojaku = "身強"
  elif score < 0:
    kyojaku = "身弱"
  else:
    kyojaku = "中和"
  #身強弱ここまで


#ここから格局判定
  kakkyokunm = ""  #一般格局
  nikkan = list(tenkan[2])
  if nikkan[2] == 144:
    nikkan[2] = 72

  if nikkan[2] == chishi[1][3]:
    if nikkan[1] % 2 == chishi[1][1] % 2:
      kakkyokunm = "建禄"
    elif nikkan[1] % 2 == 0:
      kakkyokunm = "月刃"
  else:
    for i in reversed(range(4,len(chishi[1]))):
      if kakkyokunm != "":
        break
      if tenkan[1][2] == jikkan(chishi[1][i])[2]:
        kakkyokunm = tuhensei(tenkan[2],jikkan(chishi[1][i]))[0]
        loglist.append("格局は月干で判定")
        break
    for i in reversed(range(4,len(chishi[1]))):
      if kakkyokunm != "":
        break
      if jikkan(chishi[1][i])[2] == tenkan[0][2] or jikkan(chishi[1][i])[2] == tenkan[3][2]:
         kakkyokunm = tuhensei(tenkan[2],jikkan(chishi[1][i]))[0]
         loglist.append(f"格局は年・時干で判定")
         break
  if kakkyokunm == "":  #蔵干深浅判定
    if birthday.date() - sekki(year,month).date() < datetime.timedelta(days = 0):
      month = -1
    nissu = birthday.date() - sekki(year,month - 1).date()
    nissu = int(nissu.days)
    loglist.append(f"格局は蔵干深浅で判定")
    if tuhensei(tenkan[2],zokan(chishi[1],nissu))[1] == "比肩":
      kakkyokunm = "建禄"
    elif tuhensei(tenkan[2],zokan(chishi[1],nissu))[1] == "劫財":
      kakkyokunm = "月刃"
    else:
      kakkyokunm = tuhensei(tenkan[2],zokan(chishi[1],nissu))[0]

  tuhensei_list2 = [tuhensei_list[i] for i  in range(len(tuhensei_list)) if i <= 3 or i >= 12]#天干および蔵干本気のみの通変星リスト
  tuhensei_score = 0
  if score > 10:  #極身強の特別格局
    for i in tuhensei_list2:
      tuhensei_score += i[2]
    tuhensei_score //= len(tuhensei_list2)
    if tuhensei_score == 0:
      kakkyokunm = "専旺"
    elif tuhensei_score < 144:
      kakkyokunm = "従旺"
    else:
      kakkyokunm = "従強"

  if score < -10:  #極身弱の特別格局
    for i in range(tuhensei_list2):
      tuhensei_list2[i] = tuhensei_list2[i][2]
    if tuhensei_list2.count(72) > tuhensei_list2.count(144) and tuhensei_list2.count(72) > tuhensei_list2.count(216):
      kakkyokunm = "従児"
    elif tuhensei_list2.count(144) > tuhensei_list2.count(72) and tuhensei_list2.count(144) > tuhensei_list2.count(216):
      kakkyokunm = "従財"
    elif tuhensei_list2.count(216) > tuhensei_list2.count(144) and tuhensei_list2.count(216) > tuhensei_list2.count(72):
      kakkyokunm = "従殺"
    else:
      kakkyokunm = "従勢"
#格局ここまで

#格局、身強弱の出力
  print(f"格　局：{kakkyokunm}格") #格局の出力
  #if ("従" not in kakkyokunm) or (kakkyokunm == "専旺"):
  #  typewrite("kakkyoku",kakkyokunm, "端的に", True)
  print()
  print(f"身強弱：{kyojaku}") #身強弱の出力
  print()
#出力ここまで

#ここから神判定
  kakkyoku = kakkyokunm
  if kakkyokunm == "専旺":
    kakkyoku = "従旺"
  common_tuhensei = collections.Counter(tuhensei_list2).most_common()#最多通変星を求める
  i = common_tuhensei[0][1]
  common_tuhensei = [common_tuhensei[a] for a in range(len(common_tuhensei)) if common_tuhensei[a][1] == i]
  if len(common_tuhensei) == 1:
    tuhensei_mein = tuhensei(tenkan[2],common_tuhensei[0][0])[1]
  elif tuhensei_list2[5] in common_tuhensei:#最多通変星が複数ある場合、月支を優先する。
    tuhensei_mein = tuhensei(tenkan[2],tuhensei_list[5][1])[1]
  else:#最多通変星が複数あり場合、月支が含まれない場合、地支を重視する。
    tuhensei_list3 = tuhensei_list2
    for i in range(len(tuhensei_list2)):
      if i > 3:
        tuhensei_list3.append(tuhensei_list2[i])
    common_tuhensei = collections.Counter(tuhensei_list3).most_common()
    i = common_tuhensei[0][1]
    common_tuhensei = [common_tuhensei[a] for a in range(len(common_tuhensei)) if common_tuhensei[a][1] == i]
    if tuhensei_list2[5] in common_tuhensei:
      tuhensei_mein = tuhensei(tenkan[2],tuhensei_list[5][1])[1]
    else:
      tuhensei_mein = tuhensei(tenkan[2],common_tuhensei[0][0])[1]
  kamibase = yojin(kakkyoku, kyojaku, tuhensei_mein)
  kami = []
  #ここから神のいる方をとる（どっちもいるなら多い順に出す）
  kaminame = ["用神","喜神","忌神","仇神"]
  for i in range(len(kamibase)):
    kamiangle = kamibase[i][2]
    kami_list = [a for a in tuhensei_list2 if tuhensei(tenkan[2],a)[2] == kamiangle]
    if kami_list == []:
      kami_list = [a for a in tuhensei_list if a != 0]
      kami_list = [a for a in kami_list if tuhensei(tenkan[2],a)[2] == kamiangle]
      if kami_list == []: #どれでもなければ該当する両方を出す（基本はないはずだが）
        kami_list = [jikkan(a) for a in range(10) if tuhensei(tenkan[2],jikkan(a))[2] == kamiangle]
        loglist.append(f"{kaminame[i]}は命式に該当なし")
    kami_list = collections.Counter(kami_list).most_common()
    kami_list = [tuhensei(tenkan[2],a[0]) for a in kami_list]
    kami.append(kami_list)
  for i in range(4):
    a = kaminame[i] + "："
    for j in range(len(kami[i])):
      a += kami[i][j][0]
      if j < len(kami[i]) - 1:
        a += "、"
    a += "（"
    a += fivepower[(tenkan[2][2] + kami[i][0][2]) % 360]
    a += "）"
    print(a)
  print()
  #神判定ここまで

#ここから最多五行判定
  fivelevels = {0:0.0, 72:0.0, 144:0.0, 216:0.0, 288:0.0}#各五行の強さを格納するDict変数
  jikkanlevels = [0] * 10 #十干の強さを格納するリスト
  for i in tenkan: #天干の五行を1足す
    fivelevels[i[2]] += 1
    jikkanlevels[i[1]] += 1
  for i in chishi: #地支の五行を１足す（蔵干も足す）
    for j in range(1,31):
      fivelevels[zokan(i,j)[2]] += 1/30
      jikkanlevels[zokan(i,j)[1]] += 1/30
      if i == chishi[1]: #月支なら重視して足す
        fivelevels[zokan(i,j)[2]] += 1/60
        jikkanlevels[zokan(i,j)[1]] += 1/60
  shityu = [0,0,0,0] #支沖の計算（合わせて地支の五行を削る）
  for i in range(3):
    if abs(chishi[i][2] - chishi[i+1][2]) == 180:
      shityu[i] = 1
      shityu[i+1] = 1
  for i in range(4):
    if shityu[i] == 1:
      if chishi[i][3] == 144: #土同士の支沖は土の気を足す
        fivelevels[chishi[i][3]] += 0.5
        loglist.append(f"{chishi[i][0]}支沖")
      else:
        fivelevels[chishi[i][3]] -= 0.5
        loglist.append(f"{chishi[i][0]}支沖")
  shigo = [1,1,1,1]#ここから支合の計算（合わせて地支の五行も足す）
  for i in range(3):
    if math.tan(math.radians(chishi[i][2])) == math.tan(math.radians(chishi[i+1][2])):
      if kangoFlags[i] == 0 or (kangoFlags[i] == 1 and abs(tenkan[i][1] - tenkan[i+1][1]) == 5): #天干が他柱と干合してない（この組み合わせなら可）
        shigo[i] *= -1 #妬合したら反転して元に戻る
        shigo[i+1] *= -1
  for i in range(3):
    if shigo[i] == -1 and shityu[i] == 0: #支沖してない
      if chishi[i][0] + chishi[i+1][0] in ["子丑"] and tenkan[i][0] + tenkan[i+1][0] in ["戊己丙丁"]:
        fivelevels[144] += 1 #合化土
        loglist.append(f"{chishi[i][0]}{chishi[i+1][0]}合化土")
      if chishi[i][0] + chishi[i+1][0] in ["亥寅"] and tenkan[i][0] + tenkan[i+1][0] in ["甲乙壬癸"]:
        fivelevels[0] += 1 #合化木
        loglist.append(f"{chishi[i][0]}{chishi[i+1][0]}合化木")
      if chishi[i][0] + chishi[i+1][0] in ["卯戌午未"] and tenkan[i][0] + tenkan[i+1][0] in ["甲乙丙丁"]:
        fivelevels[72] += 1 #合化火
        loglist.append(f"{chishi[i][0]}{chishi[i+1][0]}合化火")
      if chishi[i][0] + chishi[i+1][0] in ["辰酉"] and tenkan[i][0] + tenkan[i+1][0] in ["庚辛戊己"]:
        fivelevels[216] += 1 #合化金
        loglist.append(f"{chishi[i][0]}{chishi[i+1][0]}合化火")
      if chishi[i][0] + chishi[i+1][0] in ["巳申"] and tenkan[i][0] + tenkan[i+1][0] in ["庚辛壬癸"]:
        fivelevels[288] += 1 #合化水
        loglist.append(f"{chishi[i][0]}{chishi[i+1][0]}合化水")
  for i in range(len(kaikyokulib)): #会局による五行を足す
    if kaikyokulib[i][2:] in chishi:
      fivelevels[kaikyokulib[i][1]] += 0.3
      loglist.append(f"{kaikyokulib[i][0]}")
  fivelevels = sorted(fivelevels.items(), key = lambda value:value[1], reverse = True)
  maxFive = fivepower[fivelevels[0][0]]
  for i in range(1,len(fivelevels)):
    if fivelevels[i][1] == fivelevels[0][1]:
      maxFive += "・"
      maxFive += fivepower[fivelevels[i][0]]
  print(f"最多五行：{maxFive}")
  #最多五行ここまで


#ここから五行の配分図表示
  labelList = ["","乙","","丙","","丁","","戊","","己","","庚","","辛","","壬","","癸","","甲"]
  for i in range(len(labelList)):
    if i % 2 == 0:
      continue
    else:
      a = jikkan((i // 2 + 11) % 10)
      if a == tenkan[2]:
        labelList[i] = labelList[i] + "（日干・比肩）"
      else:
        for p in range(len(tuhenseilib)):
          if (a[2] - tenkan[2][2] + 360) % 360 in tuhenseilib[p]:
            if a[1] % 2 == tenkan[2][1] % 2:
              labelList[i] = labelList[i] + "（" + tuhenseilib[p][0] +"）"
            else:
              labelList[i] = labelList[i] + "（" + tuhenseilib[p+1][0] +"）"
            break

  plotlist = [0] * 5 #五行の数値を正規化
  for i in fivelevels:
    plotlist[i[0]//72] = i[1]
  plotlist.append(plotlist[0])

  lineList = [0] * 20 #十干の数値を正規化
  for i in range(len(jikkanlevels)):
    lineList[((i + 9) % 10) * 2 + 1] = jikkanlevels[i]
  for i in range(len(lineList)): # 仮の地点の値を中間値にしてなめらかにする。
    if i % 2 == 0:
      a = np.sqrt(lineList[(i + 19) % 20] * lineList[(i + 21) % 20])
      lineList[i] = a
  lineList.append(lineList[0])

  idealpowers = [0] * 5 #吉凶神を加味した理想的な五行配分
  for i in range(5):
    idealpowers[i] = plotlist[i]
    if (i * 72 - tenkan[2][2] + 360) % 360 in list(itertools.chain.from_iterable(kami[0])):
      idealpowers[i] += 2
    if (i * 72 - tenkan[2][2] + 360) % 360 in list(itertools.chain.from_iterable(kami[1])):
      idealpowers[i] += 1
    if (i * 72 - tenkan[2][2] + 360) % 360 in list(itertools.chain.from_iterable(kami[2])):
      idealpowers[i] += -2
    if (i * 72 - tenkan[2][2] + 360) % 360  in list(itertools.chain.from_iterable(kami[3])):
      idealpowers[i] += -1
  for i in range(len(idealpowers)): #目標値が０切ってれば０にする
    if idealpowers[i] < 0:
      idealpowers[i] = 0
  idealpowers.append(idealpowers[0])

  angles = np.linspace(start = 0, stop = 2*np.pi, num = len(plotlist),  endpoint = True)
  anglesA = np.linspace(start = 0, stop = 2*np.pi, num = len(labelList)+1,  endpoint = True)
  fig, ax = plt.subplots(1,1,figsize = (5,6), subplot_kw={"projection":"polar"})
  ax.plot(angles, idealpowers, "o-", color="yellow", label = "目標値")
  ax.fill(angles, idealpowers, alpha= 0.3, color = "yellow")
  ax.plot(anglesA, lineList, "-", color="blue", label = "命式")
  ax.fill(angles, plotlist, alpha= 0.3, color = "blue")
  ax.set_thetagrids(anglesA[:-1]*180/np.pi, labelList, fontsize=10)
  ax.text(0.5 + np.sin(np.radians(357))/2,0.5+ np.cos(np.radians(357))/2,"木",transform = ax.transAxes, color = "green", fontsize = 15)
  ax.text(0.5 + np.sin(np.radians(72))/2,0.5+ np.cos(np.radians(72))/2,"火",transform = ax.transAxes, color = "red", fontsize = 15)
  ax.text(0.5 + np.sin(np.radians(145))/2,0.4+ np.cos(np.radians(145))/2,"土",transform = ax.transAxes, color = "gray", fontsize = 15)
  ax.text(0.4 + np.sin(np.radians(217))/2,0.4+ np.cos(np.radians(217))/2,"金",transform = ax.transAxes, color = "gold", fontsize = 15)
  ax.text(0.4 + np.sin(np.radians(285))/2,0.5+ np.cos(np.radians(285))/2,"水",transform = ax.transAxes, color = "cyan", fontsize = 15)
  ax.set_theta_zero_location("N")
  ax.set_theta_direction(-1)
  ax.set_title("五行配分図", fontsize = 15)
  ax.legend(bbox_to_anchor=(1, 1, 0.3 ,0.1), loc='upper right', ncol=2)
  plt.show()
  #五行の配分図表示ここまで

  #ここまでのログを表示
  logprint = "特記事項："
  for i in loglist:
    logprint += i
    if i != loglist[-1]:
      logprint += "、"
  print(logprint)
  print()
  print()

#ここから大運判定
  if sex == "男性":
    sexnum = 1
  else:
    sexnum = -1
  if tenkan[0][1] % 2 == 0: #順行・逆行判定
    jungyaku = sexnum
  else:
    jungyaku = sexnum * -1
  if jungyaku == 1: #初運判定
    syoun = sekki(year,month + 1).date() - birthday.date()
  else:
    syoun =  birthday.date() - sekki(year,month).date()
  syoun = round(syoun.days / 3)

  taiun = []
  for i in range(8):
    li = []
    li.append(syoun + 10 * i)
    num = jungyaku * ( i + 1)
    li.append(tuhensei(tenkan[2],jikkan(monthnum + num))[0])
    li.append(jikkan(monthnum + num)[0])
    li.append(junishi(monthnum + num)[0])
    li.append(jikkan(junishi(monthnum + num)[6])[0])
    li.append(tuhensei(tenkan[2],jikkan(junishi(monthnum + num)[6]))[0])
    li.append(kikkyo(jikkan(monthnum + num), jikkan(junishi(monthnum + num)[6]),kami)[0])
    taiun.append(li)
  df_taiun = pd.DataFrame(taiun, columns = pd.Index(["年齢","通変星","天干","地支","蔵干","通変星","運勢"]))
  print("大運")
  print(tabulate(df_taiun, headers = df_taiun.columns, tablefmt='simple', showindex=False))
#大運判定ここまで

  taiunLine = [] #大運を折れ線グラフにする
  targetyear = 0
  for x in range(taiun[0][0]):
    thisyear = year + targetyear - 1924
    ryunenscore = kikkyo(jikkan(thisyear), junishi(thisyear), kami)[1]
    taiunLine.append(ryunenscore)
    targetyear += 1
  c = 0
  d = 0
  for x in range(8):
    kikkyo_tuhensei = [taiun[x][1], taiun[x][5]]
    a = 0 #吉凶の数値を入れる
    for i in range(2):
      for j in tuhenseilib:
        if kikkyo_tuhensei[i] in j:
          b = j[2]
      if b == kami[0][0][2]:
        a += 2 * (i + 1)
      elif b == kami[1][0][2]:
        a += 1 * (i + 1)
      elif b == kami[2][0][2]:
        a += -2 * (i + 1)
      elif b == kami[3][0][2]:
        a += -1 * (i + 1)
      else:
        a += 0
    a *= 5
    for y in range(10):
      thisyear = year + targetyear - 1924
      ryunenscore = kikkyo(jikkan(thisyear), junishi(thisyear), kami)[1]
      yearscore = c + math.log10(y + 1) * (a - c) + ryunenscore
      taiunLine.append(yearscore)
      targetyear += 1
    c = a
  df_taiungraph = pd.DataFrame(taiunLine)
  df_taiungraph.plot(title = "大運進行グラフ", grid = True, legend = False)
  #折れ線グラフここまで
