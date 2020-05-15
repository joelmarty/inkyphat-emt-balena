# InkyPhat - Madrid next bus

This project is a python application that displays on an InkyPhat display
the next arrival times for buses at a selected line and stop.

## Pre-requisites

1. Create an EMT MobilityLabs account
2. Create an EMT application in order to obtain a client id and a passkey

## Development

### Pre-requisites

1. Python 3.8
2. For API tests, add the following to `local.env`:
   ```.env
    EMT_CLIENT_ID=<emt client id>
    EMT_PASS_KEY=<emt passkey>
   ```