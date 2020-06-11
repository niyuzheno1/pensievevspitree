"""
This code is for illustration purpose only.
Use multi_agent.py for better performance and speed.
"""

import os
import numpy as np
import tensorflow as tf
import fixed_env as env
import a2c
import load_trace


S_INFO = 6  # bit_rate, buffer_size, next_chunk_size, bandwidth_measurement(throughput and time), chunk_til_video_end
S_LEN = 8  # take how many frames in the past
A_DIM = 6
ACTOR_LR_RATE = 0.0001
CRITIC_LR_RATE = 0.001
TRAIN_SEQ_LEN = 100  # take as a train batch
MODEL_SAVE_INTERVAL = 100
VIDEO_BIT_RATE = [300,750,1200,1850,2850,4300]  # Kbps
BUFFER_NORM_FACTOR = 10.0
CHUNK_TIL_VIDEO_END_CAP = 48.0
M_IN_K = 1000.0
REBUF_PENALTY = 4.3  # 1 sec rebuffering -> 3 Mbps
SMOOTH_PENALTY = 1
DEFAULT_QUALITY = 1  # default video quality without agent
RANDOM_SEED = 42
RAND_RANGE = 1000000
GRADIENT_BATCH_SIZE = 16
SUMMARY_DIR = './results'
LOG_FILE = './results/log_sim_myrl2'
# log in format of time_stamp bit_rate buffer_size rebuffer_time chunk_size download_time reward
NN_MODEL = "./models/myinfo2100.ckpt"


def main():

    np.random.seed(RANDOM_SEED)

    assert len(VIDEO_BIT_RATE) == A_DIM

    all_cooked_time, all_cooked_bw, all_file_names = load_trace.load_trace()

    if not os.path.exists(SUMMARY_DIR):
        os.makedirs(SUMMARY_DIR)

    net_env = env.Environment(all_cooked_time=all_cooked_time,
                              all_cooked_bw=all_cooked_bw)
    log_path = LOG_FILE + '_' + all_file_names[net_env.trace_idx]

    with open(LOG_FILE, 'wb') as log_file:

        network = a2c.A2CNetwork() # training monitor
        
        saver = tf.train.Saver()  # save neural net parameters

        # restore neural net parameters
        nn_model = NN_MODEL
        if nn_model is not None:  # nn_model is the path to file
            saver.restore(network.session, nn_model)
            print("Model restored.")

        epoch = 0
        time_stamp = 0

        last_bit_rate = DEFAULT_QUALITY
        bit_rate = DEFAULT_QUALITY

        action_vec = np.zeros(A_DIM)
        action_vec[bit_rate] = 1

        s_batch = [np.zeros((1, 6))]
        a_batch = [action_vec]
        r_batch = []

        video_count = 0

        while True:  # serve video forever
            # the action is from the last decision
            # this is to make the framework similar to the real
            delay, sleep_time, buffer_size, rebuf, \
            video_chunk_size, next_video_chunk_sizes, \
            end_of_video, video_chunk_remain = \
                net_env.get_video_chunk(bit_rate)

            time_stamp += delay  # in ms
            time_stamp += sleep_time  # in ms

            # reward is video quality - rebuffer penalty - smooth penalty
            reward = VIDEO_BIT_RATE[bit_rate] / M_IN_K \
                     - REBUF_PENALTY * rebuf \
                     - SMOOTH_PENALTY * np.abs(VIDEO_BIT_RATE[bit_rate] -
                                               VIDEO_BIT_RATE[last_bit_rate]) / M_IN_K
            r_batch.append(reward)
            log_file.write(str(time_stamp / M_IN_K) + '\t' +
                       str(VIDEO_BIT_RATE[bit_rate]) + '\t' +
                       str(buffer_size) + '\t' +
                       str(rebuf) + '\t' +
                       str(video_chunk_size) + '\t' +
                       str(delay) + '\t' +
                       str(reward) + '\n')
            log_file.flush()

            last_bit_rate = bit_rate

            # retrieve previous state
            state = []

            # this should be S_INFO number of terms
            state.append(VIDEO_BIT_RATE[bit_rate] / float(np.max(VIDEO_BIT_RATE)))
            state.append(buffer_size / BUFFER_NORM_FACTOR)  
            state.append(float(video_chunk_size) / float(delay) / M_IN_K )
            state.append(float(delay) / M_IN_K / BUFFER_NORM_FACTOR)
            state.append(next_video_chunk_sizes[-1] / M_IN_K / M_IN_K )
            state.append(np.minimum(video_chunk_remain, CHUNK_TIL_VIDEO_END_CAP) / float(CHUNK_TIL_VIDEO_END_CAP))
            state2 = np.asarray(state)
            state2 = np.reshape(state2,(1,6))
            action2 = network.choose_action(state2)
            action_cumsum = np.cumsum(action2)
            bit_rate = action_cumsum.argmax()
                
            if end_of_video:
                log_file.write('\n')
                log_file.close()
                last_bit_rate = DEFAULT_QUALITY
                bit_rate = DEFAULT_QUALITY  # use the default action here

                action_vec = np.zeros(A_DIM)
                action_vec[bit_rate] = 1
                print "video count", video_count
                video_count += 1

                if video_count > len(all_file_names):
                    break


                log_path = LOG_FILE + '_' + all_file_names[net_env.trace_idx]
                log_file = open(log_path, 'wb')

                s_batch.append(np.zeros((1, 6)))
                a_batch.append(action_vec)

            else:
                s_batch.append(state2)

                action_vec = np.zeros(A_DIM)
                action_vec[bit_rate] = 1
                a_batch.append(action_vec)

if __name__ == '__main__':
    main()
