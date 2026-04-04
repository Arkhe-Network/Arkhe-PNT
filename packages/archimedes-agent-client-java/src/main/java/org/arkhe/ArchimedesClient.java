package org.arkhe;

import com.google.gson.Gson;
import okhttp3.MediaType;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.RequestBody;
import okhttp3.Response;

import java.io.IOException;
import java.util.Map;

public class ArchimedesClient {
    private static final MediaType JSON = MediaType.get("application/json; charset=utf-8");
    private final OkHttpClient httpClient;
    private final Gson gson;
    private final String baseUrl;

    public ArchimedesClient(String baseUrl) {
        this.baseUrl = baseUrl;
        this.httpClient = new OkHttpClient();
        this.gson = new Gson();
    }

    public Map<String, Object> analyze(Map<String, Object> requestPayload) throws IOException {
        String json = gson.toJson(requestPayload);
        RequestBody body = RequestBody.create(json, JSON);
        Request request = new Request.Builder()
                .url(baseUrl + "/analyze")
                .post(body)
                .build();

        try (Response response = httpClient.newCall(request).execute()) {
            if (!response.isSuccessful()) {
                throw new IOException("Unexpected code " + response);
            }
            String responseBody = response.body().string();
            return gson.fromJson(responseBody, Map.class);
        }
    }
}
