import gym
import gym_colorfight


env = gym.make('Colorfight-v0')
state = env.reset()
print(state)
print(env.test_custom_func())