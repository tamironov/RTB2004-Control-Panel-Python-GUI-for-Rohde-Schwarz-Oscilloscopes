# RTB2004 Control Panel – Python GUI for Rohde & Schwarz Oscilloscopes

A modern Python GUI for controlling the **Rohde & Schwarz RTB2004** oscilloscope via **USB or LAN (TCPIP)** using **PyVISA**.  
Built with **CustomTkinter**, optimized for ATE (Automated Test Equipment) environments, and designed for smooth, intuitive operation.

---

## Features

### Connection & Communication
- VISA device scanning (USB/serial instruments)
- TCP/IP LAN connection using user-defined IP
- Real-time status bar with instrument identification (`*IDN?`)
- Automatic VISA resource handling

### Channel Controls
- Select channel (CH1–CH4)
- Vertical scale (V/div)
- Vertical offset (V)
- Coupling options: DC / AC / GND
- Probe attenuation: 1×, 10×, 100×

### Timebase Controls
- Time scale (s/div)
- Horizontal position (s)

### Trigger Controls
- Source selection (CH1–CH4, EXT)
- Trigger mode (AUTO / NORMAL / SINGLE)
- Trigger level (V)

### Acquisition Actions
- RUN
- STOP
- AutoSet
- Apply All Settings (batch SCPI execution)

### Multithreading
- All SCPI write operations are threaded to avoid GUI freezing
- Safe error handling with message popups

