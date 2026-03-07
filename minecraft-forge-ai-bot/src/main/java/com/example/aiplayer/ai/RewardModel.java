package com.example.aiplayer.ai;

import java.util.HashMap;
import java.util.Map;

public class RewardModel {
    private final Map<String, Double> scores = new HashMap<>();

    public synchronized void reinforce(String action, double reward) {
        double current = scores.getOrDefault(action, 0.0D);
        scores.put(action, current * 0.8D + reward * 0.2D);
    }

    public synchronized String bestKnownAction() {
        return scores.entrySet().stream()
                .max(Map.Entry.comparingByValue())
                .map(Map.Entry::getKey)
                .orElse("wander");
    }
}
