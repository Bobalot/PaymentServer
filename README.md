# Bitcoin Payment Server

A small flask application for providing clean addresses to people wanting to give you their money.

A new address is generated for each unique IP addresses and is then stored for 10 minutes in redis.

No private keys need to be stored on the server, addresses are generated from an electrum master public key.

## Setup
* Open config.py and set the mpk variable to your master public key.
* Install requirements
* Run DonationServer.py

