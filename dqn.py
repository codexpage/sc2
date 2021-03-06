# -*- coding: utf-8 -*-
import random
import gym
import numpy as np
from collections import deque
from keras.models import Sequential
from keras.layers import Dense
from keras.optimizers import Adam
import matplotlib.pyplot as plt

EPISODES = 1000


class DQNAgent:
    def __init__(self, state_size, action_size):
        self.state_size = state_size
        self.action_size = action_size
        self.memory = deque(maxlen=10000)
        self.gamma = 0.99  # discount rate 0.95
        self.epsilon = 1.0  # exploration rate 1-pure random
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.learning_rate = 0.6  # 0.001
        self.model = self._build_model()
        self.disallowed_actions = {}
        self.history = {'loss': []}

    def _build_model(self):
        # Neural Net for Deep-Q learning Model
        model = Sequential()
        model.add(Dense(24, input_dim=self.state_size, activation='relu'))
        model.add(Dense(24, activation='relu'))
        model.add(Dense(self.action_size, activation='linear'))
        model.compile(loss='mse',
                      optimizer=Adam(lr=self.learning_rate))
        return model

    # 存储transition
    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def act(self, state, excluded_actions=[]):
        action_available = list(range(self.action_size))
        action_available = np.delete(action_available, excluded_actions)  # delete the value by index

        if np.random.rand() <= self.epsilon:
            # return random.randrange(self.action_size)
            return random.choice(action_available)
        act_values = self.model.predict(state)  # 返回shape (1,8)
        return np.argmax(act_values[0][action_available])
        # return np.argmax(act_values[0])  # returns action index

    def replay(self, batch_size):
        print(len(self.memory))
        if len(self.memory) < batch_size:
            minibatch = list(self.memory)
        else:
            minibatch = random.sample(self.memory, batch_size)  # 随机抽取一个batch
        for state, action, reward, next_state, done in minibatch:
            if (state == next_state).all():  # skip the trasition to oneself, which do not contribute to learning
                # print("same state")
                continue
            target = reward
            if not done:
                target = (reward + self.gamma *
                          np.amax(self.model.predict(next_state)[0]))
            # print(state)
            target_f = self.model.predict(state)
            target_f[0][action] = target  # 只更改所选定的action的value
            history = self.model.fit(state, target_f, epochs=1, verbose=0)  # fit就是update模型
            # self.history['acc'].extend(history.history['acc'])
            # self.history['loss'].extend(history.history['loss'])
            # self.plot()

        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

    # 模型保存和读取
    def load(self, name):
        self.model.load_weights(name)

    def save(self, name):
        self.model.save_weights(name)

    def sample(self, batch_size):
        prob = np.array([(5 if transition[2] == 0 else 25) for transition in self.memory])  # give more prob on 1 and -1
        prob = prob / sum(prob)
        minibatch = np.random.choice(self.memory, batch_size, p=prob)
        return minibatch

    def plot(self):
        # plt.plot(self.history['acc'])
        # plt.title('acc')
        # plt.ylabel('acc')
        # plt.xlabel('epoch')
        # plt.savefig('acc.png')

        plt.plot(self.history['loss'])
        plt.title('loss')
        plt.ylabel('loss')
        plt.xlabel('epoch')
        plt.savefig('loss.png')


if __name__ == "__main__":
    env = gym.make('CartPole-v1')
    state_size = env.observation_space.shape[0]
    action_size = env.action_space.n
    agent = DQNAgent(state_size, action_size)
    # agent.load("./save/cartpole-dqn.h5")
    done = False
    batch_size = 32

    for e in range(EPISODES):
        state = env.reset()
        state = np.reshape(state, [1, state_size])
        for time in range(500):
            # env.render()
            action = agent.act(state)  # 选action
            next_state, reward, done, _ = env.step(action)  # 做action
            reward = reward if not done else -10  # 这里结束就输了，所以reward -10
            if done:
                print("done")
            next_state = np.reshape(next_state, [1, state_size])
            agent.remember(state, action, reward, next_state, done)  # 存储transition
            state = next_state
            if done:
                print("episode: {}/{}, score: {}, e: {:.2}"
                      .format(e, EPISODES, time, agent.epsilon))
                break
        if len(agent.memory) > batch_size:  # 当存储的transition足够之后，开始抽取学习
            agent.replay(batch_size)
        # if e % 10 == 0:
        #     agent.save("./save/cartpole-dqn.h5")
