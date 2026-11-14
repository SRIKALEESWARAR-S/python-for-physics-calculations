const int trigPin = 9;
const int echoPin = 10;
const float DECOHERENCE_THRESHOLD_CM = 30.0;

void setup() {
  Serial.begin(9600);
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
}

void loop() {
  // Clear the trigPin
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);

  // Trigger a 10-microsecond HIGH pulse
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  // Read the echoPin (timeout after 30ms ~ 500cm max range)
  long duration = pulseIn(echoPin, HIGH, 30000);

  // Calculate distance in cm (Speed of sound = 0.0343 cm/us)
  float distance = (duration * 0.0343) / 2.0;

  // Filter out invalid 0 readings from timeouts
  if (distance > 0 && distance < 400) {
    String state = (distance <= DECOHERENCE_THRESHOLD_CM) ? "DECOHERENCE" : "COHERENT";
    
    // Output format: distance,state
    Serial.print(distance, 2);
    Serial.print(",");
    Serial.println(state);
  }

  delay(200); // 5 Hz sampling rate
}
