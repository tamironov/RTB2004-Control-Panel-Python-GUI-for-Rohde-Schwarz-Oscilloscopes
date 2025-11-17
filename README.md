RTB2004 Control Panel – Python GUI for Rohde & Schwarz Oscilloscopes

This repository contains a modern Python GUI application for controlling the Rohde & Schwarz RTB2004 digital oscilloscope over USB or LAN using PyVISA.
The interface is built with CustomTkinter and designed with ATE-style usability in mind.

🔧 Features

VISA Device Scanner
Automatically lists all connected VISA instruments.

LAN Control (TCPIP)
Connect to the oscilloscope via Ethernet using a configurable IP address.

Connection & Status Panel
Displays real-time connection state and full instrument ID response.

Channel Control Panel

Vertical scale

Offset

Coupling (DC/AC/GND)

Probe attenuation

Timebase Control

Scale (s/div)

Time position

Trigger Control

Source (CH1–CH4, EXT)

Mode (AUTO, NORMAL, SINGLE)

Trigger level

Acquisition Commands

RUN

STOP

AutoSet

Batch Configuration
Apply all channel, timebase, and trigger settings with one button.

Threaded SCPI Execution
Prevents GUI freeze during slow VISA communication.

🧩 Technologies Used

Python 3

CustomTkinter

PyVISA

Tkinter

SCPI instrument control

Threading
