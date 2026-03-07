package com.example.aiplayer.ai;

import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Deque;
import java.util.List;

public class MemoryStore {
    private static final int MAX_EVENTS = 200;
    private final Deque<String> events = new ArrayDeque<>();

    public synchronized void remember(String event) {
        if (events.size() >= MAX_EVENTS) {
            events.removeFirst();
        }
        events.addLast(event);
    }

    public synchronized List<String> lastEvents(int limit) {
        return events.stream().skip(Math.max(0, events.size() - limit)).collect(ArrayList::new, ArrayList::add, ArrayList::addAll);
    }
}
