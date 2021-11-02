import asyncio
import websockets
import argparse
import json
import time
import math
from server_rest import register


hostname = "localhost"
port = 8080

# Some default game params
N_DEFAULT = 5
K_DEFAULT = 9
P_DEFAULT = 3

tunneler = {}
detector = {}
args = None
vertices_dict = {}
edges_list = []
guesses_dict = {"edges": [], "vertices": []}
time_tunneler = 0
time_detector = 0
    
async def main():
    # Parsing command line args
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", help = "Size of grid", type = int, default = N_DEFAULT)
    parser.add_argument("-k", help = "Max size of tunnel", type = int, default = K_DEFAULT)
    parser.add_argument("-p", help = "Number of detection phases", type = int, default = P_DEFAULT)
    global args
    args = parser.parse_args()
    print("Done parsing args")

    async with websockets.serve(evaluator, hostname, port):
        await asyncio.Future()

async def evaluator(websocket, path):    
    init_msg = json.loads(await websocket.recv())
    global time_tunneler, time_detector

    print("Initial message: " + str(init_msg))
    role = init_msg["role"]
    name = init_msg["name"]

    if(role == "Tunneler"):
        start_msg = json.dumps({"canStart": True, "n": args.n, "k": args.k, "p": args.p})
        tunneling_done = False
        while(not tunneling_done):
            await websocket.send(start_msg)
            
            start = time.time()
            path_msg = json.loads(await websocket.recv())
            end = time.time()

            time_tunneler += end - start
            print("Time taken by the tunneler: " + str(time_tunneler))
            print("Message sent by tunneler: " + str(path_msg))

            if(path_validate(path_msg)):
                tunneling_done = True
            else:
                global vertices_dict, edge_list
                vertices_dict = {}
                edge_list = []
        print("Tunneling done, no more waiting")

    elif(role == "Detector"):
        start_msg = json.dumps({"n": args.n, "k": args.k, "p": args.p})
        await websocket.send(start_msg)
        final_score = 0

        for i in range(1, args.p + 1):
            round_msg = json.dumps({"round": i})
            await websocket.send(round_msg)

            start = time.time()
            guess = json.loads(await websocket.recv())
            end = time.time()
            time_detector += end - start

            print("Time taken by the detector: " + str(time_detector))

            print("Detector sent guess: " + str(guess))
            return_msg, score = guess_validate_and_score(guess)

            print("Return message:")
            print(str(return_msg["correct_edges"]))
            print(str(return_msg["correct_vertices"]))
            final_score += score

            await websocket.send(json.dumps(return_msg))
        
        final_guess = json.loads(await websocket.recv())
        correct = valid(final_guess)
        if(not correct): 
            final_score = math.inf
        print("Hence the final score is: " + str(final_score))

def valid(final_guess):
    edges_list_copy = [ele for ele in edges_list]
    for guess_edge in final_guess["edges"]:
        for edge in edges_list:
            if(equal_edges(edge, guess_edge)):
                edges_list_copy.remove(edge)
    
    if(edges_list_copy == []):
        return True
    return False

def guess_validate_and_score(guess):
    guess_score = 0
    return_msg = {"correct_edges": [], "correct_vertices": []}
    if "edges" in guess:
        valid_edge_guesses = add_guess_edges(guess["edges"])
        guess_score += len(valid_edge_guesses)
        print("Valid edge guesses this time: " + str(valid_edge_guesses) + " score: " + str(guess_score))

    if "vertices" in guess:
         valid_vertex_guesses = add_guess_vertices(guess["vertices"])
         guess_score += len(valid_vertex_guesses)
         print("Valid vertex guesses this time: " + str(valid_vertex_guesses) + " score " + str(guess_score))

    for guess_edge in valid_edge_guesses:
        if(edge_in_path(guess_edge)):
            return_msg["correct_edges"].append(guess_edge)

    for guess_vertex in valid_vertex_guesses:
        if(vertex_in_path(guess_vertex)):
            return_msg["correct_vertices"].append(guess_vertex)

    print("Correct edges: " + str(return_msg["correct_edges"]))

    return return_msg, guess_score

def vertex_in_path(guess_vertex):
    for edge in edges_list:
        v1 = edge[0]
        v2 = edge[1]
        if(equal_vertices(v1, guess_vertex) or equal_vertices(v2, guess_vertex)):
            return True
    return False 

def edge_in_path(guess_edge):
    for edge in edges_list:
        if(equal_edges(edge, guess_edge)):
            return True
    return False

def add_guess_edges(guess_edges):
    valid_guesses = []
    for guess_edge in guess_edges:
        if(not already_guessed_edge(guess_edge) and is_valid_edge(guess_edge)):
            valid_guesses.append(guess_edge)
            guesses_dict["edges"].append(guess_edge)
    return valid_guesses

def already_guessed_edge(guess_edge):
    for edge in guesses_dict["edges"]:
        if(equal_edges(edge, guess_edge)):
            return True
    return False

def equal_vertices(vertex1, vertex2):
    if(vertex1[0] == vertex2[0] and vertex1[1] == vertex2[1]):
        return True
    return False

def equal_edges(edge1, edge2):
    if((edge1[0][0] == edge2[0][0] and edge1[0][1] == edge2[0][1]) and 
        (edge1[1][0] == edge2[1][0] and edge1[1][1] == edge2[1][1])):
        return True
    elif((edge1[0][0] == edge2[1][0] and edge1[0][1] == edge2[1][1]) and
        (edge1[1][0] == edge2[0][0] and edge1[1][1] == edge2[0][1])):
        return True
    return False

def add_guess_vertices(guess_vertices):
    valid_guesses = []
    for guess_vertex in guess_vertices:
        if(not already_guessed_vertex(guess_vertex)):
            valid_guesses.append(guess_vertex)
            guesses_dict["vertices"].append(guess_vertex)
    return valid_guesses

def already_guessed_vertex(guess_vertex):
    for vertex in guesses_dict["vertices"]:
        if equal_vertices(guess_vertex, vertex):
            return True
    return False

def path_validate(path_msg):
    edges = path_msg["edges"]
    edge_count = 0
    middle_vertex_count = 0
    v_on_top = False
    v_on_bottom = False
    within_limits = True
    valid_edges = True

    print("Edge data: " + str(edges))
    for edge in edges:
        edge_count += 1
        valid_edges = valid_edges and is_valid_edge(edge)

        if(not (edge[0][0], edge[0][1]) in vertices_dict):
            vertices_dict[(edge[0][0], edge[0][1])] = 1
        else:
            vertices_dict[(edge[0][0], edge[0][1])] += 1
        
        if(not (edge[1][0], edge[1][1]) in vertices_dict):
            vertices_dict[(edge[1][0], edge[1][1])] = 1
        else:
            vertices_dict[(edge[1][0], edge[1][1])] += 1
        
    print("number of edges:" + str(edge_count))
    print("n value:" + str(args.n))

    for key, value in vertices_dict.items():
        if(not(key[0]<= args.n and key[1] <= args.n)): within_limits = False
        if(key[1] == 0 and value == 1): v_on_bottom = True
        if(key[1] == args.n and value == 1): v_on_top = True
        if(value == 2): middle_vertex_count += 1

    print("\n\nWithin limits? " + str(within_limits))
    print("Edge count: " + str(edge_count) + " args.k: " + str(args.k))
    print("v on bottom: " + str(v_on_bottom) + " v on top: " + str(v_on_top))
    print("middle vertex count: " + str(middle_vertex_count) + " len vertices_dict: " + str(len(vertices_dict)))
    print("Valid edges? " + str(valid_edges) + "\n")

    if(within_limits and 
        edge_count <= args.k and 
        v_on_bottom and v_on_top and 
        middle_vertex_count == (len(vertices_dict)-2) and
        valid_edges):
        print("This looks like a valid path...\n")
        global edges_list
        edges_list = edges
        return True
    else:
        print("Sorry buddy, invalid path...\n")
        return False

def is_valid_edge(edge):
    if(abs(edge[0][0] - edge[1][0]) + abs(edge[0][1] - edge[1][1]) == 1):
        return True
    return False

def register_clients(message):
    data = json.loads(message)
    
    role = data.get("role")
    name = data.get("name")

    if(not name or not role):
        return "Please send both name and role (Detector/Tunneler)", role, 412
    elif(not (role == "Tunneler" or role == "Detector")):
        return "Invalid role: please send either Detector or Tunneler", role, 412
    elif(role == "Tunneler" and "reg" in tunneler):
        return "Tunneler role already taken", role, 412
    elif(role == "Detector" and "reg" in detector):
        return "Detector role already taken", role, 412
    
    if(role == "Tunneler"):
        tunneler["reg"] = name
    elif(role == "Detector"):
        detector["reg"] = name
    return "Successfully registered " + role, role, 200

asyncio.run(main())