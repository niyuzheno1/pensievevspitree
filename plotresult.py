import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd


RESULTS_FOLDER = './results/'
NUM_BINS = 100
BITS_IN_BYTE = 8.0
MILLISEC_IN_SEC = 1000.0
M_IN_B = 1000000.0
VIDEO_LEN = 48
VIDEO_BIT_RATE = [300, 750, 1200, 1850, 2850, 4300]
K_IN_M = 1000.0
REBUF_P = 4.3
SMOOTH_P = 1
COLOR_MAP = plt.cm.jet #nipy_spectral, Set1,Paired 
SIM_DP = 'sim_dp'
#SCHEMES = ['BB', 'RB', 'FIXED', 'FESTIVE', 'BOLA', 'RL',  'sim_rl', SIM_DP]
SCHEMES = ['sim_rl', 'sim_dt' ]
M_IN_K = 1000.0
REBUF_PENALTY = 4.3
SMOOTH_PENALTY = 1
HD_REWARD_2 = [1, 2, 3, 12, 15, 20]

HD_REWARD = {}
HD_REWARD[0] = 0

for i in range(0, len(HD_REWARD_2)):
    HD_REWARD[VIDEO_BIT_RATE[i]] = HD_REWARD_2[i]

def get_reward(bit_rate, rebuf, last_bit_rate, reward_type):
    if reward_type == 'lin':
        reward = bit_rate / M_IN_K - REBUF_PENALTY * rebuf - \
                 SMOOTH_PENALTY * np.abs(bit_rate - last_bit_rate) / M_IN_K
    elif reward_type == 'log':
        log_bit_rate = np.log(bit_rate / float(4300))
        log_last_bit_rate = np.log(last_bit_rate / float(4300))
        reward = log_bit_rate - REBUF_PENALTY * rebuf - REBUF_PENALTY * np.abs(log_bit_rate - log_last_bit_rate)
    elif reward_type == 'hd':
        reward = HD_REWARD[bit_rate] - REBUF_PENALTY * rebuf - \
                 SMOOTH_PENALTY * np.abs(HD_REWARD[bit_rate] - HD_REWARD[last_bit_rate])
    else:
        raise NotImplementedError
    return reward

def breakpoint():
    return 1 + 1 == 2

def main():
    time_all = {}
    bit_rate_all = {}
    buff_all = {}
    bw_all = {}
    delay_all = {}
    raw_reward_all = {}
    raw_reward_all_2 = {}
    buffer_size_avg = {}
    bandwidth_avg = {}
    delay_avg = {}

    for scheme in SCHEMES:
        time_all[scheme] = {}
        raw_reward_all[scheme] = {}
        bit_rate_all[scheme] = {}
        buff_all[scheme] = {}
        bw_all[scheme] = {}
        delay_all[scheme] = {}
        raw_reward_all_2[scheme + '|:|' + 'lin'] = {}
        raw_reward_all_2[scheme+ '|:|' + 'log'] = {}
        raw_reward_all_2[scheme+ '|:|' + 'hd'] = {}
        buffer_size_avg[scheme] = []
        bandwidth_avg[scheme] = []
        delay_avg[scheme] = []

    log_files = os.listdir(RESULTS_FOLDER)
    for log_file in log_files:

        time_ms = []
        bit_rate = []
        buff = []
        bw = []
        delay = []
        reward = []
        reward_lin = []
        reward_log = []
        reward_hd = []
        print log_file
        with open(RESULTS_FOLDER + log_file, 'rb') as f:
            if SIM_DP in log_file:
                last_t = 0
                last_b = 0
                last_q = 1
                lines = []
                for line in f:
                    lines.append(line)
                    parse = line.split()
                    if len(parse) >= 6:
                        time_ms.append(float(parse[3]))
                        bit_rate.append(VIDEO_BIT_RATE[int(parse[6])])
                        buff.append(float(parse[4]))
                        bw.append(float(parse[5]))
                
                for line in reversed(lines):
                    parse = line.split()
                    r = 0
                    if len(parse) > 1:
                        t = float(parse[3])
                        b = float(parse[4])
                        q = int(parse[6])
                        rebuff = 0
                        if b == 4:
                            rebuff = (t - last_t) - last_b
                            assert rebuff >= -1e-4
                            r -= REBUF_P * rebuff
                        r += VIDEO_BIT_RATE[q] / K_IN_M
                        r -= SMOOTH_P * np.abs(VIDEO_BIT_RATE[q] - VIDEO_BIT_RATE[last_q]) / K_IN_M
                        reward.append(r)
                        

                        last_t = t
                        last_b = b
                        last_q = q

            else:
                last_q = 750
                last_b = 0
                for line in f:
                    parse = line.split()
                    if len(parse) <= 1:
                        break
                    time_ms.append(float(parse[0]))
                    bit_rate.append(int(parse[1]))
                    buff.append(float(parse[2]))
                    bw.append(float(parse[4]) / float(parse[5]) * BITS_IN_BYTE * MILLISEC_IN_SEC / M_IN_B)
                    delay.append(float(parse[5]) / M_IN_B)
                    reward.append(float(parse[6]))
                    if int(float(parse[2])) == 4:
                        rebuff = parse[3]
                    else:
                        rebuff = '0'
                    reward_lin.append(get_reward(int(parse[1]), float(rebuff), last_q , 'lin' ))
                    reward_log.append(get_reward(int(parse[1]), float(rebuff), last_q , 'log' ))
                    reward_hd.append(get_reward(int(parse[1]), float(rebuff), last_q , 'hd' ))
                    last_q = int(parse[1])

        if SIM_DP in log_file:
            time_ms = time_ms[::-1]
            bit_rate = bit_rate[::-1]
            buff = buff[::-1]
            delay = delay[::-1]
            bw = bw[::-1]
        
        time_ms = np.array(time_ms)
        time_ms -= time_ms[0]
        
        # print log_file

        for scheme in SCHEMES:
            if scheme in log_file:
                time_all[scheme][log_file[len('log_' + str(scheme) + '_'):]] = time_ms
                bit_rate_all[scheme][log_file[len('log_' + str(scheme) + '_'):]] = bit_rate
                buff_all[scheme][log_file[len('log_' + str(scheme) + '_'):]] = buff
                bw_all[scheme][log_file[len('log_' + str(scheme) + '_'):]] = bw
                delay_all[scheme][log_file[len('log_' + str(scheme) + '_'):]] = delay
                raw_reward_all[scheme][log_file[len('log_' + str(scheme) + '_'):]] = reward
                if log_file[len('log_' + str(scheme) + '_'):] == 'bus.ljansbakken-oslo-report.2010-09-28_1407CEST.log':
                    pass
                raw_reward_all_2[scheme+ '|:|' + 'lin'][log_file[len('log_' + str(scheme) + '_'):]] = reward_lin
                raw_reward_all_2[scheme+ '|:|' +  'log'][log_file[len('log_' + str(scheme) + '_'):]] = reward_log
                raw_reward_all_2[scheme+ '|:|' +  'hd'][log_file[len('log_' + str(scheme) + '_'):]] = reward_hd
                break

    # ---- ---- ---- ----
    # Reward records
    # ---- ---- ---- ----
        
    log_file_all = []
    reward_all = {}
    reward_all_2 = {}
    for scheme in SCHEMES:
        reward_all[scheme] = []
        reward_all_2[ scheme + '|:|' +  'lin' ] = []
        reward_all_2[ scheme + '|:|' +  'log' ] = []
        reward_all_2[ scheme + '|:|' +  'hd' ] = []

    for l in time_all[SCHEMES[0]]:
        schemes_check = True
        for scheme in SCHEMES:
            if l not in time_all[scheme] :
                schemes_check = False
                break
        if schemes_check:
            log_file_all.append(l)
            for scheme in SCHEMES:
                reward_all[scheme].append(np.sum(raw_reward_all[scheme][l][1:VIDEO_LEN]))
                reward_all_2[scheme + '|:|' + 'lin'].append(np.sum(raw_reward_all_2[scheme + '|:|' +  'lin'][l][1:VIDEO_LEN]))
                reward_all_2[scheme + '|:|' +  'log'].append(np.sum(raw_reward_all_2[scheme+ '|:|' +  'log'][l][1:VIDEO_LEN]))
                reward_all_2[scheme + '|:|' +  'hd'].append(np.sum(raw_reward_all_2[scheme + '|:|' +  'hd'][l][1:VIDEO_LEN]))


    mean_rewards = {}
    sum_rewards_2 = {}
    for scheme in SCHEMES:
        mean_rewards[scheme] = np.mean(reward_all[scheme])
        sum_rewards_2[scheme + '|:|' +  'lin'] =  np.sum(reward_all_2[scheme+ '|:|' +  'lin'])
        sum_rewards_2[scheme + '|:|' +  'log'] =  np.sum(reward_all_2[scheme+ '|:|' +  'log'])
        sum_rewards_2[scheme + '|:|' +  'hd'] =  np.sum(reward_all_2[scheme+ '|:|' +  'hd'])
    df = pd.DataFrame({'metric': ['Qlin', 'Qlog', 'QHD'],
                   'Reward (Pensieve)': [1, 1, 1],
                   'Reward (PiTree)': [sum_rewards_2[ 'sim_dt' + '|:|' + 'lin' ]/sum_rewards_2[ 'sim_rl' + '|:|' + 'lin' ], sum_rewards_2[ 'sim_dt' + '|:|' + 'log' ]/ sum_rewards_2[ 'sim_rl' + '|:|' + 'log' ], sum_rewards_2[ 'sim_dt' + '|:|' + 'hd' ]/ sum_rewards_2[ 'sim_rl' + '|:|' + 'hd' ]] 
    })
    df = df[['metric','Reward (PiTree)','Reward (Pensieve)']]
    df.to_csv('statistics.csv', index=False)


    ## ax = fig.add_subplot(111)

    ## for scheme in SCHEMES:
    ##     ax.plot(reward_all[scheme])
    
    SCHEMES_REW = []
    for scheme in SCHEMES:
        SCHEMES_REW.append(scheme + ': ' + str(mean_rewards[scheme]))

    ## colors = [COLOR_MAP(i) for i in np.linspace(0, 1, len(ax.lines))]
    ## for i,j in enumerate(ax.lines):
    ##     j.set_color(colors[i])

    ##  ax.legend(SCHEMES_REW, loc=4)
    
    ## plt.ylabel('total reward')
    ## plt.xlabel('trace index')
    ## plt.show()

    # ---- ---- ---- ----
    # CDF 
    # ---- ---- ---- ----

    ##  fig = plt.figure()
    ## ax = fig.add_subplot(111)
    y = None

    for scheme in SCHEMES:
        x = reward_all[scheme]
        if y is None:
            y = x
        x = x/ np.sum(y)
        values, base = np.histogram(reward_all[scheme], bins=NUM_BINS)
        cumulative = np.cumsum(values)
    pass
    ##     ax.plot(base[:-1], cumulative)    

    ## colors = [COLOR_MAP(i) for i in np.linspace(0, 1, len(ax.lines))]
    ## for i,j in enumerate(ax.lines):
    ##     j.set_color(colors[i])    

    ## ax.legend(SCHEMES_REW, loc=4)
    
    

    # ---- ---- ---- ----
    # check each trace
    # ---- ---- ---- ----
    

    for l in time_all[SCHEMES[0]]:
        schemes_check = True
        for scheme in SCHEMES:
            if l not in time_all[scheme]:
                schemes_check = False
                break
        if schemes_check:
            ## fig = plt.figure()

            ##  ax = fig.add_subplot(311)
            ## for scheme in SCHEMES:
            ##     ax.plot(time_all[scheme][l][:VIDEO_LEN], bit_rate_all[scheme][l][:VIDEO_LEN])
            ## colors = [COLOR_MAP(i) for i in np.linspace(0, 1, len(ax.lines))]
            ## for i,j in enumerate(ax.lines):
            ##     j.set_color(colors[i])    
            # plt.title(l)
            # plt.ylabel('bit rate selection (kbps)')
            for scheme in SCHEMES:
                buffer_size_avg[scheme].append(np.average(buff_all[scheme][l][:VIDEO_LEN]))
                delay_avg[scheme].append(np.average(delay_all[scheme][l][:VIDEO_LEN]))
                bandwidth_avg[scheme].append(np.average(bw_all[scheme][l][:VIDEO_LEN]))

            ##  ax = fig.add_subplot(312)
            ## for scheme in SCHEMES:
            ##     ax.plot(time_all[scheme][l][:VIDEO_LEN], buff_all[scheme][l][:VIDEO_LEN])
            ## colors = [COLOR_MAP(i) for i in np.linspace(0, 1, len(ax.lines))]
            ## for i,j in enumerate(ax.lines):
            ##     j.set_color(colors[i])    
            ## plt.ylabel('buffer size (sec)')

            ## ax = fig.add_subplot(313)
            ## for scheme in SCHEMES:
            ##     ax.plot(time_all[scheme][l][:VIDEO_LEN], bw_all[scheme][l][:VIDEO_LEN])
            ## colors = [COLOR_MAP(i) for i in np.linspace(0, 1, len(ax.lines))]
            ## for i,j in enumerate(ax.lines):
            ##     j.set_color(colors[i])    
            ## plt.ylabel('bandwidth (mbps)')
            ## plt.xlabel('time (sec)')

            SCHEMES_REW = []
            for scheme in SCHEMES:
                SCHEMES_REW.append(scheme + ': ' + str(np.sum(raw_reward_all[scheme][l][1:VIDEO_LEN])))

            ##  ax.legend(SCHEMES_REW, loc=9, bbox_to_anchor=(0.5, -0.1), ncol=int(np.ceil(len(SCHEMES) / 2.0)))
            ## plt.show()
    a = [np.average(buffer_size_avg['sim_rl']), np.average(bandwidth_avg['sim_rl']), np.average(delay_avg['sim_rl'])]
    df = pd.DataFrame({'metric': ['average buffer size', 'average bandwidth', 'average delay'],
                   'measurement (Pensieve)': [1,1,1],
                   'measurement (PiTree)': [np.average(buffer_size_avg['sim_dt'])/a[0], np.average(bandwidth_avg['sim_dt'])/a[1], np.average(delay_avg['sim_dt'])/a[2]]
    })
    df = df[['metric','measurement (PiTree)','measurement (Pensieve)']]
    df.to_csv('BW.csv', index=False)
    breakpoint()


if __name__ == '__main__':
    main()
