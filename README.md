# Chord
This is an implementation of a scalable P2P DHT structure in Python 2.7 based on the following paper.
https://pdos.csail.mit.edu/papers/chord:sigcomm01/chord_sigcomm.pdf
_________________

### Usage

To create a root node  
`python peer.py <root_port> <root_hostname>`

To create another node and join it to an existing node in the DHT  
`python peer.py <port> <hostname> <existing_port> <existing_hostname>`

### Example

`python peer.py 3400 localhost`  
`python peer.py 3401 localhost 3400 localhost`  
`python peer.py 3403 localhost 3400 localhost`  

The above simulteneous executions of the program will yield the following structure  
