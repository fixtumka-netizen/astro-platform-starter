package com.example.aiplayer.network;

import com.example.aiplayer.config.DeepSeekConfig;

import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;

public class DeepSeekClient {
    private final HttpClient client = HttpClient.newBuilder().connectTimeout(Duration.ofSeconds(10)).build();

    public String chat(String prompt) {
        String apiKey = System.getenv().getOrDefault("DEEPSEEK_API_KEY", DeepSeekConfig.API_KEY.get());
        if (apiKey == null || apiKey.isBlank()) {
            return "[DeepSeek отключен: не задан API ключ]";
        }

        String payload = """
                {
                  \"model\": \"%s\",
                  \"messages\": [
                    {\"role\": \"system\", \"content\": \"Ты ИИ-игрок Minecraft. Отвечай коротко.\"},
                    {\"role\": \"user\", \"content\": \"%s\"}
                  ],
                  \"temperature\": 0.7
                }
                """.formatted(escapeJson(DeepSeekConfig.MODEL.get()), escapeJson(prompt));

        HttpRequest request = HttpRequest.newBuilder(URI.create(DeepSeekConfig.API_URL.get()))
                .header("Authorization", "Bearer " + apiKey)
                .header("Content-Type", "application/json")
                .timeout(Duration.ofSeconds(20))
                .POST(HttpRequest.BodyPublishers.ofString(payload))
                .build();

        try {
            HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());
            if (response.statusCode() >= 200 && response.statusCode() < 300) {
                return response.body();
            }
            return "[DeepSeek HTTP " + response.statusCode() + "] " + response.body();
        } catch (IOException | InterruptedException e) {
            return "[Ошибка DeepSeek] " + e.getMessage();
        }
    }

    private String escapeJson(String s) {
        return s.replace("\\", "\\\\").replace("\"", "\\\"").replace("\n", "\\n");
    }
}
