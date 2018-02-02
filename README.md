# eXchains

With consumers of electricity now also becoming producers at a higher rate, more imbalance is created on the electrical grid. To guarantee delivery of energy, the imbalance should be kept within the limits of the grid. Currently the transmission system operator (TSO: Tennet in Netherlands) is responsible for maintaining this balance. A problem arises when the production becomes more and more decentralized, and the balancing is still the duty of a centralized body. It becomes harder to respond on the highly fluctuating consumption and production of the different actors.

The aim of this project is to design and prototype a decentralized energy market and a so called 'smart grid' where participants of the smart grid can dynamically match their supply and demand to minimize imbalances.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

What things you need to install the software and how to install them

* Docker [Download](https://docs.docker.com/install/#supported-platforms)

on Windows: During the installation docker may ask to enable hyper-v, this is essential for running docker.

### Running

A step by step series of examples that tell you have to get a development env running

* Start Docker

* navigate to eXchains/tendermint/

* run command: docker-compose up --build

when running this for the first time this will take a while because it will pull all dependant packages from docker hub and build the python containers + dependencies. Succesive runs start considerably faster because all this work will be cached.

on Windows: Docker may ask for permission to access file system and/or network, it is needed for it to be able to properly function.

output should look someting like this:
```
Starting tendermint_app_1 ... 
Starting tendermint_web_1 ... 
Starting tendermint_client_1 ... 
Starting tendermint_app_1 ... done
Starting tendermint_web_1 ... done
Attaching to tendermint_tendermint_init_1, tendermint_app_1, tendermint_client_1, tendermint_tendermint_1, tendermint_web_1
app_1              | new connection to ('172.21.0.6', 59738)
app_1              | new connection to ('172.21.0.6', 59740)
app_1              | new connection to ('172.21.0.6', 59742)
tendermint_tendermint_init_1 exited with code 0
tendermint_1       | I[02-02|16:41:17.758] Executed block                               module=state height=1 validTxs=0 invalidTxs=0
tendermint_1       | I[02-02|16:41:17.761] Committed state                              module=state height=1 txs=0 appHash=
```

* to shutdown press ctrl-C twice and run command: docker-compose down -v

### accessing the relevant interfaces
  
  * tendermint http api is available on http://localhost:46657
  
  * web interface showing current round information on http://localhost
  

## Authors

* **Jetse Brouwer** - *Balancing Algorithm* - [JetseBrouwer](https://github.com/JetseBrouwer)
* **Evgenia Domnenkova** - *Other* - [edogithub](https://github.com/edogithub)
* **Niels Hokke** - *Balancing Algorithm* - [NielsHokke](https://github.com/NielsHokke)
* **Michał Łoin** - *Tendermint* - [Meaglin](https://github.com/Meaglin)
* **Joseph Verburg** - *Tendermint* - [michalloin](https://github.com/michalloin)

## Acknowledgments

We would like to thank the following people for their guidance, advise, and inspiration:

* Zeki Erkin, Zhijie Ren
* Ilhan Ünlü
* Sjors Hijgenaar
