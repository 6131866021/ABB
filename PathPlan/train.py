import torch
import gym
import os
from .env import *
from .model import *

def train_agent(args):

    if not os.path.exists(args.model_dir):
        os.makedirs(args.model_dir)

    env = gym.make(args.env_name)
    observation = env.reset()

    #print("Initial observation: ", observation)

    env_params = {
        # for hopper v2
        #'obs_dim' : observation.shape[0], #11
        # for fetch slide
        'obs_dim' : observation['observation'].shape[0], #(25,)
        'goal_dim': observation['desired_goal'].shape[0],  #(3,)
        'action_dim': env.action_space.shape[0], #(4,)
        'max_action' : env.action_space.high[0], # high : [1,1,1,1] low: [-1,-1,-1,-1]
    }

    if args.her:
        ddpg_agent = DDPG_HER_N(args, env, env_params)
    else:
        ddpg_agent = DDPG(args, env, env_params)

    ddpg_agent.train()

class ActorCriticTrain:
    def __init__(self):
        self.actor_model = ActorModel()
        self.actor_target = ActorModel()
        self.actor_opt = tf.keras.optimizers.Adam(learning_rate=hp.lr_actor)

        self.critic_model = CriticModel()
        self.critic_target = CriticModel()
        self.critic_opt = tf.keras.optimizers.Adam(learning_rate=hp.lr_critic)

        self.critic_target.set_weights(self.critic_model.get_weights())
        self.actor_target.set_weights(self.actor_model.get_weights())

        # tensorboard
        self.log_dir = 'logs/'
        self.train_summary_writer = tf.summary.create_file_writer(self.log_dir)
        self.reward_board = tf.keras.metrics.Mean('reward board', dtype=tf.float32)

    def update_target(self, target_weights, source_weights):
        use_locking = False
        target_variables = target_weights
        source_variables = source_weights

        update_ops = []
        for target_var, source_var in zip(target_variables, source_variables):
            update_ops.append(target_var.assign(hp.tau * source_variables + (1.0 - hp.tau) * target_var, use_locking))

        return tf.group(name="update_all_variables", *update_ops)

    def append_sample(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, amggdone))