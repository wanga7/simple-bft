# Simple-BFT

**Architecture**

- `node.py` Implementation of an actor (general/ lieutenant) in the BFT.
- `config.py` store configurations

**Testing Instructions**
- This project uses the `treelib` library to help implement the tree structure for storing received messages in lieutenants. To install the library, enter: `$ sudo easy_install -U treelib`
- This project uses the client server synchronous communication pattern from zeromq (http://learning-0mq-with-pyzmq.readthedocs.io/en/latest/pyzmq/patterns/client_server.html). So make sure you have zmq library installed on your computer.
- First launch 6 lieutenants: `python node.py <identity> <port>`
	- A good lieutenant argument is `lg`, a bad lieutenant (which will always pass "retreat" msg) argument is `lf`. The ports are predefined in `config.py`, they should be in the range 5001-5006.
	- Examples. To launch a good lieutenant at port 5001: `python node.py lg 5001`. To launch a bad lieutenant at port 5002: `python node.py lf 5002`
	- The lieutenants will print to console information of each round, and the final result based on majority vote.
	- **Note: By default, the lieutenants will print to console a tree structure of the msg tree. But this might incur display errors when running the project on AWS server and watch on local console. If you encounter such errors, comment out the line 41 `show_tree()`. If you run the project on local VM, it should be fine.**
- Then launch the general: `python node.py g`
	- The general is predefined to be at port 5000 in `config.py`. Once launched, it will send "attack" msg to all 6 lieutenants.
