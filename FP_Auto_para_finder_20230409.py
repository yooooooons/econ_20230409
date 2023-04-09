#!/usr/bin/env python
# coding: utf-8

# In[1]:


import time
import pyupbit
import pandas as pd
import numpy as np
import warnings

warnings.filterwarnings('ignore')
#import matplotlib.pyplot as plt


# In[2]:


pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)


# In[2]:


check_duration_1 = 3.5
No_of_first_candidate_coin = 20
No_of_final_candi = 7
#check_duration_2 = 30


# In[3]:


candle_type = '60min'
#candle_type = 'day'

if candle_type == '1min' :
    candle_adapt = 'minute1'
    time_unit = 1
elif candle_type == '3min' :
    candle_adapt = 'minute3'
    time_unit = 3
elif candle_type == '5min' :
    candle_adapt = 'minute5'
    time_unit = 5
elif candle_type == '10min' :
    candle_adapt = 'minute10'
    time_unit = 10
elif candle_type == '15min' :
    candle_adapt = 'minute15'
    time_unit = 15
elif candle_type == '30min' :
    candle_adapt = 'minute30'
    time_unit = 30
elif candle_type == '60min' :
    candle_adapt = 'minute60'
    time_unit = 60
elif candle_type == '240min' :
    candle_adapt = 'minute240'
    time_unit = 240
elif candle_type == 'day' :
    candle_adapt = 'day'
    time_unit = (60 * 24)
elif candle_type == 'month' :
    candle_adapt = 'month'
    time_unit = 60 * 24 * 30




tickers = pyupbit.get_tickers()

LIST_coin_KRW = []

for i in range (0, len(tickers), 1):
    if tickers[i][0:3] == 'KRW':
        LIST_coin_KRW.append(tickers[i])

LIST_check_coin_currency = []

for i in range (0, len(LIST_coin_KRW), 1):
    LIST_check_coin_currency.append(LIST_coin_KRW[i][4:])

LIST_check_coin_currency_2 = []

for i in range (0, len(LIST_check_coin_currency), 1) :
    temp = 'KRW-' + LIST_check_coin_currency[i]
    LIST_check_coin_currency_2.append(temp)


# In[4]:

# 정밀 대상 후보군 추출 함수 정의
def find_profitable_coin () :
    candle_count = round((60 / time_unit) * 24 * check_duration_1 * 1)

    # Test setting

    ### moving average 산출 구간 설정
    ma_duration_short = 2  # 단기 ma 산출 기간
    ma_duration_long = 50  # 장기 ma 산출 기간

    ### stochastic 산출 구간 설정
    slow_sto_k_duration = 100  # slow stochastic_k 산출 기간
    slow_sto_d_duration = 30  # slow stochastic_k 산출 기간

    ### buy_transaction 조건값 설정
    ma_short_under_duration = 3  # 최근 몇개 기간동안의 ma_short의추이를 살펴볼것인지 지정
    mid_duration = 30
    ema_long_duration = ma_duration_long
    buy_cri_vol_times = 0.1  # 전 구간 평균 거래량 대비, 직전 구간 (또는 직전직전 구간)에서 거래량이 얼마 이상이여야 buy_transaction을 수행할 것인가
    vol_duration = 12  # 몇 개월 동안의 평균 거래량 기준으로 ref vol을 설정할 것인가
    ratio_ema_o_short_long_buy_1 = [0.98, 1.03]
    ratio_ema_long_1 = 1.0002  # 현재 구간에서의 ema_long값과 직전구간 ema_long값의 비율이 얼마 이상일때 buy transaction을 수행하는가 (여러 필요 조건중의 하나) 1.0003
    buy_price_buffer_ratio = 0.0002

    start_point = 50

    ratio_ema_o_short_long_buy_2 = [1.001, 1.003]  # [0.996, 0.999]
    ratio_ema_long_2 = 1.0001

    decrese_day_duration = 22
    test_day2 = 30

    ### sell transaction 조건값 설정
    sellable_profit = 0.0  # 판매가능 이익율
    sell_force_loss = 0.02  # 강제 판매 손실율
    sell_ma_long_ratio = 1.001  # 1.00079
    sell_ma_mid_ratio = 1.001  # 1.00079
    slow_sto_k_cri = 0.9
    slow_sto_k_count = 1
    ratio_sell_ema_long_chg_state = 0.9999  # 권장 판매조건이 만족 안된 상태에서, ema_long 비율이 어느정도 미만이 되면 자동 판매 되게끔 (매수시의 상승추세가 꺾였다고 판단)
    ratio_sell_ema_mid_chg_state = 0.9995  # 권장 판매조건이 만족 안된 상태에서, ema_long 비율이 어느정도 미만이 되면 자동 판매 되게끔 (매수시의 상승추세가 꺾였다고 판단)
    sell_normal_profit_ratio = 0.003

    ### 거래 후 check 조건값 설정
    check_time_dur = 2  # 거래 이후, 몇개 구간 동안의 추이 (거래값 대비 최대값의 비율, 거래값 대비 구간내 평균값의 비율, 거래값 대비 최소값의 비율 등)
    test_money = 1000000

    DF_result = pd.DataFrame(columns=['Coin_No', 'Coin', 'No_of_buy', 'average_Highest_ratio', 'average_aver_ratio_duration', 'average_L_ratio', 'std_open_value', 'Ref_value'])

    temp_data = {'Coin_No': [0], 'Coin': ['name'], 'No_of_buy': [0], 'average_Highest_ratio': [0.0],
                 'average_aver_ratio_duration': [0.0], 'average_L_ratio': [0.0], 'std_open_value': [0.0],
                 'Ref_value': [0.0]}
    DF_immediate = pd.DataFrame(temp_data)

    # for Test

    for h in range(0, len(LIST_check_coin_currency_2), 1):

        time.sleep(0.1)

        DF_immediate['Coin_No'] = 0
        DF_immediate['Coin'] = 'name'
        DF_immediate['No_of_buy'] = 0
        DF_immediate['average_Highest_ratio'] = 0.0
        DF_immediate['average_aver_ratio_duration'] = 0.0
        DF_immediate['average_L_ratio'] = 0.0
        DF_immediate['std_open_value'] = 0.0
        DF_immediate['Ref_value'] = 0.0

        DF_volume_cri = pyupbit.get_ohlcv(LIST_check_coin_currency_2[h], count=vol_duration, interval='month')
        volume_cri = DF_volume_cri['volume'].sum() / int((60 / time_unit) * 24 * 30 * vol_duration)

        DF_raw = pyupbit.get_ohlcv(LIST_check_coin_currency_2[h], count=candle_count, interval=candle_adapt)
        DF_test = DF_raw.copy()

        DF_test['buy_signal'] = 0
        DF_test['buy_signal_flag'] = 0

        DF_test['ratio_prior_to_cur'] = 0
        DF_test['ratio_vol_to_aver'] = 0

        DF_test['ema_open_short'] = 0
        DF_test['ema_open_mid'] = 0

        DF_test['ema_open_long'] = 0

        DF_test['diff_s_l'] = 0
        DF_test['diff_s_m'] = 0

        DF_test['ratio_prior_to_cur'] = DF_test['open'] / DF_test['open'].shift(1)
        DF_test['ratio_vol_to_aver'] = DF_test['volume'] / volume_cri

        DF_test['ema_open_short'] = DF_test['open'].ewm(span=ma_duration_short, adjust=False).mean()
        DF_test['ema_open_mid'] = DF_test['open'].ewm(span=mid_duration, adjust=False).mean()

        DF_test['ema_open_long'] = DF_test['open'].ewm(span=ma_duration_long, adjust=False).mean()

        DF_test['diff_s_l'] = DF_test['ema_open_short'] - DF_test['ema_open_long']
        DF_test['diff_s_m'] = DF_test['ema_open_short'] - DF_test['ema_open_mid']

        DF_test['ema_o_s_consecutive_rise'] = 0
        DF_test['ema_o_m_consecutive_rise'] = 0
        DF_test['ema_o_l_consecutive_rise'] = 0

        for e in range(0, len(DF_test), 1):
            if (DF_test['ema_open_short'][e] > DF_test['ema_open_short'][e - 1]):
                DF_test['ema_o_s_consecutive_rise'][e] = 1

            if (DF_test['ema_open_mid'][e] > DF_test['ema_open_mid'][e - 1]):
                DF_test['ema_o_m_consecutive_rise'][e] = 1

            if (DF_test['ema_open_long'][e] > DF_test['ema_open_long'][e - 1]):
                DF_test['ema_o_l_consecutive_rise'][e] = 1

        for i in range(start_point + 1, len(DF_test), 1):

            if ((DF_test['ema_o_l_consecutive_rise'][(i - ema_long_duration): i].sum() > 5) and \
                (DF_test['ema_o_s_consecutive_rise'][(i - ma_short_under_duration): i].sum() > (ma_short_under_duration - 2)) and \
                ((DF_test['ema_open_long'][i] / DF_test['ema_open_long'][i - 1]) > ratio_ema_long_1) and \
                ((DF_test['ratio_vol_to_aver'][i - 2] > buy_cri_vol_times) or (DF_test['ratio_vol_to_aver'][i - 1] > buy_cri_vol_times)) and \
                (DF_test['ema_open_short'][i] / DF_test['ema_open_long'][i] > ratio_ema_o_short_long_buy_1[0]) and (DF_test['ema_open_short'][i] / DF_test['ema_open_long'][i] < ratio_ema_o_short_long_buy_1[1])) or \
                    ((DF_test['ema_o_l_consecutive_rise'][(i - ema_long_duration): i].sum() > 6) and \
                     (DF_test['ema_o_s_consecutive_rise'][(i - ma_short_under_duration): i].sum() > 0) and \
                     ((DF_test.loc[DF_test.iloc[(i - decrese_day_duration): (i - 1)]['ema_open_long'].idxmin()]['ema_open_long'] * 1.0019) > DF_test['ema_open_long'][i]) and \
                     ((DF_test['ratio_vol_to_aver'][i - 2] > (0.7 * buy_cri_vol_times)) or (DF_test['ratio_vol_to_aver'][i - 1] > (0.7 * buy_cri_vol_times))) and \
                     (DF_test['ema_open_short'][i] / DF_test['ema_open_long'][i] > ratio_ema_o_short_long_buy_2[0]) and (DF_test['ema_open_short'][i] / DF_test['ema_open_long'][i] < ratio_ema_o_short_long_buy_2[1]) and \
                     ((DF_test['ema_open_long'][i] / DF_test['ema_open_long'][i - 1]) > ratio_ema_long_2)):
                DF_test['buy_signal'][i] = 1
                DF_test['buy_signal_flag'][i] = 1
                buy_price = DF_test['open'][i]

            DF_test['Highest_in_duration'] = 0
            DF_test['Highest_ratio'] = 0.0
            DF_test['Lowest_in_duration'] = 0
            DF_test['Lowest_ratio'] = 0.0
            DF_test['aver_ratio_duration_1'] = 0.0
            DF_test['aver_ratio_duration_2'] = 0.0
            No_of_test_stock = 0
            transaction_No = 0

        for j in range(0, (len(DF_test) - check_time_dur), 1):
            if (DF_test['buy_signal'][j] == 1):
                DF_test['Highest_in_duration'][j] = DF_test.loc[DF_test.iloc[j: (j + check_time_dur)]['high'].idxmax()]['high']
                DF_test['Highest_ratio'][j] = DF_test['Highest_in_duration'][j] / DF_test['open'][j]

                DF_test['Lowest_in_duration'][j] = DF_test.loc[DF_test.iloc[j: (j + check_time_dur)]['low'].idxmin()]['low']
                DF_test['Lowest_ratio'][j] = DF_test['Lowest_in_duration'][j] / DF_test['open'][j]

                DF_test['aver_ratio_duration_1'][j] = DF_test.iloc[(j + 1): ((j + 1) + check_time_dur)]['ratio_prior_to_cur'].sum() / check_time_dur
                DF_test['aver_ratio_duration_2'][j] = DF_test.iloc[(j + 1): ((j + 1) + check_time_dur)]['ratio_prior_to_cur'].mean()

        DF_bought = DF_test[DF_test['buy_signal'] == 1]

        print('\n\
        \nCoin_No : {0}  / Coin : {1}  / No_of_buy : {2}  /  average_Highest_ratio : {3}  / average_aver_ratio_duration : {4}  / average_L_ratio : {5}  / std_open_value : {6:,}  /  Ref_value : {7}'.format(
            h, LIST_check_coin_currency_2[h], DF_test['buy_signal'].sum(), \
            DF_bought['Highest_ratio'].mean(), DF_bought['aver_ratio_duration_2'].mean(),
            DF_bought['Lowest_ratio'].mean(), DF_test['open'].std(), (DF_bought['Highest_ratio'].mean() * DF_bought['aver_ratio_duration_1'].mean() * DF_bought['Lowest_ratio'].mean())))
        print('------------------------------------------------------------------------------------------------------------------------------------------------------')

        DF_immediate['Coin_No'] = h
        DF_immediate['Coin'] = LIST_check_coin_currency_2[h]
        DF_immediate['No_of_buy'] = DF_test['buy_signal'].sum()
        DF_immediate['average_Highest_ratio'] = DF_bought['Highest_ratio'].mean()
        DF_immediate['average_aver_ratio_duration'] = DF_bought['aver_ratio_duration_2'].mean()
        DF_immediate['average_L_ratio'] = DF_bought['Lowest_ratio'].mean()
        DF_immediate['std_open_value'] = DF_test['open'].std()
        DF_immediate['Ref_value'] = (DF_bought['Highest_ratio'].mean() * DF_bought['aver_ratio_duration_1'].mean() * DF_bought['Lowest_ratio'].mean())

        DF_result = pd.concat([DF_result, DF_immediate], axis=0)

    #DF_result.sort_values('average_Highest_ratio', ascending=False).head(No_of_first_candidate_coin)['Coin_No'].values[0]

    list_candidate_coin = []

    for i in range(0, No_of_first_candidate_coin, 1):
        list_candidate_coin.append(
            DF_result.sort_values('average_Highest_ratio', ascending=False).head(No_of_first_candidate_coin)['Coin_No'].values[i])

    print(list_candidate_coin)

    return list_candidate_coin



candle_count_1 = round((60/time_unit) * 24 * check_duration_1 * 1)
#candle_count_2 = int((60/time_unit) * 24 * check_duration_2 * 1)


transaction_fee_ratio = 0.0005   # 거래 수수료 비율

test_money_init = 1000000


# In[5]:



# 투자 대상 코인
coin_No = find_profitable_coin ()


# Test setting

### moving average 산출 구간 설정
ma_duration_short = [1, 4, 1]   # 단기 ma 산출 기간
ma_duration_mid = [30, 60, 10]   # 중기 ma 산출 기간, "2차 상세 조정 대상"
ma_duration_long = [30, 60, 10]   # 장기 ma 산출 기간


### buy_transaction 조건값 설정
ma_short_under_duration = [1, 4, 1]   # 최근 몇개 기간동안의 ma_short의추이를 살펴볼것인지 지정
buy_cri_vol_times = 0.1   # 전 구간 평균 거래량 대비, 직전 구간 (또는 직전직전 구간)에서 거래량이 얼마 이상이여야 buy_transaction을 수행할 것인가
vol_duration = 12   ######### 몇 개월 동안의 평균 거래량 기준으로 ref vol을 설정할 것인가
ratio_ema_o_short_long_buy = [0.9, 1.05]   #########
ratio_ema_long = [1.0, 1.0001, 1.0002]   # 현재 구간에서의 ema_long값과 직전구간 ema_long값의 비율이 얼마 이상일때 buy transaction을 수행하는가 (여러 필요 조건중의 하나), "2차 상세 조정 대상"
ema_Not_buy_check_duration = 100   # 매수해서는 안되는 구간(지속 하락)을 점검하기 위한 ema 값 산출 구간 단위
ema_Not_buy_check_cri = [1.0, 1.0001, 1.0002]   # 몇 단위 이전값대비 현재 ema 값의 비율이 얼마 이상이여야 매수할 것인지 설정, "2차 상세 조정 대상"
buy_price_up_unit = 1

ma_trend_check_duration = 70
ratio_average_duraion_long = 20
ratio_average_duraion_short = 5

start_point = 50


### sell transaction 조건값 설정
sellable_profit = 0.0   ######### 판매가능 이익율
sell_force_loss = [0.03, 0.04, 0.05, 0.06, 0.07] # 강제 판매 손실율
ratio_sell_ema_mid_chg_state = [0.9993, 0.9994, 0.9995, 0.9996, 0.9997]   # 권장 판매조건이 만족 안된 상태에서, ema_long 비율이 어느정도 미만이 되면 자동 판매 되게끔 (매수시의 상승추세가 꺾였다고 판단)
sell_price_buffer = 5
sell_normal_profit_ratio = [0.03, 0.04, 0.05, 0.06, 0.07]
time_out_hour = 13   # 매수 후 몇시간 뒤면 자동 매도 할것인지

'''
### moving average 산출 구간 설정
ma_duration_short = [1, 2, 1]   # 단기 ma 산출 기간
ma_duration_mid = [30, 40, 10]   # 중기 ma 산출 기간, "2차 상세 조정 대상"
ma_duration_long = [30, 40, 10]   # 장기 ma 산출 기간


### buy_transaction 조건값 설정
ma_short_under_duration = [1, 2, 1]   # 최근 몇개 기간동안의 ma_short의추이를 살펴볼것인지 지정
buy_cri_vol_times = 0.1   # 전 구간 평균 거래량 대비, 직전 구간 (또는 직전직전 구간)에서 거래량이 얼마 이상이여야 buy_transaction을 수행할 것인가
vol_duration = 12   ######### 몇 개월 동안의 평균 거래량 기준으로 ref vol을 설정할 것인가
ratio_ema_o_short_long_buy = [0.9, 1.05]   #########
ratio_ema_long = [1.0, 1.0001]   # 현재 구간에서의 ema_long값과 직전구간 ema_long값의 비율이 얼마 이상일때 buy transaction을 수행하는가 (여러 필요 조건중의 하나), "2차 상세 조정 대상"
ema_Not_buy_check_duration = 100   # 매수해서는 안되는 구간(지속 하락)을 점검하기 위한 ema 값 산출 구간 단위
ema_Not_buy_check_cri = [1.0, 1.0001]   # 몇 단위 이전값대비 현재 ema 값의 비율이 얼마 이상이여야 매수할 것인지 설정, "2차 상세 조정 대상"
buy_price_up_unit = 1

start_point = 50


### sell transaction 조건값 설정
sellable_profit = 0.0   ######### 판매가능 이익율
sell_force_loss = [0.03, 0.04] # 강제 판매 손실율
ratio_sell_ema_mid_chg_state = [0.9993, 0.9994]   # 권장 판매조건이 만족 안된 상태에서, ema_long 비율이 어느정도 미만이 되면 자동 판매 되게끔 (매수시의 상승추세가 꺾였다고 판단)
sell_price_buffer = 2
sell_normal_profit_ratio = [0.03, 0.04]
'''


### 거래 후 check 조건값 설정 
check_time_dur = 5   # 거래 이후, 몇개 구간 동안의 추이 (거래값 대비 최대값의 비율, 거래값 대비 구간내 평균값의 비율, 거래값 대비 최소값의 비율 등)






#####################################
def main_parameter_finder(DF_simul, coin, simul_days, ma_duration_s, ma_duration_l, ma_s_under_duration, ratio_force_l,
                          ratio_sell_ema_m_chg_state, ratio_sell_normal):
    #print('[Coin : {0}__Main parameter finder with {1} days - ma_duration_short : {2}  / ma_duration_long : {3}  /  ma_short_under_duration : {4}  /  ratio_force_loss : {5}  / ratio_sell_ema_mid_chg_state : {6}  /  ratio_sell_normal : {7}'.        format(coin, simul_days, ma_duration_s, ma_duration_l, ma_s_under_duration, ratio_force_l, ratio_sell_ema_m_chg_state, ratio_sell_normal))

    test_money = test_money_init
    # 기초 수치 생성 (e_ma 등)
    DF_test = DF_simul.copy()
    # DF_test = DF_simul.iloc[(24 * 125) :(24 * 145), :]

    DF_test['ratio_prior_to_cur'] = DF_test['open'] / DF_test['open'].shift(1)
    DF_test['ratio_vol_to_aver'] = DF_test['volume'] / volume_cri

    DF_test['ema_open_short'] = DF_test['open'].ewm(span=ma_duration_s, adjust=False).mean()
    DF_test['ema_open_mid'] = DF_test['open'].ewm(span=ma_duration_mid[0], adjust=False).mean()
    DF_test['ema_open_long'] = DF_test['open'].ewm(span=ma_duration_l, adjust=False).mean()

    DF_test['ma_trend_check'] = DF_test['open'].ewm(span=ma_trend_check_duration, adjust=False).mean()
    DF_test['ratio_trend'] = DF_test['ma_trend_check'] / DF_test['ma_trend_check'].shift(1)


    DF_test['diff_s_l'] = DF_test['ema_open_short'] - DF_test['ema_open_long']
    DF_test['diff_s_m'] = DF_test['ema_open_short'] - DF_test['ema_open_mid']

    DF_test['ema_o_s_consecutive_rise'] = 0
    DF_test['ema_o_m_consecutive_rise'] = 0
    DF_test['ema_o_l_consecutive_rise'] = 0

    DF_test['ema_o_s_consecutive_rise'] = np.where(DF_test['ema_open_short'] > DF_test['ema_open_short'].shift(1), 1, 0)
    DF_test['ema_o_m_consecutive_rise'] = np.where(DF_test['ema_open_mid'] > DF_test['ema_open_mid'].shift(1), 1, 0)
    DF_test['ema_o_l_consecutive_rise'] = np.where(DF_test['ema_open_long'] > DF_test['ema_open_long'].shift(1), 1, 0)

    DF_test['ema_Not_buy_check'] = DF_test['open'].ewm(span=ema_Not_buy_check_duration, adjust=False).mean()
    DF_test['ratio_ema_Not_buy_check'] = DF_test['ema_Not_buy_check'] / DF_test['ema_Not_buy_check'].shift(3)

    # Buy / Sell logic

    DF_test['buy_signal'] = 0
    DF_test['buy_signal_flag'] = 0
    DF_test['sell_signal'] = 0
    DF_test['sell_normal'] = 0
    DF_test['sell_state_change'] = 0
    DF_test['sell_time_out'] = 0
    DF_test['sell_loss'] = 0
    DF_test['sold_price'] = 0
    buy_price = 0
    buy_time = 0
    sell_forced = 0

    for j in range(start_point + 1, len(DF_test), 1):

        # 매수
        if (sell_forced == 0) and (DF_test['buy_signal_flag'][j - 1] == 0):
            if ((DF_test['ema_o_l_consecutive_rise'][(j - ma_duration_l): j].sum() > 5) and \
                (DF_test['ema_o_s_consecutive_rise'][(j - ma_s_under_duration): j].sum() > (ma_s_under_duration - 2)) and \
                ((DF_test['ema_open_long'][j] / DF_test['ema_open_long'][j - 1]) > ratio_ema_long[0]) and \
                ((DF_test['ratio_vol_to_aver'][j - 2] > buy_cri_vol_times) or (DF_test['ratio_vol_to_aver'][j - 1] > buy_cri_vol_times)) and \
                (DF_test['ema_open_short'][j] / DF_test['ema_open_long'][j] > ratio_ema_o_short_long_buy[0]) and \
                (DF_test['ema_open_short'][j] / DF_test['ema_open_long'][j] < ratio_ema_o_short_long_buy[1]) and \
                (DF_test['ratio_ema_Not_buy_check'][j] > ema_Not_buy_check_cri[0]) and \
                ((DF_test['ema_open_mid'][j - 1] / DF_test['ema_open_mid'][j - 2]) >= ratio_sell_ema_m_chg_state) and \
                ((DF_test['ema_open_mid'][j] / DF_test['ema_open_mid'][j - 1]) >= ratio_sell_ema_m_chg_state) and \
                (DF_test.iloc[j : (j + 1), :]['ratio_trend'].mean() > (0.9998 * DF_test.iloc[(j - ratio_average_duraion_long): j, :]['ratio_trend'].mean())) and \
                (DF_test.iloc[j : (j + 1), :]['ratio_trend'].mean() > (0.9998 * DF_test.iloc[(j - ratio_average_duraion_short): j, :]['ratio_trend'].mean()))) :

                DF_test['buy_signal'][j] = 1
                DF_test['buy_signal_flag'][j] = 1
                buy_price = DF_test['open'][j] + (buy_price_up_unit * unit_value)
                buy_time = DF_test.index[j]

        # 매도
        if DF_test['buy_signal_flag'][j - 1] == 1:
            DF_test['buy_signal_flag'][j] = 1
            DF_test['sold_price'][j] = DF_test['sold_price'][j - 1]

            if (DF_test['high'][j] / buy_price) > (1 + ratio_sell_normal):
                DF_test['sell_signal'][j] = 1
                DF_test['buy_signal_flag'][j] = 0
                DF_test['sell_normal'][j] = 1
                DF_test['sold_price'][j] = (buy_price * (1 + ratio_sell_normal))

            elif ((DF_test['ema_open_mid'][j - 1] / DF_test['ema_open_mid'][j - 2]) < ratio_sell_ema_m_chg_state) and (
                    (DF_test['ema_open_mid'][j] / DF_test['ema_open_mid'][j - 1]) < ratio_sell_ema_m_chg_state):
                DF_test['sell_signal'][j] = 1
                DF_test['buy_signal_flag'][j] = 0
                DF_test['sell_state_change'][j] = 1

            elif ((DF_test.index[j] - buy_time).seconds / 3600) > time_out_hour :
                DF_test['sell_signal'][j] = 1
                DF_test['buy_signal_flag'][j] = 0
                DF_test['sell_time_out'][j] = 1

            elif (DF_test['low'][j] / buy_price) < (1 - ratio_force_l):
                DF_test['sell_signal'][j] = 1
                DF_test['buy_signal_flag'][j] = 0
                DF_test['sell_loss'][j] = 1
                DF_test['sold_price'][j] = (buy_price * (1 - ratio_force_l))
                sell_forced = 1

    # DF_test.to_excel ('DF_temp.xls')

    # 누적 결과분석
    DF_test['H_duration'] = 0
    DF_test['H_ratio'] = 0.0
    DF_test['L_duration'] = 0
    DF_test['L_ratio'] = 0.0
    DF_test['aver_ratio_duration'] = 0.0
    # DF_test['std'] = 0
    No_of_test_stock = 0
    transaction_No = 0

    for k in range(check_time_dur, (len(DF_test) - check_time_dur), 1):
        if (DF_test['buy_signal'][k] == 1):
            DF_test['H_duration'][k] = DF_test.loc[DF_test.iloc[k: (k + check_time_dur)]['high'].idxmax()]['high']
            DF_test['L_duration'][k] = DF_test.loc[DF_test.iloc[k: (k + check_time_dur)]['low'].idxmin()]['low']
            DF_test['H_ratio'][k] = DF_test['H_duration'][k] / DF_test['open'][k]
            DF_test['L_ratio'][k] = DF_test['L_duration'][k] / DF_test['open'][k]
            DF_test['aver_ratio_duration'][k] = DF_test.iloc[(k + 1): ((k + 1) + check_time_dur)][
                                                    'ratio_prior_to_cur'].sum() / check_time_dur

    for m in range(0, len(DF_test), 1):
        if DF_test['buy_signal'][m] == 1:
            transaction_No = transaction_No + 1
            No_of_test_stock = (test_money / (DF_test['open'][m] + (buy_price_up_unit * unit_value))) * (
                        1 - transaction_fee_ratio)
            test_money = test_money - ((DF_test['open'][m] + (buy_price_up_unit * unit_value)) * No_of_test_stock)
            # print ('[transaction_BUY] transaction_No : {0}  / residual_money : {1:,}  / No_of_stock : {2}'.format(transaction_No, test_money, No_of_test_stock))

        elif DF_test['sell_signal'][m] == 1:
            if DF_test['sell_normal'][m] == 1:
                test_money = test_money + (
                            ((DF_test['sold_price'][m] - (sell_price_buffer * unit_value)) * No_of_test_stock) * (
                                1 - transaction_fee_ratio))
                No_of_test_stock = 0
                # print ('[transaction_SELL_Normal] {0}  transaction_No : {1}  / Sell_type : {2}_{3}_{4}_{5}  /  residual_money : {6:,}  / No_of_stock : {7}'.format(DF_test.index[m], transaction_No, DF_test['sell_normal'][m], DF_test['sell_state_change'][m], DF_test['sell_time_out'][m], DF_test['sell_loss'][m], test_money, No_of_test_stock))
            elif DF_test['sell_state_change'][m] == 1:
                test_money = test_money + (
                            ((DF_test['open'][m] - (sell_price_buffer * unit_value)) * No_of_test_stock) * (
                                1 - transaction_fee_ratio))
                No_of_test_stock = 0
                # print ('[transaction_SELL_Normal] {0}  transaction_No : {1}  / Sell_type : {2}_{3}_{4}_{5}  /  residual_money : {6:,}  / No_of_stock : {7}'.format(DF_test.index[m], transaction_No, DF_test['sell_normal'][m], DF_test['sell_state_change'][m], DF_test['sell_time_out'][m], DF_test['sell_loss'][m], test_money, No_of_test_stock))
            else:
                test_money = test_money + (
                            ((DF_test['sold_price'][m] - (sell_price_buffer * unit_value)) * No_of_test_stock) * (
                                1 - transaction_fee_ratio))
                No_of_test_stock = 0
                # print ('[transaction_SELL_Normal] {0}  transaction_No : {1}  / Sell_type : {2}_{3}_{4}_{5}  /  residual_money : {6:,}  / No_of_stock : {7}'.format(DF_test.index[m], transaction_No, DF_test['sell_normal'][m], DF_test['sell_state_change'][m], DF_test['sell_time_out'][m], DF_test['sell_loss'][m], test_money, No_of_test_stock))

    DF_bought = DF_test[DF_test['buy_signal'] == 1]

    begin_data = {'Coin_No': [coin], 'Coin': [LIST_check_coin_currency[coin]], 'check_duration': [simul_days],
                  'resi_money': [test_money], 'stock_value': [(No_of_test_stock * DF_test['open'][-1])],
                  'resi_value': [max([test_money, (No_of_test_stock * DF_test['open'][-1])])],
                  'No_of_buy': [transaction_No], 'No_of_N_sell': [DF_test['sell_normal'].sum()],
                  'No_of_S_C_sell': [DF_test['sell_state_change'].sum()], 'No_of_time_out_sell': [DF_test['sell_time_out'].sum()], 'No_of_F_sell': [DF_test['sell_loss'].sum()],
                  'average_Highest_ratio': [DF_bought['H_ratio'].mean()],
                  'average_aver_ratio_duration': [DF_bought['aver_ratio_duration'].mean()],
                  'average_L_ratio': [DF_bought['L_ratio'].mean()], 'ma_duration_short': [ma_duration_s],
                  'ma_duration_mid': ma_duration_mid[0], 'ma_duration_long': [ma_duration_l],
                  'ma_short_under_duration': [ma_s_under_duration], 'buy_cri_vol_times': buy_cri_vol_times,
                  'ratio_ema_long': ratio_ema_long[0], 'ema_Not_buy_check_cri': ema_Not_buy_check_cri[0],
                  'sell_force_loss': [ratio_force_l], 'ratio_sell_ema_mid_chg_state': [ratio_sell_ema_m_chg_state],
                  'sell_normal_profit_ratio': [ratio_sell_normal]}

    DF_output = pd.DataFrame(begin_data)

    return DF_output
#########################################################


total_accum_data = {'Coin_No': [coin_No], 'Coin': [0], 'check_duration': [0.0], \
                    'resi_money': [0.0], 'stock_value': [0.0], 'resi_value': [0.0], \
                    'No_of_buy': [0], 'No_of_N_sell': [0], 'No_of_S_C_sell': [0], 'No_of_time_out_sell': [0], 'No_of_F_sell': [0], \
                    'average_Highest_ratio': [0.0], 'average_aver_ratio_duration': [0.0], \
                    'average_L_ratio': [0.0], 'ma_duration_short': [0], 'ma_duration_mid': [0], 'ma_duration_long': [0],
                    'ma_short_under_duration': [0], 'buy_cri_vol_times': buy_cri_vol_times,
                    'ratio_ema_long': [0.0], 'ema_Not_buy_check_cri': [0],
                    'sell_force_loss': [0.0], 'ratio_sell_ema_mid_chg_state': [0.0],
                    'sell_normal_profit_ratio': [0.0]}

DF_total_accum = pd.DataFrame(total_accum_data)

for i_coin in coin_No :
    print ('\n\n\n$$$$$$$$$$$$$$$ coin No : {0} / coin : {1} $$$$$$$$$$$$$$$$$$$'.format(i_coin, LIST_check_coin_currency_2[i_coin]))
    print('Main parameter finder with {0} days'.format (check_duration_1))


    DF_result_accum_total = pd.DataFrame(
        columns=['Coin_No', 'Coin', 'check_duration', 'resi_money', 'stock_value', 'resi_value', 'No_of_buy',
                 'No_of_N_sell', 'No_of_S_C_sell', 'No_of_time_out_sell', 'No_of_F_sell', 'average_Highest_ratio',
                 'average_aver_ratio_duration', 'average_L_ratio', 'ma_duration_short', 'ma_duration_mid',
                 'ma_duration_long', 'ma_short_under_duration', 'buy_cri_vol_times', 'ratio_ema_long',
                 'ema_Not_buy_check_cri', 'sell_force_loss', 'ratio_sell_ema_mid_chg_state',
                 'sell_normal_profit_ratio'])

    DF_volume_cri = pyupbit.get_ohlcv(LIST_check_coin_currency_2[i_coin], count = vol_duration , interval = 'month')
    volume_cri = DF_volume_cri['volume'].sum() / int((60/time_unit) * 24 * 30 * vol_duration)

    # 매수 최소단위 산출

    if DF_volume_cri['open'][-1] >= 1000000 :  # 200만원 이상은 거래단위가 1000원, 100~200만원은 거래단위가 500원이지만 편의상 200만원 이상과 함께 처리
        unit_factor = -3
        unit_value = 1000
    elif DF_volume_cri['open'][-1] >= 100000 :
        unit_factor = -2
        unit_value = 50
    elif DF_volume_cri['open'][-1] >= 10000 :
        unit_factor = -1
        unit_value = 10
    elif DF_volume_cri['open'][-1] >= 1000 :
        unit_factor = -1
        unit_value = 5
    elif DF_volume_cri['open'][-1] >= 100 :
        unit_factor = 0
        unit_value = 1
    else :
        DF_volume_cri['open'][-1] <= 100   # 100원 미만은 별도로 code에서 int형이 아닌 float형으로 형변환 해줘야함
        unit_factor = 1
        unit_value = 0.1

    print ('DF_volume_cri[open][-1] : {0}  / unit_value : {1}'.format(DF_volume_cri['open'][-1], unit_value))


    # In[11]:



    DF_result_accum = pd.DataFrame(columns = ['Coin_No', 'Coin', 'check_duration', 'resi_money', 'stock_value', 'resi_value', 'No_of_buy', 'No_of_N_sell', 'No_of_S_C_sell', 'No_of_time_out_sell' ,'No_of_F_sell', 'average_Highest_ratio', 'average_aver_ratio_duration', 'average_L_ratio', 'ma_duration_short',                                           'ma_duration_mid', 'ma_duration_long', 'ma_short_under_duration', 'buy_cri_vol_times', 'ratio_ema_long', 'ema_Not_buy_check_cri',                                           'sell_force_loss', 'ratio_sell_ema_mid_chg_state', 'sell_normal_profit_ratio'])


    # check_duration_1 기준 주요 파라미터값 추출

    DF_duration_1_main_parameter = pyupbit.get_ohlcv(LIST_check_coin_currency_2[i_coin], count = candle_count_1, interval = candle_adapt)


    for v_0 in range (ma_duration_short[0], (ma_duration_short[1] + ma_duration_short[2]), ma_duration_short[2]) :

        for v_1 in range (ma_duration_long[0], (ma_duration_long[1] + ma_duration_long[2]), ma_duration_long[2]) :

            for v_2 in range (ma_short_under_duration[0], (ma_short_under_duration[1] + ma_short_under_duration[2]), ma_short_under_duration[2]) :

                for v_3 in sell_force_loss :

                    for v_4 in ratio_sell_ema_mid_chg_state :

                        for v_5 in sell_normal_profit_ratio :

                            DF_main_para_setting = main_parameter_finder (DF_duration_1_main_parameter, i_coin, check_duration_1, v_0, v_1, v_2, v_3, v_4, v_5)
                            DF_result_accum = pd.concat([DF_result_accum, DF_main_para_setting], axis = 0)



    # In[ ]:


    #DF_selected_1 = DF_result_accum[DF_result_accum['resi_value'] > (test_money_init * 1.1)]
    DF_selected_1 = DF_result_accum.sort_values('resi_value', ascending = False).head(1)


    # In[ ]:





    # 상세 파라미터값 최적화


    DF_final_accum = pd.DataFrame(columns = ['Coin_No', 'Coin', 'check_duration', 'resi_money', 'stock_value', 'resi_value', 'No_of_buy', 'No_of_N_sell', 'No_of_S_C_sell', \
                                             'No_of_time_out_sell', 'No_of_F_sell', 'average_Highest_ratio', 'average_aver_ratio_duration', 'average_L_ratio', 'ma_duration_short', \
                                             'ma_duration_mid', 'ma_duration_long', 'ma_short_under_duration', 'buy_cri_vol_times', 'ratio_ema_long', 'ema_Not_buy_check_cri', \
                                             'sell_force_loss', 'ratio_sell_ema_mid_chg_state', 'sell_normal_profit_ratio'])

    print ('$$$$$$$$$$$$$ precise parameter-value optimizing $$$$$$$$$$$$$')
    for x_0 in range(ma_duration_mid[0], (ma_duration_mid[1] + ma_duration_mid[2]), ma_duration_mid[2]) :

        for x_1 in ratio_ema_long :

            for x_2 in ema_Not_buy_check_cri :

                #print('\nprocessing in ma_duration_short : {0} / ma_duration_mid : {1}  / ma_duration_long : {2}  / ma_short_under_duration : {3}  / buy_cri_vol_times : {4}  /  ratio_ema_long : {5}  / ema_Not_buy_check_cri : {6} / sell_force_loss : {7}  / ratio_sell_ema_mid_chg_state : {8}  / sell_normal_profit_ratio : {9}'.format(DF_chosen['ma_duration_short'].values[0], x_0, DF_chosen['ma_duration_long'].values[0], DF_chosen['ma_short_under_duration'].values[0], buy_cri_vol_times, x_1, x_2, DF_chosen['sell_force_loss'].values[0], DF_chosen['ratio_sell_ema_mid_chg_state'].values[0], DF_chosen['sell_normal_profit_ratio'].values[0]))

                test_money = 1000000

                # 기초 수치 생성 (e_ma 등)
                DF_test = DF_duration_1_main_parameter.copy()
                # DF_test = DF_raw.iloc[(24 * 125) :(24 * 145), :]

                DF_test['ratio_prior_to_cur'] = DF_test['open'] / DF_test['open'].shift(1)
                DF_test['ratio_vol_to_aver'] = DF_test['volume'] / volume_cri

                DF_test['ema_open_short'] = DF_test['open'].ewm(span = DF_selected_1['ma_duration_short'].values[0], adjust=False).mean()
                DF_test['ema_open_mid'] = DF_test['open'].ewm(span = x_0, adjust=False).mean()
                DF_test['ema_open_long'] = DF_test['open'].ewm(span = DF_selected_1['ma_duration_long'].values[0], adjust=False).mean()

                DF_test['ma_trend_check'] = DF_test['open'].ewm(span=ma_trend_check_duration, adjust=False).mean()
                DF_test['ratio_trend'] = DF_test['ma_trend_check'] / DF_test['ma_trend_check'].shift(1)

                DF_test['diff_s_l'] = DF_test['ema_open_short'] - DF_test['ema_open_long']
                DF_test['diff_s_m'] = DF_test['ema_open_short'] - DF_test['ema_open_mid']

                DF_test['ema_o_s_consecutive_rise'] = 0
                DF_test['ema_o_m_consecutive_rise'] = 0
                DF_test['ema_o_l_consecutive_rise'] = 0

                DF_test['ema_o_s_consecutive_rise'] = np.where(DF_test['ema_open_short'] > DF_test['ema_open_short'].shift(1), 1, 0)
                DF_test['ema_o_m_consecutive_rise'] = np.where(DF_test['ema_open_mid'] > DF_test['ema_open_mid'].shift(1), 1, 0)
                DF_test['ema_o_l_consecutive_rise'] = np.where(DF_test['ema_open_long'] > DF_test['ema_open_long'].shift(1), 1, 0)

                DF_test['ema_Not_buy_check'] = DF_test['open'].ewm(span=ema_Not_buy_check_duration, adjust=False).mean()
                DF_test['ratio_ema_Not_buy_check'] = DF_test['ema_Not_buy_check'] / DF_test['ema_Not_buy_check'].shift(3)

                # Buy / Sell logic

                DF_test['buy_signal'] = 0
                DF_test['buy_signal_flag'] = 0
                DF_test['sell_signal'] = 0
                DF_test['sell_normal'] = 0
                DF_test['sell_state_change'] = 0
                DF_test['sell_time_out'] = 0
                DF_test['sell_loss'] = 0
                DF_test['sold_price'] = 0
                buy_price = 0
                sell_forced = 0

                for j in range(start_point + 1, len(DF_test), 1):

                    # 매수
                    if (sell_forced == 0) and (DF_test['buy_signal_flag'][j - 1] == 0):
                        if ((DF_test['ema_o_l_consecutive_rise'][(j - DF_selected_1['ma_duration_long'].values[0]): j].sum() > 5) and \
                            (DF_test['ema_o_s_consecutive_rise'][(j - DF_selected_1['ma_short_under_duration'].values[0]): j].sum() > (DF_selected_1['ma_short_under_duration'].values[0] - 2)) and \
                            ((DF_test['ema_open_long'][j] / DF_test['ema_open_long'][j - 1]) > x_1) and \
                            ((DF_test['ratio_vol_to_aver'][j - 2] > buy_cri_vol_times) or (DF_test['ratio_vol_to_aver'][j - 1] > buy_cri_vol_times)) and \
                            (DF_test['ema_open_short'][j] / DF_test['ema_open_long'][j] > ratio_ema_o_short_long_buy[0]) and \
                            (DF_test['ema_open_short'][j] / DF_test['ema_open_long'][j] < ratio_ema_o_short_long_buy[1]) and \
                            (DF_test['ratio_ema_Not_buy_check'][j] > x_2) and \
                            ((DF_test['ema_open_mid'][j - 1] / DF_test['ema_open_mid'][j - 2]) >= DF_selected_1['ratio_sell_ema_mid_chg_state'].values[0]) and \
                            ((DF_test['ema_open_mid'][j] / DF_test['ema_open_mid'][j - 1]) >= DF_selected_1['ratio_sell_ema_mid_chg_state'].values[0]) and \
                            (DF_test.iloc[j : (j + 1), :]['ratio_trend'].mean() > (0.9998 * DF_test.iloc[(j - ratio_average_duraion_long): j, :]['ratio_trend'].mean())) and \
                            (DF_test.iloc[j : (j + 1), :]['ratio_trend'].mean() > (0.9998 * DF_test.iloc[(j - ratio_average_duraion_short): j, :]['ratio_trend'].mean()))) :

                            DF_test['buy_signal'][j] = 1
                            DF_test['buy_signal_flag'][j] = 1
                            buy_price = DF_test['open'][j] + (buy_price_up_unit * unit_value)
                            buy_time = DF_test.index[j]

                    # 매도
                    if DF_test['buy_signal_flag'][j - 1] == 1:
                        DF_test['buy_signal_flag'][j] = 1
                        DF_test['sold_price'][j] = DF_test['sold_price'][j - 1]

                        if (DF_test['high'][j] / buy_price) > (1 + DF_selected_1['sell_normal_profit_ratio'].values[0]):
                            DF_test['sell_signal'][j] = 1
                            DF_test['buy_signal_flag'][j] = 0
                            DF_test['sell_normal'][j] = 1
                            DF_test['sold_price'][j] = (buy_price * (1 + DF_selected_1['sell_normal_profit_ratio'].values[0]))

                        elif ((DF_test['ema_open_mid'][j - 1] / DF_test['ema_open_mid'][j - 2]) < DF_selected_1['ratio_sell_ema_mid_chg_state'].values[0]) and \
                                ((DF_test['ema_open_mid'][j] / DF_test['ema_open_mid'][j - 1]) < DF_selected_1['ratio_sell_ema_mid_chg_state'].values[0]):
                            DF_test['sell_signal'][j] = 1
                            DF_test['buy_signal_flag'][j] = 0
                            DF_test['sell_state_change'][j] = 1

                        elif ((DF_test.index[j] - buy_time).seconds / 3600) > time_out_hour :
                            DF_test['sell_signal'][j] = 1
                            DF_test['buy_signal_flag'][j] = 0
                            DF_test['sell_time_out'][j] = 1

                        elif (DF_test['open'][j] / buy_price) < (1 - DF_selected_1['sell_force_loss'].values[0]):
                            DF_test['sell_signal'][j] = 1
                            DF_test['buy_signal_flag'][j] = 0
                            DF_test['sell_loss'][j] = 1
                            DF_test['sold_price'][j] = (buy_price * (1 - DF_selected_1['sell_normal_profit_ratio'].values[0]))
                            sell_forced = 1

                # DF_test.to_excel ('DF_temp.xls')

                # 누적 결과분석
                DF_test['H_duration'] = 0
                DF_test['H_ratio'] = 0.0
                DF_test['L_duration'] = 0
                DF_test['L_ratio'] = 0.0
                DF_test['aver_ratio_duration'] = 0.0
                # DF_test['std'] = 0
                No_of_test_stock = 0
                transaction_No = 0

                for k in range(check_time_dur, (len(DF_test) - check_time_dur), 1):
                    if (DF_test['buy_signal'][k] == 1):
                        DF_test['H_duration'][k] = \
                        DF_test.loc[DF_test.iloc[k: (k + check_time_dur)]['high'].idxmax()]['high']
                        DF_test['L_duration'][k] = \
                        DF_test.loc[DF_test.iloc[k: (k + check_time_dur)]['low'].idxmin()]['low']
                        DF_test['H_ratio'][k] = DF_test['H_duration'][k] / DF_test['open'][k]
                        DF_test['L_ratio'][k] = DF_test['L_duration'][k] / DF_test['open'][k]
                        DF_test['aver_ratio_duration'][k] = DF_test.iloc[(k + 1): ((k + 1) + check_time_dur)]['ratio_prior_to_cur'].sum() / check_time_dur

                for m in range(0, len(DF_test), 1):
                    if DF_test['buy_signal'][m] == 1:
                        transaction_No = transaction_No + 1
                        No_of_test_stock = (test_money / (DF_test['open'][m] + (buy_price_up_unit * unit_value))) * (1 - transaction_fee_ratio)
                        test_money = test_money - ((DF_test['open'][m] + (buy_price_up_unit * unit_value)) * No_of_test_stock)
                        # print ('[transaction_BUY] transaction_No : {0}  / residual_money : {1:,}  / No_of_stock : {2}'.format(transaction_No, test_money, No_of_test_stock))

                    elif DF_test['sell_signal'][m] == 1:
                        if DF_test['sell_normal'][m] == 1:
                            test_money = test_money + (((DF_test['sold_price'][m] - (sell_price_buffer * unit_value)) * No_of_test_stock) * (1 - transaction_fee_ratio))
                            No_of_test_stock = 0
                            # print ('[transaction_SELL_Normal] transaction_No : {0}  / Sell_type : {1}_{2}_{3}  /  residual_money : {4:,}  / No_of_stock : {5}'.format(transaction_No, DF_test['sell_normal'][i], DF_test['sell_state_change'][i], DF_test['sell_loss'][i], test_money, No_of_test_stock))

                        elif DF_test['sell_state_change'][m] == 1:
                            test_money = test_money + (((DF_test['open'][m] - (sell_price_buffer * unit_value)) * No_of_test_stock) * (1 - transaction_fee_ratio))
                            No_of_test_stock = 0
                            # print ('[transaction_SELL_Other-way] transaction_No : {0}  / Sell_type : {1}_{2}_{3}  /  residual_money : {4:,}  / No_of_stock : {5}'.format(transaction_No, DF_test['sell_normal'][i], DF_test['sell_state_change'][i], DF_test['sell_loss'][i], test_money, No_of_test_stock))

                        elif DF_test['sell_state_change'][m] == 1:
                            test_money = test_money + (((DF_test['open'][m] - (sell_price_buffer * unit_value)) * No_of_test_stock) * (1 - transaction_fee_ratio))
                            No_of_test_stock = 0
                            # print ('[transaction_SELL_Other-way] transaction_No : {0}  / Sell_type : {1}_{2}_{3}  /  residual_money : {4:,}  / No_of_stock : {5}'.format(transaction_No, DF_test['sell_normal'][i], DF_test['sell_state_change'][i], DF_test['sell_loss'][i], test_money, No_of_test_stock))

                        else :
                            test_money = test_money + (((DF_test['sold_price'][m] - (sell_price_buffer * unit_value)) * No_of_test_stock) * (1 - transaction_fee_ratio))
                            No_of_test_stock = 0
                            # print ('[transaction_SELL_Normal] transaction_No : {0}  / Sell_type : {1}_{2}_{3}  /  residual_money : {4:,}  / No_of_stock : {5}'.format(transaction_No, DF_test['sell_normal'][i], DF_test['sell_state_change'][i], DF_test['sell_loss'][i], test_money, No_of_test_stock))

                DF_bought = DF_test[DF_test['buy_signal'] == 1]

                begin_data = {'Coin_No': [i_coin], 'Coin': [LIST_check_coin_currency[i_coin]],
                                'check_duration': [check_duration_1], \
                                'resi_money': [test_money], 'stock_value': [(No_of_test_stock * DF_test['open'][-1])], \
                                'resi_value': [max([test_money, (No_of_test_stock * DF_test['open'][-1])])], \
                                'No_of_buy': [transaction_No], 'No_of_N_sell': [DF_test['sell_normal'].sum()], 'No_of_S_C_sell': [DF_test['sell_state_change'].sum()], \
                              'No_of_time_out_sell': [DF_test['sell_time_out'].sum()], 'No_of_F_sell': [DF_test['sell_loss'].sum()], 'average_Highest_ratio': [DF_bought['H_ratio'].mean()], \
                                'average_aver_ratio_duration': [DF_bought['aver_ratio_duration'].mean()], 'average_L_ratio': [DF_bought['L_ratio'].mean()], \
                                'ma_duration_short': [DF_selected_1['ma_duration_short'].values[0]], 'ma_duration_mid': [x_0], \
                                'ma_duration_long': [DF_selected_1['ma_duration_long'].values[0]], 'ma_short_under_duration': [DF_selected_1['ma_short_under_duration'].values[0]], \
                                'buy_cri_vol_times': buy_cri_vol_times, 'ratio_ema_long': [x_1], 'ema_Not_buy_check_cri': [x_2], \
                                'sell_force_loss': [DF_selected_1['sell_force_loss'].values[0]], 'ratio_sell_ema_mid_chg_state': [DF_selected_1['ratio_sell_ema_mid_chg_state'].values[0]], \
                                'sell_normal_profit_ratio': [DF_selected_1['sell_normal_profit_ratio'].values[0]]}

                DF_temp = pd.DataFrame(begin_data)
                DF_final_accum = pd.concat([DF_final_accum, DF_temp], axis=0)

    DF_final_accum.to_excel('DF_final_accum_{0}_{1}.xlsx'.format(LIST_check_coin_currency[i_coin], check_duration_1))

    DF_optimized = DF_final_accum.sort_values('resi_value', ascending = False).head(1)

    DF_total_accum = pd.concat([DF_total_accum, DF_optimized], axis=0)

    print ('DF_optimized_Top\n', DF_optimized)

    print ('================== optimized parameter-values =======================\n')

    print ('\n# 투자 대상 코인')
    print ('coin_No = {0}'.format(i_coin))

    print('\n# Test setting')
    print ('\n### moving average 산출 구간 설정')
    print ('ma_duration_short = {0}   # 단기 ma 산출 기간'.format(DF_optimized['ma_duration_short'].values[0]))
    print ('ma_duration_mid = {0}   # 중기 ma 산출 기간'.format(DF_optimized['ma_duration_mid'].values[0]))
    print ('ma_duration_long = {0}   # 장기 ma 산출 기간'.format(DF_optimized['ma_duration_long'].values[0]))

    print('\n### buy_transaction 조건값 설정')
    print('ma_short_under_duration = {0}   # 최근 몇개 기간동안의 ma_short의추이를 살펴볼것인지 지정'.format(DF_optimized['ma_short_under_duration'].values[0]))
    print('buy_cri_vol_times = {0}   # 전 구간 평균 거래량 대비, 직전 구간 (또는 직전직전 구간)에서 거래량이 얼마 이상이여야 buy_transaction을 수행할 것인가'.format(buy_cri_vol_times))
    print('vol_duration = {0}   # 몇 개월 동안의 평균 거래량 기준으로 ref vol을 설정할 것인가'.format(vol_duration))
    print('ratio_ema_o_short_long_buy_1 = [0.9, 1.05]')
    print('ratio_ema_long = {0}   # 현재 구간에서의 ema_long값과 직전구간 ema_long값의 비율이 얼마 이상일때 buy transaction을 수행하는가 (여러 필요 조건중의 하나)'.format(DF_optimized['ratio_ema_long'].values[0]))
    print('ema_Not_buy_duration = {0}'.format(ema_Not_buy_check_duration))
    print('ema_Not_buy_cri = {0}'.format(DF_optimized['ema_Not_buy_check_cri'].values[0]))
    print('buy_price_up_unit = {0}'.format(buy_price_up_unit))

    print('\n### sell transaction 조건값 설정')
    print('sellable_profit = 0.0   # 판매가능 이익율')
    print('sell_force_loss = {0}  # 강제 판매 손실율'.format(DF_optimized['sell_force_loss'].values[0]))
    print('ratio_sell_ema_mid_chg_state = {0}   # 권장 판매조건이 만족 안된 상태에서, ema_long 비율이 어느정도 미만이 되면 자동 판매 되게끔 (매수시의 상승추세가 꺾였다고 판단)'.format(DF_optimized['ratio_sell_ema_mid_chg_state'].values[0]))
    print('sell_normal_profit_ratio = {0}   # 정상 판매 이익율'.format(DF_optimized['sell_normal_profit_ratio'].values[0]))
    print('time_out_hour = {0}   # 매수 후 몇시간 경과시까지 매도가 안되면 자동 매도 할것인지'.format(time_out_hour))

    print('###################################################################################')

    DF_result_accum_total = pd.concat([DF_result_accum_total, DF_optimized], axis=0)

    DF_result_accum_total.to_excel('DF_result_accum_total.xlsx')

#print(DF_total_accum)

DF_total_accum['overall'] = DF_total_accum['resi_value'] * (1 + (DF_total_accum['sell_normal_profit_ratio'] - DF_total_accum['sell_force_loss']))

DF_total_accum.to_excel('DF_total_accum.xlsx')

DF_target = DF_total_accum.sort_values('overall', ascending = False).head(No_of_final_candi)

print ('DF_target\n', DF_target)

for k in range (0, len(DF_target), 1) :

    print ('k :', k)

    print ('######################### Final Target Candidate ##############################')

    print ('\n# 투자 대상 코인')
    print ('coin_No = {0}'.format(DF_target['Coin_No'].values[k]))

    print('\n# Test setting')
    print ('\n### moving average 산출 구간 설정')
    print ('ma_duration_short = {0}   # 단기 ma 산출 기간'.format(DF_target['ma_duration_short'].values[k]))
    print ('ma_duration_mid = {0}   # 중기 ma 산출 기간'.format(DF_target['ma_duration_mid'].values[k]))
    print ('ma_duration_long = {0}   # 장기 ma 산출 기간'.format(DF_target['ma_duration_long'].values[k]))

    print('\n### buy_transaction 조건값 설정')
    print('ma_short_under_duration = {0}   # 최근 몇개 기간동안의 ma_short의추이를 살펴볼것인지 지정'.format(DF_target['ma_short_under_duration'].values[k]))
    print('buy_cri_vol_times = {0}   # 전 구간 평균 거래량 대비, 직전 구간 (또는 직전직전 구간)에서 거래량이 얼마 이상이여야 buy_transaction을 수행할 것인가'.format(buy_cri_vol_times))
    print('vol_duration = {0}   # 몇 개월 동안의 평균 거래량 기준으로 ref vol을 설정할 것인가'.format(vol_duration))
    print('ratio_ema_o_short_long_buy_1 = [0.9, 1.05]')
    print('ratio_ema_long = {0}   # 현재 구간에서의 ema_long값과 직전구간 ema_long값의 비율이 얼마 이상일때 buy transaction을 수행하는가 (여러 필요 조건중의 하나)'.format(DF_target['ratio_ema_long'].values[k]))
    print('ema_Not_buy_duration = {0}'.format(ema_Not_buy_check_duration))
    print('ema_Not_buy_cri = {0}'.format(DF_target['ema_Not_buy_check_cri'].values[k]))
    print('buy_price_up_unit = {0}'.format(buy_price_up_unit))
    print('ma_trend_check_duration = {0}   # 구매가 적정한 구간인지, 최근의 전반적인 상승장 수중 확인'.format(ma_trend_check_duration))
    print('ratio_average_duraion_long = {0}   # 두 가지 참조 구간중, 더 오래된 참조시작 시점 설정'.format(ratio_average_duraion_long))
    print('ratio_average_duraion_short = {0}   # 두 가지 참조 구간중, 더 근래의 참조시작 시점 설정'.format(ratio_average_duraion_short))

    print('\n### sell transaction 조건값 설정')
    print('sellable_profit = 0.0   # 판매가능 이익율')
    print('sell_force_loss = {0}  # 강제 판매 손실율'.format(DF_target['sell_force_loss'].values[k]))
    print('ratio_sell_ema_mid_chg_state = {0}   # 권장 판매조건이 만족 안된 상태에서, ema_long 비율이 어느정도 미만이 되면 자동 판매 되게끔 (매수시의 상승추세가 꺾였다고 판단)'.format(DF_target['ratio_sell_ema_mid_chg_state'].values[k]))
    print('sell_normal_profit_ratio = {0}   # 정상 판매 이익율'.format(DF_target['sell_normal_profit_ratio'].values[k]))
    print('time_out_hour = {0}   # 매수 후 몇시간 경과시까지 매도가 안되면 자동 매도 할것인지'.format(time_out_hour))

    print('###################################################################################')




import winsound as sd

def beepsound() :
    fr = 1000    # range : 37 ~ 32767
    du = 1000     # 1000 ms ==1second
    sd.Beep(fr, du) # winsound.Beep(frequency, duration)


