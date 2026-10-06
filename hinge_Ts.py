from v1b_reduced_algorithm import get_v1b_reduced_diagram,check_type_1_box_for_simplification,shift_vertex_set
from snowplow_gates_sorting_simplifications import perform_v1b_corner_rigid_simplifications
from rechoosing_infinity import *
from rectangular_diagram_manipulation import *
from drawing_rectangular_diagrams_src.draw_rectangular_diagram import *
from drawing_rectangular_diagrams_src.draw_type_2_boxes import *
from GridPyM import *
from snappy import *

#9/27/2026: You are verifying still an unknot after both types of hinge Ts. Comment out this check when done. Also you are not doing snowplows and hinge simplification checks after each T just v1b reduced.  You can fix that too see commented part.

#9/27/2026: I fixed an issue with hinge Ts elevatoring indefinitely. Currently it checks both the current diagram V and the exit disk to be sure that they have not both been done before. 

### THIS FUNCTION ALLOWS FOR T's to have  a top at any y level #############
def find_all_possible_top_Ts(V):
    n = len(V) // 2
    half_x = [i + 0.5 for i in range(0, n+1)]
    ys = [-i - 0.5 for i in range(1, n)]  # candidate bottom y-values for the neck

    Ttops = []
    _, verticals = sort_vertices_into_verticals_and_horizontals(V)

    # all admissible top y-values (floating T-top)
    #top_y_levels = [-i - 0.5 for i in range(1, n)]  # can adjust range if needed
    top_y_levels = [-i - 0.5 for i in range(0, n)]  # can adjust range if needed

    for top_y in top_y_levels:
        for i, x in enumerate(half_x):
            for x1 in half_x[i + 2:]:
                for y in ys:
                    if y >= top_y:
                        continue  # bottom cannot be above or at top

                    # Build candidate T-top
                    Ttop = [[x, top_y], [x, y], [x1, top_y], [x1, y]]

                    # Check narrowest neck: at least one vertical adjacent to x and x1 inside the T
                    verticals_near_xs = [
                        v for v in verticals
                        if (v[0][0] == x + 0.5 or v[0][0] == x1 - 0.5 or
                            v[1][0] == x + 0.5 or v[1][0] == x1 - 0.5)
                        and (min(v[0][1], v[1][1]) < top_y)  # vertical reaches below top
                    ]

                    if len(verticals_near_xs) < 2:
                        continue  # cannot form a valid narrow-neck T-top

                    # Verify that these verticals have vertices inside Ttop
                    valid_verticals = 0
                    for v in verticals_near_xs[:2]:  # check first two
                        if check_if_vertex_in_box(v[0], Ttop, where='std') or \
                           check_if_vertex_in_box(v[1], Ttop, where='std'):
                            valid_verticals += 1
                    if valid_verticals < 2:
                        continue  # both sides of neck need to touch T-top

                    # Check that the b-arc region is well-layered
                    verts_crossing_b_arc_region = find_vertices_in_box(Ttop, V, where='horiz-infty')
                    boolean1 = check_type_1_box_for_simplification(Ttop, V, where='horiz-infty')

                    # Ensure no vertical crosses the box (trivially well-layered)
                    verticals_crossing_box = [
                        v for v in verticals
                        if (v[0] in verts_crossing_b_arc_region) ^ (v[1] in verts_crossing_b_arc_region)
                    ]

                    if boolean1 and not verticals_crossing_box:
                        Ttops.append(Ttop)

    return Ttops

def find_all_possible_bottom_Ts(V):
    n = len(V) // 2
    half_x = [i + 0.5 for i in range(0, n+1)]
    ys = [-i - 0.5 for i in range(0, n)]  # candidate bottom y-values for the neck

    Tbots = []
    _, verticals = sort_vertices_into_verticals_and_horizontals(V)

    # all admissible top y-values (floating T-top)
    bottom_y_levels = [-i - 0.5 for i in range(1, n)]  # can adjust range if needed

    for bottom_y in bottom_y_levels:
        for i, x in enumerate(half_x):
            for x1 in half_x[i + 2:]:
                for y in ys:
                    if y <= bottom_y:
                        continue  # top cannot be above or at bottom

                    # Build candidate T-bot
                    Tbot = [[x, bottom_y], [x, y], [x1,bottom_y], [x1, y]]

                    # Check narrowest neck: at least one vertical adjacent to x and x1 inside the T
                    verticals_near_xs = [
                        v for v in verticals
                        if (v[0][0] == x + 0.5 or v[0][0] == x1 - 0.5 or
                            v[1][0] == x + 0.5 or v[1][0] == x1 - 0.5)
                        and (min(v[0][1], v[1][1]) > bottom_y)  # vertical reaches above bottom
                    ]

                    if len(verticals_near_xs) < 2:
                        continue  # cannot form a valid narrow-neck T-bot

                    # Verify that these verticals have vertices inside Tbot
                    valid_verticals = 0
                    for v in verticals_near_xs[:2]:  # check first two
                        if check_if_vertex_in_box(v[0], Tbot, where='std') or \
                           check_if_vertex_in_box(v[1], Tbot, where='std'):
                            valid_verticals += 1
                    if valid_verticals < 2:
                        continue  # both sides of neck need to touch T-bot

                    # Check that the b-arc region is well-layered
                    verts_crossing_b_arc_region = find_vertices_in_box(Tbot, V, where='horiz-infty')
                    boolean1 = check_type_1_box_for_simplification(Tbot, V, where='horiz-infty')

                    # Ensure no vertical crosses the box (trivially well-layered)
                    verticals_crossing_box = [
                        v for v in verticals
                        if (v[0] in verts_crossing_b_arc_region) ^ (v[1] in verts_crossing_b_arc_region)
                    ]

                    if boolean1 and not verticals_crossing_box:
                        Tbots.append(Tbot)

    return Tbots


def find_all_essential_hinge_Ts(V):
    n = len(V) // 2
    horizontals, verticals = sort_vertices_into_verticals_and_horizontals(V)
    
    #If you uncomment the next line, and comment out the one below it it will only do hinges at the top of the diagram
    #Ttops=find_all_possible_top_Ts_depreciated(V) #these are trivially well-layered through horizontal infinity at top of diagram
    
    Ttops=find_all_possible_top_Ts(V) #these are trivially well-layered through horizontal infinity.
    upper_hinge_Ts = [] # all possible half-integer y-levels in the diagram
    #Notice it does not go to the bottom of the diagram.  Since we are looking for Ttops with top value of -0.5 this would just be a cyclic permutation
    #all_y_levels = [-i - 0.5 for i in range(1, n-1)]
    all_y_levels = [-i - 0.5 for i in range(0, n+1)]

    for Ttop in Ttops:
        xs = [v[0] for v in Ttop]
        ys = [v[1] for v in Ttop]

        x = min(xs)
        x1 = max(xs)
        y_top = max(ys)
        bot_of_Ttop = min(ys)

        # possible bottom y-values strictly below y_top,
        # but no lower than 0.5 above the bottom of the diagram
        bottom_ys = [
            y_bot for y_bot in all_y_levels
            if -n + 0.5 <= y_bot < y_top
        ]
        
        
        #bottom_ys = [y_bot for y_bot in all_y_levels if y_bot < y_top]
        
        #now for this Tbot it does not actually occur below Ttop.  It is a valid Tbot from before along with Ttop in the standard infinity
        for y_bot in bottom_ys:
            
            #y_top is actually the top of T_top so this is exactly the "middle" part and down to some y_bot of Ttop through horiz-infty
            Tmid = [
                [x, y_top],
                [x, y_bot],
                [x1, y_top],
                [x1, y_bot]
            ]
            
            
            #Check if the neck of the T is well-layered
            boolean=check_type_1_box_for_simplification(Tmid,V,where='std')
            
            #We need to check for essential too
            verts_in_complement_of_neck=find_vertices_in_box(Tmid,V,where='horiz-infty')
            verts_in_complement_of_neck=[v for v in verts_in_complement_of_neck if v[1]<bot_of_Ttop]
            
            #BEGIN CONDITION FOR THE LONGEST NECK IN THE UPPER HINGE T: If longest neck is_blocked=True
            
            #look at the bottom of the neck and find the horizontal edge just above it this should be interleaved! Its the 'hinge'
            y_val_above_neck=int(y_bot+0.5)
            
            #Debugging
            #if boolean==True and verts_in_complement_of_neck:
            #    print('y_val_above_neck=',y_val_above_neck)
            #    draw_virtual_type2_boxes_diagram(Ttop, Tmid, V, where1='horiz-infty', where2='std',color1='red')
            
             # The 'next' finds the first/next instance there will only be one or none.  If the neck is at the bottom of the diagram None and you can continue
            horizontal_above_neck = next((h for h in horizontals if h[0][1] == y_val_above_neck),None)
            is_blocked = False
            if horizontal_above_neck is None:
                is_blocked = True
                
            else:
                x_left, x_right = sorted([horizontal_above_neck[0][0],
                                          horizontal_above_neck[1][0]])
                neck_left, neck_right = sorted([x, x1])
                #below is a boolean value checking if these two interleave
                interleaves = ((x_left < neck_left < x_right < neck_right) or(neck_left < x_left < neck_right < x_right))
                
                if interleaves:
                    is_blocked = True
            
            ### END CONDITION FOR LONGEST NECK    
            if boolean==True and verts_in_complement_of_neck and is_blocked==True:
                upper_hinge_Ts.append([Ttop,Tmid])
                #draw_virtual_type2_boxes_diagram(Ttop, Tmid, V, where1='horiz-infty', where2='std',color1='red')
                
    #Tbots=find_all_possible_bottom_Ts_depreciated(V)            
    Tbots=find_all_possible_bottom_Ts(V) #these are trivially well-layered through horizontal infinity.
    lower_hinge_Ts=[]
    for Tbot in Tbots:
        xs = [v[0] for v in Tbot]
        ys = [v[1] for v in Tbot]

        x = min(xs)
        x1 = max(xs)
        y_bot = min(ys)
        top_of_Tbot = max(ys)

        # possible bottom y-values strictly below y_top
        top_ys = [y_top for y_top in all_y_levels if y_top > y_bot]
        
        #now for this Ttop it does not actually occur above Tbot.  It is a valid Ttop from before along with Tbot in the standard infinity
        for y_top in top_ys:
            
            #y_bot is actually the bottom of T_bot so this is exactly the "middle" part and down to some y_top of Tbot through horiz-infty
            Tmid = [
                [x, y_top],
                [x, y_bot],
                [x1, y_top],
                [x1, y_bot]
            ]
            #Check if the neck of the T is well-layered
            boolean=check_type_1_box_for_simplification(Tmid,V,where='std')
            
            #We need to check for essential too
            verts_in_complement_of_neck=find_vertices_in_box(Tmid,V,where='horiz-infty')
            verts_in_complement_of_neck=[v for v in verts_in_complement_of_neck if v[1]>top_of_Tbot]
            
            
            #BEGIN CONDITION FOR THE LONGEST NECK IN THE UPPER HINGE T: If longest neck is_blocked=True
            
            #look at the bottom of the neck and find the horizontal edge just above it this should be interleaved! Its the 'hinge'
            y_val_below_neck=int(y_top-0.5)
            
            #Debugging
            #if boolean==True and verts_in_complement_of_neck:
            #    print('y_val_below_neck=',y_val_below_neck)
            #    draw_virtual_type2_boxes_diagram(Tbot, Tmid, V, where1='horiz-infty', where2='std',color1='red')
            
             # The 'next' finds the first/next instance there will only be one or none.  If the neck is at the bottom of the diagram None and you can continue
            horizontal_below_neck = next((h for h in horizontals if h[0][1] == y_val_below_neck),None)
            is_blocked = False
            if horizontal_below_neck is None:
                is_blocked = True
                
            else:
                x_left, x_right = sorted([horizontal_below_neck[0][0],
                                          horizontal_below_neck[1][0]])
                neck_left, neck_right = sorted([x, x1])
                #below is a boolean value checking if these two interleave
                interleaves = ((x_left < neck_left < x_right < neck_right) or(neck_left < x_left < neck_right < x_right))
                
                if interleaves:
                    is_blocked = True
            
            ### END CONDITION FOR LONGEST NECK 
            
           
            if boolean==True and verts_in_complement_of_neck and is_blocked==True:
                lower_hinge_Ts.append([Tbot,Tmid])
                
    
    return upper_hinge_Ts, lower_hinge_Ts 






"""def perform_vertical_commutation(vertical_edges,target_edge,V):
    #vertical_edges must be sorted by x-val from smallest to largest.
    import copy
    vertical_edges_copy=copy.deepcopy(vertical_edges)
    V_new = copy.deepcopy(V)
    if vertical_edges[0][0][0]<target_edge[0][0]: # you are commuting right
        
        count=0
        while vertical_edges_copy:
            edge=vertical_edges_copy[-1]
            new_edge=[[target_edge[0][0]-count+0.5,edge[0][1]],[target_edge[0][0]-count+0.5,edge[1][1]]]
            V_new=[v for v in V_new if v!=edge[0] and v!=edge[1] ]
            V_new=commute_vertex_set(V_new,new_edge,direction='right')
            vertical_edges_copy.pop(-1)
            count=count+1
    else: # you are commuting left
        count=0
        while vertical_edges_copy:
            edge=vertical_edges_copy[0]
            new_edge=[[target_edge[0][0]+count-0.5,edge[0][1]],[target_edge[0][0]+count-0.5,edge[1][1]]]
            V_new=[v for v in V_new if v!=edge[0] and v!=edge[1] ]
            V_new=commute_vertex_set(V_new,new_edge,direction='left')
            vertical_edges_copy.pop(0)
            count=count+1     
    
    # 9/15/26 There has been some trouble with hinge T's leaving gaps I am troubleshooting
    n=len(V_new)//2
    xs=[v[0] for v in V_new]
    ys=[v[1] for v in V_new]
    for x in range(1,n+1):
        if x not in xs:
            print('perform_vertical_commutation error')
            print('this x value is not seen',x)
            raise TypeError('Theres an x gap')
    for y in range(-n,0):
        if y not in ys:
            print('this y value is not seen',y)
            raise TypeError('Theres an y gap')
            
            
    return V_new"""

"""
##########################################################
def perform_horizontal_commutation(horizontal_edges,target_edge,V):
    #Seth something important: the horizontal_edges must be sorted y-val with larger y-val first
    import copy
    if horizontal_edges[0][0][1]<=target_edge[0][1]: # you are commuting up
        horizontal_edges_copy=copy.deepcopy(horizontal_edges)
        V_new = copy.deepcopy(V)
        count=0
        while horizontal_edges_copy:
            edge=horizontal_edges_copy[0]
            new_edge=[[edge[0][0],target_edge[0][1]-count+0.5],[edge[1][0],target_edge[0][1]-count+0.5]]
            V_new=[v for v in V_new if v!=edge[0] and v!=edge[1] ]
            V_new=commute_vertex_set(V_new,new_edge,direction='up')
            horizontal_edges_copy.pop(0)
            count=count+1
    else: # you are commuting down
        horizontal_edges_copy=copy.deepcopy(horizontal_edges)
        V_new = copy.deepcopy(V)
        count=0
        while horizontal_edges_copy:
            edge=horizontal_edges_copy[-1]
            new_edge=[[edge[0][0],target_edge[0][1]+count-0.5],[edge[1][0],target_edge[0][1]+count-0.5]]
            V_new=[v for v in V_new if v!=edge[0] and v!=edge[1] ]
            V_new=commute_vertex_set(V_new,new_edge,direction='down')
            horizontal_edges_copy.pop(-1)
            count=count+1        
     # 9/15/26 There has been some trouble with hinge T's leaving gaps I am troubleshooting
    n=len(V_new)//2
    xs=[v[0] for v in V_new]
    ys=[v[1] for v in V_new]
    for x in range(1,n+1):
        if x not in xs:
            print('perform_horizontal_commutation error')
            print('this x value is not seen',x)
            raise TypeError('Theres an x gap')
    for y in range(-n,0):
        if y not in ys:
            print('this y value is not seen',y)
            raise TypeError('Theres an y gap')
                    
    return V_new"""


def perform_horizontal_downward_hinge(horizontal_edges, target_edge, V):
    import copy
    V_new = copy.deepcopy(V)
    n = len(V)//2
    
    
    # 1) Determine the target y-value
    target_y = target_edge[0][1]
    num_moving = len(horizontal_edges)
    
    # 2) Identify all vertices strictly below the target edge
    below_vertices = [v for v in V_new if v[1] < target_y]
    
    # 3) Push all these vertices down by len(horizontal_edges) to make room
    V_new_rest = [v for v in V_new if v[1] >= target_y]  # keep everything else in place
    V_new_rest.extend([[v[0], v[1] - num_moving] for v in below_vertices])
    
    # 4) Remove old horizontal_edges from V_new
    old_horiz_vertices = [v for edge in horizontal_edges for v in edge]
    V_new_rest = [v for v in V_new_rest if v not in old_horiz_vertices]
    
    # 5) Place horizontal_edges in the gap
    # Top horizontal_edge goes at target_y - 1, next at target_y - 2, ...
    for i, edge in enumerate(sorted(horizontal_edges, key=lambda e: e[0][1], reverse=True)):
        new_y = target_y - 1 - i
        x1, x2 = edge[0][0], edge[1][0]
        V_new_rest.extend([[x1, new_y], [x2, new_y]])
    
    # 6) Now fix gaps in x-values and y-values using shift_vertex_set
    
    V_shifted=shift_vertex_set_simpler(V_new_rest)
    #troubleshooting
    # First convert tuples as shift_vertex_set expects tuples
    #V_tuple = [tuple(v) for v in V_new_rest]
    #V_shifted = shift_vertex_set(V_tuple)
    #V_shifted = shift_vertex_set(V_tuple)
    #V_shifted=[list(v) for v in V_shifted]
    
    # Anchor topmost y-value at -1
    max_y = max(v[1] for v in V_shifted)
    delta = max_y + 1

    V_shifted = [[x, y - delta] for [x, y] in V_shifted]
    
    
    # 9/15/26 There has been some trouble with hinge T's leaving gaps I am troubleshooting
    #xs=[v[0] for v in V_shifted]
    #ys=[v[1] for v in V_shifted]
    #for x in range(1,n+1):
    #    if x not in xs:
    #        print('this x value is not seen',x)
    #        raise TypeError('Theres an x gap')
    #for y in range(-n,0):
    #    if y not in ys:
    #        print('this y value is not seen',y)
    #        raise TypeError('Theres an y gap')
    
    return V_shifted


def perform_horizontal_upward_hinge(horizontal_edges, target_edge, V):
    import copy
    V_new = copy.deepcopy(V)
    n = len(V)//2
    
    
    # 1) Determine the target y-value
    target_y = target_edge[0][1]
    num_moving = len(horizontal_edges)
    
    # 2) Identify all vertices strictly above the target edge
    above_vertices = [v for v in V_new if v[1] > target_y]
    
    # 3) Push all these vertices up by len(horizontal_edges) to make room
    V_new_rest = [v for v in V_new if v[1] <= target_y]  # keep everything else in place
    V_new_rest.extend([[v[0], v[1] + num_moving] for v in above_vertices])
    
    # 4) Remove old horizontal_edges from V_new
    old_horiz_vertices = [v for edge in horizontal_edges for v in edge]
    V_new_rest = [v for v in V_new_rest if v not in old_horiz_vertices]
    
    # 5) Place horizontal_edges in the gap
    # Top horizontal_edge goes at target_y + num_moving, next at target_y + num_moving-1, ...
    for i, edge in enumerate(sorted(horizontal_edges, key=lambda e: e[0][1], reverse=True)):
        new_y = target_y + num_moving - i
        x1, x2 = edge[0][0], edge[1][0]
        V_new_rest.extend([[x1, new_y], [x2, new_y]])
    
    # 6) Now fix gaps in x-values and y-values using shift_vertex_set
    # First convert tuples as shift_vertex_set expects tuples
    V_tuple = [tuple(v) for v in V_new_rest]
    V_shifted=shift_vertex_set_simpler(V_new_rest)
    
    #troubleshooting
    #V_shifted = shift_vertex_set(V_tuple)
    #V_shifted = shift_vertex_set(V_tuple)
    #V_shifted=[list(v) for v in V_shifted]
    
    
    # Anchor topmost y-value at -1
    max_y = max(v[1] for v in V_shifted)
    delta = max_y + 1

    V_shifted = [[x, y - delta] for [x, y] in V_shifted]
    
    #9/15/26 hinge T issues with leaving gaps being fixed
    #xs=[v[0] for v in V_shifted]
    #ys=[v[1] for v in V_shifted]
    #for x in range(1,n+1):
    #    if x not in xs:
    #        raise TypeError('Theres an x gap')
    #for y in range(-n,0):
    #    if y not in ys:
    #        raise TypeError('Theres an y gap')
    
    return V_shifted

def perform_upper_hinge_T_isotopy_with_consolidation_box(hinge_T,V):
    
    _, verticals = sort_vertices_into_verticals_and_horizontals(V)

    Ttop = hinge_T[0]   # 4 vertices defining the top box of the T
    
    Tmid = hinge_T[1]   # 4 vertices defining the middle box of the T
    
    #Now we need to define Tbot as in the perform_push_T_isotopy because we have Ttop but they have to go past the parts in Tbot
    xs = [vert[0] for vert in Ttop]
    left_side_of_Ttop = min(xs)
    right_side_of_Ttop = max(xs)
    
    ys = [vert[1] for vert in Ttop]
    top_of_Ttop = max(ys)
    bot_of_Ttop = min(ys)
    
    xs = [vert[0] for vert in Tmid]
    left_side_of_Tmid = min(xs)
    right_side_of_Tmid = max(xs)
    
    ys = [vert[1] for vert in Tmid]
    top_of_Tmid = max(ys)
    bot_of_Tmid = min(ys)
    
    Tbot=[[left_side_of_Tmid,bot_of_Ttop],[left_side_of_Tmid,bot_of_Tmid],[right_side_of_Tmid,bot_of_Ttop],[right_side_of_Tmid,bot_of_Tmid]]
    
    xs = [vert[0] for vert in Tbot]
    left_side_of_Tbot = min(xs)
    right_side_of_Tbot = max(xs)
    
    ys = [vert[1] for vert in Tbot]
    top_of_Tbot = max(ys)
    bot_of_Tbot = min(ys)
    orig_bot_of_Tbot=bot_of_Tbot
    
    #Now we perform the same isotopy: Shrink the wings of Ttop, then perform a series of "commutations".  This will not be valid commutations but will be a series of hinges. 
    #################### 6/8/2026 ########################################################################################
    length_of_T=top_of_Ttop-bot_of_Tbot
    number_of_commutations=top_of_Ttop-bot_of_Ttop
    vertices_crossing_b_arc_region = find_vertices_in_box(Ttop, V, where='horiz-infty')
    verticals_in_left_wing = [
        v for v in verticals
        if v[0] in vertices_crossing_b_arc_region
        and v[1] in vertices_crossing_b_arc_region
        and v[0][0] < left_side_of_Ttop]
    
   
    verticals_in_right_wing = [
        v for v in verticals
        if v[0] in vertices_crossing_b_arc_region
        and v[1] in vertices_crossing_b_arc_region
        and v[0][0] > right_side_of_Ttop]
   
    #to perform the series of commutations there need to be vertices under the left wing, otherwise we will have to change the boundary of the Ttop. 
    vertices_under_wings = find_vertices_in_box(Ttop, V, where='horiz-vert-infty') #this will capture everything under the wings on both sides
    vertices_under_left_wing=[v for v in vertices_under_wings if v[0]<left_side_of_Ttop and v[1]<bot_of_Ttop]
    vertices_above_left_wing=[v for v in vertices_under_wings if v[0]<left_side_of_Ttop and v[1]>top_of_Ttop]
    vertices_under_right_wing=[v for v in vertices_under_wings if v[0]>right_side_of_Ttop and v[1]<bot_of_Ttop]
    vertices_above_right_wing=[v for v in vertices_under_wings if v[0]>right_side_of_Ttop and v[1]>top_of_Ttop]
    
    vertices_under_wings =[v for v in vertices_under_wings if bot_of_Tbot<v[1]<bot_of_Ttop] #these are actually the vertices under the wings
    
    #Note the strange thing I just did is because we used to only consider Ts with top at the actual top of the diagram. 
    ###################################################################################################
    #From the dimensions of T make a vertex map and return it.  Then update the consolidation boxes list with this map.
    
    V_tuple=[tuple(v) for v in V]
    xs_under_left_wing = set(v[0] for v in vertices_under_left_wing)
    xs_above_left_wing = set(v[0] for v in vertices_above_left_wing)
    xs_under_right_wing = set(v[0] for v in vertices_under_right_wing)
    xs_above_right_wing = set(v[0] for v in vertices_above_right_wing)
    ys_under_wings = set(v[1] for v in vertices_under_wings)
    
    xs_verts_in_right_wing = set(v[0] for verts in verticals_in_right_wing for v in verts)
    xs_verts_in_left_wing=set(v[0] for verts in verticals_in_left_wing for v in verts)
    
    coord_map = {}
    for v in V_tuple:
        if bot_of_Tbot<v[1]<top_of_Ttop:
            if v[0] in xs_under_left_wing:
                count=0
                for x in xs_verts_in_left_wing:
                    if x>v[0]:
                        count=count+1
                #coord_map[v] = (v[0] + len(verticals_in_right_wing),v[1])
                coord_map[v] = (v[0] - count,v[1] + number_of_commutations)

            elif v[0] in xs_under_right_wing:
                count=0
                for x in xs_verts_in_right_wing:
                    if x>v[0]:
                        count=count+1
                coord_map[v] = (v[0] + count,v[1] + number_of_commutations)
            
            else:
                coord_map[v] = (v[0],v[1] + number_of_commutations)
       
        elif v[0] in xs_above_right_wing and v[1] not in ys_under_wings:
            count=0
            for x in xs_verts_in_right_wing:
                if x>v[0]:
                    count=count+1
            #coord_map[v] = (v[0] + len(verticals_in_right_wing),v[1])
            coord_map[v] = (v[0] + count,v[1])
            
        elif v[0] in xs_above_left_wing and v[1] not in ys_under_wings:
            count=0
            for x in xs_verts_in_left_wing:
                if x<v[0]:
                    count=count+1
            coord_map[v] = (v[0] - count,v[1])
            #coord_map[v] = (v[0] - len(verticals_in_left_wing),v[1])
       
        #elif the v is a subbox of the current T
        else:
            coord_map[v] = v

    ################## END 6/8/2026 #######################################################################################
    #Now we perform a series of commutations that push in these verticals:
    #Step 1: Commute the verticals in the left wing to the right past the left side of Ttop
    
    #The verticals need to be sorted correctly so the pushing occurs in the correct order:
    if verticals_in_left_wing:
        #print('There are no verticals in left wing')
        if not vertices_under_left_wing:
            #redefine the top box to include the far left side of the diagram.
            left_side_of_Ttop = 0.5
            Ttop = [[left_side_of_Ttop,top_of_Ttop],[left_side_of_Ttop,bot_of_Ttop],[right_side_of_Ttop, top_of_Ttop],[right_side_of_Ttop, bot_of_Ttop]]   # 4 vertices defining the top box of the T
            Tbot = [[left_side_of_Ttop,top_of_Tbot],[left_side_of_Ttop,bot_of_Tbot],[right_side_of_Ttop, top_of_Tbot],[right_side_of_Ttop, bot_of_Tbot]]
            Tmid = [[left_side_of_Ttop,top_of_Tmid],[left_side_of_Ttop,bot_of_Tmid],[right_side_of_Ttop, top_of_Tmid],[right_side_of_Ttop, bot_of_Tmid]]
          
        else:
            #perform the regular commutations
            verticals_in_left_wing.sort(key=lambda v: v[0][0])
            #print('These are verticals in the left wing',verticals_in_left_wing)
            number_of_left_commutations=len(verticals_in_left_wing)
            #print('These are number of commutations from left wing',number_of_left_commutations)
            
            #print('The left side of the box will be at',left_side_of_Ttop,'after the commutations')
            #The -0.5 comes from the fact that the edge of this box is on a half value, and the edges that it must commute past are on integer values.
            target_edge=[[left_side_of_Ttop-0.5,top_of_Ttop],[left_side_of_Ttop-0.5,bot_of_Ttop]]

            V=perform_vertical_commutation(verticals_in_left_wing,target_edge,V) #perform the series of commutations
            
            #the commutations will move the edge of the box to the left by the number of commutations
            left_side_of_Ttop=left_side_of_Ttop-number_of_left_commutations
            
            #redefine the box now after the commuations
            Ttop = [[left_side_of_Ttop,top_of_Ttop],[left_side_of_Ttop,bot_of_Ttop],[right_side_of_Ttop, top_of_Ttop],[right_side_of_Ttop, bot_of_Ttop]]   # 4 vertices defining the top box of the T
            Tbot = [[left_side_of_Ttop,top_of_Tbot],[left_side_of_Ttop,bot_of_Tbot],[right_side_of_Ttop, top_of_Tbot],[right_side_of_Ttop, bot_of_Tbot]]
            Tmid = [[left_side_of_Ttop,top_of_Tmid],[left_side_of_Ttop,bot_of_Tmid],[right_side_of_Ttop, top_of_Tmid],[right_side_of_Ttop, bot_of_Tmid]]
            #print('this is top_of_Ttop',top_of_Ttop)
            #print('This is the T after the left wing is shrunk')
            #draw_virtual_type2_boxes_diagram(Ttop, Tmid, V, where1='horiz-infty', where2='std',color1='deeppink')
    
    #Step 2: Commute the verticals in the right wing to the left past the right side of Ttop
    
    if verticals_in_right_wing:
        if not vertices_under_right_wing:
            right_side_of_Ttop = len(V)//2+0.5 
            Ttop = [[left_side_of_Ttop,top_of_Ttop],[left_side_of_Ttop,bot_of_Ttop],[right_side_of_Ttop, top_of_Ttop],[right_side_of_Ttop, bot_of_Ttop]]
            Tbot = [[left_side_of_Ttop,top_of_Tbot],[left_side_of_Ttop,bot_of_Tbot],[right_side_of_Ttop, top_of_Tbot],[right_side_of_Ttop, bot_of_Tbot]]
            Tmid = [[left_side_of_Ttop,top_of_Tmid],[left_side_of_Ttop,bot_of_Tmid],[right_side_of_Ttop, top_of_Tmid],[right_side_of_Ttop, bot_of_Tmid]]
        else:
            verticals_in_right_wing.sort(key=lambda v: v[0][0])
            
            number_of_right_commutations=len(verticals_in_right_wing)
            
            
            target_edge=[[right_side_of_Ttop+0.5,top_of_Ttop],[right_side_of_Ttop+0.5,bot_of_Ttop]]
           
            V=perform_vertical_commutation(verticals_in_right_wing,target_edge,V) #perform the series of commutations
            
            #the commutations will move the edge of the box to the right by the number of commutations
            right_side_of_Ttop=right_side_of_Ttop+number_of_right_commutations
            
            #redefine the box now after the commuations
            Ttop = [[left_side_of_Ttop,top_of_Ttop],[left_side_of_Ttop,bot_of_Ttop],[right_side_of_Ttop, top_of_Ttop],[right_side_of_Ttop, bot_of_Ttop]]   # 4 vertices defining the top box of the T
            Tbot = [[left_side_of_Ttop,top_of_Tbot],[left_side_of_Ttop,bot_of_Tbot],[right_side_of_Ttop, top_of_Tbot],[right_side_of_Ttop, bot_of_Tbot]]
            Tmid = [[left_side_of_Ttop,top_of_Tmid],[left_side_of_Ttop,bot_of_Tmid],[right_side_of_Ttop, top_of_Tmid],[right_side_of_Ttop, bot_of_Tmid]]
            
            #print('This is the T after the right wing is shrunk')
            #draw_virtual_type2_boxes_diagram(Ttop, Tmid, V, where1='horiz-infty', where2='std',color1='deeppink')
    #Uncomment for Debugging
    #print('This is the T after the wings are shrunk')
    #draw_virtual_type2_boxes_diagram(Ttop, Tmid, V, where1='horiz-infty', where2='std',color1='deeppink')
    
    #Step 3: Commute the horizontals in this box down past the bottom edge of the Tbot.
    xs = [vert[0] for vert in Tbot]
    left_side_of_Tbot = min(xs)
    right_side_of_Tbot = max(xs)
    
    ys = [vert[1] for vert in Tbot]
    top_of_Tbot = max(ys)
    bot_of_Tbot = min(ys)
    
    #now with this new vertex set we need to find the horizontals in Ttop in the standard infinity
    vertices_in_Ttop = find_vertices_in_box(Ttop, V, where='std')
    horizontals, _ = sort_vertices_into_verticals_and_horizontals(V) #find the new horizontals in V after the wings have shrunk
    
    horizontals_in_Ttop=[h for h in horizontals
        if h[0] in vertices_in_Ttop
        and h[1] in vertices_in_Ttop]
    
    #NOTE: I want the topmost horizontal in T top to be commuted to just below bot_of_Tbot, then the next topmost horizontal below that etc.
    horizontals_in_Ttop.sort(key=lambda v: v[0][1], reverse=True)
    #horizontals_in_Ttop.sort(key=lambda v: v[0][1])
    target_edge=[[left_side_of_Tbot,int(bot_of_Tbot+0.5)],[right_side_of_Tbot,int(bot_of_Tbot+0.5)]]
    #print('This is the target edge',target_edge)
    V=perform_horizontal_downward_hinge(horizontals_in_Ttop,target_edge,V)
    
    
    #Now I need to update Ttop... Its now the image of Ttop, the consolidation box
    number_of_horizontal_commutations = len(horizontals_in_Ttop)
    top_of_Ttop = target_edge[0][1]-0.5
    bot_of_Ttop = top_of_Ttop+number_of_horizontal_commutations 

    Ttop=[
        [left_side_of_Tbot, top_of_Ttop],
        [left_side_of_Tbot, bot_of_Ttop],
        [right_side_of_Tbot, top_of_Ttop],
        [right_side_of_Tbot, bot_of_Ttop]
    ]
    #print('This is the consolidation box after the full isotopy')
    #draw_virtual_type2_boxes_diagram(Ttop, Ttop, V, where1='std', where2='std',color1='red')
    consolidation_box=Ttop
    
    
    return [coord_map,consolidation_box,V]
###############################################################################################

##############################################################################################
def perform_lower_hinge_T_isotopy_with_consolidation_box(hinge_T,V):
    _, verticals = sort_vertices_into_verticals_and_horizontals(V)
    Tbot = hinge_T[0]   # 4 vertices defining the top box of the T
    Tmid = hinge_T[1]   # 4 vertices defining the middle box of the T
    #Now we need to define Tbot as in the perform_push_T_isotopy because we have Ttop but they have to go past the parts in Tbot
    xs = [vert[0] for vert in Tbot]
    left_side_of_Tbot = min(xs)
    right_side_of_Tbot = max(xs)
    
    ys = [vert[1] for vert in Tbot]
    top_of_Tbot = max(ys)
    bot_of_Tbot = min(ys)
    
    xs = [vert[0] for vert in Tmid]
    left_side_of_Tmid = min(xs)
    right_side_of_Tmid = max(xs)
    
    ys = [vert[1] for vert in Tmid]
    top_of_Tmid = max(ys)
    bot_of_Tmid = min(ys)
    
    
    Ttop=[[left_side_of_Tmid,top_of_Tbot],[left_side_of_Tmid,top_of_Tmid],[right_side_of_Tmid,top_of_Tbot],[right_side_of_Tmid,top_of_Tmid]]
    
   
    
    xs = [vert[0] for vert in Ttop]
    left_side_of_Ttop = min(xs)
    right_side_of_Ttop = max(xs)
    
    ys = [vert[1] for vert in Ttop]
    top_of_Ttop = max(ys)
    bot_of_Ttop = min(ys)
    
    
    ############################### NEW ADD 6/7/2026########################################
    length_of_T=top_of_Ttop-bot_of_Tbot
    number_of_commutations=top_of_Tbot-bot_of_Tbot
    vertices_crossing_b_arc_region = find_vertices_in_box(Tbot, V, where='horiz-infty')
    
    verticals_in_left_wing = [
        v for v in verticals
        if v[0] in vertices_crossing_b_arc_region
        and v[1] in vertices_crossing_b_arc_region
        and v[0][0] < left_side_of_Tbot]

    
   
    verticals_in_right_wing = [
        v for v in verticals
        if v[0] in vertices_crossing_b_arc_region
        and v[1] in vertices_crossing_b_arc_region
        and v[0][0] > right_side_of_Tbot]
   
    #to perform the series of commutations there need to be vertices under the left wing, otherwise we will have to change the boundary of the Ttop. 
    vertices_under_wings = find_vertices_in_box(Tbot, V, where='horiz-vert-infty') #this will capture everything under the wings on both sides
    vertices_under_left_wing=[v for v in vertices_under_wings if v[0]<left_side_of_Ttop and v[1]<bot_of_Tbot]
    vertices_above_left_wing=[v for v in vertices_under_wings if v[0]<left_side_of_Ttop and v[1]>top_of_Tbot]
    vertices_under_right_wing=[v for v in vertices_under_wings if v[0]>right_side_of_Ttop and v[1]<bot_of_Tbot]
    vertices_above_right_wing=[v for v in vertices_under_wings if v[0]>right_side_of_Ttop and v[1]>top_of_Tbot]
    
    vertices_under_wings =[v for v in vertices_under_wings if top_of_Tbot<v[1]<top_of_Ttop] #these are actually the vertices under the wings
    
    #Note the strange thing I just did is because we used to only consider Ts with top at the actual top of the diagram. 

    ###############################################################################################
    #From the dimensions of T make a vertex map and return it.  Then update the consolidation boxes list with this map.
    
    V_tuple=[tuple(v) for v in V]
    xs_under_left_wing = set(v[0] for v in vertices_under_left_wing)
    xs_above_left_wing = set(v[0] for v in vertices_above_left_wing)
    xs_under_right_wing = set(v[0] for v in vertices_under_right_wing)
    xs_above_right_wing = set(v[0] for v in vertices_above_right_wing)
    ys_under_wings = set(v[1] for v in vertices_under_wings)
    
    xs_verts_in_right_wing = set(v[0] for verts in verticals_in_right_wing for v in verts)
    xs_verts_in_left_wing=set(v[0] for verts in verticals_in_left_wing for v in verts)
    
    coord_map = {}
    for v in V_tuple:
        #if v[0] in xs_above_left_wing and v[1] in ys_under_wings:
        if top_of_Tbot<v[1]< top_of_Ttop:
            if v[0] in xs_above_left_wing:
                count=0
                for x in xs_verts_in_left_wing:
                    if x>v[0]:
                        count=count+1
                #coord_map[v] = (v[0] + len(verticals_in_right_wing),v[1])
                coord_map[v] = (v[0] - count,v[1] - number_of_commutations)
            elif v[0] in xs_above_right_wing:
                count=0
                for x in xs_verts_in_right_wing:
                    if x>v[0]:
                        count=count+1
                coord_map[v] = (v[0] + count,v[1] - number_of_commutations)
            else: #It is in the neck   
                coord_map[v] = (v[0],v[1] - number_of_commutations)
                
       
        elif v[0] in xs_under_right_wing and v[1] not in ys_under_wings:
            count=0
            for x in xs_verts_in_right_wing:
                if x>v[0]:
                    count=count+1
            #coord_map[v] = (v[0] + len(verticals_in_right_wing),v[1])
            coord_map[v] = (v[0] + count,v[1])
            
        elif v[0] in xs_under_left_wing and v[1] not in ys_under_wings:
            count=0
            for x in xs_verts_in_left_wing:
                if x<v[0]:
                    count=count+1
            coord_map[v] = (v[0] - count,v[1])
            #coord_map[v] = (v[0] - len(verticals_in_left_wing),v[1])
       
        #elif the v is a subbox of the current T
        else:
            coord_map[v] = v
    ############################# END NEW ADD 6/7/2026#############################
    
    #Now we perform a series of commutations that push in these verticals:
    #Step 1: Commute the verticals in the left wing to the right past the left side of Ttop
    
    #The verticals need to be sorted correctly so the pushing occurs in the correct order:
    if verticals_in_left_wing:
        #print('There are no verticals in left wing')
        if not vertices_above_left_wing:
            #redefine the top box to include the far left side of the diagram.
            left_side_of_Tbot = 0.5
            Tbot = [[left_side_of_Tbot,top_of_Tbot],[left_side_of_Tbot,bot_of_Tbot],[right_side_of_Tbot, top_of_Tbot],[right_side_of_Tbot, bot_of_Tbot]]   # 4 vertices defining the top box of the T
                     
            Ttop = [[left_side_of_Tbot,top_of_Ttop],[left_side_of_Tbot,bot_of_Ttop],[right_side_of_Tbot, top_of_Ttop],[right_side_of_Tbot, bot_of_Ttop]]
            Tmid = [[left_side_of_Tbot,top_of_Tmid],[left_side_of_Tbot,bot_of_Tmid],[right_side_of_Tbot, top_of_Tmid],[right_side_of_Tbot, bot_of_Tmid]]
          
        else:
            #perform the regular commutations
            verticals_in_left_wing.sort(key=lambda v: v[0][0])
            #print('These are verticals in the left wing',verticals_in_left_wing)
            number_of_left_commutations=len(verticals_in_left_wing)
            #print('These are number of commutations from left wing',number_of_left_commutations)
            
            #print('The left side of the box will be at',left_side_of_Ttop,'after the commutations')
            #The -0.5 comes from the fact that the edge of this box is on a half value, and the edges that it must commute past are on integer values.
            target_edge=[[left_side_of_Tbot-0.5,top_of_Tbot],[left_side_of_Tbot-0.5,bot_of_Tbot]]

            V=perform_vertical_commutation(verticals_in_left_wing,target_edge,V) #perform the series of commutations
            
            #the commutations will move the edge of the box to the left by the number of commutations
            left_side_of_Tbot=left_side_of_Tbot-number_of_left_commutations
            
            #redefine the box now after the commuations
            Tbot = [[left_side_of_Tbot,top_of_Tbot],[left_side_of_Tbot,bot_of_Tbot],[right_side_of_Tbot, top_of_Tbot],[right_side_of_Tbot, bot_of_Tbot]]   # 4 vertices defining the bottom box of the T
            Ttop = [[left_side_of_Tbot,top_of_Ttop],[left_side_of_Tbot,bot_of_Ttop],[right_side_of_Tbot, top_of_Ttop],[right_side_of_Tbot, bot_of_Ttop]]
            Tmid = [[left_side_of_Tbot,top_of_Tmid],[left_side_of_Tbot,bot_of_Tmid],[right_side_of_Tbot, top_of_Tmid],[right_side_of_Tbot, bot_of_Tmid]]
            #print('this is top_of_Tbot',top_of_Tbot)
            #print('This is the T after the left wing is shrunk')
            #draw_virtual_type2_boxes_diagram(Tbot, Tmid, V, where1='horiz-infty', where2='std',color1='deeppink')
    
    #Step 2: Commute the verticals in the right wing to the left past the right side of Ttop
    
    if verticals_in_right_wing:
        if not vertices_above_right_wing:
            right_side_of_Tbot = len(V)//2+0.5 
            Tbot = [[left_side_of_Tbot,top_of_Tbot],[left_side_of_Tbot,bot_of_Tbot],[right_side_of_Tbot, top_of_Tbot],[right_side_of_Tbot, bot_of_Tbot]]
            Ttop = [[left_side_of_Tbot,top_of_Ttop],[left_side_of_Tbot,bot_of_Ttop],[right_side_of_Tbot, top_of_Ttop],[right_side_of_Tbot, bot_of_Ttop]]
            Tmid = [[left_side_of_Tbot,top_of_Tmid],[left_side_of_Tbot,bot_of_Tmid],[right_side_of_Tbot, top_of_Tmid],[right_side_of_Tbot, bot_of_Tmid]]
        else:
            verticals_in_right_wing.sort(key=lambda v: v[0][0])
            
            number_of_right_commutations=len(verticals_in_right_wing)
            target_edge=[[right_side_of_Tbot+0.5,top_of_Tbot],[right_side_of_Tbot+0.5,bot_of_Tbot]]
            V=perform_vertical_commutation(verticals_in_right_wing,target_edge,V) #perform the series of commutations
            #the commutations will move the edge of the box to the right by the number of commutations
            right_side_of_Tbot=right_side_of_Tbot+number_of_right_commutations
            
            #redefine the box now after the commuations
            Tbot = [[left_side_of_Tbot,top_of_Tbot],[left_side_of_Tbot,bot_of_Tbot],[right_side_of_Tbot, top_of_Tbot],[right_side_of_Tbot, bot_of_Tbot]]   # 4 vertices defining the bottom box of the T
            Ttop = [[left_side_of_Tbot,top_of_Ttop],[left_side_of_Tbot,bot_of_Ttop],[right_side_of_Tbot, top_of_Ttop],[right_side_of_Tbot, bot_of_Ttop]]
            Tmid = [[left_side_of_Tbot,top_of_Tmid],[left_side_of_Tbot,bot_of_Tmid],[right_side_of_Tbot, top_of_Tmid],[right_side_of_Tbot, bot_of_Tmid]]
            
            #print('This is the T after the right wing is shrunk')
            #draw_virtual_type2_boxes_diagram(Tbot, Tmid, V, where1='horiz-infty', where2='std',color1='deeppink')
       
    
    #Uncomment for Debugging
    #print('This is the T after the wings are shrunk')
    #draw_virtual_type2_boxes_diagram(Tbot, Tmid, V, where1='horiz-infty', where2='std',color1='deeppink')
    
    #Step 3: Commute the horizontals in this box up past the top edge of the Ttop.
    
    xs = [vert[0] for vert in Ttop]
    left_side_of_Ttop = min(xs)
    right_side_of_Ttop = max(xs)
    
    ys = [vert[1] for vert in Ttop]
    top_of_Ttop = max(ys)
    bot_of_Ttop = min(ys)
    
    #now with this new vertex set we need to find the horizontals in Tbot in the standard infinity
    vertices_in_Tbot = find_vertices_in_box(Tbot, V, where='std')
    horizontals, _ = sort_vertices_into_verticals_and_horizontals(V) #find the new horizontals in V after the wings have shrunk
    
    horizontals_in_Tbot=[h for h in horizontals
        if h[0] in vertices_in_Tbot
        and h[1] in vertices_in_Tbot]
    
    #NOTE: I want the topmost horizontal in T bot to be commuted to just below bot_of_Tbot, then the next topmost horizontal below that etc.
    horizontals_in_Tbot.sort(key=lambda v: v[0][1], reverse=True)
    #horizontals_in_Ttop.sort(key=lambda v: v[0][1])
    target_edge=[[left_side_of_Ttop,int(top_of_Ttop-0.5)],[right_side_of_Ttop,int(top_of_Ttop-0.5)]]
    #print('This is the target edge',target_edge)
    V=perform_horizontal_upward_hinge(horizontals_in_Tbot,target_edge,V)
    #print('This is the hinge T after the full isotopy')
    #draw_virtual_type2_boxes_diagram(Tbot, Tmid, V, where1='horiz-infty', where2='std',color1='deeppink')
    
     #Now I need to update Tbot... Its now the image of Tbot, the consolidation box
    
    number_of_horizontal_commutations = len(horizontals_in_Tbot)
    bot_of_Tbot = top_of_Tmid-number_of_horizontal_commutations 
    top_of_Tbot = bot_of_Tbot+number_of_horizontal_commutations 

    Tbot = [
        [left_side_of_Ttop, top_of_Tbot],
        [left_side_of_Ttop, bot_of_Tbot],
        [right_side_of_Ttop, top_of_Tbot],
        [right_side_of_Ttop, bot_of_Tbot]
    ]

    
    
    #print('This is the consolidation box after the full isotopy')
    #draw_virtual_type2_boxes_diagram(Tbot, Tbot, V, where1='std', where2='std',color1='red')
    
    consolidation_box=Tbot
         
    
    return [coord_map,consolidation_box,V]
###########################################################################################################



########################################################################################
def shift_vertex_set_simpler(V_new):

    # --- Compress x coordinates ---
    xs = sorted(set(v[0] for v in V_new))
    x_map = {x: i+1 for i, x in enumerate(xs)}

    V_new = [(x_map[x], y) for x, y in V_new]

    # --- Compress y coordinates ---
    ys = sorted(set(v[1] for v in V_new))
    y_map = {y: -len(ys) + i for i, y in enumerate(ys)}

    V_new = [(x, y_map[y]) for x, y in V_new]

    V_new.sort()

    return [list(v) for v in V_new]
##############################################################################################
##############################################################################################

def perform_hinge_Ts_and_simplify(V1):
    #####################################################
    seen_diagrams=[V1]
    if len(V1)//2!=2:
        valid_switch = 1
        invalid_exit_disks = []
        continue_switch = 0
        while valid_switch == 1:
            valid_switch = 0
            if continue_switch == 0:
                upper_hinge_Ts, lower_hinge_Ts = find_all_essential_hinge_Ts(V1)
                 # Ensure they are not through infinity on the original diagram
                hinge_Ts_not_through_infinity = []
                for hinge_T in upper_hinge_Ts:
                    if check_if_T_through_infinity(hinge_T, [0,0], whichT='upper'):
                        hinge_Ts_not_through_infinity.append(hinge_T)

                upper_hinge_Ts = hinge_Ts_not_through_infinity
                # Ensure they are not through infinity on the original diagram
                hinge_Ts_not_through_infinity = []
                for hinge_T in lower_hinge_Ts:
                    if check_if_T_through_infinity(hinge_T, [0,0], whichT='lower'):
                        hinge_Ts_not_through_infinity.append(hinge_T)

                lower_hinge_Ts = hinge_Ts_not_through_infinity

           
            
            if upper_hinge_Ts:
                # Filter out those whose exit disks are already invalid
                filtered_Ts = []
                for T in upper_hinge_Ts:
                    #T=[Ttop,Tmid]
                    T_mid=T[1]
                    min_y=min([v[1] for v in T_mid])
                    exit_disk = sorted([v for v in T_mid if v[1]==min_y])
                    if V1 not in seen_diagrams or exit_disk not in invalid_exit_disks:
                        filtered_Ts.append(T)

                # If every T had an invalid exit disk, break out — no further simplification is possible
                if not filtered_Ts:
                    #print("All remaining hinge T-moves correspond to previously invalid exit disks. Exiting hinge T-move loop.")
                    break

                valid_switch = 1
                continue_switch = 0

                # Pick the first T's strand set and find the smallest exit disk among those
                # Choose the best hinge T using the same criterion as push Ts
                #T = filtered_Ts[0]
                
                #This is a change. I want the T with the most vertices inside T[1].
                def most_vertices_inside(T):
                    verts = find_vertices_in_box(T[1], V1, where='std')
                    return len(verts)

                T = max(filtered_Ts, key=most_vertices_inside)

                vertices_in_T = (
                find_vertices_in_box(T[0], V1, where='std')
                + find_vertices_in_box(T[1], V1, where='std')
                )

                candidates = []
                for T in filtered_Ts:
                    vertices = (
                        find_vertices_in_box(T[0], V1, where='std')
                        + find_vertices_in_box(T[1], V1, where='std')
                    )

                    if vertices == vertices_in_T:
                        candidates.append(T)


                # Among these, choose the T with the greatest height of T[0].
                def boundary_height(T):
                    ys = [point[1] for point in T[0]]
                    return max(ys) - min(ys)

                max_height = max(boundary_height(T) for T in candidates)

                best_Ts = [
                T for T in candidates
                if boundary_height(T) == max_height
                ]


                # Among those, choose the T with the widest width of T[0].
                max_width = max(
                abs(T[0][0][0] - T[0][1][0])
                for T in best_Ts
                )

                best_T = [
                T for T in best_Ts
                if abs(T[0][0][0] - T[0][1][0]) == max_width
                ]

                T = best_T[0]
                print('This is a valid and essential hinge T')
                
                T_mid=T[1]
                min_y=min([v[1] for v in T_mid])
                exit_disk = sorted([v for v in T_mid if v[1]==min_y])
                #print('this is the exit disk',exit_disk)
                invalid_exit_disks.append(exit_disk) #we append it now becuase if we see the same diagram this will be the exit disk computed 
                
                draw_virtual_type2_boxes_diagram(T[0], T[1], V1,where1='horiz-infty',where2='std',color1='deeppink')
                _, consolidation_box, V_new = perform_upper_hinge_T_isotopy_with_consolidation_box([T[0], T[1]], V1)
                
                draw_rectangular_diagram(V_new)
                  
                # 9/27/2026 Code verification: Uncomment when checked    
                #if not verify_unknot_boolean(V_new):
                #    raise TypeError("The last simplification changed knot type!")
                
                V1=V_new
                if V1 not in seen_diagrams:
                    #computationally expensive but covers a lot of bases
                    V1=perform_v1b_corner_rigid_simplifications(V1)
                    #easier computationally
                    #VS = get_v1b_reduced_diagram(V1)
                    #V1 = VS[-1]

                else:
                    print('This rectangular diagram has been seen before, attempting to find another valid and essential hinge T')
                seen_diagrams.append(V1)
                              
            elif lower_hinge_Ts:
                # Filter out those whose exit disks are already invalid
                filtered_Ts = []
                for T in lower_hinge_Ts:
                    #T=[Ttop,Tmid]
                    T_mid=T[1]
                    max_y=max([v[1] for v in T_mid])
                    exit_disk = sorted([v for v in T_mid if v[1]==max_y])
                    if V1 not in seen_diagrams or exit_disk not in invalid_exit_disks:
                        filtered_Ts.append(T)

                # If every T had an invalid exit disk, break out — no further simplification is possible
                if not filtered_Ts:
                    print("All remaining hinge T-moves correspond to previously invalid exit disks. Exiting hinge T-move loop.")
                    break

                valid_switch = 1
                continue_switch = 0

                # This is a change. I want the T with the most vertices inside T[1].
                def most_vertices_inside(T):
                    verts = find_vertices_in_box(T[1], V1, where='std')
                    return len(verts)

                T = max(filtered_Ts, key=most_vertices_inside)

                vertices_in_T = (
                find_vertices_in_box(T[0], V1, where='std')
                + find_vertices_in_box(T[1], V1, where='std')
                )

                candidates = []
                for T in filtered_Ts:
                    vertices = (
                        find_vertices_in_box(T[0], V1, where='std')
                        + find_vertices_in_box(T[1], V1, where='std')
                    )

                    if vertices == vertices_in_T:
                        candidates.append(T)


                # Among these, choose the T with the greatest height of T[0].
                def boundary_height(T):
                    ys = [point[1] for point in T[0]]
                    return abs(max(ys) - min(ys))

                max_height = max(boundary_height(T) for T in candidates)

                best_Ts = [
                T for T in candidates
                if boundary_height(T) == max_height
                ]


                # Among those, choose the T with the largest width of T[0].
                max_width = max(
                abs(T[0][0][0] - T[0][1][0])
                for T in best_Ts
                )

                best_T = [
                T for T in best_Ts
                if abs(T[0][0][0] - T[0][1][0]) == max_width
                ]

                T = best_T[0]
                print('This is a valid and essential hinge T')
                draw_virtual_type2_boxes_diagram(T[0], T[1], V1,where1='horiz-infty',where2='std',color1='deeppink')
                
                T_mid=T[1]
                max_y=max([v[1] for v in T_mid])
                exit_disk = sorted([v for v in T_mid if v[1]==max_y])
                #print('this is the exit disk',exit_disk)
                invalid_exit_disks.append(exit_disk)
                
                _, consolidation_box, V_new = perform_lower_hinge_T_isotopy_with_consolidation_box([T[0], T[1]], V1)
                top_y = max([v[1] for v in consolidation_box])
                exit_disk = sorted([v for v in consolidation_box if v[1] == top_y])
                #print('this is the exit disk after isotopy',exit_disk)
                #invalid_exit_disks.append(exit_disk)
                print('This is the diagram after the hinge T isotopy')
                draw_rectangular_diagram(V_new)
                
                #9/27/2026 Code verification comment out when done
                #if not verify_unknot_boolean(V_new):
                #    raise TypeError("The last simplification changed knot type!")
                
                V1=V_new
                if V1 not in seen_diagrams:
                    #computationally expensive but covers a lot of bases
                    V1=perform_v1b_corner_rigid_simplifications(V1)
                    #easier computationally
                    #VS = get_v1b_reduced_diagram(V1)
                    #V1 = VS[-1]

                else:
                    print('This rectangular diagram has been seen before, attempting to find another valid and essential push T')
                seen_diagrams.append(V1)
                              
            else:
                # No valid T's at all → stop
                break
    return V1
    

def perform_single_hinge_T_and_simplify(V1, seen_diagrams, invalid_exit_disks):

    ############################################################
    # Perform exactly ONE valid essential hinge T move.
    #
    # The function returns:
    #     (V_new, exit_disk)
    #
    # where exit_disk is the exit disk associated to the
    # selected hinge T BEFORE the isotopy.
    #
    # If no valid hinge T is available, returns:
    #     (V1, None)
    #
    # invalid_exit_disks and seen_diagrams are passed in so that
    # the outer simplification loop can maintain this state
    # across successive single hinge T moves.
    ############################################################

    if len(V1) // 2 == 2:
        return V1, None

    ############################################################
    # Find essential hinge T's
    ############################################################

    upper_hinge_Ts, lower_hinge_Ts = find_all_essential_hinge_Ts(V1)

    ############################################################
    # Filter upper hinge T's that do not pass through infinity
    ############################################################

    hinge_Ts_not_through_infinity = []

    for hinge_T in upper_hinge_Ts:
        if check_if_T_through_infinity(
            hinge_T, [0, 0], whichT='upper'
        ):
            hinge_Ts_not_through_infinity.append(hinge_T)

    upper_hinge_Ts = hinge_Ts_not_through_infinity

    ############################################################
    # Filter upper hinge T's whose exit disks have already
    # been marked invalid
    ############################################################

    filtered_Ts = []

    for T in upper_hinge_Ts:

        T_mid = T[1]

        min_y = min(v[1] for v in T_mid)

        exit_disk = sorted(
            [v for v in T_mid if v[1] == min_y]
        )

        if exit_disk not in invalid_exit_disks:
            filtered_Ts.append(T)

    ############################################################
    # If there is an eligible upper hinge T, choose one
    ############################################################

    if filtered_Ts:

        # Determine the strand set associated to the first T
        T = filtered_Ts[0]

        vertices_in_T = (
            find_vertices_in_box(T[0], V1, where='std')
            + find_vertices_in_box(T[1], V1, where='std')
        )

        # Only compare T's involving the same set of strands
        candidates = []

        for T in filtered_Ts:

            vertices = (
                find_vertices_in_box(T[0], V1, where='std')
                + find_vertices_in_box(T[1], V1, where='std')
            )

            if vertices == vertices_in_T:
                candidates.append(T)

        ########################################################
        # Choose minimum width
        ########################################################

        widths = [
            abs(T[0][0][0] - T[0][1][0])
            for T in candidates
        ]

        min_width = min(widths)

        best_Ts = [
            T for T in candidates
            if abs(T[0][0][0] - T[0][1][0]) == min_width
        ]

        ########################################################
        # Among minimum-width T's, choose maximum boundary
        # height
        ########################################################

        def boundary_height(T):
            ys = [point[1] for point in T[0]]
            return max(ys) - min(ys)

        best_T = max(best_Ts, key=boundary_height)

        T = best_T

        ########################################################
        # Compute the exit disk for THIS selected T
        # before performing the isotopy
        ########################################################

        T_mid = T[1]

        min_y = min(v[1] for v in T_mid)

        exit_disk = sorted(
            [v for v in T_mid if v[1] == min_y]
        )

        print('This is a valid and essential upper hinge T')

        draw_virtual_type2_boxes_diagram(
            T[0],
            T[1],
            V1,
            where1='horiz-infty',
            where2='std',
            color1='deeppink'
        )

        ########################################################
        # Perform exactly ONE upper hinge T isotopy
        ########################################################

        _, consolidation_box, V_new = \
            perform_upper_hinge_T_isotopy_with_consolidation_box(
                [T[0], T[1]],
                V1
            )

        draw_rectangular_diagram(V_new)

        ########################################################
        # Return immediately after this ONE hinge T
        ########################################################

        return V_new, exit_disk

    ############################################################
    # If no eligible upper T exists, check lower hinge T's
    ############################################################

    hinge_Ts_not_through_infinity = []

    for hinge_T in lower_hinge_Ts:
        if check_if_T_through_infinity(
            hinge_T, [0, 0], whichT='lower'
        ):
            hinge_Ts_not_through_infinity.append(hinge_T)

    lower_hinge_Ts = hinge_Ts_not_through_infinity

    ############################################################
    # Filter lower hinge T's by invalid exit disks
    ############################################################

    filtered_Ts = []

    for T in lower_hinge_Ts:

        T_mid = T[1]

        max_y = max(v[1] for v in T_mid)

        exit_disk = sorted(
            [v for v in T_mid if v[1] == max_y]
        )

        if exit_disk not in invalid_exit_disks:
            filtered_Ts.append(T)

    ############################################################
    # If there is an eligible lower hinge T, choose one
    ############################################################

    if filtered_Ts:

        T = filtered_Ts[0]

        vertices_in_T = (
            find_vertices_in_box(T[0], V1, where='std')
            + find_vertices_in_box(T[1], V1, where='std')
        )

        candidates = []

        for T in filtered_Ts:

            vertices = (
                find_vertices_in_box(T[0], V1, where='std')
                + find_vertices_in_box(T[1], V1, where='std')
            )

            if vertices == vertices_in_T:
                candidates.append(T)

        ########################################################
        # Choose minimum width
        ########################################################

        widths = [
            abs(T[0][0][0] - T[0][1][0])
            for T in candidates
        ]

        min_width = min(widths)

        best_Ts = [
            T for T in candidates
            if abs(T[0][0][0] - T[0][1][0]) == min_width
        ]

        ########################################################
        # Among minimum-width T's, choose maximum boundary
        # height
        ########################################################

        def boundary_height(T):
            ys = [point[1] for point in T[0]]
            return max(ys) - min(ys)

        best_T = max(best_Ts, key=boundary_height)

        T = best_T

        ########################################################
        # Compute exit disk for the selected lower T
        ########################################################

        T_mid = T[1]

        max_y = max(v[1] for v in T_mid)

        exit_disk = sorted(
            [v for v in T_mid if v[1] == max_y]
        )

        print('This is a valid and essential lower hinge T')

        draw_virtual_type2_boxes_diagram(
            T[0],
            T[1],
            V1,
            where1='horiz-infty',
            where2='std',
            color1='deeppink'
        )

        ########################################################
        # Perform exactly ONE lower hinge T isotopy
        ########################################################

        _, consolidation_box, V_new = \
            perform_lower_hinge_T_isotopy_with_consolidation_box(
                [T[0], T[1]],
                V1
            )

        draw_rectangular_diagram(V_new)

        ########################################################
        # Return immediately after this ONE hinge T
        ########################################################

        return V_new, exit_disk

    ############################################################
    # No eligible hinge T exists
    ############################################################

    print('No valid essential hinge T moves remain.')

    return V1, None
    





        
##########################################################################################################################        
def check_if_T_through_infinity(T,cyclic_permutation,whichT):
    
    phi_infinity=cyclic_permutation[1]
    theta_infinity=cyclic_permutation[0]
    
    box_1=T[0] #this is the wings of the T
    box_2=T[1] #this is the neck or landing zone
    
    if whichT=='upper':
         #We need to find the dimensions of the T in the diagram V, and compare it to the i,j values
        y_values = [y for _, y in box_2] #look at the y_values of the neck
        min_y = min(y_values)
        bottom_of_T=min_y

        if not -bottom_of_T<phi_infinity: 
            #If you have an upward T (so that the exit disk is the minimal y-value of the T) then the top of the T
            #was never at the bottom of the diagram.  It was somewhere in the diagram and then moved up.  
            # If the bottom of the T has a -y-value smaller than the number of vertical perms then it began at the top.  I am checking this does not happen
            return True #This T was not through infinity, sorry about all the negation. 
        return False  
    
    #Is it the same criterion for a lower T? When is a lower T actually realized at the bottom of the diagram? Do we need to go through the cyclic permutations again?
    
    elif whichT=='lower':  #DOUBLE CHECK THIS 3/6/2026
        y_values = [y for _, y in box_2]
        max_y = max(y_values)
        top_of_T = max_y

        if -top_of_T > phi_infinity:
            return True
        return False
        
        
        
    else: raise TypeError("whichT must be either 'upper' or 'lower'")
        
        
        
def simplify_with_T_and_cyclic_permutations(V):
    ################################################
    #Aux function for looking at consolidation boxes
    def intersects_any_box(vertices, boxes):
        for box in boxes:
            box_vertices = find_vertices_in_box(box, vertices, where='std')
            if box_vertices:
                return True
        return False
    ################################################
    n = len(V) // 2
    seen_diagrams=[]
    performed_Ts=[]
    while True: #I will only exit this loop on a break
        horizontals, _ = sort_vertices_into_verticals_and_horizontals(V) #find the new horizontals in V after the wings have shrunk
        consolidation_boxes=[]
        seen_diagrams.append(V)
        
        made_progress = False #this conditional is set to True if a T-move is performed
        # -------------------------
        # APPLY T-MOVES
        # -------------------------
        
        while True: 
            upper_push_Ts, lower_push_Ts = find_all_essential_push_Ts(V)
            upper_hinge_Ts, lower_hinge_Ts = find_all_essential_hinge_Ts(V)

            moves = []
            for T in upper_push_Ts:
                moves.append(('push_upper', T))
            for T in lower_push_Ts:
                moves.append(('push_lower', T))
            for T in upper_hinge_Ts:
                moves.append(('hinge_upper', T))
            for T in lower_hinge_Ts:
                moves.append(('hinge_lower', T))

            if not moves:
                break   # This breaks the inside while loop I cannot find anymore T's and will do a cyclic perm 
            
            #There are T's but now we need to be sure they do not correspond to previously done T's
            found_move = False
            for kind, T in moves:
                vertices_in_T=find_vertices_in_box(T[0], V, where='std') #these are the vertices not in the neck. They cannot be a part of a previous consolidation box
                if [T, V] not in performed_Ts and not intersects_any_box(vertices_in_T, consolidation_boxes): #A new one exists that is not apart of a consolidated box
                        
                    #Note eventually you will want to just check the part of the T that is important. This may require some case counting
                    found_move = True # we found a new T
                    break #Exit for loop 

            if not found_move: #if you do not have a new T move do a cyclic perm, otherwise do the T 
                break
                
            #If you are here there is a T move on the diagram so we will 'make_progress'
            #This means we will not exit the inner while loop on this iteration
            made_progress = True
                
            print('Applying move:', kind) 
            draw_virtual_type2_boxes_diagram(
                T[0], T[1], V,
                where1='horiz-infty', where2='std',
                color1='purple' if 'push' in kind else 'deeppink'
            )

            performed_Ts.append([T,V]) #I never want to do this T with this particular V again.
            
            if kind == 'push_upper':
                box,V = perform_upper_push_T_isotopy_with_consolidation_box([T[0], T[1]], V)
                consolidation_boxes.append(box)
            elif kind == 'push_lower':
                box,V = perform_lower_push_T_isotopy_with_consolidation_box([T[0], T[1]], V)
                consolidation_boxes.append(box)
            elif kind == 'hinge_upper':
                box,V = perform_upper_hinge_T_isotopy_with_consolidation_box([T[0], T[1]], V)
                consolidation_boxes.append(box)
            elif kind == 'hinge_lower':
                box,V = perform_lower_hinge_T_isotopy_with_consolidation_box([T[0], T[1]], V)
                consolidation_boxes.append(box)
            draw_rectangular_diagram(V)
            

            if obviously_split_q(V): #Did the last T move split the link?
                return V #If yes exit the outer while loop

        # -------------------------
        # 2. If no moves we broke the inner while loop and will apply a cylic permutation
        # -------------------------
        
        if not made_progress:
            # try all cyclic permutations and pick one (or just pick one rule)
            R_matrix = generate_all_cyclic_permutations_matrix(V)

            found_new = False
            for i in range(n):
                for j in range(n):
                    V1 = R_matrix[j][i]
                    if V1 not in seen_diagrams:
                        V = V1
                        found_new = True
                        break
                if found_new:
                    print('Applying a cyclic permutation')
                    break #restart the outer while loop with this new vertex set 
            # if no permutation changes anything, we're truly stuck
            if not found_new:
                return V
            
        
        

################################################# AUXILLARY ###############################################################

def verify_unknot(V):
    G=vertexset_to_XOGrid(V)
    braid=convert_to_braid(G, optimized = 'Y', verbose = False)
    #B = ClosedBraid(braid)
    B = Link(braid_closure=braid)
    print(B.knot_floer_homology())
    
def verify_unknot_boolean(V):
    G = vertexset_to_XOGrid(V)
    braid = convert_to_braid(G, optimized='Y', verbose=False)
    try:
        B = Link(braid_closure=braid)
        B.simplify('global')
        if len(B.crossings)==0:
        # Return True if seifert_genus is 0, else False
            return True
        else:
            return False
    except ValueError:
        print('Could not verify')
        return False    
    

        
############################################### END FUNCTIONS NEEDED FOR T'S ##############################################     ###################################################################################################################
def update_consolidation_boxes_after_isotopy(consolidation_boxes,V_old,coord_map):
    new_consolidation_boxes=[]
    for box in consolidation_boxes:
        verts_in_box=find_vertices_in_box(box,V_old,where='std')
        if not verts_in_box: #6/5/2026 Figuring out why this happens. I think if current T encompasses a previous one this happens.
            continue
        #print('These are verts in current box',verts_in_box)
        tuple_verts_in_box=[tuple(c) for c in verts_in_box]
        vertices_in_box_after_isotopy = [coord_map.get(v,v) for v in tuple_verts_in_box]
        #print('These are verts in box after T isotopy',vertices_in_box_after_isotopy)
        xs = [x for x,y in vertices_in_box_after_isotopy]
        ys = [y for x,y in vertices_in_box_after_isotopy]
        if xs and ys:
            xmin = min(xs)
            xmax = max(xs)
            ymin = min(ys)
            ymax = max(ys)
            new_box = [
                [xmin - 0.5, ymax + 0.5],
                [xmin - 0.5, ymin - 0.5],
                [xmax + 0.5, ymax + 0.5],
                [xmax + 0.5, ymin - 0.5]]
            new_consolidation_boxes.append(new_box)
        else:
            raise Exception('There is something wrong')
    return new_consolidation_boxes
################################################################################################################   
        
###### DEMO #####
"""G=load_unknot('culprit')
V=grid_to_vertex_set(G)
fully_simplify_via_cyclic_permutations(V, verbose=True)"""

        
        
#### DEMO ###
"""G=load_unknot('Hard_Unknot_D')
V=grid_to_vertex_set(G)
VS = All_Virtual_Boxes_Simplification_Updated(V_new) #This function does exactly this until it cannot anymore
R = VS[-1]
draw_rectangular_diagram(R)
R_matrix=generate_all_cyclic_permutations_matrix(R)

def show_all_essential_push_Ts_across_cyclic_permutations(R_matrix):
    n = len(R_matrix) #The number of rows
    for i in range(n):          # vertical cyclic permutations
        for j in range(n):      # horizontal cyclic permutations
            print('Checking cyclic permutation',[i,j])
            V = R_matrix[i][j] #the vertex set obtained by the original by i,j perms
            push_Ts=find_all_essential_push_Ts(V)
    return []
V=show_all_essential_push_Ts_across_cyclic_permutations(R_matrix)
"""
#### DEMO 2 ####

""""G=load_unknot('Hard_Unknot_A')
V=grid_to_vertex_set(G)
R_matrix=generate_all_cyclic_permutations_matrix(V)

def show_all_essential_hinge_Ts_across_cyclic_permutations(R_matrix):
    n = len(R_matrix) #The number of rows
    for i in range(n):          # vertical cyclic permutations
        for j in range(n):      # horizontal cyclic permutations
            print('Checking cyclic permutation',[i,j])
            V = R_matrix[i][j] #the vertex set obtained by the original by i,j perms
            hinge_Ts=find_all_essential_hinge_Ts(V)
    return []
V=show_all_essential_hinge_Ts_across_cyclic_permutations(R_matrix)"""