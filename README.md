# Soft Sensor System

A real-time 5x5 capacitive touch matrix sensor with OLED display feedback, featuring optimized performance for fast refresh rates.

## System Architecture

This system implements a **5x5 capacitive touch matrix sensor** with real-time visual feedback, consisting of two main components that communicate over serial:

### 1. Pico Controller (`pico_grid.py`) - Hardware Interface Layer

**Core Functionality:**
- **Matrix Scanning**: Implements efficient row-column scanning of a 5x5 touch grid
- **Pin Configuration**: 
  - Rows (GP2-GP6): Output pins for driving the matrix
  - Columns (GP7-GP11): Input pins with pull-up resistors for reading
- **Touch Detection Logic**: Uses inverted logic where `0` = touch detected, `1` = no touch

**Performance Optimizations:**
- **State Change Detection**: Only transmits data when the touch state changes, reducing unnecessary serial traffic
- **Fast Scanning**: 10μs settling delay between row activations for rapid matrix scanning
- **Buffered Communication**: Uses UART with flushing to ensure immediate data transmission
- **High Refresh Rate**: Runs at ~50Hz (20ms loop time) for responsive touch detection
- **Periodic Sync**: Sends full state every 50 iterations (1 second) to maintain synchronization

**Data Format**: Transmits comma-separated values representing the entire 25-cell grid state

### 2. Pi Display Controller (`soft_sense_pico.py`) - Visualization Layer

**Core Functionality:**
- **Serial Communication**: Receives touch data from Pico over USB serial at 115200 baud
- **OLED Display**: Renders real-time grid visualization on SH1106 OLED display via I2C
- **Grid Rendering**: Draws 5x5 grid with filled squares for touched cells, empty for untouched

**Performance Optimizations:**
- **Smart Redrawing**: Only redraws the display when grid state actually changes
- **Non-blocking Serial**: Uses 0.1s timeout to prevent hanging on missing data
- **Efficient Rendering**: Pre-calculates grid positioning and uses canvas buffering
- **High Responsiveness**: 50Hz loop rate (20ms) for near real-time visual feedback
- **Error Handling**: Robust handling of incomplete serial data and Unicode errors

**Visual Design:**
- **Grid Layout**: 10px cells with 2px gaps, centered on display
- **Touch Indication**: White-filled squares for active touches, outlined squares for inactive
- **Responsive UI**: Immediate visual feedback upon touch detection

## System Integration & Fast Refresh Rate

### Communication Protocol
- **Serial Link**: 115200 baud USB serial connection between Pico and Pi
- **Data Efficiency**: Only transmits on state changes, minimizing bandwidth usage
- **Synchronization**: Periodic full-state broadcasts ensure system stays in sync

### Performance Characteristics
- **Touch Detection**: Sub-millisecond matrix scanning with 10μs settling time
- **Data Transmission**: Immediate UART flushing for minimal latency
- **Visual Response**: 50Hz refresh rate provides smooth, responsive user interaction
- **Optimization Strategy**: State change detection prevents unnecessary processing on both ends

### Key Design Benefits
1. **Low Latency**: Optimized scanning and immediate transmission minimize delay
2. **Bandwidth Efficient**: Change-based updates reduce serial traffic
3. **Robust Operation**: Error handling and periodic sync maintain reliability
4. **Scalable Architecture**: Modular design allows easy modification of grid size or display type

## Hardware Requirements

- **Raspberry Pi Pico H** (with headers for easy connection)
- **Raspberry Pi 5** (or compatible Pi model)
- **SH1106 OLED Display** (I2C interface)
- **5x5 Capacitive Touch Matrix** (custom or commercial)
- **USB Cable** (for Pico-Pi communication)

## Software Dependencies

### Pico (MicroPython)
- `machine` - Hardware interface
- `time` - Timing functions

### Pi (Python)
- `serial` - Serial communication
- `luma.core` - OLED display core functions
- `luma.oled` - OLED device drivers
- `time` - Timing functions

## Configuration

### System Config
- **Serial Port**: `/dev/ttyACM0`
- **Baud Rate**: 115200
- **I2C Address**: 0x3C (OLED display)

### Grid Config
- **Grid Size**: 5x5 (25 cells)
- **Cell Size**: 10px
- **Cell Gap**: 2px
- **Refresh Rate**: 50Hz

## Usage

1. Connect the 5x5 touch matrix to the Pico pins as specified
2. Connect the OLED display to Pi's I2C bus
3. Connect Pico to Pi via USB
4. Upload `pico_grid.py` to the Pico
5. Run `soft_sense_pico.py` on the Pi
6. Touch the matrix to see real-time visualization on the OLED display

This architecture achieves a fast, responsive soft sensor suitable for real-time interactive applications, with the Pico handling the time-critical hardware interface while the Pi provides rich visual feedback and potential for additional processing or networking capabilities.
