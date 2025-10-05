// grid configuration
const int ROW_COUNT = 5;
const int COL_COUNT = 5;

// rows (outputs): D2, D3, D4, D5, D6
const int rowPins[ROW_COUNT] = {2, 3, 4, 5, 6};

// columns (inputs): D7, D8, D9, D10, D11
const int colPins[COL_COUNT] = {7, 8, 9, 10, 11};

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

  // set column pins as inputs, with pull-up resistors
  for (int i = 0; i < COL_COUNT; i++) {
    pinMode(colPins[i], INPUT_PULLUP);
  }
}

void loop() {
  String dataString = "";

  // scan the matrix
  for (int r = 0; r < ROW_COUNT; r++) {
    // set current row to LOW (active)
    digitalWrite(rowPins[r], LOW);

    for (int c = 0; c < COL_COUNT; c++) {
      // read digital state (HIGH or LOW)
      int reading = digitalRead(colPins[c]);
      int index = r * COL_COUNT + c;

      // update grid state based on reading
      if (reading == LOW) {
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