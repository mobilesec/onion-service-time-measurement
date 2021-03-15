# Measurement of onion service depoyment times

Using onion services in dynamic scenarios is only possible if their creation happens within predictable time frames. This project was created as part of a research effort to measure just how log the creation of onion services usually takes.


## Measurement Setup
The repository cotains all required pieces of software to create a Docker container, which can be used to collect timing information on onion services. For this purpose, create a new container with `docker build -t <whatever> .` and run the image with: `docker run --rm -v results:/results -v /etc/localtime:/etc/localtime:ro -v X -t 180 -i 3`.
The arguments allow you to specify the version of Tor you would like to use (2,3,3NE,3VN), the timeout (how long to wait before assuming that an onion-service will never become available) and the number of introduction points you want for your service. 

### Supported Onion Service versions
- 2: Version 2 of the onion service protocol
- 3: Version 3 of the onion service protocol. As suggested by the Tor project, this version uses ephemeral services to create temporary onion services. 
- 3NE: This option allows you to measure non-ephemeral V3 onion services. 
- 3VN: This option measures ephemeral onion services, with the Vanguard extension to harden the onion service against attacks. 

## How it works
The container uses a basic debian image, where it installs all dependencies needed to run the measurement. The Tor source code is built directly within the container to produce a working Tor instance. Pay attention that a few changes had to be made on the Tor source code to enable timing measurements, if you want to measure a newer version of Tor, those changes must be replicated. 
When the container is started, a bash script starts Tor and uses the Python STEM library to create the required onion service. It then attaches several event listeners via STEM to log the times of the following events: 

- Service creation started
- Circuit to introduction point started
- Circuit to introduction point completed
- Introduction point ready
- Descriptor generation started
- Descriptor generation completed
- Descriptor upload circuit started
- Descriptor upload circuit completed
- Descriptor HTTP upload started
- Descriptor HTTp upload complete

Once all times have been measured (or the timeout is reached) the container shuts down. To obtain statistically significant data, it is recommended to run the measurement repeatedly over a longer period of time. 

## Acknowledgement
This work has been carried out within the scope of Digidow, the Christian Doppler Laboratory for Private Digital Authentication in the Physical World, funded by the Christian Doppler Forschungsgesellschaft, 3 Banken IT GmbH, Kepler Universitätsklinikum GmbH, NXP Semiconductors Austria GmbH, and Österreichische Staatsdruckerei GmbH and has partially been supported by the LIT Secure and Correct Systems Lab funded by the State of Upper Austria.
