from itertools import combinations
from shapely.geometry import Point, Polygon
import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict
from virtual_boxes_in_rectangular_diagrams import *
from topological_ordering import *
from v1b_reduced_algorithm import get_v1b_reduced_diagram
from snowplow_gates_sorting_simplifications import perform_v1b_corner_rigid_simplifications
from rechoosing_infinity import *
from GridPyM import *
from rectangular_diagram_manipulation import *
from drawing_rectangular_diagrams_src.draw_rectangular_diagram import *
#from New_T_Method import check_for_hinge_Ts_and_simplify




###### Step 1: Find all possible horizontal exit disks ###########  
#The function below will generate every horizontal exit disk.  First by taking every possible fixed half y-value and every pair of half x_values (see horizontal_exit_disks list).  Then each exit disk (or mouth) is checked to ensure that it is the ''smallest'' i.e. it actually has verticals exactly 1/2 distance into each end of the mouth. The output of this function is then all horizonal mouths that have vertical edges of RD directly inside either end of the mouth. The output of this function is then all horizonal mouths that have vertical edges of RD directly inside either end of the mouth.

def find_all_possible_exit_disks(V):
    #The output of this function will be all horizonal mouths that have vertical edges of RD directly inside either end of the mouth.
    n = len(V) // 2
    horizontals,verticals=sort_vertices_into_verticals_and_horizontals(V)
    #half_x_val = [i + 0.5 for i in range(0,n)]  
    #half_y_val = [-x for x in half_x_val]
   
    half_x_val = [i + 0.5 for i in range(0,n+1)]  
    half_y_val = [-x for x in half_x_val]
   
    # Build all possible vertex points
    all_vertices = [[x, y] for x in half_x_val for y in half_y_val]
    # Horizontal segments: same y, different x
    horizontal_exit_disks = []
    for y in half_y_val:
        xs = [x for x in half_x_val]
        horizontal_exit_disks += [[[x1, y], [x2, y]] for x1, x2 in combinations(xs, 2)]
       

    horizontal_exit_disks1 = []
    for horizontal_disk in horizontal_exit_disks:
        x_min,x_max=sorted([horizontal_disk[0][0],horizontal_disk[1][0]])
        if int(x_max-x_min)>1: #if the exit disk is width 1 we dont want it
            y_val=horizontal_disk[0][1]
            intersecting_verticals=[]
            for vertical in verticals:
                vertical.sort()
                if vertical[0][1]<y_val<vertical[1][1] and x_min<vertical[0][0]<x_max:
                    intersecting_verticals.append(vertical)
            if intersecting_verticals:
                right_vert=max([vertical[0][0] for vertical in intersecting_verticals])  
                left_vert=min([vertical[0][0] for vertical in intersecting_verticals])
        #This requires that this mouth is the ''smallest'' i.e. it actually has verticals exactly 1/2 distance into each end of the mouth.  
                if int(x_min+0.5)==left_vert and int(x_max-0.5)==right_vert:
                    horizontal_exit_disks1.append(horizontal_disk)

    horizontal_exit_disks=horizontal_exit_disks1
    return horizontal_exit_disks  

##### Step 2: Given a horizontal exit disk, determine if this corresponds to a T.#####

#The next two functions take an exit disk and look at the strands (above it) that cross it.  If any strand crosses it twice it is added to the strands_in_T list. Towards the bottom of this function 3 additional conditionals are checked, including if it is ''essential'' that is, it does not contain the horizontal directly above (below) the upward (downward) mouth. The output of this function is either [[],[]] or a vaild exit disk and its strands set, [horizontal_disk,strands_in_T].  Linking must later be detected using the generate_strands_graph_for_T function.

def upward_T_generation(horizontal_disk,V):
   
    n = len(V) // 2
    horizontals,verticals=sort_vertices_into_verticals_and_horizontals(V)
   
    y_val_of_disk = horizontal_disk[0][1]
    x_start, x_end = sorted([horizontal_disk[0][0], horizontal_disk[1][0]])
 
    strands_in_T=[]
    strands_crossing_mouth=[]
   
    #1) Find the vertices above the horizontal disk:
    vertices_above_disk=[v for v in V if v[1]>y_val_of_disk]
    if not vertices_above_disk:
        return [[],[],[]] #There must be vertices above the disk

    #2) Now connect these vertices as strands
    strands=build_strands_graph(vertices_above_disk)

    #3) The end points of the strands will be vertices above the disk incident to vertical edges that cross the y-val.  We want to know if they cross the disk
    for strand in strands:
       
        one_end_vertex=strand[0]
        other_end_vertex=strand[-1]
        vertical_crossing_one_end=[vertical for vertical in verticals if one_end_vertex in vertical]
        vertical_crossing_one_end=vertical_crossing_one_end[0]#flattening
       
        vertical_crossing_other_end=[vertical for vertical in verticals if other_end_vertex in vertical]
        vertical_crossing_other_end=vertical_crossing_other_end[0]#flattening
       
       
        #both these verticals must either cross the exit disk or be disjoint from it
        x_val_of_vertical = vertical_crossing_one_end[0][0]
        y_start, y_end = sorted([vertical_crossing_one_end[0][1],vertical_crossing_one_end[1][1]])
        crossed1=False
        crossed2=False

        if y_start < y_val_of_disk < y_end and x_start < x_val_of_vertical < x_end:
            crossed1 = True
           
        x_val_of_vertical = vertical_crossing_other_end[0][0]
        y_start, y_end = sorted([vertical_crossing_other_end[0][1],vertical_crossing_other_end[1][1]])
        if y_start < y_val_of_disk < y_end and x_start < x_val_of_vertical < x_end:
            crossed2 = True
       
        if (crossed1== True and crossed2== True):#this strand is in the T and contributes two punctures
            strands_in_T.append(strand)  #if you have a valid T at the end this should be double the punctures
       
        if (crossed1==True and crossed2==False) or (crossed1==False and crossed2==True) :#XOR so if crossed once
            strands_crossing_mouth.append(strand)  #if you have a valid T at the end this should be double the punctures    
           
    if not strands_in_T:
        return[[],[],[]]
   
   
    # We will run through some preliminary conditionals to ensure that this will result in a T region.
    verts_of_all_strands = []
    for strand in strands_in_T:
        verts_of_all_strands.extend(strand)

    #I am going to check a bunch of conditionals now:
    #1)This ensures that the width of the exit disk is as small as possible. It has edges of strands in T at half values inside each end of mouth.
    narrowest_T= False
    #2) This ensures that it doesnt just grab top two horizontal edges of diagram etc.
    not_full_subdiagram=False
    #3) This ensures that the horizontal directly above (below) mouth of T is not in the T.
    essential_T=False
    #4) Longest neck
    longest_neck=False
    

    #For the parts of the strands that are in the x-support of the mouth we want to ensure that the leftmost and rightmost values are near the edge of the mouth
    restricted_verts_of_strand=[v for v in verts_of_all_strands if x_start< v[0]<x_end]
    x_left=min([v[0] for v in restricted_verts_of_strand])
    x_right=max([v[0] for v in restricted_verts_of_strand])
    if int(x_start+0.5)==x_left and int(x_end-0.5)==x_right: #this requires that actual strands in T define its shape.
        narrowest_T=True



    if len(verts_of_all_strands)<len(vertices_above_disk): #your T did not just grab some whole part of the diagram
        not_full_subdiagram=True

    horizontal_just_above_T=[h for h in horizontals if h[0][1]== int(y_val_of_disk+0.5)]
    horizontal_just_above_T=horizontal_just_above_T[0] #flattening
    x_left, x_right = sorted([horizontal_just_above_T[0][0],horizontal_just_above_T[1][0]])
    if horizontal_just_above_T[0] and horizontal_just_above_T[1] not in verts_of_all_strands:
        #essential_T=True
       
        if x_right < x_start or x_end<x_left: #the horizontal just above exit disk is disjoint from exit disk width
            essential_T=True
        elif x_left<x_start<x_end<x_right: #the horizontal just above has larger x-support than the exit disk (its behind it)
            essential_T=True
            
    horizontal_just_below_T=[h for h in horizontals if h[0][1]== int(y_val_of_disk-0.5)]
    horizontal_just_below_T=horizontal_just_below_T[0] #flattening
    horizontal_xs=sorted([v[0] for v in horizontal_just_below_T])
    
    if (horizontal_xs[0] < x_start< horizontal_xs[1]<x_end) or (x_start<horizontal_xs[0]<x_end<horizontal_xs[1]): #the horizontal just above exit disk is disjoint from exit disk width
        longest_neck=True
   
    #print('[narrowest_T,not_full_subdiagram,essential_T]=', [narrowest_T,not_full_subdiagram,essential_T])
    if narrowest_T+not_full_subdiagram+essential_T+longest_neck==4: #if all conditionals are met
        return [horizontal_disk,strands_in_T,strands_crossing_mouth]
    return[[],[],[]]  
   
#Now given a horizontal_exit_disk we must form a proposed T.
def downward_T_generation(horizontal_disk,V):
   
    n = len(V) // 2
    horizontals,verticals=sort_vertices_into_verticals_and_horizontals(V)
   
    y_val_of_disk = horizontal_disk[0][1]
    x_start, x_end = sorted([horizontal_disk[0][0], horizontal_disk[1][0]])
 
    #We are checking for a T that opens downward now
    strands_in_T=[]
    strands_crossing_mouth=[]
    #1) Find the vertices above the horizontal disk:
    vertices_below_disk=[v for v in V if v[1]<y_val_of_disk]
    if not vertices_below_disk:
        return [[],[],[]]
    #2) Now connect these vertices
    strands=build_strands_graph(vertices_below_disk)
    #3) The end points of the strands will be vertices above the disk incident to vertical edges that cross the y-val.  We want to know if they cross the disk
    for strand in strands:
        one_end_vertex=strand[0]
        other_end_vertex=strand[-1]
        vertical_crossing_one_end=[vertical for vertical in verticals if one_end_vertex in vertical]
        vertical_crossing_one_end=vertical_crossing_one_end[0]#flattening
        vertical_crossing_other_end=[vertical for vertical in verticals if other_end_vertex in vertical]
        vertical_crossing_other_end=vertical_crossing_other_end[0]#flattening
        #both these verticals must either cross the exit disk or be disjoint from it
        x_val_of_vertical = vertical_crossing_one_end[0][0]
        y_start, y_end = sorted([vertical_crossing_one_end[0][1],vertical_crossing_one_end[1][1]])
        crossed1=False
        crossed2=False
       
        if y_start < y_val_of_disk < y_end and x_start < x_val_of_vertical < x_end:
            crossed1 = True
           
        x_val_of_vertical = vertical_crossing_other_end[0][0]
        y_start, y_end = sorted([vertical_crossing_other_end[0][1],vertical_crossing_other_end[1][1]])
        if y_start < y_val_of_disk < y_end and x_start < x_val_of_vertical < x_end:
            crossed2 = True
           
        if (crossed1== True and crossed2== True):#this strand is in the T and contributes two punctures
            strands_in_T.append(strand)  #if you have a valid T at the end this should be double the punctures
       
        if (crossed1==True and crossed2==False) or (crossed1==False and crossed2==True) :#XOR so if crossed once
            strands_crossing_mouth.append(strand)  #if you have a valid T at the end this should be double the punctures    
   
    if not strands_in_T:
        return[[],[],[]]        
    # We will run through some preliminary conditionals to ensure that this will result in an essential T.
    verts_of_all_strands = []
    for strand in strands_in_T:
        verts_of_all_strands.extend(strand)        
   
    #I am going to check a bunch of conditionals now see above description
    narrowest_T= False
    not_full_subdiagram=False
    essential_T=False
    #4) Longest neck
    longest_neck=False

    restricted_verts_of_strand=[v for v in verts_of_all_strands if x_start< v[0]<x_end]
    x_left=min([v[0] for v in restricted_verts_of_strand])
    x_right=max([v[0] for v in restricted_verts_of_strand])
    if int(x_start+0.5)==x_left and int(x_end-0.5)==x_right: #this requires that actual strands in T define its shape.
        narrowest_T=True


    if len(verts_of_all_strands)<len(vertices_below_disk): #your T did not just grab some whole part of the diagram
        not_full_subdiagram=True

    horizontal_just_below_T=[h for h in horizontals if h[0][1]== int(y_val_of_disk-0.5)]
    horizontal_just_below_T=horizontal_just_below_T[0] #flattening
    x_left, x_right = sorted([horizontal_just_below_T[0][0],horizontal_just_below_T[1][0]])
   
    if horizontal_just_below_T[0] and horizontal_just_below_T[1] not in verts_of_all_strands:
        #essential_T=True

        if x_right < x_start or x_end<x_left: #the horizontal just below exit disk is disjoint from exit disk width
            essential_T=True
        elif x_left<x_start<x_end<x_right: #the horisontal just below has larger x-support than the exit disk (its behind it)
            essential_T=True
            
    horizontal_just_above_T=[h for h in horizontals if h[0][1]== int(y_val_of_disk+0.5)]
    horizontal_just_above_T=horizontal_just_above_T[0] #flattening
    horizontal_xs=sorted([v[0] for v in horizontal_just_above_T])
    
    if (horizontal_xs[0] < x_start< horizontal_xs[1]<x_end) or (x_start<horizontal_xs[0]<x_end<horizontal_xs[1]): #the horizontal just above exit disk is disjoint from exit disk width
        longest_neck=True
           
    #print('[narrowest_T,not_full_subdiagram,essential_T]=', [narrowest_T,not_full_subdiagram,essential_T])
    if narrowest_T+not_full_subdiagram+essential_T+longest_neck==4: #if all conditionals are met
         return [horizontal_disk,strands_in_T,strands_crossing_mouth]
    return[[],[],[]]



##### Step 3: Now we must determine the actual dimensions of this T using the strands_in_T and mouth ######

###The function below does this.  It returns a list of 8 vertices (called octagon) which defines the boundary of the T.  Important note: The first two vertices of the octagon (aka boundary of the T) correspond to the mouth of the T. ####

def generate_full_T(exit_disk,strands_in_T):
    # Collect all strand points
    strand_points = []
    for strand in strands_in_T:
        strand_points.extend(strand)
    # We are only considering horizontal exit disks:
           
    if strand_points[0][1]>exit_disk[0][1]: #its an upper T
        # Extract exit_disk y value and make sure it's ordered
        vy = exit_disk[0][1]
        vx_left = max(exit_disk[0][0], exit_disk[1][0])
        vx_right = min(exit_disk[0][0], exit_disk[1][0])

        # Get extreme values
        xs = [p[0] for p in strand_points]
        ys = [p[1] for p in strand_points]

        min_x = min(xs)
        max_x = max(xs)
        min_y = min(ys)
        max_y = max(ys)

        # Fit to half-grid
        min_x_h = min_x - 0.5
        max_x_h = max_x + 0.5
        min_y_h = min_y - 0.5
        max_y_h = max_y + 0.5




        # Define octagon points in CCW order
        octagon = [
            [vx_right,      vy],       # left edge of exit disk
            [vx_left,      vy],         # right edge of exit disk
            [vx_left, min_y_h],          
            [min_x_h, min_y_h],        
            [min_x_h, max_y_h],      
            [max_x_h, max_y_h],        
            [max_x_h, min_y_h],        
            [vx_right, min_y_h],        
            [vx_right,      vy],        
        ]
           
           
    elif strand_points[0][1]<exit_disk[0][1]: #its a lower T  
        # Extract exit_disk y value and make sure it's ordered
        vy = exit_disk[0][1]
        vx_left = max(exit_disk[0][0], exit_disk[1][0])
        vx_right = min(exit_disk[0][0], exit_disk[1][0])

        # Get extreme values
        xs = [p[0] for p in strand_points]
        ys = [p[1] for p in strand_points]

        min_x = min(xs)
        max_x = max(xs)
        min_y = min(ys)
        max_y = max(ys)

        # Fit to half-grid
        min_x_h = min_x - 0.5
        max_x_h = max_x + 0.5
        min_y_h = min_y - 0.5
        max_y_h = max_y + 0.5




        # Define octagon points in CCW order
        octagon = [
            [vx_right,      vy],       # left edge of exit disk
            [vx_left,       vy],        
            [vx_left, max_y_h],          
            [min_x_h, max_y_h],        
            [min_x_h, min_y_h],      
            [max_x_h, min_y_h],        
            [max_x_h, max_y_h],        
            [vx_right, max_y_h],        
            [vx_right,      vy],        
        ]



    else: raise TypeError("This T is not recognized")
    return octagon

### Begin_T Checking code

def find_all_T_regions(V):
    T_regions=[]
    mouths=find_all_possible_exit_disks(V)
    for mouth in mouths:
        [horizontal_disk_up,strands_in_T_up,strands_crossing_disk_up]=upward_T_generation(mouth,V)
        [horizontal_disk_down,strands_in_T_down,strands_crossing_disk_down]=downward_T_generation(mouth,V)
        if horizontal_disk_up:
            boundary_of_T=generate_full_T(horizontal_disk_up,strands_in_T_up)
            #draw_virtual_T_diagram(boundary_of_T, V)
            T_regions.append([horizontal_disk_up,strands_in_T_up,strands_crossing_disk_up])
        if horizontal_disk_down:
            boundary_of_T=generate_full_T(horizontal_disk_down,strands_in_T_down)
            #draw_virtual_T_diagram(boundary_of_T, V)
            T_regions.append([horizontal_disk_down,strands_in_T_down,strands_crossing_disk_down])
    return T_regions


def valid_T_check(G):
    # Step 1: Condense the graph and invert SCC mapping
    condensed = nx.condensation(G)
    mapping = condensed.graph['mapping']  # original_node → scc_index
   
    scc_to_nodes = {}
    for node, scc in mapping.items():
        scc_to_nodes.setdefault(scc, []).append(node)
   
    # Step 2: Relabel 'I' nodes based on SCC content
    new_labels = {}

    used_O_indices = set(n[1] for n in G.nodes if n[0] == 'O')
    used_M_indices = set(n[1] for n in G.nodes if n[0] == 'M')
    next_O_index = max(used_O_indices, default=-1) + 1
    next_M_index = max(used_M_indices, default=-1) + 1

    for scc_idx, nodes in scc_to_nodes.items():
        contains_O = any(n[0] == 'O' for n in nodes)
        contains_M = any(n[0] == 'M' for n in nodes)

        if contains_O:
            for n in nodes:
                if n[0] == 'I':
                    while next_O_index in used_O_indices:
                        next_O_index += 1
                    new_labels[n] = ('O', next_O_index)
                    used_O_indices.add(next_O_index)
                    next_O_index += 1
                else:
                    new_labels[n] = n
        elif contains_M:
            for n in nodes:
                if n[0] == 'I':
                    while next_M_index in used_M_indices:
                        next_M_index += 1
                    new_labels[n] = ('M', next_M_index)
                    used_M_indices.add(next_M_index)
                    next_M_index += 1
                else:
                    new_labels[n] = n
        else:
            for n in nodes:
                new_labels[n] = n  # unchanged

    # Step 3: Relabel the graph
    G_new = nx.relabel_nodes(G, new_labels, copy=True)
    #print('You are in valid T check, and here is G_new')
    #draw_strand_graph(G_new)
   
    # Step 4: Topological sort the relabeled graph
    def get_topo_order(GX):
        condensed_new = nx.condensation(GX)
        new_mapping = condensed_new.graph['mapping']
        new_scc_to_nodes = {}
        for node, scc in new_mapping.items():
            new_scc_to_nodes.setdefault(scc, []).append(node)

        topo_order_sccs = list(nx.topological_sort(condensed_new))
        order = []
        for scc in topo_order_sccs:
            order.extend(sorted(new_scc_to_nodes[scc]))
        return order

    topo_order_original = get_topo_order(G_new)
    #print('You are in valid T check, and here is top order')
    #print(topo_order_original)
    # Step 5: Check for 'O' appearing before any 'I'
    seen_O = set()
    for v in topo_order_original:
        if v[0] == 'O':
            seen_O.add(v)
        elif v[0] == 'I' and seen_O:
            #Debugging 11/21/2025
            #print('There is an O before an I!')
            # Relabel v as an 'O' node with a new unused index
            while next_O_index in used_O_indices:
                next_O_index += 1
            new_label = ('O', next_O_index)
            nx.relabel_nodes(G_new, {v: new_label}, copy=False)
            used_O_indices.add(next_O_index)
            next_O_index += 1
            #break
            #Debugging
            #return False, []  

    # Step 5.5: Check for 'M' appearing before any 'I'
    topo_order_original = get_topo_order(G_new)  # refresh after relabel Does this take step 5 into account?
    seen_M = set()
    for v in topo_order_original:
        if v[0] == 'M':
            seen_M.add(v)
        elif v[0] == 'I' and seen_M:
            # Relabel v as an 'M' node with a new unused index
            while next_M_index in used_M_indices:
                next_M_index += 1
            new_label = ('M', next_M_index)
            nx.relabel_nodes(G_new, {v: new_label}, copy=False)
            used_M_indices.add(next_M_index)
            next_M_index += 1
            #break
            #return False, []

    # Step 6: Get any remaining 'I' nodes (in G_new)
    remaining_I_vertices = [n for n in G_new.nodes if n[0] == 'I']
    if remaining_I_vertices:
        #print('these are the remaining inside vertices',remaining_I_vertices)
        return True, remaining_I_vertices
    else:
        #print('Not a valid T')
        return False, []  
 
def get_topo_order(GX):
    condensed_new = nx.condensation(GX)
    new_mapping = condensed_new.graph['mapping']
    new_scc_to_nodes = {}
    for node, scc in new_mapping.items():
        new_scc_to_nodes.setdefault(scc, []).append(node)

    topo_order_sccs = list(nx.topological_sort(condensed_new))
    order = []
    for scc in topo_order_sccs:
        order.extend(sorted(new_scc_to_nodes[scc]))
    return order
   
   
def find_all_valid_Ts(T_regions,V):
    valid_Ts=[]
    for i in range(len(T_regions)):
        exit_disk=T_regions[i][0]
        strands_in_T=T_regions[i][1]
        strands_crossing_mouth=T_regions[i][2]
        boundary_of_T=generate_full_T(exit_disk,strands_in_T)
        #draw_virtual_T_diagram(boundary_of_T, V)
        G,number_of_distinguished_strands,number_of_strands_crossing_mouth,ordered_strands=generate_strands_graph_for_T(exit_disk,strands_in_T,strands_crossing_mouth,V)
        #draw_strand_graph(G)
        boolean,I=valid_T_check(G)
        if boolean==True:
            indices=[i for (_,i) in I]
            inside_strands=[ordered_strands[j] for j in indices]
            #print('these are the inside strands',inside_strands)
            inside_vertices = []
            for strand in inside_strands:
                inside_vertices.extend(strand)
            #print('these are the inside strands')
            #print(inside_strands)
           
            horizontals,verticals=sort_vertices_into_verticals_and_horizontals(V)
            #12/09/2025 SETH: RIGHT HERE INSTEAD OF APPENDING THIS T, GENERATE THE SMALLER T WITH THE INSIDE VERTICES
            #New exit disk is +- 1/2 rightmost and leftmost stands of T
            y_val_of_disk=exit_disk[0][1]
            x_start, x_end = sorted([exit_disk[0][0], exit_disk[1][0]])
           
            #draw_virtual_T_diagram(boundary_of_T, V)
   
            verticals_crossing_mouth=[]
            #3) The end points of the strands will be vertices above the disk incident to vertical edges that cross the y-val.  We want to know if they cross the disk
            for strand in inside_strands:
                one_end_vertex=strand[0]
                other_end_vertex=strand[-1]
                vertical_crossing_one_end=[vertical for vertical in verticals if one_end_vertex in vertical]
                vertical_crossing_one_end=vertical_crossing_one_end[0]#flattening
                vertical_crossing_other_end=[vertical for vertical in verticals if other_end_vertex in vertical]
                vertical_crossing_other_end=vertical_crossing_other_end[0]#flattening
                #both these verticals must either cross the exit disk or be disjoint from it
                x_val_of_vertical = vertical_crossing_one_end[0][0]
                y_start, y_end = sorted([vertical_crossing_one_end[0][1],vertical_crossing_one_end[1][1]])
                crossed1=False
                crossed2=False
                if y_start < y_val_of_disk < y_end and x_start < x_val_of_vertical < x_end:
                    verticals_crossing_mouth.append(vertical_crossing_one_end)
                x_val_of_vertical = vertical_crossing_other_end[0][0]
                y_start, y_end = sorted([vertical_crossing_other_end[0][1],vertical_crossing_other_end[1][1]])
                if y_start < y_val_of_disk < y_end and x_start < x_val_of_vertical < x_end:
                    verticals_crossing_mouth.append(vertical_crossing_other_end)  
            #strands in T are the inside_strands (may need to do some parsing making sure these objects are the same)
            #print('these are verticals crossing mouth: ',verticals_crossing_mouth)
            # Extract all x-values
            x_vals = [pair[0] for sublist in verticals_crossing_mouth for pair in sublist]
            # Get min and max
            min_x = min(x_vals)
            max_x = max(x_vals)
            new_exit_disk=[[min_x-0.5,y_val_of_disk],[max_x+0.5,y_val_of_disk]]
            #print('this is the original exit disk', exit_disk)
            #print('this is the new exit disk;',new_exit_disk)
            #Now currently inside_strands has the vertex that is outside of the T and crosses the exit disk.  We have to get rid of that
            in_original_T=vertices_inside_T(boundary_of_T, V)
            inside_vertices=[v for v in inside_vertices if v in in_original_T] #this takes the inside_vertices(which includes the edge crossing disk and intersects it with only the vertices in the T
            #print('these are the inside vertices',inside_vertices)
            new_strands=build_strands_graph(inside_vertices)
            boundary_of_new_T=generate_full_T(new_exit_disk,new_strands)
            #print('this is the new T')
            #draw_virtual_T_diagram(boundary_of_new_T, V)
            valid_Ts.append([boundary_of_new_T,inside_vertices]) #the inside vertices are the same
    return valid_Ts
   
###### Auxillary #######

#The input to this function should be an exit_disk and strands_in_T list that was passed from upward_T_generation(mouth,V) or  downward_T_generation(mouth,V).  The output is the strands crossing graph and the number of distinguished strands.  These can be plotted using draw_strand_graph(G)

### You might need to return empty if the T is pierced? You will need then the strand_type.  

def generate_strands_graph_for_T(exit_disk,strands_in_T,strands_crossing_mouth,V):
    horizontals,verticals=sort_vertices_into_verticals_and_horizontals(V)
   
    T_strand_points = []
    for strand in strands_in_T:
        T_strand_points.extend(strand)
   
    T_mouth_points = []
    for strand in strands_crossing_mouth:
        T_mouth_points.extend(strand)
   
    boundary_of_T=generate_full_T(exit_disk,strands_in_T)
   
    #find all vertices inside the T and not just the strands crossing the exit disk
    all_vertices_in_T=vertices_inside_T(boundary_of_T, V) #These are just the vertices inside the T

    all_strands=build_strands_graph(all_vertices_in_T) #These are just parts of the strands entirely inside the T.  You need to add the parts of the strands (additional vertices) that cross the boundary of the T as well.
    #Note: We want to be sure that strands_in_T do not link with parts of other strands as they enter and leave the T so we must add the horizontal/vertical edges of the strands that enter the T but are not the distinguished strands.
     
    for strand in all_strands:
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
        skip_other_end=False
        #Note: If you need to know the way the strands enter the T you can add a 'type' here.  See commented out below
        type_of_strand=[1,1]
        if w not in all_vertices_in_T: #this vertex is out of the T so the strand enters T on a horizontal
            type_of_strand[0]='H'
            strand.insert(0,w) #add this vertex to the strand

        elif z not in all_vertices_in_T: #this vertex is out of the T so the strand enters T on a vertical
            type_of_strand[0]='V'
            strand.insert(0,z) #add this vertex to the strand

        elif w in all_vertices_in_T and z in all_vertices_in_T: #this occurs when there is a link component entirely within the T
            print("There is a connected component within this T")
            draw_virtual_T_diagram(boundary_of_T, V)
            print("connected component:", strand)
            skip_other_end=True
            
        else:
             #Debugging
            print("DEBUGGING")
            draw_virtual_T_diagram(boundary_of_T, V)
            print("DEBUG Strand:", strand)
            #print("first_vertex:", first_vertex_of_strand)
            print("last_vertex:", last_vertex_of_strand)
            print("w the other vertex of the horizontal:", w, "in T?", w in all_vertices_in_T)
            print("is w not in the strand set?", w not in strand)
            print("z the other vertex of vertical:", z, "in T?", z in all_vertices_in_T)
            print("is z not in the strand set?", z not in strand)
            print("T boundary:", boundary_of_T)
            raise TypeError("There is an issue with the strands") #9/29/2025: putting in a link threw this error.
        if skip_other_end==False:
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

            #the not in strand condition is needed if there is a single vertex in the T
            if w not in all_vertices_in_T and w not in strand: #this vertex is out of the T so the strand exits T on a horizontal
                type_of_strand[1]='H'
                strand.insert(-1,w) #add this vertex to the strand
            elif z not in all_vertices_in_T and z not in strand: #this vertex is out of the T so the strand exits T on a vertical
                type_of_strand[1]='V' #the beginning of this strand crosses a horizontal
                strand.insert(-1,z) #add this vertex to the strand

             # If you have a link and you have a single vertex of that link not in the T, then it is the beginnning of the strand and then when you come to the end of the strand, that vertex (which is truly (geometrically) outside but has been added to the strand set so now it is in the strand) to fix this we add this conditional:
            elif w not in all_vertices_in_T and w in strand: #then you have a link component almost in the T and w was orginally not in the T but was added because it was the start of a strand.
                type_of_strand[1]='H'
                strand.insert(-1,w) #add this vertex to the strand
            #if the end of strand is adjacent to the vertex in the start of the strand you have "caught" a link component
            #Condition 1 for links
            elif z not in all_vertices_in_T and z in strand: #this vertex is geometrically out of the T so the strand exits T on a vertical
                type_of_strand[1]='V' #the beginning of this strand crosses a horizontal
                strand.insert(-1,z) #add this vertex to the strand
       
            #Condition 2 for links    
            #elif w not in all_vertices_in_T and w not in strand: #this vertex is out of the T so the strand exits T on a horizontal
            #    type_of_strand[1]='H'
            #    strand.insert(-1,w) #add this vertex to the strand

            else:
                #Debugging
                print("DEBUGGING PROBLEM 2")
                draw_virtual_T_diagram(boundary_of_T, V)
                print("DEBUG Strand:", strand)
                #print("first_vertex:", first_vertex_of_strand)
                print("last_vertex:", last_vertex_of_strand)
                print("w the other vertex of the horizontal:", w, "in T?", w in all_vertices_in_T)
                print("is w not in the strand set?", w not in strand)
                print("z the other vertex of vertical:", z, "in T?", z in all_vertices_in_T)
                print("is z not in the strand set?", z not in strand)
                print("T boundary:", boundary_of_T)
                raise TypeError("There is an issue with the strands") #9/29/2025: putting in a link threw this error.

            #if len(set(type_of_strand))==2: #the strand enters on a V and leaves on a H or vice versa
            #    hooking_strands.append(strand)
       
   
    distinguished_strands=[]
    for strand in all_strands:
        if any(v in strand for v in T_strand_points):
            distinguished_strands.append(strand)
   
    strands_crossing_mouth=[]
    for strand in all_strands:
        if any(v in strand for v in T_mouth_points):
            strands_crossing_mouth.append(strand)
                           
    if not distinguished_strands: #if all of them have been hooked. #Depreciated! Due to above comment out
        number_of_distinguished_strands=0 # I am making a graph that will yield a non-valid T in the valid T check
        number_of_strands_crossing_mouth=0
        G = nx.DiGraph()
        return G,number_of_distinguished_strands,number_of_strands_crossing_mouth
       
   
    number_of_strands_crossing_mouth=len(strands_crossing_mouth)
    #inside all_strands are the distintinguished strands crossing the exit disk strands_in_T
    number_of_distinguished_strands=len(distinguished_strands)
   
    # We do not need to worry about how the strands_in_T are crossing the T we care about their linking inside. See note above
    ordered_strands = distinguished_strands + [strand for strand in all_strands if (strand not in distinguished_strands and strand not in strands_crossing_mouth)]+strands_crossing_mouth
   
    #I want ordered_strands returned so that if I have a valid T, the (I, index) will tell me the index of the strand(s) in ordered_strands that is in the T.
   
   
    G=build_directed_strand_graph(ordered_strands,number_of_distinguished_strands,number_of_strands_crossing_mouth)
   
    return G,number_of_distinguished_strands,number_of_strands_crossing_mouth,ordered_strands





##### This is the function that actually builds the strand interaction graph ########
def build_directed_strand_graph(strands, num_disting_strands, num_over_strands):
    G = nx.DiGraph()  # Initialize directed graph
    n = len(strands)
    strand_data = []
    label_map = {}  # Map from index to consistent node labels

    for i, strand in enumerate(strands):
        verticals, horizontals = extract_segments(strand)
        strand_data.append((verticals, horizontals))

        # Assign node labels
        if i < num_disting_strands:
            label = ('I', i)
        elif i >= n - num_over_strands:
            label = ('O', i)
        else:
            label = ('M', i)
           
       
        label_map[i] = label
        G.add_node(label)

    # Add directed edges: from under to over
    for i in range(n):
        verticals_i = strand_data[i][0]
        for j in range(n):
            if i == j:
                continue
            horizontals_j = strand_data[j][1]
            for v in verticals_i:
                for h in horizontals_j:
                    if segments_intersect(v, h):
                        G.add_edge(label_map[j], label_map[i])  # j points to i
                        break
                else:
                    continue
                break  # Stop checking after first intersection

    return G


#### Auxilliary of Auxilliary lol ####

def vertices_inside_T(boundary_of_T, V):
    # Create polygon from boundary (assumes boundary is closed — last point equals first)
    polygon = Polygon(boundary_of_T)

    # Check which vertices lie inside the polygon
    inside_vertices = [v for v in V if polygon.contains(Point(v))]

    return inside_vertices



def draw_strand_graph(G):
    pos = nx.circular_layout(G)  
    labels = nx.get_node_attributes(G, 'label')

    plt.figure(figsize=(6,6))
    nx.draw(G, pos, with_labels=True, node_color='skyblue', node_size=1000,
            edge_color='gray', arrows=True, arrowstyle='-|>')
    nx.draw_networkx_labels(G, pos, labels, font_size=10, font_weight='bold')
    plt.title("Directed Strand Interaction Graph with Vertex Labels")
    plt.show()  
   
   
   
#DRAW THE T function
def draw_virtual_T_diagram(octagon, V):
    from matplotlib import pyplot as plt
    import numpy as np
    def _distance_markings(A, B, J):
        for I in range(len(B)):
            if A[J] == B[I]:
                return I - J  

    def rectangulardiagram_to_orientedrectangulardiagram(V):
        tuple_V = []
        for v in V:
            v = tuple(v)
            tuple_V.append(v)
        V = tuple_V    
        oriented_vertex_set = [V[0] + (0,)]
        V.pop(0)
        while V:
            xindex = [j for j in range(len(V)) if (V[j][0] == oriented_vertex_set[-1][0])]
            yindex = [j for j in range(len(V)) if (V[j][1] == oriented_vertex_set[-1][1])]
            if xindex:
                oriented_vertex_set.append(V[xindex[0]] + ((oriented_vertex_set[-1][2] + 1) % 2,))
                V.pop(xindex[0])
            elif yindex:
                oriented_vertex_set.append(V[yindex[0]] + ((oriented_vertex_set[-1][2] + 1) % 2,))
                V.pop(yindex[0])
            else:
                first_vertex = V[0]
                oriented_vertex_set.append(first_vertex + (0,))
                V.remove(first_vertex)
        return oriented_vertex_set

    def vertexset_to_XOGrid(V):
        V1 = rectangulardiagram_to_orientedrectangulardiagram(V)
        output = sorted(V1, key=lambda x: x[-1])
        X = [(output[i][0], output[i][1]) for i in range(len(output)) if output[i][2] == 0]
        X = sorted(X, key=lambda x: x[-1])
        Xlist = [X[i][0] - 1 for i in range(len(X))]
        O = [(output[i][0], output[i][1]) for i in range(len(output)) if output[i][2] == 1]
        O = sorted(O, key=lambda x: x[-1])
        Olist = [O[i][0] - 1 for i in range(len(O))]
        G = [Xlist, Olist]
        return G
    G = vertexset_to_XOGrid(V)
   
   
    color = 'black'
    A = G[0]
    B = G[1]
    n = len(A)
    plt.figure(figsize=(7, 7))  # Increase the figure size to 15x15 inches
    for j in range(n + 1):
        plt.plot([j, j], [0, n], 'k-', lw=0.1)
        plt.plot([0, n], [j, j], 'k-', lw=0.1)
        if j != n and color != 0:
            plt.plot([B[j] + 1 / 2, A[j] + 1 / 2], [j + 1 / 2, j + 1 / 2], color=color)
            plt.plot([A[j] + 1 / 2, A[j] + 1 / 2], [j + 1 / 2, j + 1 / 2 + _distance_markings(A, B, j)], color=color)

    # Define the vertices of the rectangle as a list of (x, y) tuples
    tuple_box = []
    V_by_y = sorted(V, key=lambda x: x[1])
    vertical_shift = -V_by_y[0][1] + 0.5
    for v in octagon: #the sorting has been done already so we commented that out
        tuple_box.append((v[0] - 0.5, v[1] + vertical_shift))  # Shift the y-coordinate
        x_coords = [v[0] for v in tuple_box]
        y_coords = [v[1] for v in tuple_box]

    # Plot the points and connect them with lines
    #plt.plot(x_coords, y_coords, linestyle='-',color='purple',alpha=0.3)

    # Fill the region enclosed by the lines
    #plt.fill(x_coords, y_coords, color='purple',alpha=0.3)
    # Plot the filled region as before
    plt.fill(x_coords, y_coords, color='purple', alpha=0.3)

    # Plot all the edges in purple (light)
    for i in range(len(tuple_box)):
        x0, y0 = tuple_box[i]
        x1, y1 = tuple_box[(i + 1) % len(tuple_box)]
        if i == 0:
            # Draw first edge (between first two vertices) in red
            plt.plot([x0, x1], [y0, y1], color='red', linewidth=2)
        else:
            # Draw other edges in light purple
            plt.plot([x0, x1], [y0, y1], color='purple', alpha=0.3)
    plt.axis('off')
    plt.axis('equal')
    plt.show()


##### performing the T isotopy! ##########
#the input valid_T is an element of the valid_Ts=find_all_valid_Ts(T_regions,V) list.  It is a list of lists, a valid_T= [boundary_of_T,inside_vertices]

#the inside vertices are the vertices of the strands that are inside the T.
#the input valid_T is an element of the valid_Ts=find_all_valid_Ts(T_regions,V) list.  It is a list of lists, a valid_T= [boundary_of_T,inside_vertices]

#the inside vertices are the vertices of the strands that are inside the T.
# At the start the inside_vertices are the vertices of the strands that are inside the T.


def perform_T_move_isotopy(valid_T,V):
    #Getting the required dimensions of the T.
    boundary_of_T=valid_T[0]
    inside_vertices=valid_T[1] #the inside vertices actually contain the vertices directly outside the T that have an edge cross into the T. So this will have to be cleaned
    mouth_of_T=[boundary_of_T[0],boundary_of_T[1]] #by construction the boundary of the T always has the first two vertices the exit disk
    
    #You will have to update the mouth after this so that it is added to the "not allowed mouths"
    mouth_x_left, mouth_x_right = sorted([mouth_of_T[0][0], mouth_of_T[1][0]])
    y_values = [y for _, y in boundary_of_T]
    min_y = min(y_values)
    max_y = max(y_values)
    y_value_of_wings_of_T=min([y for _, y in boundary_of_T[2:]])
    top_of_T=max_y
    bottom_of_T=min_y
    x_values = [x for x, _ in boundary_of_T]
    T_x_left = min(x_values)
    T_x_right = max(x_values)
    width_of_wings=int(T_x_right-mouth_x_right)
    
    all_verts_inside=vertices_inside_T(boundary_of_T, V)
    verts_from_inside_strands=[v for v in all_verts_inside if v in inside_vertices] #these are the vertices are parts of inside strands
    #print('these are the vertices from the inside strands:',verts_from_inside_strands)
    
    all_verts_outside=[v for v in V if v not in all_verts_inside]
    
    #first we want to push out any vertices that are under the 'wings' of the T.
    
    #first we want to push out any vertices that are under or over the 'wings' of the T.
    verts_to_push=[v for v in all_verts_outside if (T_x_left<v[0]<mouth_x_left or mouth_x_right<v[0]<T_x_right)]
    #print('these are the vertices under the wings of the T',verts_to_push)
    
    _,verticals=sort_vertices_into_verticals_and_horizontals(V)
    verticals = [v for v in verticals if any(w in verts_to_push for w in v)]
    #print('These are all the verticals in verts to push',verticals)
    
    
    
    
    
    perform_horizontal_push=False
    
    updated_all_verts_inside=[]
    updated_verts_from_inside_strands=[]
    
    if verts_to_push:
        perform_horizontal_push=True

        for vertical in verticals:
            if (vertical[0] in all_verts_inside and vertical[1] in all_verts_outside) or (vertical[0] in all_verts_outside and vertical[1] in all_verts_inside):
                #9/29/2025: rather than not performing any maybe remove this vertical from the list of verticals to be pushed?
                #print('this vertical is causing issues',vertical)
                #print('I will remove it')
                verts_to_push=[v for v in verts_to_push if v not in vertical]
 #10/12/2025 SETH YOU UNCOMMENTED THE LINE BELOW THIS. It changed the isotopy class by skipping hooks and changing crossing number.         
                perform_horizontal_push=False
                #print("perform_horizontal_push is set to false")
   ## End conditional check

    if perform_horizontal_push==True: 
        target_edge_left=[[int(T_x_left+0.5),-1],[int(T_x_left+0.5),-1]] #I just need the proper x-value
        target_edge_right=[[int(T_x_right-0.5),-1],[int(T_x_right-0.5),-1]] #I just need the proper x-value
        #print('these are the target edges look just at x-vals:',target_edge_left,target_edge_right)

        verticals = [v1 for v1 in verticals if all(v in verts_to_push for v in v1)]
        #print('I will push these verticals past the target edge',verticals)
        #verticals = [v1 for v1 in verticals if T_x_left<v1[0][0]<T_x_right and not any(v in verts_to_push ]
        verticals.sort(key=lambda v: v[0][0], reverse=False)

        right_commute_verticals=[]
        left_commute_verticals=[]

        for vertical in verticals:
            if vertical[0][0]>mouth_x_right:
                right_commute_verticals.append(vertical)
            else:
                left_commute_verticals.append(vertical)


        #the edges must be sorted properly to pass to perform_vertical_commutation function
        right_commute_verticals.sort(key=lambda v: v[0][0])
        left_commute_verticals.sort(key=lambda v: v[0][0])

        #The pushing we are about to do will change the coordinates of all_verts_inside and verts_from_inside_strands we need to update these 
        #sets as well to use for the next isotopy.
        updated_all_verts_inside=[]
        updated_verts_from_inside_strands=[]
        updated_mouth_of_T=[]

        if left_commute_verticals:
            for vertex in all_verts_inside:
                count=0
                for vertical in left_commute_verticals:
                    if vertical[0][0]>vertex[0]:
                        count=count+1       
                updated_all_verts_inside.append([vertex[0]+count,vertex[1]])  
                 
                #This updates the mouth
                if vertex in mouth_of_T:
                    updated_mouth_of_T.append([vertex[0]+count,vertex[1]])
           
            #same game for verts_from_inside_strands                         
            for vertex in verts_from_inside_strands:
                count=0
                for vertical in left_commute_verticals:
                    if vertical[0][0]>vertex[0]:
                        count=count+1
                updated_verts_from_inside_strands.append([vertex[0]+count,vertex[1]])  


            V=perform_vertical_commutation(left_commute_verticals,target_edge_left,V)
  
        #Now we update the vertex sets to pass to the next step 
        if updated_all_verts_inside:
            all_verts_inside=updated_all_verts_inside
        if updated_verts_from_inside_strands:     
            verts_from_inside_strands=updated_verts_from_inside_strands  
        if updated_mouth_of_T:
            mouth_of_T=updated_mouth_of_T

        updated_all_verts_inside=[]
        updated_verts_from_inside_strands=[]
        updated_mouth_of_T=[]

        if right_commute_verticals:
            #print('there are right_commute_verticals')
            #now vertices in all_verts_inside will be pushed back if they have verticals to the left of them. So we will update this too.     
            for vertex in all_verts_inside:
                count=0
                for vertical in right_commute_verticals:
                    if vertical[0][0]<vertex[0]:
                        count=count+1
                updated_all_verts_inside.append([vertex[0]-count,vertex[1]])
                
                #This updates the mouth
                if vertex in mouth_of_T:
                    updated_mouth_of_T.append([vertex[0]-count,vertex[1]])
            #same game for verts_from_inside_strands                         

            for vertex in verts_from_inside_strands:
                count=0
                for vertical in right_commute_verticals:
                    if vertical[0][0]<vertex[0]:
                        count=count+1
                updated_verts_from_inside_strands.append([vertex[0]-count,vertex[1]])             

            V=perform_vertical_commutation(right_commute_verticals,target_edge_right,V)
    
    
        #Now we update the vertex sets to pass to the next step 
        if updated_all_verts_inside:
            all_verts_inside=updated_all_verts_inside
        if updated_verts_from_inside_strands:     
            verts_from_inside_strands=updated_verts_from_inside_strands
        if updated_mouth_of_T:
            mouth_of_T=updated_mouth_of_T

#The rest is isotoping the strands just above or below the exit disk so it will not have to change the height of the exit disk.### 

    #second we want to push all vertices that are in the T but not part of the strands up. (assuming T is upward)
    verts_to_push=[v for v in all_verts_inside if v not in verts_from_inside_strands]
    #print('These are the verts_to_push:',verts_to_push)
    
    if not verts_to_push: #there are no strands that are inside.  We will just perform the isotopy taking the inside strands near the exit disk
        #print('there are no inside vertices to remove')
        #print('these are the vertices from the strands', verts_from_inside_strands)
        #print('We will just perform the isotopy taking the inside strands near the exit disk')
        # group by y
        groups = defaultdict(list)
        for x, y in verts_from_inside_strands:
            groups[y].append([x, y])

        ## pair into list of lists with list comprehension
        horizontals = [[vs[i], vs[i+1]] 
                           for vs in groups.values() if len(vs) == 2 
                           for i in range(0, len(vs), 2)]
        #The pairing len(vs)==2 may be an issue
        horizontals.sort(key=lambda v: v[0][1], reverse=True)
        #print('these are the horizontals I will push',horizontals)
 
        if verts_from_inside_strands[0][1]>mouth_of_T[0][1]: #its an upward T
            #print('its an upward T')
            above_mouth=int(mouth_of_T[0][1]+0.5) 
            target_edge=[[0,above_mouth],[0,above_mouth]] 
            #print('the target edge is', target_edge)
        else:#its a downward T
            #print('its an downward T')
            below_mouth=int(mouth_of_T[0][1]-0.5)
            target_edge=[[0,below_mouth],[0,below_mouth]] #I just need the proper y-value.    
        V=perform_horizontal_commutation(horizontals,target_edge,V)
        
        return V,mouth_of_T
    #Now there may be an obstruction to the isotopy below.  A horizontal edge may intersect the T, in which case pushing the horizontals will not work. 
    
    horizontals,_=sort_vertices_into_verticals_and_horizontals(V)
    
    perform_vertical_push=False
    
    if verts_to_push:
        perform_vertical_push=True

        for horizontal in horizontals:
            if (horizontal[0] in all_verts_inside and horizontal[1] in all_verts_outside) or (horizontal[0] in all_verts_outside and horizontal[1] in all_verts_inside):
                perform_vertical_push=False
   ## End conditional check
    
    if perform_vertical_push==True:
        #print('there are inside vertices to push up')
        #print('these are the vertices to push',verts_to_push)
        groups = defaultdict(list)
        for x, y in verts_to_push:
            groups[y].append([x, y])

        ## pair into list of lists with list comprehension
        horizontals = [[vs[i], vs[i+1]] 
                           for vs in groups.values() if len(vs) == 2 
                           for i in range(0, len(vs), 2)]
         #this may be an issue! See above too.
        #The pairing len(vs)==2 may be an issue

        horizontals.sort(key=lambda v: v[0][1], reverse=True)
        #horizontals,_=sort_vertices_into_verticals_and_horizontals(V)
        #horizontals = [h for h in horizontals if any(v in verts_to_push for v in h)]
        #horizontals = [h for h in horizontals if all(v in verts_to_push for v in h)] #troubleshooting
        horizontals.sort(key=lambda v: v[0][1], reverse=True)
        #print('these are the horizontals of the strands inside the T to be pushed',horizontals)


        if verts_to_push[0][1]>mouth_of_T[0][1]: #its an upward T
            #print('its an upward T')
            above_T=int(top_of_T-0.5) 
            #above_T=int(top_of_T+0.5) 
            target_edge=[[0,above_T],[0,above_T]] 
            #print('the target edge is',target_edge)
            #print('these are the updated horizontals of the strands inside the T',horizontals)
        else:#its a downward T
            #print('its an downward T')
            below_T=int(bottom_of_T+0.5)
            target_edge=[[0,below_T],[0,below_T]] #I just need the proper y-value... it may be -0.5 i forget    
            #print('the target_edge is:',target_edge)

        if horizontals:
            V_old=V
            V=perform_horizontal_commutation(horizontals,target_edge,V)
            if V!=V_old:
                return V,mouth_of_T
        
      
    #If you cannot push the horizontals out, and you have a valid T. Then the horizontals in the strands in T can commute to the exit disk.
    #We perform this now.
    #9/5/2025 even if you can do this.  You still want to push the horizontals down to the exit disk! That is why I commented out the above return. 
    # group by y
    groups = defaultdict(list)
    for x, y in verts_from_inside_strands:
        groups[y].append([x, y])

    ## pair into list of lists with list comprehension
    horizontals = [[vs[i], vs[i+1]] 
                       for vs in groups.values() if len(vs) == 2 
                       for i in range(0, len(vs), 2)]
    #The pairing len(vs)==2 may be an issue
    horizontals.sort(key=lambda v: v[0][1], reverse=True)
    #print('these are the horizontals I will push',horizontals)

    if verts_from_inside_strands[0][1]>mouth_of_T[0][1]: #its an upward T
       # print('its an upward T')
        above_mouth=int(mouth_of_T[0][1]+0.5) 
        target_edge=[[0,above_mouth],[0,above_mouth]] 
       # print('the target edge is', target_edge)
    else:#its a downward T
        #print('its an downward T')
        below_mouth=int(mouth_of_T[0][1]-0.5)
        target_edge=[[0,below_mouth],[0,below_mouth]] #I just need the proper y-value.    
    V=perform_horizontal_commutation(horizontals,target_edge,V)

    return V,mouth_of_T
   

def perform_push_T_move_and_v1b_reduce(V):
    seen_diagrams=[V]
    if len(V)//2!=2:
        valid_switch = 1
        invalid_exit_disks = []
        continue_switch = 0

        while valid_switch == 1:
            valid_switch = 0

            if continue_switch == 0:
                T_regions = find_all_T_regions(V)
                valid_Ts = find_all_valid_Ts(T_regions, V)

            if valid_Ts:
                # Filter out those whose exit disks are already invalid
                filtered_Ts = []
                for T in valid_Ts:
                    boundary = T[0]
                    exit_disk = [boundary[0], boundary[1]]
                    if exit_disk not in invalid_exit_disks:
                        filtered_Ts.append(T)

                # If every T had an invalid exit disk, break out — no further simplification is possible
                if not filtered_Ts:
                    print("All remaining T-moves correspond to previously invalid exit disks. Exiting T-move loop.")
                    break

                valid_switch = 1
                continue_switch = 0

                # Pick the first T's strand set and find the smallest exit disk among those
                strands_in_T = filtered_Ts[0][1]
                candidates = [T for T in filtered_Ts if T[1] == strands_in_T]
                
                
                ########################## 6/1/2025 #################################
                widths = [abs(t[0][0][0] - t[0][1][0]) for t in candidates]
                min_width = min(widths)
                best_Ts = [t for t in candidates if abs(t[0][0][0] - t[0][1][0]) == min_width]
                
                def boundary_height(T):
                    ys = [point[1] for point in T[0]]
                    return max(ys) - min(ys)

                best_T = max(best_Ts, key=boundary_height) #this is the smallest mouth among those the longest T
               
                
                #####################################################################
                # Choose the T with the smallest horizontal mouth
                #best_T = min(candidates,key=lambda t: abs(t[0][0][0] - t[0][1][0]))
                boundary_of_T = best_T[0]
                exit_disk = [boundary_of_T[0], boundary_of_T[1]]
                
                

                print('A valid and essential T has been found:')
                #print('The mouth of the T is:', exit_disk)
                #print('strands_in_T:', strands_in_T)
                draw_virtual_T_diagram(boundary_of_T, V)

                V_pushed, mouth_of_T = perform_T_move_isotopy(best_T, V)
                V = V_pushed
                invalid_exit_disks.append(mouth_of_T)
                

                #print('The T move isotopy has been performed')
                #print('This exit disk has been added to invalid exit disks:', mouth_of_T)
                #draw_rectangular_diagram(V_pushed)
                draw_T_and_rectangular_diagram(V_pushed, mouth_of_T)
                if V not in seen_diagrams:
                    #computationally expensive but covers a lot of bases
                    V=perform_v1b_corner_rigid_simplifications(V)
                    #easier computationally
                    #VS=get_v1b_reduced_diagram(V)
                    #V=VS[-1]
                else:
                    print('This rectangular diagram has been seen before, attempting to find another valid and essential push T')
                seen_diagrams.append(V)
            else:
                # No valid T's at all → stop
                break
    return V, seen_diagrams, invalid_exit_disks


def simplify_across_all_cyclic_permutations(V):
    rotations = 0

    while True:
        n = len(V) // 2

        # Already the unknot
        if n == 2:
            print("The diagram is unknotted")
            draw_rectangular_diagram(V)
            return V

        reduced = False

        for h in range(n):
            for v in range(n):
                print(f"Checking cyclic permutation: horizontal={h}, vertical={v}")

                V_new,_,_ = perform_push_T_move_and_v1b_reduce(copy.deepcopy(V))

                # Success: complexity dropped
                if len(V_new) // 2 < n:
                    print(f"Complexity reduced from {n} to {len(V_new)//2}")
                    draw_rectangular_diagram(V_new)

                    V = V_new
                    rotations = 0      # New diagram: search all orientations again
                    reduced = True
                    break

                # Continue searching from the simplified diagram
                V = vertical_cyclic_permutation_1(
                    V_new, which="left-to-right"
                )

            if reduced:
                break

            # Move to the next horizontal cyclic permutation
            V = horizontal_cyclic_permutation_1(
                V_new, which="top-to-bottom"
            )

        if reduced:
            continue

        # No reduction in this orientation
        if rotations == 3:
            print("No simplifying T-move found.")
            draw_rectangular_diagram(V)
            return V

        print("Attempting rotation")
        V = rotate_vertex_set_90_ccw(V)
        rotations += 1
   
