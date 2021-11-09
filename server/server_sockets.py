import asyncio
import websockets
import argparse
import json
import time
import math
from selenium import webdriver
from selenium.webdriver.common.by import By
import os

# Some default game params
N_DEFAULT = 5
K_DEFAULT = 9
P_DEFAULT = 3
HOSTNAME_DEFAULT = "127.0.0.1"
PORT_DEFAULT = 8081

# Some variables maintaining game state
tunneler = {}
detector = {}
args = None
vertices_dict = {}
edges_list = []
guesses_dict = {"edges": [], "vertices": []}
time_tunneler = 0
time_detector = 0
tunneling_done = False
driver = None

# Main function
async def main():
    global driver

    # Parsing command line args
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", help = "Size of grid", type = int, default = N_DEFAULT)
    parser.add_argument("-k", help = "Max size of tunnel", type = int, default = K_DEFAULT)
    parser.add_argument("-p", help = "Number of detection phases", type = int, default = P_DEFAULT)
    parser.add_argument("--view", help = "View the game on a browser window", action="store_true")
    parser.add_argument("--host", help = "Host IP address of the server", type = str, default = HOSTNAME_DEFAULT)
    parser.add_argument("--port", help = "Host port number", type = int, default = PORT_DEFAULT)
    global args

    args = parser.parse_args()
    print("Done parsing args")
    
    # Notes about visualization:
    # Cannot visualize grid size less than 4
    # For given grid size, the value of max path length is fixed
    if(args.view):
        print("Opening viz")
        driver = webdriver.Firefox(executable_path='../viz/geckodriver')
        driver.get("file:///" + os.getcwd() + "/../viz/iframe.html")
        driver.find_element(By.ID, "grid-size").click()
        driver.find_element(By.ID, "size-" + str(args.n)).click()

        driver.find_element(By.ID, "start-game").click()
        driver.switch_to.alert.accept()

    # Running evaluator forever
    async with websockets.serve(evaluator, args.host, args.port):
        await asyncio.Future()

def draw_tunnel(path, isFinal = False):
    global driver
    print("path was valid, here it is:" + str(path))

    for edge in path["edges"]:
        edge_trans = translate_edge(edge)
        html_id = None
        orientation = h_or_v(edge_trans)
        if(orientation == "hrev"):
            html_id = "hedge-" + str(edge_trans[1][0]) + "-" + str(edge_trans[1][1])
        elif(orientation == "hfwd"):
            html_id = "hedge-" + str(edge_trans[0][0]) + "-" + str(edge_trans[0][1])
        elif(orientation == "vrev"):
            html_id = "vedge-" + str(edge_trans[1][0]) + "-" + str(edge_trans[1][1])
        elif(orientation == "vfwd"):
            html_id = "vedge-" + str(edge_trans[0][0]) + "-" + str(edge_trans[0][1])
        # print("path edge transformed:" + orientation + html_id)
        driver.find_element(By.ID, html_id).click()

    if(not(isFinal)):
        driver.find_element(By.ID, "finished_tunneling").click()
        driver.switch_to.alert.accept()

def draw_guess(guess, round):
    global driver
    for vertex in guess["vertices"]:
        vertex_trans = translate_vertex(vertex)
        html_id = "node-" + str(vertex_trans[0]) + "-" + str(vertex_trans[1])
        driver.find_element(By.ID, html_id).click()

    driver.find_element(By.ID, "finish_round").click()
    

def h_or_v(edge):
    if(edge[0][0] - edge[1][0] == 1):
        return "hrev"
    elif(edge[0][0] - edge[1][0] == -1):
        return "hfwd"
    elif(edge[0][1] - edge[1][1] == 1):
        return "vrev"
    elif(edge[0][1] - edge[1][1] == -1):
        return "vfwd"
    return "e"

def translate_edge(edge):
    edge_trans = []
    for vertex in edge:
        edge_trans.append(translate_vertex(vertex))
    return edge_trans

def translate_vertex(vertex):
    return(vertex[0], args.n - vertex[1])

# Main evaluator function
async def evaluator(websocket, path):
    # Receiving initial communication from client with "name" and "role"
    init_msg = json.loads(await websocket.recv())
    print("Initial message: " + str(init_msg))

    # Sending params to client
    params = json.dumps({"n": args.n, "k": args.k, "p": args.p})
    await websocket.send(params)

    # Establishing role and name of client
    role = init_msg["role"]
    name = init_msg["name"]

    # Declaring time variables to be global
    global time_tunneler, time_detector

    # Tunneler evaluation
    if(role == "Tunneler"):
        global tunneling_done

        while(not tunneling_done):

            # Sending signal for tunneler to start along with args
            start_msg = json.dumps({"canStart": True})
            await websocket.send(start_msg)

            # Calculating time taken for tunneler to send back path
            start = time.time()
            path_msg = json.loads(await websocket.recv())
            end = time.time()
            time_tunneler += end - start
            
            print("Time taken by the tunneler: " + str(time_tunneler))
            print("Message sent by tunneler: " + str(path_msg))

            # Validating path sent by tunneler client
            # If not a valid path, refreshing variables and waiting for another message
            if(path_validate(path_msg)):
                if(args.view):
                    draw_tunnel(path_msg, isFinal=False)
                tunneling_done = True
            else:
                global vertices_dict, edge_list
                vertices_dict = {}
                edge_list = []
            end_msg = json.dumps({"tunneling_done": tunneling_done})
            await websocket.send(end_msg)
        
        print("Tunneling done, no more waiting")

    elif(role == "Detector" and not tunneling_done):
        print("It's the tunneler's turn, cannot detect yet...")

    elif(role == "Detector" and tunneling_done):
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
            return_msg, score = guess_validate_and_score_2(guess)

            if(args.view):
                draw_guess(guess, i)
            #print("Return message:")
            #print(str(return_msg["correct_edges"]))
            #print(str(return_msg["correct_vertices"]))
            final_score += score

            await websocket.send(json.dumps(return_msg))
        
        if(args.view):
            driver.switch_to.alert.accept()
        
        final_guess = json.loads(await websocket.recv())

        correct = valid(final_guess)
        if(args.view):
            draw_tunnel(final_guess, isFinal=True)
            driver.find_element(By.ID, "finish_final_guess").click()

        if(not correct): 
            final_score = math.inf
        print("Hence the final score is: " + str(final_score))

# Checking if the final guess is valid
def valid(final_guess):
    edges_list_copy = [ele for ele in edges_list]
    for guess_edge in final_guess["edges"]:
        for edge in edges_list:
            if(equal_edges(edge, guess_edge)):
                edges_list_copy.remove(edge)
    
    if(edges_list_copy == []):
        return True
    return False

def guess_validate_and_score_2(guess):
    guess_score = 0
    temp = []
    return_msg = {"correct_edges": []}
    if "vertices" in guess:
        valid_vertex_guesses = add_guess_vertices(guess["vertices"])
        guess_score += len(valid_vertex_guesses)

    for guess_vertex in valid_vertex_guesses:
        for edge in edges_list:
            v1 = edge[0]
            v2 = edge[1]
            if(equal_vertices(v1, guess_vertex) or equal_vertices(v2, guess_vertex)):
                temp.append(edge)
    
    for edge in temp:
        already_exists = False
        for correct_edge in return_msg["correct_edges"]:
            if(equal_edges(edge, correct_edge)):
                already_exists = True
                break
        if(not already_exists):
            return_msg["correct_edges"].append(edge)

    return return_msg, guess_score
    

# Considering valid edge and vertex guesses (within range and not guessed before)
def guess_validate_and_score(guess):
    guess_score = 0
    return_msg = {"correct_edges": [], "correct_vertices": []}
    
    
    if "edges" in guess:
        valid_edge_guesses = add_guess_edges(guess["edges"])
        guess_score += len(valid_edge_guesses)
        #print("Valid edge guesses this time: " + str(valid_edge_guesses) + " score: " + str(guess_score))

    if "vertices" in guess:
         valid_vertex_guesses = add_guess_vertices(guess["vertices"])
         guess_score += len(valid_vertex_guesses)
         #print("Valid vertex guesses this time: " + str(valid_vertex_guesses) + " score " + str(guess_score))

    for guess_edge in valid_edge_guesses:
        if(edge_in_path(guess_edge)):
            return_msg["correct_edges"].append(guess_edge)

    for guess_vertex in valid_vertex_guesses:
        if(vertex_in_path(guess_vertex)):
            return_msg["correct_vertices"].append(guess_vertex)

    return return_msg, guess_score

# Check if a guessed vertex is in the path
def vertex_in_path(guess_vertex):
    for edge in edges_list:
        v1 = edge[0]
        v2 = edge[1]
        if(equal_vertices(v1, guess_vertex) or equal_vertices(v2, guess_vertex)):
            return True
    return False 

# Check if a guessed edge is in the path
def edge_in_path(guess_edge):
    for edge in edges_list:
        if(equal_edges(edge, guess_edge)):
            return True
    return False

# Add a valid and non-guessed edge to the list of already guessed edges
def add_guess_edges(guess_edges):
    valid_guesses = []
    for guess_edge in guess_edges:
        if(not already_guessed_edge(guess_edge) and is_valid_edge(guess_edge)):
            valid_guesses.append(guess_edge)
            guesses_dict["edges"].append(guess_edge)
    return valid_guesses

# Add a valid and non-guessed vertex to the list of already guessed edges
def add_guess_vertices(guess_vertices):
    valid_guesses = []
    for guess_vertex in guess_vertices:
        if(not already_guessed_vertex(guess_vertex)):
            valid_guesses.append(guess_vertex)
            guesses_dict["vertices"].append(guess_vertex)
    return valid_guesses

# Check if an edge has already been guessed
def already_guessed_edge(guess_edge):
    for edge in guesses_dict["edges"]:
        if(equal_edges(edge, guess_edge)):
            return True
    return False

# Check if a vertex has already been guessed
def already_guessed_vertex(guess_vertex):
    for vertex in guesses_dict["vertices"]:
        if equal_vertices(guess_vertex, vertex):
            return True
    return False

# Determine if two vertices are equal
def equal_vertices(vertex1, vertex2):
    if(vertex1[0] == vertex2[0] and vertex1[1] == vertex2[1]):
        return True
    return False

# Determine if two edges are equal (order of vertices is irrelevant)
def equal_edges(edge1, edge2):
    if((edge1[0][0] == edge2[0][0] and edge1[0][1] == edge2[0][1]) and 
        (edge1[1][0] == edge2[1][0] and edge1[1][1] == edge2[1][1])):
        return True
    elif((edge1[0][0] == edge2[1][0] and edge1[0][1] == edge2[1][1]) and
        (edge1[1][0] == edge2[0][0] and edge1[1][1] == edge2[0][1])):
        return True
    return False

# Validating path sent by the tunneler
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


    for key, value in vertices_dict.items():
        if(not(key[0]<= args.n and key[1] <= args.n)): within_limits = False
        if(key[1] == 0 and value == 1): v_on_bottom = True
        if(key[1] == args.n and value == 1): v_on_top = True
        if(value == 2): middle_vertex_count += 1

    print("Within limits: " + str(within_limits))
    print("Edge count: " + str(edge_count) + " args.k: " + str(args.k))
    print("Middle vertex count: " + str(middle_vertex_count))
    print("vertices dictionary:" + str(vertices_dict))
    print("valid edges: " + str(valid_edges))
    
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
    if((abs(edge[0][0] - edge[1][0]) + abs(edge[0][1] - edge[1][1]) == 1) and 
        (edge[0][0] >= 0 and edge[1][0] >= 0 and edge[0][1] >= 0 and edge[1][1] >= 0) and 
        (edge[0][0] <= args.n and edge[1][0] <= args.n and edge[0][1] <= args.n and edge[1][1] <= args.n)):
        return True
    return False

asyncio.run(main())