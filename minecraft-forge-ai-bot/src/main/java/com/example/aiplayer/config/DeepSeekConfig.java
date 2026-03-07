package com.example.aiplayer.config;

import net.minecraftforge.common.ForgeConfigSpec;

public class DeepSeekConfig {
    public static final ForgeConfigSpec SPEC;

    public static final ForgeConfigSpec.ConfigValue<String> API_URL;
    public static final ForgeConfigSpec.ConfigValue<String> API_KEY;
    public static final ForgeConfigSpec.ConfigValue<String> MODEL;

    static {
        ForgeConfigSpec.Builder builder = new ForgeConfigSpec.Builder();

        builder.push("deepseek");
        API_URL = builder.comment("DeepSeek-compatible chat completions endpoint")
                .define("apiUrl", "https://api.deepseek.com/chat/completions");
        API_KEY = builder.comment("НЕ храните ключ в репозитории. Лучше задайте через переменную окружения DEEPSEEK_API_KEY")
                .define("apiKey", "");
        MODEL = builder.comment("DeepSeek model name")
                .define("model", "deepseek-chat");
        builder.pop();

        SPEC = builder.build();
    }

    private DeepSeekConfig() {}
}
