import tensorflow as tf
import numpy as np
class A2CNetwork:
    def __init__(self):
        self.state = tf.placeholder("float64", (1,  6))
        self.__init_actor__()
        self.__init_critic__()
        self.__init_session__()
        pass
    def __init_session__(self):
        
        self.session = tf.InteractiveSession()
        self.session.run(tf.global_variables_initializer())
    def __init_actor__(self):
        self.dense4 = tf.layers.dense(self.state, 10, activation=tf.nn.relu, name='dense_4')
        self.dense5 = tf.layers.dense(self.dense4, 100, activation=tf.nn.relu, name='dense_5')
        self.dense6 = tf.layers.dense(self.dense5, 100, activation=tf.nn.relu, name='dense_6')
        self.policy = tf.layers.dense(self.dense6, 6, activation=tf.nn.relu, name='dense_7')
        self.targety = tf.placeholder("float64", [None, 6])
        self.actor_loss =  tf.reduce_sum(tf.square(self.targety - self.policy))
        self.ourtarget2 = tf.train.RMSPropOptimizer(learning_rate=0.001).minimize(self.actor_loss)
    def __init_critic__(self):
        self.dense1 = tf.layers.dense(self.state, 10, activation=tf.nn.relu, name='dense_1')
        self.dense2 = tf.layers.dense(self.dense1, 100, activation=tf.nn.relu, name='dense_2')
        self.dense8 = tf.layers.dense(self.dense2, 100, activation=tf.nn.relu, name='dense_8')
        self.dense3 = tf.layers.dense(self.dense8, 1, activation=tf.nn.relu, name='dense_3')
        self.targetx = tf.placeholder("float64", [None, 1])
        self.critic_loss =  tf.reduce_sum(tf.square(self.targetx - self.dense3))
        self.ourtarget1 = tf.train.RMSPropOptimizer(learning_rate=0.001).minimize(self.critic_loss)
        pass
    def choose_action(self, state):
        answer = self.session.run(self.policy, feed_dict={self.state: state})
        
        from numpy.random import randint
        y = randint(0, 6)
        z = randint(0, 2)
        u = [0 for i in range(0,6)]
        u[y] = 1
        array = answer
        return array
        
    def train(self, oldstate, newstate, action, reward):
        t_v = np.zeros((1, 1))
        t_c = np.zeros((1, 6))
        v_0= self.session.run(self.dense3, feed_dict={self.state: oldstate})
        v_1 = self.session.run(self.dense3, feed_dict={self.state: newstate})
        t_c = self.session.run(self.policy,  feed_dict={self.state: oldstate})
        if t_c[0][action] > 0 :
            pass
        t_v[0][0] = reward
        t_c[0][action] = reward - v_0
        _ = self.session.run([self.ourtarget1, self.ourtarget2], {self.state: oldstate, self.targety:t_c, self.targetx:t_v })
        pass
