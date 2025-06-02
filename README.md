# CHI 2025 Sign Language Dictionary

## Setup

Create a Conda environment with Python=>3.9. Once activated, install the dependencies using `pip install -r requirements.txt`.

Depending on where you host the main dictionary interface (see Section Run > Main dictionary interface), make sure to change all mentions of `$HOST_MAIN$` to a relevant URL. Similarly, depending on your hosting choice for the detailed analysis (see section Run > Detailed Analysis below), make sure to change all instances of `$HOST_DETAIL$` to a relevant URL.

Finally, copy the assets from `static-assets` to your detailed analysis host as well. Ensure that paths (directories) are preserved.

## Run

### Main dictionary interface

In the Conda environment, navigate to `gradio-recognition-screen` and run `python -m app`. If you run this locally, you will be able to access a port on the localhost (the output console will provide this port). If you run this on a server, make sure to reroute your HTTP (or HTTPS) port to this port.

### Detailed analysis

Host the contents of `results-screen` as a regular HTML website. There are many ways to achive this. For development and testing purposes, you may want to simply run this on `localhost`. For productionizing, a simple FPT server will do.
