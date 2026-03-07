package com.example.aiplayer;

import com.example.aiplayer.config.DeepSeekConfig;
import com.example.aiplayer.entity.ModEntities;
import net.minecraftforge.common.MinecraftForge;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.fml.ModLoadingContext;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.config.ModConfig;
import net.minecraftforge.fml.javafmlmod.FMLJavaModLoadingContext;

@Mod(AIPlayerMod.MOD_ID)
public class AIPlayerMod {
    public static final String MOD_ID = "aiplayer";

    public AIPlayerMod() {
        IEventBus modBus = FMLJavaModLoadingContext.get().getModEventBus();
        ModEntities.register(modBus);
        ModLoadingContext.get().registerConfig(ModConfig.Type.COMMON, DeepSeekConfig.SPEC);
        MinecraftForge.EVENT_BUS.register(this);
    }
}
