from virtual_boxes_in_rectangular_diagrams import *
import matplotlib.pyplot as plt
import networkx as nx
from collections import deque

#the input in V is a collection of vertices in a region (virtual box for now, eventually a T) the output is a collection of strands its a list of lists
def build_strands_graph(V):
    # Build adjacency list: vertices connected if they share x or y coordinate
    adjacency = {tuple(v): [] for v in V}
    for i, v1 in enumerate(V):
        for v2 in V[i+1:]:
            if v1[0] == v2[0] or v1[1] == v2[1]:
                adjacency[tuple(v1)].append(tuple(v2))
                adjacency[tuple(v2)].append(tuple(v1))

    visited = set()
    strands = []

    for vertex in adjacency:
        if vertex not in visited:
            # Collect all points in this connected component
            queue = deque([vertex])
            component = []
            while queue:
                current = queue.popleft()
                if current not in visited:
                    visited.add(current)
                    component.append(current)
                    for neighbor in adjacency[current]:
                        if neighbor not in visited:
                            queue.append(neighbor)
            # Order the component by walking from an endpoint
            strand = order_strand(component, adjacency)
            strands.append([list(p) for p in strand])

    return strands

#This one is not working for some reason: 10/01/2025
def order_strand_depreciated(component, adjacency):
    # Build local adjacency for the component
    local_adj = {p: [n for n in adjacency[p] if n in component] for p in component}
    # Find endpoints (degree 1 nodes)
    endpoints = [p for p, neighbors in local_adj.items() if len(neighbors) == 1]
    if not endpoints:
        # This might happen for a cycle (e.g., a closed loop). Just return as is.
        return list(component)
    start = endpoints[0]
    # Walk the strand
    ordered = []
    current = start
    prev = None
    while True:
        ordered.append(current)
        neighbors = [n for n in local_adj[current] if n != prev]
        if not neighbors:
            break
        prev = current
        current = neighbors[0]
    return ordered

def order_strand(component, adjacency):
    # Restrict adjacency to this component
    local_adj = {p: [n for n in adjacency[p] if n in component] for p in component}

    # Check for invalid branching
    for v, nbrs in local_adj.items():
        if len(nbrs) > 2:
            raise ValueError(f"Vertex {v} has degree {len(nbrs)} (branching) — not a strand.")

    # Find endpoints (degree 1 nodes)
    endpoints = [p for p, neighbors in local_adj.items() if len(neighbors) == 1]

    if endpoints:
        # Path strand: start from endpoint
        start = endpoints[0]
    else:
        # Cycle strand: pick arbitrary start
        start = next(iter(component))

    ordered = []
    visited = set()
    current, prev = start, None

    while True:
        ordered.append(current)
        visited.add(current)
        neighbors = [n for n in local_adj[current] if n != prev]

        if not neighbors:
            # End of a path
            break

        next_node = neighbors[0]
        if next_node in visited:
            # We've closed a cycle
            break

        prev, current = current, next_node

    return ordered


def check_no_crossings(vertical_segments, horizontal_segments,where):
        def segments_cross(vertical, horizontal,where):
            (xv, yv1), (_, yv2) = vertical
            (xh1, yh), (xh2, _) = horizontal

            yv_min, yv_max = sorted([yv1, yv2])
            xh_min, xh_max = sorted([xh1, xh2])
            if where=='std':
                return (xh_min <= xv <= xh_max) and (yv_min <= yh <= yv_max)
            
            if where=='std-no-boundary':
                return (xh_min < xv < xh_max) and (yv_min < yh < yv_max)
            
            
            elif where=='horiz-infty':
                return (xh_min>= xv or xv >= xh_max) and (yv_min <= yh <= yv_max)
            
            elif where=='horiz-infty-no-boundary':
                return (xh_min> xv or xv > xh_max) and (yv_min < yh < yv_max)
            
            elif where=='vert-infty':
                return (xh_min <= xv <= xh_max) and (yv_min >= yh or yh >= yv_max)
            
            elif where=='vert-infty-no-boundary':
                return (xh_min < xv < xh_max) and (yv_min > yh or yh > yv_max)
            
            elif where=='horiz-vert-infty':
                return (xh_min>= xv or xv >= xh_max) and (yv_min >= yh or yh >= yv_max)
            
            elif where=='horiz-vert-infty-no-boundary':
                return (xh_min> xv or xv > xh_max) and (yv_min > yh or yh > yv_max)

        for v_seg in vertical_segments:
            for h_seg in horizontal_segments:
                if segments_cross(v_seg, h_seg,where):
                    return False  # Found a crossing  
        return True  # No crossings found
    

def build_strands_in_box(V):
    # Build adjacency list: vertices connected if they share x or y coordinate
    adjacency = {tuple(v): [] for v in V}
    for i, v1 in enumerate(V):
        for v2 in V[i+1:]:
            if v1[0] == v2[0] or v1[1] == v2[1]:
                adjacency[tuple(v1)].append(tuple(v2))
                adjacency[tuple(v2)].append(tuple(v1))

    visited = set()
    strands = []

    for vertex in adjacency:
        if vertex not in visited:
            # Collect all points in this connected component
            queue = deque([vertex])
            component = []
            while queue:
                current = queue.popleft()
                if current not in visited:
                    visited.add(current)
                    component.append(current)
                    for neighbor in adjacency[current]:
                        if neighbor not in visited:
                            queue.append(neighbor)
            # Order the component by walking from an endpoint
            strand = order_strand(component, adjacency)
            strands.append([list(p) for p in strand])
            
    

    return strands

def order_strand(component, adjacency):
    # Build local adjacency for the component
    local_adj = {p: [n for n in adjacency[p] if n in component] for p in component}
    # Find endpoints (degree 1 nodes)
    endpoints = [p for p, neighbors in local_adj.items() if len(neighbors) == 1]
    if not endpoints:
        # This might happen for a cycle (e.g., a closed loop). Just return as is.
        return list(component)
    start = endpoints[0]
    # Walk the strand
    ordered = []
    current = start
    prev = None
    while True:
        ordered.append(current)
        neighbors = [n for n in local_adj[current] if n != prev]
        if not neighbors:
            break
        prev = current
        current = neighbors[0]
    return ordered




def find_horizontal_edges_entering_box(box,V,where):
    [horizontals,verticals]=sort_vertices_into_verticals_and_horizontals(V)
    horizontals_entering=[]
    for horizontal in horizontals:
        left_vertex_in_box_q=check_if_vertex_in_box(horizontal[0],box,where='std') and not check_if_vertex_in_box(horizontal[0],box,where='std-no-boundary') #vertex on boundary
        right_vertex_in_box_q=check_if_vertex_in_box(horizontal[1],box,where='std') and not check_if_vertex_in_box(horizontal[1],box,where='std-no-boundary') #vertex on boundary
        if left_vertex_in_box_q+right_vertex_in_box_q==1: #one end of the horizontal is on the boundary
            horizontals_entering.append(horizontal) 
    return horizontals_entering


##### The function finds vertical edges that intersect the horizontal edges of the virtual box.
# These edges have a vertex that will be in a strand through the box
def find_vertical_edges_entering_box(box,V,where):
    [horizontals,verticals]=sort_vertices_into_verticals_and_horizontals(V)
    verticals_entering=[]
    for vertical in verticals:
        bottom_vertex_in_box_q=check_if_vertex_in_box(vertical[0],box,where='std') and not check_if_vertex_in_box(vertical[0],box,where='std-no-boundary')
        top_vertex_in_box_q=check_if_vertex_in_box(vertical[0],box,where='std') and not check_if_vertex_in_box(vertical[0],box,where='std-no-boundary')
        if top_vertex_in_box_q+bottom_vertex_in_box_q==1:
             verticals_entering.append(vertical)
    return verticals_entering

def sort_vertices_into_verticals_and_horizontals(V):
    V.sort() #This sorts on x-values we will be sorting into tuples the pairs of vertices that share the same x-values 
    it = iter(V)
    verticals=list(list(zip(it, it))) #this gives the vertices of each vertical edge
    verticals.sort() #each vertical edge is a tuple below we change it to a list
    templist=[]
    for vert in verticals:
        vert=list(vert)
        templist.append(vert)
    verticals=templist
    V = sorted(V, key= lambda elem : elem[1], reverse=True)
    it = iter(V)
    # zip the iterator with itself
    horizontals=list(list(zip(it, it))) #this gives the vertices of each horizontal edge
    horizontals.sort() 
    templist=[]
    for vert in horizontals:
        vert=list(vert)
        templist.append(vert)
    horizontals=templist  
    return[horizontals,verticals]

def strand_crossing_graph(box,V,where):
    
    if where=='std':
        where1='std-no-boundary'
    elif where=='horiz-infty':
        where1='horiz-infty-no-boundary'
    elif where=='vert-infty':
        where1='vert-infty-no-boundary'
    elif where=='horiz-vert-infty':
        where1='horiz-vert-infty-no-boundary'   
    else: where1=where
    #if where=='std-no-boundary':
    #    where1='std' 
    horizontals,verticals=sort_vertices_into_verticals_and_horizontals(V)
    vertices_in_box=find_vertices_in_box(box,V,where1) #these will just give vertices on the inside of the box.  We add vertices to the end if they are on the boundary
    strands=build_strands_in_box(vertices_in_box) #these are just the strand parts inside the box we need to add the parts that cross the box as well
    vertical_strands=[]
    horizontal_strands=[]
    for strand in strands:
        if len(strand)==1: #this strand hooks the box
            #print('This box is hooked')
            return []
        else:
            type_of_strand=[1,1] #initization
            #These are the endpoints of the strand
            first_vertex_of_strand=strand[0]
            last_vertex_of_strand=strand[-1]
            
            #Look at the horizontal and vertical adjacent to the first vertex.  
            horizontal_adj_to_first_vertex=[h for h in horizontals if first_vertex_of_strand in h]
            horizontal_adj_to_first_vertex=horizontal_adj_to_first_vertex[0]
            vertical_adj_to_first_vertex=[v for v in verticals if first_vertex_of_strand in v]
            vertical_adj_to_first_vertex=vertical_adj_to_first_vertex[0]
            other_vertex_of_vertical=[z for z in vertical_adj_to_first_vertex if z!=first_vertex_of_strand]
           
            z=other_vertex_of_vertical[0] #vertex on vertical adjacent to the first vertex of the strand
            
            other_vertex_of_horizontal=[w for w in horizontal_adj_to_first_vertex if w!=first_vertex_of_strand]
            w=other_vertex_of_horizontal[0] #vertex on horizontal adjacent to the first vertex of the strand
            
            if check_if_vertex_in_box(w,box,where1)==False and check_if_vertex_in_box(w,box,where)==True :#this vertex is on the boundary
                #in this case the strand will start with the vertex on the box 
                strand.insert(0,w) #add this vertex to the strand
                type_of_strand[0]='V'  #the beginning of this strand has a vertex of a horizontal on the boundary which is adjacent to a vertical
                
            elif check_if_vertex_in_box(w,box,where1)==False and check_if_vertex_in_box(w,box,where)==False: #this vertex is out of the box
                #We do not append this one. The strand then starts truly in the interior of the box
                type_of_strand[0]='H' #the beginning of this strand crosses a horizontal
                strand.insert(0,w) #add this vertex to the strand to get old picture
            elif check_if_vertex_in_box(z,box,where1)==False and check_if_vertex_in_box(z,box,where)==True :#this vertex is on the boundary   
                 #in this case the strand will start with the vertex on the box 
                strand.insert(0,z) #add this vertex to the strand
                type_of_strand[0]='H'  #the beginning of this strand crosses a vertical on the boundary which is adjacent to a horizontal
            else: #this vertex is out of the box
                strand.insert(0,z) #add this vertex to the strand to get old picture
                type_of_strand[0]='V' #otherwise the strand crosses a vertical
            
            #same game for end of strand
            horizontal_adj_to_last_vertex=[h for h in horizontals if last_vertex_of_strand in h]
            horizontal_adj_to_last_vertex=horizontal_adj_to_last_vertex[0]
            other_vertex_of_horizontal=[w for w in horizontal_adj_to_last_vertex if w!=last_vertex_of_strand]
            vertical_adj_to_last_vertex=[v for v in verticals if last_vertex_of_strand in v]
            vertical_adj_to_last_vertex=vertical_adj_to_last_vertex[0]
            other_vertex_of_vertical=[z for z in vertical_adj_to_last_vertex if z!=last_vertex_of_strand]
            z=other_vertex_of_vertical[0]
            other_vertex_of_horizontal=[w for w in horizontal_adj_to_last_vertex if w!=last_vertex_of_strand]
            w=other_vertex_of_horizontal[0]
            
            if check_if_vertex_in_box(w,box,where1)==False and check_if_vertex_in_box(w,box,where)==True :#this vertex is on the boundary
                strand.insert(-1,w) #add this vertex to the strand
                type_of_strand[1]='V'  #the beginning of this strand crosses a horizontal on the boundary which is adjacent to a vertical
            elif check_if_vertex_in_box(w,box,where1)==False and check_if_vertex_in_box(w,box,where)==False: #this vertex is out of the box
                strand.insert(-1,w) #add this vertex to the strand to get old picture
                type_of_strand[1]='H' #the beginning of this strand crosses a horizontal
                
            elif check_if_vertex_in_box(z,box,where1)==False and check_if_vertex_in_box(z,box,where)==True :#this vertex is on the boundary   
                strand.insert(-1,z) #add this vertex to the strand
                type_of_strand[1]='H'  #the beginning of this strand crosses a horizontal on the boundary which is adjacent to a vertical
            else: #this vertex is out of the box
                strand.insert(-1,z) #add this vertex to the strand to get old picture
                type_of_strand[1]='V' #otherwise the strand crosses a vertical
            
            if len(set(type_of_strand))==2: #the strand enters on a V and leaves on a H or vice versa
                print(strand)
                print(set(type_of_strand))
                print('This box is hooked')
                return [] #There is a strand that enters and leaves on V and H 

            #### I have not done anything with these sets yet ##################
            if set(type_of_strand)== {'H'}:
                horizontal_strands.append(strand) #these are the strands that are under
            else:
                vertical_strands.append(strand)   #these are the strands that are over

        
    #Now I want to find the distinguished strand.  The one that has edges on the box.

    distinguished_strand = box #now I am viewing the vertices of the box as a strand.  The distinguished one
    # Reorder the list: put distinguished_strand first, others after
    reordered_strands = [distinguished_strand] + [
        strand for strand in strands]  #this list has the distinquished strand in entry 0

    print('These are the strands in the box',reordered_strands)
    G = build_directed_strand_graph(reordered_strands)
    
    
    
    
    return G #this is a directed graph object with vertex 0 the distinguished strand



def extract_segments(strand):
    """Returns lists: verticals and horizontals from a strand."""
    flattened = [point for point in strand]
    verticals = [[group[i], group[i+1]]for x in set(p[0] for p in flattened)for group in [sorted([p for p in flattened if p[0] == x], key=lambda p: p[1])]for i in range(0, len(group) - 1, 2)]
    flattened = [point for point in strand]
    horizontals = [[group[i], group[i+1]]
    for y in set(p[1] for p in flattened)
    for group in [sorted([p for p in flattened if p[1] == y], key=lambda p: p[0])]
    for i in range(0, len(group) - 1, 2)]
    return verticals, horizontals

def segments_intersect(v_seg, h_seg):
    """Checks whether a vertical and horizontal segment intersect."""
    (vx1, vy1), (vx2, vy2) = v_seg
    (hx1, hy1), (hx2, hy2) = h_seg
    x = vx1
    y = hy1

    #if min(vy1, vy2) <= y <= max(vy1, vy2) and min(hx1, hx2) <= x <= max(hx1, hx2):
    #I think this is what we want? 6/18/2025
    if min(vy1, vy2) < y < max(vy1, vy2) and min(hx1, hx2) < x < max(hx1, hx2):
        return True
    return False



def build_directed_strand_graph(strands):
    G = nx.DiGraph() #initialization
    strand_data = [] #each strand will have horiz and vert edges sorted
    for i, strand in enumerate(strands):
        
        verticals, horizontals = extract_segments(strand)
        strand_data.append((verticals, horizontals))
        #Use index of strand as label 0 will be distinguished
        # Use the first vertex in the strand as label (tuple)
        G.add_node(i, label=str(i))

    for i in range(len(strands)):
        verticals_i = strand_data[i][0] #the vertical segements of current strand 
        for j in range(len(strands)):
            if i == j: #dont compare a strand to itself
                continue
            horizontals_j = strand_data[j][1] #now look at horizontal segments of every strand
            for v in verticals_i: #for each vertical of the current strand 
                for h in horizontals_j: #for each horizontal of each strands 
                    if segments_intersect(v, h): #if v intersects h add an edge
                        G.add_edge(i, j)
                        break #no need to keep looking 
                    else:
                        continue
                    break

    return G

def draw_strand_graph(G):
    pos = nx.circular_layout(G)  
    labels = nx.get_node_attributes(G, 'label')

    plt.figure(figsize=(6,6))
    nx.draw(G, pos, with_labels=False, node_color='skyblue', node_size=1000, 
            edge_color='gray', arrows=True, arrowstyle='-|>')
    nx.draw_networkx_labels(G, pos, labels, font_size=10, font_weight='bold')
    plt.title("Directed Strand Interaction Graph with Vertex Labels")
    plt.show()
    
    
 
def get_quotient_graph(G):
    # Suppose G is your original strand_crossing_graph.  The quotient by cycles is called a condensation I guess
    #On output the vertex 0 will be the distinguished strand
    # Step 1: Condense the graph
    condensed = nx.condensation(G)
    original_mapping = condensed.graph['mapping']  # original → scc node
    scc_of_distinguished = original_mapping[0]

    # Step 2: Relabel so distinguished SCC is node 0
    new_labels = {}
    for old_label in condensed.nodes:
        if old_label == scc_of_distinguished:
            new_labels[old_label] = 0
        elif old_label == 0:
            new_labels[old_label] = scc_of_distinguished
        else:
            new_labels[old_label] = old_label

    condensed = nx.relabel_nodes(condensed, new_labels, copy=True)
    new_mapping = {orig: new_labels[scc] for orig, scc in original_mapping.items()}

    # condensed is a DAG where each node represents an SCC of G
    print("Number of SCCs (nodes in condensation):", condensed.number_of_nodes())

    # This gives a topological order on condensed:
    order = list(nx.topological_sort(condensed))
    print("Topological order of SCCs:", order)

    # Step 3: Prepare SCC labels for plotting
    scc_labels = {}
    for orig_node, scc_node in new_mapping.items():
        scc_labels.setdefault(scc_node, []).append(orig_node)
    labels = {scc: str(sorted(members)) for scc, members in scc_labels.items()}

    # Step 4: Layout and plotting
    pos = nx.circular_layout(condensed)

    plt.figure(figsize=(6, 6))
    nx.draw(condensed, pos, with_labels=False, node_color='lightgreen',
            node_size=1000, edge_color='gray', arrows=True, arrowstyle='-|>')
    nx.draw_networkx_labels(condensed, pos, labels, font_size=10, font_weight='bold')
    plt.title("Condensed Graph with Distinguished Strand as Node 0")
    plt.show()

    return condensed  


######
"""
>>>
G = load_unknot('thistletwaite')
V = grid_to_vertex_set(G)
type1,_=find_all_virtual_boxes(V)
box=type1[-2]
G=strand_crossing_graph(box,V,where='std')
if G: #if the box is hooked G=[]
    draw_virtual_box_diagram(box,V,where='std')
    draw_strand_graph(G)
    quotient_G=get_quotient_graph(G)
    
>>>
#The link below has a wrinkled v_1^b simplification
test=[[1,-3],[1,-5],[2,-6],[2,-14],[3,-4],[3,-12],[4,-3],[4,-10],[5,-5],[5,-7],[6,-6],[6,-8],[7,-7],[7,-9],[8,-2],[8,-11],[9,-10],[9,-14],[10,-11],[10,-13],[11,-1],[11,-12],[12,-2],[12,-8],[13,-9],[13,-13],[14,-1],[14,-4]]
# the link below has a double infinity simplification
test1=[[1,-4],[1,-6],[2,-2],[2,-5],[3,-1],[3,-6],[4,-3],[4,-5],[5,-2],[5,-4],[6,-1],[6,-3]]

#the link below has a type 2 simplification
test2=[[1,-2],[1,-5],[2,-1],[2,-3],[3,-5],[3,-7],[4,-3],[4,-6],[5,-4],[5,-7],[6,-1],[6,-6],[7,-2],[7,-4]]
#Vertex_sets=perform_all_type_1_box_simplifications(test)
knot_7_7=[[1,-1],[1,-8],[2,-2],[2,-10],[3,-5],[3,-7],[4,-1],[4,-9],[5,-4],[5,-6],[6,-3],[6,-5],[7,-7],[7,-10],[8,-4],[8,-8],[9,-2],[9,-6],[10,-3],[10,-9]]

>>>
V=test
type1,_=find_all_virtual_boxes(V)
box= type1[4]
G=strand_crossing_graph(box,V,where='std-no-boundary')
draw_virtual_box_diagram(box,V,where='std')
draw_strand_graph(G)
quotient_G=get_quotient_graph(G)
"""