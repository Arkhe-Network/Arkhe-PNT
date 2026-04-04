package org.arkhe;

import okhttp3.*;
import com.google.gson.Gson;
import java.io.IOException;

public class ArchimedesClient {
    private final OkHttpClient httpClient;
    private final String baseUrl;
    private final Gson gson = new Gson();

    public ArchimedesClient(String baseUrl) {
        this.baseUrl = baseUrl;
        this.httpClient = new OkHttpClient();
    }

    public String analyze() throws IOException {
        Request httpRequest = new Request.Builder()
                .url(baseUrl + "/analyze")
                .post(RequestBody.create("", MediaType.parse("application/json")))
                .build();
        try (Response response = httpClient.newCall(httpRequest).execute()) {
            if (!response.isSuccessful()) throw new IOException("Unexpected code " + response);
            return response.body().string();
        }
    }

    public String simulateSU2(Object request) throws IOException {
        String json = gson.toJson(request);
        RequestBody body = RequestBody.create(json, MediaType.parse("application/json"));
        Request httpRequest = new Request.Builder()
                .url(baseUrl + "/simulate/su2")
                .post(body)
                .build();
        try (Response response = httpClient.newCall(httpRequest).execute()) {
            if (!response.isSuccessful()) throw new IOException("Unexpected code " + response);
            return response.body().string();
        }
    }
}
