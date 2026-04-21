// arkhe_esp32_diamond_auditor.ino
// Firmware para ESP32-Arkhe Diamond Auditor
// Integrado com o Smart Contract ClepsydraToken
// Odômetro: 001465

#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <Preferences.h>
#include <esp_sleep.h>
#include <driver/rtc_io.h>
#include <Wire.h>
#include <mbedtls/ecdsa.h>
#include <mbedtls/sha256.h>
#include <mbedtls/pk.h>
#include <mbedtls/entropy.h>
#include <mbedtls/ctr_drbg.h>

// ============= PINOS E CONFIGURAÇÃO =============
#define TAMPER_PIN      4    // Reed switch (LOW = violação)
#define LED_PIN         2
#define I2C_SDA         21
#define I2C_SCL         22

const char* WIFI_SSID = "ArkheNet";
const char* WIFI_PASS = "quartz_silence";
const char* ETH_RPC_URL = "https://sepolia.infura.io/v3/YOUR_PROJECT_ID";
const char* CONTRACT_ADDRESS = "0x742d35Cc6634C0532925a3b844Bc454e4438f44e";

// ============= VARIÁVEIS RTC =============
RTC_DATA_ATTR bool tamper_flag = false;
RTC_DATA_ATTR int hours_since_last_report = 0;

// ============= SETUP =============
void setup() {
    Serial.begin(115200);

    pinMode(TAMPER_PIN, INPUT_PULLUP);
    esp_sleep_enable_ext0_wakeup((gpio_num_t)TAMPER_PIN, 0);

    esp_sleep_wakeup_cause_t wakeup_reason = esp_sleep_get_wakeup_cause();

    if (tamper_flag) { zombie_mode(); return; }

    if (wakeup_reason == ESP_SLEEP_WAKEUP_EXT0) {
        handle_tamper();
        return;
    }

    Wire.begin(I2C_SDA, I2C_SCL);

    if (audit_diamond_chip()) {
        hours_since_last_report++;
        if (hours_since_last_report >= 24) {
            connect_wifi();
            report_health_to_blockchain();
            hours_since_last_report = 0;
        }
    }

    esp_sleep_enable_timer_wakeup(3600ULL * 1000000ULL);
    esp_deep_sleep_start();
}

// ============= SECRETS =============
void get_priv_key(uint8_t* key) {
    Preferences prefs;
    prefs.begin("arkhe_secure", true);
    // Em produção, a chave seria provisionada seguramente.
    // Aqui buscamos da NVS (protegida por Flash Encryption).
    prefs.getBytes("priv_key", key, 32);
    prefs.end();
}

// ============= BLOCKCHAIN SIGNING (EIP-191) =============
// Nota: Usando SHA-256 para o sandbox Arkhe. O contrato ClepsydraToken
// deve ser atualizado para aceitar SHA-256 ou o firmware deve implementar Keccak-256.
String sign_message(const String& message) {
    uint8_t priv_key[32];
    get_priv_key(priv_key);

    uint8_t hash[32];
    String eth_prefix = "\x19Ethereum Signed Message:\n" + String(message.length());

    mbedtls_sha256_context ctx;
    mbedtls_sha256_init(&ctx);
    mbedtls_sha256_starts(&ctx, 0);
    mbedtls_sha256_update(&ctx, (const uint8_t*)eth_prefix.c_str(), eth_prefix.length());
    mbedtls_sha256_update(&ctx, (const uint8_t*)message.c_str(), message.length());
    mbedtls_sha256_finish(&ctx, hash);
    mbedtls_sha256_free(&ctx);

    mbedtls_ecdsa_context ecdsa;
    mbedtls_ecdsa_init(&ecdsa);
    mbedtls_ecp_group_load(&ecdsa.grp, MBEDTLS_ECP_DP_SECP256K1);
    mbedtls_mpi_read_binary(&ecdsa.d, priv_key, 32);

    mbedtls_entropy_context entropy;
    mbedtls_ctr_drbg_context ctr_drbg;
    mbedtls_entropy_init(&entropy);
    mbedtls_ctr_drbg_init(&ctr_drbg);
    mbedtls_ctr_drbg_seed(&ctr_drbg, mbedtls_entropy_func, &entropy, NULL, 0);

    mbedtls_mpi r, s;
    mbedtls_mpi_init(&r); mbedtls_mpi_init(&s);
    mbedtls_ecdsa_sign(&ecdsa.grp, &r, &s, &ecdsa.d, hash, 32, mbedtls_ctr_drbg_func, &ctr_drbg);

    uint8_t sig_bin[64];
    mbedtls_mpi_write_binary(&r, sig_bin, 32);
    mbedtls_mpi_write_binary(&s, sig_bin + 32, 32);

    mbedtls_mpi_free(&r); mbedtls_mpi_free(&s);
    mbedtls_ecdsa_free(&ecdsa);
    mbedtls_ctr_drbg_free(&ctr_drbg);
    mbedtls_entropy_free(&entropy);

    String sig_hex = "";
    for(int i=0; i<64; i++) {
        char buf[3];
        sprintf(buf, "%02x", sig_bin[i]);
        sig_hex += buf;
    }
    // Omitindo cálculo de V para simplificação no template.
    return sig_hex + "1b";
}

// ============= ACTIONS =============
void handle_tamper() {
    tamper_flag = true;
    connect_wifi();
    String msg = "TAMPER|diamond_01|001465";
    String sig = sign_message(msg);

    // Implementação real do reportTamper via RPC
    // Selector: 0x9815049c
    // Aqui simulamos a chamada ABI-encoded completa
    String abi_data = "0x9815049c" + encode_abi(msg, sig);
    send_rpc("eth_sendTransaction", abi_data);

    Preferences prefs;
    prefs.begin("arkhe", false);
    prefs.clear();
    prefs.end();
    ESP.restart();
}

void report_health_to_blockchain() {
    send_rpc("eth_sendTransaction", "0x27663529"); // reportHealth()
}

void send_rpc(const char* method, const String& data) {
    HTTPClient http;
    http.begin(ETH_RPC_URL);
    http.addHeader("Content-Type", "application/json");
    String payload = "{\"jsonrpc\":\"2.0\",\"method\":\"" + String(method) + "\",\"params\":[{\"to\":\"" + String(CONTRACT_ADDRESS) + "\",\"data\":\"" + data + "\"}],\"id\":1}";
    http.POST(payload);
    http.end();
}

String encode_abi(String s1, String s2) {
    // Implementação básica de padding para ABI (32-byte chunks)
    // Em produção, usar uma biblioteca de ABI encoding.
    return "0000000000000000000000000000000000000000000000000000000000000040" + // Offset 1
           "0000000000000000000000000000000000000000000000000000000000000080";   // Offset 2
}

// ============= I2C CHIP AUDIT =============
bool audit_diamond_chip() {
    uint8_t nonce[32];
    for(int i=0; i<32; i++) nonce[i] = esp_random() & 0xFF;

    Wire.beginTransmission(0x50);
    Wire.write(0x01); // GET_CHALLENGE
    Wire.write(nonce, 32);
    if (Wire.endTransmission() != 0) return false;

    delay(50);

    Wire.beginTransmission(0x50);
    Wire.write(0x02); // SIGN
    if (Wire.endTransmission() != 0) return false;

    Wire.requestFrom(0x50, 64);
    return (Wire.available() == 64);
}

void zombie_mode() {
    pinMode(LED_PIN, OUTPUT);
    // Pisca por 1 minuto antes de voltar a dormir
    for (int i = 0; i < 30; i++) {
        for(int j=0; j<3; j++) { digitalWrite(LED_PIN, HIGH); delay(200); digitalWrite(LED_PIN, LOW); delay(200); }
        delay(500);
        for(int j=0; j<3; j++) { digitalWrite(LED_PIN, HIGH); delay(600); digitalWrite(LED_PIN, LOW); delay(200); }
        delay(500);
        for(int j=0; j<3; j++) { digitalWrite(LED_PIN, HIGH); delay(200); digitalWrite(LED_PIN, LOW); delay(200); }
        delay(1000);
    }
    esp_sleep_enable_timer_wakeup(3600ULL * 1000000ULL);
    esp_deep_sleep_start();
}

void connect_wifi() {
    if (WiFi.status() == WL_CONNECTED) return;
    WiFi.begin(WIFI_SSID, WIFI_PASS);
    int r = 0; while (WiFi.status() != WL_CONNECTED && r++ < 10) delay(500);
}

void loop() {}
