// grid configuration
const int ROW_COUNT = 5;
const int COL_COUNT = 5;

// rows (outputs): D2, D3, D4, D5, D6
const int rowPins[ROW_COUNT] = {2, 3, 4, 5, 6};

// columns (inputs): A1, A2, A3, A4, A5
const int colPins[COL_COUNT] = {A1, A2, A3, A4, A5};

// ADC threshold for touch detection (3V on a 5V system)
// (3.0 / 5.0) * 1023 = 613.8, rounded to 614
const int TOUCH_THRESHOLD = (4.7 / 5.0) * 1023;

// array to store grid states grid states (according to size of grid) (1 = no touch, 0 = touch)
int gridState[ROW_COUNT * COL_COUNT];

void setup() {
  // begin serial communication with Raspberry Pi 5
  Serial.begin(115200);

  // set row pins as outputs, default to HIGH (inactive)
  for (int i = 0; i < ROW_COUNT; i++) {
    pinMode(rowPins[i], OUTPUT);
    digitalWrite(rowPins[i], HIGH);
  }

  // set column pins as analog inputs
  for (int i = 0; i < COL_COUNT; i++) {
    pinMode(colPins[i], INPUT);
    digitalWrite(colPins[i], HIGH);
  }
}

void loop() {
  String dataString = "";

  // scan the matrix
  for (int r = 0; r < ROW_COUNT; r++) {
    // set current row to LOW (active)
    digitalWrite(rowPins[r], LOW);
    delayMicroseconds(10); // Small delay for signal to settle

    for (int c = 0; c < COL_COUNT; c++) {
      // read analog value from ADC
      int reading = analogRead(colPins[c]);
      int index = r * COL_COUNT + c;

      // update grid state based on threshold
      if (reading < TOUCH_THRESHOLD) {
        gridState[index] = 0; // 0 = TOUCH
      } else {
        gridState[index] = 1; // 1 = NO TOUCH
      }

      dataString += String(gridState[index]);
      // add comma if not the last element
      if (index < (ROW_COUNT * COL_COUNT - 1)) {
        dataString += ",";
      }
    }

    // reset current row to HIGH (inactive)
    digitalWrite(rowPins[r], HIGH);
  }

  // send grid state over serial to Raspberry Pi 5
  Serial.println(dataString);

  // wait 50ms for a ~20Hz refresh rate
  delay(50);
}