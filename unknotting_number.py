from itertools import combinations
from Full_Unknotting_Algorithm import*
from unknotting_and_generalized_commutations import *
from draw_rectangular_diagram import *
from knot_representations import*
from GridPyM import *
import random 

def verify_unknot_boolean_1(V):
    G = vertexset_to_XOGrid(V)
    braid = convert_to_braid(G, optimized='Y', verbose=False)
    try:
        B = Link(braid_closure=braid)
        # Return True if seifert_genus is 0, else False
        if B.knot_floer_homology()['seifert_genus'] == 0:
            B.simplify('global')
            if len(B.crossings)==0:
                return True
            else:
                return False
        else:
                return False        
    except ValueError:
        return verify_unknot_boolean(V)  # stop at first success or continue for all
     
        
def verify_unknot_boolean(V):
    G = vertexset_to_XOGrid(V)
    braid = convert_to_braid(G, optimized='Y', verbose=False)
    try:
        B = Link(braid_closure=braid)
        B.simplify('pickup')
        if len(B.crossings)==0:
        # Return True if seifert_genus is 0, else False
            return True
        else:
            return False
    except ValueError:
        print('Could not verify')
        return False

def simplify_knot_snappy(V):
    G = vertexset_to_XOGrid(V)
    braid = convert_to_braid(G, optimized='Y', verbose=False)
    try:
        B = Link(braid_closure=braid)
        B.simplify('pickup')
        return B
    except ValueError:
        print('Could not verify')
        return []
    
    
    
def locate_crossings(V):
    horizontals, verticals = sort_vertices_into_verticals_and_horizontals(V)
    crossings = []

    # convert horizontals to interval form
    horizontal_segments = []
    for h in horizontals:
        x1, y = h[0]
        x2, _ = h[1]
        left = min(x1, x2)
        right = max(x1, x2)
        horizontal_segments.append((left, right, y))

    # convert verticals to interval form
    vertical_segments = []
    for v in verticals:
        x, y1 = v[0]
        _, y2 = v[1]
        bottom = min(y1, y2)
        top = max(y1, y2)
        vertical_segments.append((x, bottom, top))

    # test intersections
    for left, right, y in horizontal_segments:
        for x, bottom, top in vertical_segments:
            if left < x < right and bottom < y < top:
                crossings.append([x, y])
                
    crossings.sort(key=lambda p: (p[0], p[1]))
    return crossings  

def locate_crossings_vert_horiz_form_demo(V):
    horizontals, verticals = sort_vertices_into_verticals_and_horizontals(V)
    crossings = []

    # test intersections
    for h in horizontals:
        for v in verticals:
            xvals_of_h=[h[0][0],h[1][0]]
            yval_of_h=h[0][1]
            yvals_of_v=[v[0][1],v[1][1]]
            xval_of_v=v[0][0]
            if min(xvals_of_h) < xval_of_v < max(xvals_of_h) and min(yvals_of_v) < yval_of_h < max(yvals_of_v):
                crossings.append([h, v])
    return crossings  
        
def normalize_vertices(V):
    # remove duplicates
    V = list({tuple(v) for v in V})
    
    # sorted unique coordinates
    xs = sorted({v[0] for v in V})
    ys = sorted({v[1] for v in V}, reverse=True)
    
    # maps using dictionary comprehension
    x_map = {x: i+1 for i, x in enumerate(xs)}
    y_map = {y: -(i+1) for i, y in enumerate(ys)}
    
    # relabel vertices in one line with list comprehension
    V_normalized = [[x_map[v[0]], y_map[v[1]]] for v in V]
    
    # sort by y descending (top to bottom) in-place
    V_normalized.sort(key=lambda v: v[1], reverse=True)
    return V_normalized

def change_crossing(crossing, V):
    x_val = crossing[0] #the x_value of the vertical in the crossing
    y_val = crossing[1] #the y_value of the horizontal in the crossing
    V_shifted = [] 
    for v in V:
        if v[0]== x_val and v[1]>y_val: #if this is the vertical being crossed
            V_shifted.append([v[0]+0.5,v[1]]) #shift the top vertex to the right and keep the y-value
        elif  v[0]== x_val and v[1]<y_val: #if this is the vertical being crossed    
            V_shifted.append([v[0]-0.5,v[1]])
        elif v[1]==y_val and v[0]< x_val: #if you are the vertex to the right
            V_shifted.append([v[0],v[1]+0.5]) #move up by 1 and keep your x-value
        elif v[1]==y_val and v[0]> x_val: #if you are the vertex to the right
            V_shifted.append([v[0],v[1]-0.5]) #move up by 1 and keep your x-value    
        else:
            V_shifted.append(v) 
    new1=[x_val+0.5,y_val]
    new2=[x_val-0.5,y_val]
    new3=[x_val,y_val+0.5]
    new4=[x_val,y_val-0.5]
    list1=[new1,new2,new3,new4]
    V_shifted=V_shifted+list1
    V=normalize_vertices(V_shifted)
    return  V

def change_crossing_and_update_crossings_demo(crossing, crossings, V):
    horizontals, verticals = sort_vertices_into_verticals_and_horizontals(V)
    x_val = crossing[1][0][0]  # vertical x-coordinate
    y_val = crossing[0][0][1]  # horizontal y-coordinate
    V_shifted = []

    # Copy crossings as segments
    horizontals_shifted = [h.copy() for h in horizontals]
    verticals_shifted = [v.copy() for v in verticals]

    for v in V:
        v_after = v[:]
        if v[0] == x_val and v[1] > y_val:  # top of vertical being crossed
            v_after = [v[0]+0.5, v[1]]
        elif v[0] == x_val and v[1] < y_val:  # bottom of vertical being crossed
            v_after = [v[0]-0.5, v[1]]
        elif v[1] == y_val and v[0] < x_val:  # left of horizontal being crossed
            v_after = [v[0], v[1]+0.5]
        elif v[1] == y_val and v[0] > x_val:  # right of horizontal being crossed
            v_after = [v[0], v[1]-0.5]

        V_shifted.append(v_after)

        # Update crossings segments in-place
        for h in horizontals_shifted:
            for i, vert in enumerate(h):
                if vert == v:
                    h[i] = v_after
        for vert_seg in verticals_shifted:
            for i, vert in enumerate(vert_seg):
                if vert == v:
                    vert_seg[i] = v_after

    # Add new vertices for crossing change
    new_vertices = [
        [x_val+0.5, y_val],
        [x_val-0.5, y_val],
        [x_val, y_val+0.5],
        [x_val, y_val-0.5]
    ]
    V_shifted.extend(new_vertices)

    # Normalize vertices
    V_new = normalize_vertices(V_shifted)

    # Now remap the crossings to the normalized vertices
    # Create a dict mapping old vertex -> new normalized vertex
    old_to_new = {tuple(old_v): new_v for old_v, new_v in zip(V_shifted, V_new)}

    horizontals_norm = []
    for h in horizontals_shifted:
        horizontals_norm.append([old_to_new[tuple(h[0])], old_to_new[tuple(h[1])]])

    verticals_norm = []
    for v in verticals_shifted:
        verticals_norm.append([old_to_new[tuple(v[0])], old_to_new[tuple(v[1])]])

    # Combine back into crossings
    #crossings_shifted = list(zip(horizontals_norm, verticals_norm))
    crossings_shifted = [list(tup) for tup in zip(horizontals_norm, verticals_norm)]

    return crossings_shifted, V_new

#The idea is that when performing a crossing change on a rectangular diagram the number of crossings does not actually 
#change.  The number of edges does.  
# The idea behind this is that the index in crossings=locate_crossings(V) does not change between diagrams.  
#So if you do something silly like:

#crossing=crossings[0]
#V1=change_crossing(crossing, V)
#next_crossings=locate_crossings(V1)
#next_crossing=next_crossings[0]
#V2=change_crossing(next_crossing, V1)
#You have just changed back to the same diagram.

def perform_multiple_crossing_changes(V, number_of_changes):
    """
    Try all combinations of crossing changes with sequential flips,
    recomputing crossings after each flip.
    """
    original_V = V.copy()
    crossings = locate_crossings(V)
    k = len(crossings)
    
    if number_of_changes > k:
        raise ValueError("The number_of_changes exceeds number of crossings")
    
    index_combos = [list(c) for c in combinations(range(k), number_of_changes)]
   
    for combo in index_combos:
        #print('Attempting crossing changes on crossings',combo,'(read left to right)')
        V_current = original_V.copy()  # start fresh for each combination
        crossings = locate_crossings(V_current)  # recompute in updated diagram
        for idx in combo:
            crossings, V_current= change_crossing_and_update_crossings(crossings[idx], crossings, V)
            #V_current = change_crossing(crossings[idx], V_current)
        # After full combo, simplify and check
        #V_current=apply_full_simplification(V_current, max_iterations=1)
        VS = All_Virtual_Boxes_Simplification_Updated(V_current)
        V_current = VS[-1]

        # --- Check if unknotted ---
        if len(V_current) // 2 == 2:
            result = f"Original Vertex Set: {original_V}\nCombo: {combo}\n Current Vertex Set:{V_current} \n"
            print(result)
            return True # stop at first success or continue for all
        #else: 
            #print('This combination failed to unknot the diagram')

def perform_multiple_crossing_changes_not_verbose(V, number_of_changes):
    """
    Try all combinations of crossing changes with sequential flips,
    recomputing crossings after each flip.
    """

    original_V = V.copy()
    crossings = locate_crossings(V)
    k = len(crossings)
    crossing_changes_simplified=[]
    
    if number_of_changes > k:
        raise ValueError("The number_of_changes exceeds number of crossings")

    index_combos = [list(c) for c in combinations(range(k), number_of_changes)]

    for combo in index_combos:
        #print('Attempting crossing changes on crossings',combo,'(read left to right)')
        V_current = original_V.copy()  # start fresh for each combination
        for idx in combo:
            crossings = locate_crossings(V_current)  # recompute in updated diagram
            V_current = change_crossing(crossings[idx], V_current)
        #draw_rectangular_diagram(V_current)
        # After full combo, simplify and check
        #B=simplify_knot_snappy(V)
        if verify_unknot_boolean(V_current): 
            result = f"Original Vertex Set: {original_V}\nCombo: {combo}\n Current Vertex Set:{V_current} \n"
            print(result)
            with open("unknot_number_results.txt", "a") as f:
                f.write(result)
            return True  # stop at first success or continue for all
        
    return False

def perform_multiple_crossing_changes_simplified(V, number_of_changes):
    """
    Try all combinations of crossing changes with sequential flips,
    recomputing crossings after each flip.
    """

    original_V = V.copy()
    crossings = locate_crossings(V)
    k = len(crossings)
    crossing_changes_simplified=[]
    
    if number_of_changes > k:
        raise ValueError("The number_of_changes exceeds number of crossings")

    index_combos = [list(c) for c in combinations(range(k), number_of_changes)]

    for combo in index_combos:
        #print('Attempting crossing changes on crossings',combo,'(read left to right)')
        V_current = original_V.copy()  # start fresh for each combination
        for idx in combo:
            crossings = locate_crossings(V_current)  # recompute in updated diagram
            V_current = change_crossing(crossings[idx], V_current)
        #draw_rectangular_diagram(V_current)
        # After full combo, simplify and check
        crossing_changes_simplified.append(simplify_knot_snappy(V_current))
        
    return crossing_changes_simplified


def scrambled_knot_diagrams(V,length,number_unique_diagrams):
    failsafe=number_unique_diagrams*3 #the idea here is maybe there are not that many unique diagrams and I do not want to be stuck
    n=len(V)//2
    unique_diagrams=[]
    count=0
    while count<failsafe:
        commutation_box=find_a_random_generalized_commutation(V)
        #draw_virtual_box_diagram(commutation_box,V,where='std')
        V=perform_commutation(V,commutation_box)
        #print('I am performing a permutation')
        choice_of_infty=[random.randint(1, n),random.randint(-n,-1)]
        #the new vertex set will place the real_corner_vertex at the vertex [1,-1] on the RD.
        which_vertical=random.choice(['left-to-right','right-to-left'])
        which_horizontal=random.choice(['top-to-bottom','bottom-to-top'])
        V=perform_cylic_permutations(V,choice_of_infty[0]-1,choice_of_infty[1]-1,which_vertical,which_horizontal)
        crossings=locate_crossings(V)
        if len(crossings)>length and V not in unique_diagrams:
            #print("Here is the new diagram")
            #draw_rectangular_diagram(V)
            unique_diagrams.append(V)
            count=count+1
            if len(unique_diagrams)==number_unique_diagrams:
                return unique_diagrams
    return unique_diagrams    
    
def braid_scrambled_knot_diagrams(V,number_unique_diagrams):
    G = vertexset_to_XOGrid(V)
    unique_diagrams=[]
    count=0
    while count<number_unique_diagrams:
        Gnew=scramble_grid(G, effort = 'medium', legendrian = False, transverse = False)
        braid = convert_to_braid(Gnew, optimized='N', verbose=False)
        unique_diagrams.append(Braid_to_RD(braid))
        count=count+1
    return unique_diagrams    
        
    
import ast
def knot_atlas_to_grid_diagram(knot):
    s = str(knot).replace("{", "[").replace("}", "]")
    L=ast.literal_eval(s)
    firsts=[l[0]-1 for l in L]
    seconds=[l[1]-1 for l in L]
    return [firsts,seconds]
    
"""G=[[11,0,8,1,7,10,9,2,3,4,5,6],[1,7,2,3,9,8,11,4,5,6,10,0]]
Knot_10_8=grid_to_vertex_set(G)
draw_rectangular_diagram(Knot_10_8) #This 10 crossing knot has unknotting number 2 but minimal crossing diagram has unknotting number 3 
V=Knot_10_8
crossings=locate_crossings(V)
print('these are the for the 10_8 knot',crossings)
V1=change_crossing(crossings[3], V)
crossings1=locate_crossings(V1)
draw_rectangular_diagram(V1)
print('these are the crossings for the 10_8_knot after one crossing change',crossings1)
V2=change_crossing(crossings1[7], V1)
print('these are the crossings for the 10_8_knot after two crossing changes')
draw_rectangular_diagram(V2)"""