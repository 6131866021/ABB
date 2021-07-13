from collections import deque
from .env import *
from .model import *

num_action = 1

class ActorCriticTrain:
    def __init__(self):
        self.N_std = 0.1

        self.actor_model = ActorModel()
        self.actor_target = ActorModel()
        self.actor_opt = tf.keras.optimizers.Adam(learning_rate=hp.lr_actor)

        self.critic_model = CriticModel()
        self.critic_target = CriticModel()
        self.critic_opt = tf.keras.optimizers.Adam(learning_rate=hp.lr_critic)

        self.critic_target.set_weights(self.critic_model.get_weights())
        self.actor_target.set_weights(self.actor_model.get_weights())

        self.memory = deque(maxlen=10000)

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
        self.memory.append((state, action, reward, next_state, done))

    def train(self):
        mini_batch = np.random.sample(self.memory, hp.batch_size)

        states = np.zeros((hp.batch_size, hp.state_size))
        next_states = np.zeros((hp.batch_size, hp.state_size))
        actions, rewards, dones = [], [], []

        for i in range(hp.batch_size):
            states[i] = mini_batch[i][0]
            actions.append(mini_batch[i][1])
            rewards.append(mini_batch[i][2])
            next_states[i] = mini_batch[i][3]
            dones.append(mini_batch[i][4])

        states = tf.cast(states, tf.float32)

        target_actions = self.actor_target(tf.convert_to_tensor(np.vstack(next_states), dtype=tf.float32))

        with tf.GradientTape() as tape_critic:
            state_actions = tf.concat([states, actions], 1)
            state_actions = tf.cast(state_actions, tf.float32)

            target_state_actions = tf.concat([next_states, target_actions], 1)
            target_state_actions = tf.cast(target_state_actions, tf.float32)

            target = self.critic_model(tf.convert_to_tensor(np.vstack(state_actions), dtype=tf.float32))
            target_val = self.critic_target(tf.convert_to_tensor(np.vstack(target_state_actions), dtype=tf.float32))

            target = np.array(target)
            target_val = np.array(target_val)

            for i in range(hp.batch_size):
                next_v = np.array(target_val[i]).max()
                if dones[i]:
                    target[i] = rewards[i]
                else:
                    target[i] = rewards[i] + hp.discount_factor * next_v

            values = self.critic_model(tf.convert_to_tensor(np.vstack(state_actions), dtype=tf.float32))
            error = tf.square(values - target) * 0.5
            error = tf.reduce_mean(error)

        critic_grads = tape_critic.gradient(error, self.critic_model.trainable_variables)
        self.critic_opt.apply_gradients(zip(critic_grads, self.critic_model.trainable_variables))

        with tf.GradientTape() as tape:
            actions = self.actor_model(tf.convert_to_tensor(states, dtype=tf.float32))
            state_actions = tf.concat([states, actions], 1)
            state_actions = tf.cast(state_actions, tf.float32)
            Q_values = self.critic_model(tf.convert_to_tensor(state_actions, dtype=tf.float32))
            actor_loss = -tf.reduce_mean(Q_values)

        actor_grads = tape.gradient(actor_loss, self.actor_model.trainable_variables)
        self.actor_opt.apply_gradients(zip(actor_grads, self.actor_model.trainable_variables))

        self.train_loss = tf.reduce_mean(actor_loss)
        self.train_loss_c = tf.reduce_mean(error)

    def run(self):
        t_end = 1000
        epi = 10000

        # reset
        # state = env.reset()

        for e in range(epi):
            total_reward = 0

            for i in range(t_end):
                action = self.actor_model(tf.convert_to_tensor(state[None, :], dtype=tf.float32))
                action = np.array(action)[0] + np.random.normal(loc=0.0, scale=self.N_std, size=[num_action])

                next_state, reward, done, _ = env.step(action)

                if e > 100 : env.render()
                #print(state[0])

                if t == t_end :
                    done = True

                total_reward += reward
                self.append_sample(state, action, reward, next_state, done)
                state = next_state

                if done :
                    if len(self.memory) >= self.train_start:
                        self.train()
                        with self.train_summary_writer.as_default():
                            tf.summary.scalar('actor_loss', self.train_loss, step=e)
                            tf.summary.scalar('critic_loss', self.train_loss_c, step=e)
                        self.update_target(self.actor_target.weights, self.actor_model.weights)
                        self.update_target(self.critic_target.weights, self.critic_model.weights)
                    self.reward_board(total_reward)
                    print("e : ", e, " reward : ", total_reward, " step : ", t)
                    env.reset()
                    with self.train_summary_writer.as_default():
                        tf.summary.scalar('reward', total_reward, step=e)
                    break

# def train_agent(args):

#     if not os.path.exists(args.model_dir):
#         os.makedirs(args.model_dir)

#     env = gym.make(args.env_name)
#     observation = env.reset()

#     #print("Initial observation: ", observation)

#     env_params = {
#         # for hopper v2
#         #'obs_dim' : observation.shape[0], #11
#         # for fetch slide
#         'obs_dim' : observation['observation'].shape[0], #(25,)
#         'goal_dim': observation['desired_goal'].shape[0],  #(3,)
#         'action_dim': env.action_space.shape[0], #(4,)
#         'max_action' : env.action_space.high[0], # high : [1,1,1,1] low: [-1,-1,-1,-1]
#     }

#     if args.her:
#         ddpg_agent = DDPG_HER_N(args, env, env_params)
#     else:
#         ddpg_agent = DDPG(args, env, env_params)

#     ddpg_agent.train()