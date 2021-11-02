# dig-that-arch
Architecture for the "Dig That!" game - Heuristic Problem Solving

[Here](https://cs.nyu.edu/courses/fall21/CSCI-GA.2965-001/digthatcomp.html) is a brief from the course website about the game itself.

The game is designed largely in websockets and JSON. The player sends and receives messages in a particular order, as described below.

First, the Tunneler connects to the server and sends a message with the player name and their role. Then the tunneler receives a JSON containing the parameters of the game - namely, the values of n (grid size), k (maximum path length) and p (number of phases). Then the tunneler must dig his tunnel and send the corresponding co-ordinates to the server. If the path is invalid, the server will send a JSON stating that the path is invalid and the client must resend their path.

Next, the Detector will connect to the server, and receive the same JSON containing parameters as described above. Then, the detector, in each of the p phases, must send a list of edges and vertices that he wants to probe. The server will then return a list of vertices and edges that coincide with the tunneler's path. Once all the phases are over, the client must send a list of edges as its final guess.

As described on the website, the final score is the number of unique probes that the detector has used to identify the tunneler's path. Each team will play as both the tunneler and the detector and the team with the lowest score wins!

**Note:** The "viz" folder contains a browser implementation of the game. The viz part is being integrated with the server architecture.


For clients using Python, a few requirements need to be installed. Run the following command:
```bash
pip install -r requirements.txt
```

The JSON formats are given below:

Initial JSON sent by the clients. The name should be changed to your team's name, but the role must be the same.

```json
{
"name": "TunnelerClient",
"role": "Tunneler"
}
```

```json
{
"name": "DetectorClient",
"role": "Detector"
}
```
Both tunneler and detector clients receive the parameters in the following JSON:
```json
{
"n": 5, 
"p": 3,
"k": 9
}
```


Before tunneling, the client is sent the following JSON:
```json
{
"canStart": True
}
```
Once the tunneler is done designing the tunnel, they need to send a reply in the following format: (tuples and lists will both work)
```json
{
"name": "TunnelerClient",
"edges" : [(0, 0), (0, 1)], [(0, 1), (1, 1)], [(1, 1), (1, 2)], [(1, 2), (2, 2)], [(2, 2), (2, 3)],
}
```
After the attempted tunnel, the tunneler will receive the following JSON:
```json
{
"tunneling_done": True/False
}
```

Now for the detector. They receive the round number before each round, indicating when they can start building their guess for that turn.
```json
{
"round": 1
}
```
In each round, the detector must send the following format of JSON:
```json
{
"name": "DetectorClient", 
"edges": [[(0, 1), (0, 0)], [(0, 1), (1, 1)], [(1, 3), (1, 2)]], 
"vertices": [(1, 1), (2, 3)]
}
```
After the guess has been evaluated, the vertices and edges matching the path are returned to the client:
```json
{
"correct_edges": [(0, 1), (0, 0)], [(0, 1), (1, 1)]],
"correct_vertices": [(1, 1), (2, 3)]
}
```
Once the results of each guess has been returned to the detector client, it's time for the final guess, which should look like this:
```json
{
"edges": [[(0, 0), (0, 1)], [(0, 1), (1, 1)], [(1, 1), (1, 2)], [(1, 2), (2, 2)], [(2, 2), (2, 3)]]
}
```

Then the final score is displayed.


**Note:** The "viz" folder contains a browser implementation of the game. The viz part is being integrated with the server architecture.

For clients using Python, a few requirements need to be installed. Run the following command:
```bash
pip install -r requirements.txt
```

For clients using Java, the below maven dependencies are required (for JSON-Simple and java-websocket):
```
<dependency>
    <groupId>com.googlecode.json-simple</groupId>
    <artifactId>json-simple</artifactId>
    <version>1.1.1</version>
</dependency>

<dependency>
  <groupId>org.java-websocket</groupId>
  <artifactId>Java-WebSocket</artifactId>
  <version>1.5.2</version>
</dependency>
```
