# backend/ai_model/rl_model.py

import numpy as np
import random
import os
import json

# Parameters
# How finely we discretize threat scores (0-10 divided into 20 bins)
STATE_BINS = 20
ACTIONS = [-0.5, 0, 0.5]  # Decrease, No change, Increase
ALPHA = 0.1       # Learning rate
GAMMA = 0.9       # Discount factor
EPSILON = 0.1     # Exploration vs Exploitation

# File to save Q-table
QTABLE_FILE = os.path.abspath("backend/ai_model/q_table.json")

# Load or initialize Q-table


def load_q_table():
    if os.path.exists(QTABLE_FILE):
        with open(QTABLE_FILE, "r") as file:
            return json.load(file)
    else:
        return {}


def save_q_table(q_table):
    with open(QTABLE_FILE, "w") as file:
        json.dump(q_table, file)

# Discretize a score


def discretize(score):
    return int(score / (10 / STATE_BINS))

# Convert state (score + topic) into key


def get_state_key(score, topic):
    return f"{discretize(score)}_{topic}"

# Choose an action


def choose_action(state_key, q_table):
    if random.random() < EPSILON:
        return random.choice([0, 1, 2])  # Explore
    else:
        # Exploit best known action
        return np.argmax(q_table.get(state_key, [0, 0, 0]))

# Update Q-table


def update_q_table(q_table, state_key, action, reward, next_state_key):
    if state_key not in q_table:
        q_table[state_key] = [0, 0, 0]
    if next_state_key not in q_table:
        q_table[next_state_key] = [0, 0, 0]

    predict = q_table[state_key][action]
    target = reward + GAMMA * max(q_table[next_state_key])
    q_table[state_key][action] += ALPHA * (target - predict)

# Apply action to adjust score


def adjust_score(score, topic):
    q_table = load_q_table()
    state_key = get_state_key(score, topic)
    action = choose_action(state_key, q_table)

    # Apply action: -0.5, 0, or +0.5
    new_score = round(min(max(score + ACTIONS[action], 0), 10), 2)

    # Simulate reward (can later use real alerts, analyst feedback, etc.)
    reward = random.choice([1, 0, -1])

    next_state_key = get_state_key(new_score, topic)
    update_q_table(q_table, state_key, action, reward, next_state_key)

    save_q_table(q_table)

    print(
        f"🧠 RL: {state_key} → action {ACTIONS[action]} → new score {new_score} (reward: {reward})")

    return new_score
