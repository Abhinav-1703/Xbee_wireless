bool isPowerOn = false;  // Track power state

void setup() {
    Serial.begin(9600);
    Serial.println("ESP Debugging System Started");
}

void loop() {
    char rxBuffer[50];
    if (Serial.available()) {
        int len = Serial.readBytesUntil('\n', rxBuffer, sizeof(rxBuffer) - 1);
        rxBuffer[len] = '\0';
        Serial.print("Received: "); Serial.println(rxBuffer);

        if (strncmp(rxBuffer, "R", 1) == 0) {
            sendLogData();
        } else if (strncmp(rxBuffer, "0", 1) == 0) {
            isPowerOn = false;
            Serial.println("STATUS: Powering Off (Simulation)");
        } else if (strncmp(rxBuffer, "1", 1) == 0) {
            isPowerOn = true;
            Serial.println("STATUS: Powering On (Simulation)");
        } else {
            Serial.println("STATUS: Unknown Command");
        }
        memset(rxBuffer, 0, sizeof(rxBuffer));
    }

    // Send periodic data for plotting only if power is ON
    static unsigned long lastTime = 0;
    if (isPowerOn && millis() - lastTime >= 2000) {
        lastTime = millis();
        int speed = random(20, 100);
        float battery_voltage = random(360, 420) / 100.0;
        char msg[100];
        snprintf(msg, sizeof(msg), "PLOT DATA: Speed=%d%%, Battery=%.2fV", speed, battery_voltage);
        Serial.println(msg);
    }
} 

void sendLogData() {
    int speed = random(20, 100);
    float battery_voltage = random(360, 420) / 100.0;
    float current = random(10, 50) / 10.0;
    float temp = random(20, 40);
    const char* mode = "AUTO";
    int error_code = 0;

    char msg[300];
    snprintf(msg, sizeof(msg), "LOG DATA: Speed=%d%%, Battery=%.2fV, Current=%.2fA, Temp=%.1fC, Mode=%s, ErrorCode=%d", 
             speed, battery_voltage, current, temp, mode, error_code);
    Serial.println(msg);
}
