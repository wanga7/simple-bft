# Anjie Wang
# config.py

# max number of faulty nodes
numFaults=2

# designated ports for 6 lieutenants
ports=("5001","5002","5003","5004","5005","5006")

# designated port for general
general_port="5000"

# total number of actors
numNodes=7

# last round No. (starting from round 0)
lastRoundNo=numFaults

# total number of msg to be received during each round by each actor
roundInfo=[1,numNodes-1,(numNodes-1)*(numNodes-2)]
