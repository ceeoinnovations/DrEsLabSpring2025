"""
File: environment.py
Authors: Amanda-Lexine Sunga (Feb 2025)
         --> Modified from original activity code by Tanushree Burman
Purpose: Handles environment aspects of episodes (i.e. sensing colors and moving)
*** For Engineering with Artificial Intelligence Pre-College Program at Tufts University ***
"""

import time
import math

class Environment:
    def __init__(self, points, index, servo, sensor):
        self.states = dict(zip(index, points))
        self.goal_state = [len(points) - 1]
        self.end_state = [0, len(index)-1]
        self.reward_default = -1
        self.reward_goal = 10
        self.current_state = None
        self.action_space = ["LEFT", "RIGHT"]
        self.current_angle = 0
        self.angle = 180 // len(points)
        self.servo = servo
        self.sensor = sensor

    def reset(self):
        self.servo.write_angle(self.angle)
        time.sleep(2)
        self.current_state = self.nearestNeighbor(self.sensor.rgb)
        return self.current_state

    def reset_cur_angle(self, reset_angle):
        self.current_angle = reset_angle

    # nearest neighbor algorithm to determine closest color match
    def euclidean_distance(self, color1, color2):
        return math.sqrt(sum((c1 - c2) ** 2 for c1, c2 in zip(color1, color2)))

    def nearestNeighbor(self, current_rgb):
        closest_color = None
        min_distance = float('inf')
        for color_name, color_value in self.states.items():
            distance = self.euclidean_distance(current_rgb, color_value)
            if distance < min_distance:
                min_distance = distance
                closest_color = color_name
        print("The closest color is:", closest_color)
        return closest_color

    def step(self, action):
        if action == "LEFT":
            self.current_angle = min(180, self.current_angle + self.angle)
            self.servo.write_angle(self.current_angle)
        elif action == "RIGHT":
            if self.current_state != self.end_state[0]:
                self.current_angle = max(0, self.current_angle - self.angle)
                self.servo.write_angle(self.current_angle)
        time.sleep(2)
        self.current_state = self.nearestNeighbor(self.sensor.rgb)
        reward = self.reward_goal if self.current_state in self.goal_state else self.reward_default
        done = self.current_state in self.goal_state
        return self.current_state, reward, done
