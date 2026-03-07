package com.example.aiplayer.entity;

import com.example.aiplayer.AIPlayerMod;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.MobCategory;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

public class ModEntities {
    public static final DeferredRegister<EntityType<?>> ENTITIES = DeferredRegister.create(ForgeRegistries.ENTITY_TYPES, AIPlayerMod.MOD_ID);

    public static final RegistryObject<EntityType<AICompanionEntity>> AI_COMPANION = ENTITIES.register("ai_companion", () ->
            EntityType.Builder.of(AICompanionEntity::new, MobCategory.CREATURE)
                    .sized(0.6F, 1.95F)
                    .build("ai_companion"));

    public static void register(IEventBus eventBus) {
        ENTITIES.register(eventBus);
    }

    private ModEntities() {}
}
