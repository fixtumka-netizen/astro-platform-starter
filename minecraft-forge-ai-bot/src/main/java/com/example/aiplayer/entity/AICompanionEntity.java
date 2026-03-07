package com.example.aiplayer.entity;

import com.example.aiplayer.ai.MemoryStore;
import com.example.aiplayer.ai.RewardModel;
import com.example.aiplayer.network.DeepSeekClient;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.PathfinderMob;
import net.minecraft.world.entity.ai.goal.RandomStrollGoal;
import net.minecraft.world.entity.ai.goal.FloatGoal;
import net.minecraft.world.entity.ai.goal.LookAtPlayerGoal;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;

public class AICompanionEntity extends PathfinderMob {
    private final MemoryStore memory = new MemoryStore();
    private final RewardModel rewardModel = new RewardModel();
    private final DeepSeekClient deepSeekClient = new DeepSeekClient();
    private int decisionCooldown = 0;

    protected AICompanionEntity(EntityType<? extends PathfinderMob> type, Level level) {
        super(type, level);
    }

    @Override
    protected void registerGoals() {
        this.goalSelector.addGoal(0, new FloatGoal(this));
        this.goalSelector.addGoal(1, new RandomStrollGoal(this, 1.0D));
        this.goalSelector.addGoal(2, new LookAtPlayerGoal(this, Player.class, 8.0F));
    }

    @Override
    public void tick() {
        super.tick();
        if (level().isClientSide()) {
            return;
        }

        if (this.horizontalCollision) {
            rewardModel.reinforce("wander", -0.3D);
            memory.remember("Столкнулся с препятствием");
        } else {
            rewardModel.reinforce("wander", 0.05D);
        }

        if (--decisionCooldown <= 0) {
            decisionCooldown = 20 * 20;
            decideAndSpeak();
        }
    }

    private void decideAndSpeak() {
        String action = rewardModel.bestKnownAction();
        String prompt = "Память: " + String.join("; ", memory.lastEvents(10)) + ". Предложи следующее действие для режима: " + action;
        String raw = deepSeekClient.chat(prompt);
        String shortReply = raw.length() > 180 ? raw.substring(0, 180) + "..." : raw;

        if (this.level() instanceof ServerLevel serverLevel) {
            serverLevel.getServer().getPlayerList().broadcastSystemMessage(
                    Component.literal("[AI Companion] " + shortReply),
                    false
            );
        }
        memory.remember("Сказал в чат: " + shortReply);
    }
}
