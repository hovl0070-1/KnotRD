from collections import defaultdict
from v1b_reduced_algorithm import get_v1b_reduced_diagram, check_type_1_box_for_simplification
from rechoosing_infinity import *
from rectangular_diagram_manipulation import *

def find_all_possible_top_Ts(V):
    n = len(V) // 2
    half_x = [i + 0.5 for i in range(0, n + 1)]
    ys = [-i - 0.5 for i in range(1, n)]

    Ttops = []
    _, verticals = sort_vertices_into_verticals_and_horizontals(V)

    # Pre-index verticals by x-coordinate for O(1) lookups
    verts_by_x = defaultdict(list)
    for v in verticals:
        verts_by_x[v[0][0]].append(v)

    top_y_levels = [-i - 0.5 for i in range(0, n)]

    for top_y in top_y_levels:
        # Pre-filter valid y-levels below top_y
        valid_ys = [y for y in ys if y < top_y]
        if not valid_ys:
            continue

        for i, x in enumerate(half_x):
            # Pre-filter left verticals near x
            verts_left = [v for v in verts_by_x[x + 0.5] if min(v[0][1], v[1][1]) < top_y]

            for x1 in half_x[i + 2:]:
                # Pre-filter right verticals near x1
                verts_right = [v for v in verts_by_x[x1 - 0.5] if min(v[0][1], v[1][1]) < top_y]

                verticals_near_xs = verts_left + verts_right
                if len(verticals_near_xs) < 2:
                    continue

                v_check = verticals_near_xs[:2]

                for y in valid_ys:
                    Ttop = [[x, top_y], [x, y], [x1, top_y], [x1, y]]

                    # Verify verticals have vertices inside Ttop
                    valid_verticals = sum(
                        1 for v in v_check 
                        if check_if_vertex_in_box(v[0], Ttop, where='std') or 
                           check_if_vertex_in_box(v[1], Ttop, where='std')
                    )
                    if valid_verticals < 2:
                        continue

                    verts_crossing_b_arc_region = find_vertices_in_box(Ttop, V, where='horiz-infty')
                    if not check_type_1_box_for_simplification(Ttop, V, where='horiz-infty'):
                        continue

                    # Fast set lookup for vertical crossing check
                    verts_set = set(map(tuple, verts_crossing_b_arc_region))
                    has_crossing = any(
                        (tuple(v[0]) in verts_set) ^ (tuple(v[1]) in verts_set)
                        for v in verticals
                    )

                    if not has_crossing:
                        Ttops.append(Ttop)

    return Ttops


def find_all_possible_bottom_Ts(V):
    n = len(V) // 2
    half_x = [i + 0.5 for i in range(0, n + 1)]
    ys = [-i - 0.5 for i in range(0, n)]

    Tbots = []
    _, verticals = sort_vertices_into_verticals_and_horizontals(V)

    # Pre-index verticals by x-coordinate
    verts_by_x = defaultdict(list)
    for v in verticals:
        verts_by_x[v[0][0]].append(v)

    bottom_y_levels = [-i - 0.5 for i in range(1, n)]

    for bottom_y in bottom_y_levels:
        valid_ys = [y for y in ys if y > bottom_y]
        if not valid_ys:
            continue

        for i, x in enumerate(half_x):
            verts_left = [v for v in verts_by_x[x + 0.5] if max(v[0][1], v[1][1]) > bottom_y]

            for x1 in half_x[i + 2:]:
                verts_right = [v for v in verts_by_x[x1 - 0.5] if max(v[0][1], v[1][1]) > bottom_y]

                verticals_near_xs = verts_left + verts_right
                if len(verticals_near_xs) < 2:
                    continue

                v_check = verticals_near_xs[:2]

                for y in valid_ys:
                    Tbot = [[x, bottom_y], [x, y], [x1, bottom_y], [x1, y]]

                    valid_verticals = sum(
                        1 for v in v_check 
                        if check_if_vertex_in_box(v[0], Tbot, where='std') or 
                           check_if_vertex_in_box(v[1], Tbot, where='std')
                    )
                    if valid_verticals < 2:
                        continue

                    verts_crossing_b_arc_region = find_vertices_in_box(Tbot, V, where='horiz-infty')
                    if not check_type_1_box_for_simplification(Tbot, V, where='horiz-infty'):
                        continue

                    verts_set = set(map(tuple, verts_crossing_b_arc_region))
                    has_crossing = any(
                        (tuple(v[0]) in verts_set) ^ (tuple(v[1]) in verts_set)
                        for v in verticals
                    )

                    if not has_crossing:
                        Tbots.append(Tbot)

    return Tbots


def find_all_essential_push_Ts(V):
    n = len(V) // 2
    horizontals, _ = sort_vertices_into_verticals_and_horizontals(V)
    
    # Pre-index horizontals by y-coordinate for O(1) lookup
    horiz_by_y = {h[0][1]: h for h in horizontals}

    Ttops = find_all_possible_top_Ts(V)
    upper_push_Ts = []
    all_y_levels = [-i - 0.5 for i in range(1, n + 1)]

    for Ttop in Ttops:
        xs = [v[0] for v in Ttop]
        ys = [v[1] for v in Ttop]
        x, x1 = min(xs), max(xs)
        y_top, y_real_top = min(ys), max(ys)

        bottom_ys = [y_bot for y_bot in all_y_levels if y_bot < y_top]

        for y_bot in bottom_ys:
            Tbot = [[x, y_top], [x, y_bot], [x1, y_top], [x1, y_bot]]
            full_neck = [[x, y_real_top], [x1, y_real_top], [x, y_bot], [x1, y_bot]]

            if not check_type_1_box_for_simplification(full_neck, V, where='std'):
                continue

            verts_in_complement = find_vertices_in_box(Tbot, V, where='horiz-infty')
            if not verts_in_complement:
                continue

            y_val_below_neck = int(y_bot - 0.5)
            horizontal_below_neck = horiz_by_y.get(y_val_below_neck, None)

            is_blocked = False
            if horizontal_below_neck is None:
                is_blocked = True
            else:
                x_left, x_right = sorted([horizontal_below_neck[0][0], horizontal_below_neck[1][0]])
                neck_left, neck_right = sorted([x, x1])
                interleaves = ((x_left < neck_left < x_right < neck_right) or 
                               (neck_left < x_left < neck_right < x_right))
                if interleaves:
                    is_blocked = True

            if is_blocked:
                upper_push_Ts.append([Ttop, Tbot])

    Tbots = find_all_possible_bottom_Ts(V)
    lower_push_Ts = []

    for Tbot in Tbots:
        xs = [v[0] for v in Tbot]
        ys = [v[1] for v in Tbot]
        x, x1 = min(xs), max(xs)
        y_bot, y_real_bot = max(ys), min(ys)

        top_ys = [y_top for y_top in all_y_levels if y_top > y_bot]

        for y_top in top_ys:
            Ttop = [[x, y_bot], [x, y_top], [x1, y_bot], [x1, y_top]]
            full_neck = [[x, y_real_bot], [x1, y_real_bot], [x, y_bot], [x1, y_bot]]

            if not check_type_1_box_for_simplification(full_neck, V, where='std'):
                continue

            verts_in_complement = find_vertices_in_box(Ttop, V, where='horiz-infty')
            if not verts_in_complement:
                continue

            y_val_above_neck = int(y_top + 0.5)
            horizontal_above_neck = horiz_by_y.get(y_val_above_neck, None)

            is_blocked = False
            if horizontal_above_neck is None:
                is_blocked = True
            else:
                x_left, x_right = sorted([horizontal_above_neck[0][0], horizontal_above_neck[1][0]])
                neck_left, neck_right = sorted([x, x1])
                interleaves = ((x_left < neck_left < x_right < neck_right) or 
                               (neck_left < x_left < neck_right < x_right))
                if interleaves:
                    is_blocked = True

            if is_blocked:
                lower_push_Ts.append([Tbot, Ttop])

    return upper_push_Ts, lower_push_Ts


def find_all_essential_hinge_Ts(V):
    n = len(V) // 2
    horizontals, _ = sort_vertices_into_verticals_and_horizontals(V)
    horiz_by_y = {h[0][1]: h for h in horizontals}

    Ttops = find_all_possible_top_Ts(V)
    upper_hinge_Ts = []
    all_y_levels = [-i - 0.5 for i in range(1, n)]

    for Ttop in Ttops:
        xs = [v[0] for v in Ttop]
        ys = [v[1] for v in Ttop]
        x, x1 = min(xs), max(xs)
        y_top, bot_of_Ttop = max(ys), min(ys)

        bottom_ys = [y_bot for y_bot in all_y_levels if y_bot < y_top]

        for y_bot in bottom_ys:
            Tmid = [[x, y_top], [x, y_bot], [x1, y_top], [x1, y_bot]]

            if not check_type_1_box_for_simplification(Tmid, V, where='std'):
                continue

            verts_in_complement = [
                v for v in find_vertices_in_box(Tmid, V, where='horiz-infty') 
                if v[1] < bot_of_Ttop
            ]
            if not verts_in_complement:
                continue

            y_val_above_neck = int(y_bot + 0.5)
            horizontal_above_neck = horiz_by_y.get(y_val_above_neck, None)

            is_blocked = False
            if horizontal_above_neck is None:
                is_blocked = True
            else:
                x_left, x_right = sorted([horizontal_above_neck[0][0], horizontal_above_neck[1][0]])
                neck_left, neck_right = sorted([x, x1])
                interleaves = ((x_left < neck_left < x_right < neck_right) or 
                               (neck_left < x_left < neck_right < x_right))
                if interleaves:
                    is_blocked = True

            if is_blocked:
                upper_hinge_Ts.append([Ttop, Tmid])

    Tbots = find_all_possible_bottom_Ts(V)
    lower_hinge_Ts = []

    for Tbot in Tbots:
        xs = [v[0] for v in Tbot]
        ys = [v[1] for v in Tbot]
        x, x1 = min(xs), max(xs)
        y_bot, top_of_Tbot = min(ys), max(ys)

        top_ys = [y_top for y_top in all_y_levels if y_top > y_bot]

        for y_top in top_ys:
            Tmid = [[x, y_top], [x, y_bot], [x1, y_top], [x1, y_bot]]

            if not check_type_1_box_for_simplification(Tmid, V, where='std'):
                continue

            verts_in_complement = [
                v for v in find_vertices_in_box(Tmid, V, where='horiz-infty') 
                if v[1] > top_of_Tbot
            ]
            if not verts_in_complement:
                continue

            y_val_below_neck = int(y_top - 0.5)
            horizontal_below_neck = horiz_by_y.get(y_val_below_neck, None)

            is_blocked = False
            if horizontal_below_neck is None:
                is_blocked = True
            else:
                x_left, x_right = sorted([horizontal_below_neck[0][0], horizontal_below_neck[1][0]])
                neck_left, neck_right = sorted([x, x1])
                interleaves = ((x_left < neck_left < x_right < neck_right) or 
                               (neck_left < x_left < neck_right < x_right))
                if interleaves:
                    is_blocked = True

            if is_blocked:
                lower_hinge_Ts.append([Tbot, Tmid])

    return upper_hinge_Ts, lower_hinge_Ts

def perform_upper_push_T_isotopy(push_T,V):
    
    #this is if push_T is an upper push T
    _, verticals = sort_vertices_into_verticals_and_horizontals(V)

    Ttop = push_T[0]   # 4 vertices defining the top box of the T
    Tbot = push_T[1]   # 4 vertices defining the bottom box of the T

    xs = [vert[0] for vert in Ttop]
    left_side_of_Ttop = min(xs)
    right_side_of_Ttop = max(xs)
    
    ys = [vert[1] for vert in Ttop]
    top_of_Ttop = max(ys)
    bot_of_Ttop = min(ys)
    
    xs = [vert[0] for vert in Tbot]
    left_side_of_Tbot = min(xs)
    right_side_of_Tbot = max(xs)
    
    ys = [vert[1] for vert in Tbot]
    top_of_Tbot = max(ys)
    bot_of_Tbot = min(ys)
    

    vertices_crossing_b_arc_region = find_vertices_in_box(Ttop, V, where='horiz-infty')
   
    

    verticals_in_left_wing = [
        v for v in verticals
        if v[0] in vertices_crossing_b_arc_region
        and v[1] in vertices_crossing_b_arc_region
        and v[0][0] < left_side_of_Ttop]
    
    
    #to perform the series of commutations there need to be vertices under the left wing, otherwise we will have to change the boundary of the Ttop. 
    vertices_under_wings = find_vertices_in_box(Ttop, V, where='horiz-vert-infty') #this will capture everything under the wings on both sides
    vertices_under_left_wing=[v for v in vertices_under_wings if v[0]<left_side_of_Ttop]
    vertices_under_right_wing=[v for v in vertices_under_wings if v[0]>right_side_of_Ttop]
    
    verticals_in_right_wing = [
        v for v in verticals
        if v[0] in vertices_crossing_b_arc_region
        and v[1] in vertices_crossing_b_arc_region
        and v[0][0] > right_side_of_Ttop]
    
    
    #Now we perform a series of commutations that push in these verticals:
    #Step 1: Commute the verticals in the left wing to the right past the left side of Ttop
    
    #The verticals need to be sorted correctly so the pushing occurs in the correct order:
    if verticals_in_left_wing:
        if not vertices_under_left_wing:
            #redefine the top box to include the far left side of the diagram.
            
            left_side_of_Ttop = 0.5
            Ttop = [[left_side_of_Ttop,top_of_Ttop],[left_side_of_Ttop,bot_of_Ttop],[right_side_of_Ttop, top_of_Ttop],[right_side_of_Ttop, bot_of_Ttop]]   # 4 vertices defining the top box of the T
            Tbot = [[left_side_of_Ttop,top_of_Tbot],[left_side_of_Ttop,bot_of_Tbot],[right_side_of_Ttop, top_of_Tbot],[right_side_of_Ttop, bot_of_Tbot]]
          
        else: #perform the regular commutations
            verticals_in_left_wing.sort(key=lambda v: v[0][0])
            number_of_left_commutations=len(verticals_in_left_wing)
            
            
            
            #The -0.5 comes from the fact that the edge of this box is on a half value, and the edges that it must commute past are on integer values.
            target_edge=[[left_side_of_Ttop-0.5,top_of_Ttop],[left_side_of_Ttop-0.5,bot_of_Ttop]]

            V=perform_vertical_commutation(verticals_in_left_wing,target_edge,V) #perform the series of commutations
            
            #the commutations will move the edge of the box to the left by the number of commutations
            left_side_of_Ttop=left_side_of_Ttop-number_of_left_commutations
            
            #redefine the box now after the commuations
            Ttop = [[left_side_of_Ttop,top_of_Ttop],[left_side_of_Ttop,bot_of_Ttop],[right_side_of_Ttop, top_of_Ttop],[right_side_of_Ttop, bot_of_Ttop]]   # 4 vertices defining the top box of the T
            Tbot = [[left_side_of_Ttop,top_of_Tbot],[left_side_of_Ttop,bot_of_Tbot],[right_side_of_Ttop, top_of_Tbot],[right_side_of_Ttop, bot_of_Tbot]]
    
    #Step 2: Commute the verticals in the right wing to the left past the right side of Ttop
    
    if verticals_in_right_wing:
        if not vertices_under_right_wing:
            right_side_of_Ttop = len(V)//2+0.5
            Ttop = [[left_side_of_Ttop,top_of_Ttop],[left_side_of_Ttop,bot_of_Ttop],[right_side_of_Ttop, top_of_Ttop],[right_side_of_Ttop, bot_of_Ttop]]
            Tbot = [[left_side_of_Ttop,top_of_Tbot],[left_side_of_Ttop,bot_of_Tbot],[right_side_of_Ttop, top_of_Tbot],[right_side_of_Ttop, bot_of_Tbot]]
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
    
    #Uncomment for Debugging
    #print('This is the T after the wings are shrunk')
    #draw_virtual_type2_boxes_diagram(Ttop, Tbot, V, where1='horiz-infty', where2='std',color1-)
    
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
    
    
    #Now the horizontals need to be sorted by y-value with larger y-value first
    horizontals_in_Ttop.sort(key=lambda v: v[0][1], reverse=True)
    target_edge=[[left_side_of_Tbot,bot_of_Tbot-0.5],[right_side_of_Tbot,bot_of_Tbot-0.5]]
    target_edge=[[left_side_of_Tbot,bot_of_Tbot+0.5],[right_side_of_Tbot,bot_of_Tbot+0.5]]
    V=perform_horizontal_commutation(horizontals_in_Ttop,target_edge,V)
    
    #print('This is the push T after the full isotopy')
    #draw_virtual_type2_boxes_diagram(Ttop, Tbot, V, where1='horiz-infty', where2='std')
    
    
    return V



def perform_lower_push_T_isotopy(push_T,V):
    
    
    #this is if push_T is a lower push T
    _, verticals = sort_vertices_into_verticals_and_horizontals(V)

    Ttop = push_T[1]   # 4 vertices defining the top box of the T
    Tbot = push_T[0]   # 4 vertices defining the bottom box of the T

    xs = [vert[0] for vert in Tbot]
    left_side_of_Tbot = min(xs)
    right_side_of_Tbot = max(xs)
    
    ys = [vert[1] for vert in Tbot]
    top_of_Tbot = max(ys)
    bot_of_Tbot = min(ys)
    
    xs = [vert[0] for vert in Ttop]
    left_side_of_Ttop = min(xs)
    right_side_of_Ttop = max(xs)
    
    ys = [vert[1] for vert in Ttop]
    top_of_Ttop = max(ys)
    bot_of_Ttop = min(ys)

    vertices_crossing_b_arc_region = find_vertices_in_box(Tbot, V, where='horiz-infty')
   
    

    verticals_in_left_wing = [
        v for v in verticals
        if v[0] in vertices_crossing_b_arc_region
        and v[1] in vertices_crossing_b_arc_region
        and v[0][0] < left_side_of_Tbot]
    
    #print('here are the verticals in the left wing',verticals_in_left_wing)
    #to perform the series of commutations there need to be vertices under the left wing, otherwise we will have to change the boundary of the Ttop. 

    vertices_above_wings = find_vertices_in_box(Tbot, V, where='horiz-vert-infty') #this will capture everything under the wings on both sides
    vertices_under_left_wing=[v for v in vertices_above_wings if v[0]<left_side_of_Tbot]
    vertices_under_right_wing=[v for v in vertices_above_wings if v[0]>right_side_of_Tbot]
    
    verticals_in_right_wing = [
        v for v in verticals
        if v[0] in vertices_crossing_b_arc_region
        and v[1] in vertices_crossing_b_arc_region
        and v[0][0] > right_side_of_Tbot]
    
    
    #Now we perform a series of commutations that push in these verticals:
    #Step 1: Commute the verticals in the left wing to the right past the left side of Ttop
    
    #The verticals need to be sorted correctly so the pushing occurs in the correct order:
    if verticals_in_left_wing:
        if not vertices_under_left_wing:
            #redefine the top box to include the far left side of the diagram.
            
            left_side_of_Tbot = 0.5
            Tbot = [[left_side_of_Tbot,top_of_Tbot],[left_side_of_Tbot,bot_of_Tbot],[right_side_of_Tbot, top_of_Tbot],[right_side_of_Tbot, bot_of_Tbot]]   # 4 vertices defining the bottom box of the T
            Ttop = [[left_side_of_Tbot,top_of_Ttop],[left_side_of_Tbot,bot_of_Ttop],[right_side_of_Tbot, top_of_Ttop],[right_side_of_Tbot, bot_of_Ttop]]
          
        else: #perform the regular commutations
            verticals_in_left_wing.sort(key=lambda v: v[0][0])
            number_of_left_commutations=len(verticals_in_left_wing)
            
            
            
            #The -0.5 comes from the fact that the edge of this box is on a half value, and the edges that it must commute past are on integer values.
            target_edge=[[left_side_of_Tbot-0.5,top_of_Tbot],[left_side_of_Tbot-0.5,bot_of_Tbot]]

            V=perform_vertical_commutation(verticals_in_left_wing,target_edge,V) #perform the series of commutations
            
            #the commutations will move the edge of the box to the left by the number of commutations
            left_side_of_Tbot=left_side_of_Tbot-number_of_left_commutations
            
            #redefine the box now after the commuations
            Tbot = [[left_side_of_Tbot,top_of_Tbot],[left_side_of_Tbot,bot_of_Tbot],[right_side_of_Tbot, top_of_Tbot],[right_side_of_Tbot, bot_of_Tbot]]   # 4 vertices defining the bottom box of the T
            Ttop = [[left_side_of_Tbot,top_of_Ttop],[left_side_of_Tbot,bot_of_Ttop],[right_side_of_Tbot, top_of_Ttop],[right_side_of_Tbot, bot_of_Ttop]]
    
    #Step 2: Commute the verticals in the right wing to the left past the right side of Ttop
    
    if verticals_in_right_wing:
        if not vertices_under_right_wing:
            right_side_of_Tbot = len(V)//2+0.5
            Tbot = [[left_side_of_Tbot,top_of_Tbot],[left_side_of_Tbot,bot_of_Tbot],[right_side_of_Tbot, top_of_Tbot],[right_side_of_Tbot, bot_of_Tbot]]
            Ttop = [[left_side_of_Tbot,top_of_Ttop],[left_side_of_Tbot,bot_of_Ttop],[right_side_of_Tbot, top_of_Ttop],[right_side_of_Tbot, bot_of_Ttop]]
        else:
            verticals_in_right_wing.sort(key=lambda v: v[0][0])
            
            number_of_right_commutations=len(verticals_in_right_wing)
           
            
            target_edge=[[right_side_of_Tbot+0.5,top_of_Tbot],[right_side_of_Tbot+0.5,bot_of_Tbot]]

            V=perform_vertical_commutation(verticals_in_right_wing,target_edge,V) #perform the series of commutations
            
            #the commutations will move the edge of the box to the right by the number of commutations
            right_side_of_Tbot=right_side_of_Tbot+number_of_right_commutations
            
            #redefine the box now after the commuations
            Tbot = [[left_side_of_Tbot,top_of_Tbot],[left_side_of_Tbot,bot_of_Tbot],[right_side_of_Tbot, top_of_Tbot],[right_side_of_Tbot, bot_of_Tbot]]   # 4 vertices defining the top box of the T
            Ttop = [[left_side_of_Tbot,top_of_Ttop],[left_side_of_Tbot,bot_of_Ttop],[right_side_of_Tbot, top_of_Ttop],[right_side_of_Tbot, bot_of_Ttop]]
    
    #Uncomment for Debugging
    #print('This is the T after the wings are shrunk')
    #draw_virtual_type2_boxes_diagram(Ttop, Tbot, V, where1='std', where2='horiz-infty',color1='purple')
    
    #Step 3: Commute the horizontals in this box down past the top edge of the Ttop.
    
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
    
    
    #Now the horizontals need to be sorted by y-value with larger y-value first
    horizontals_in_Tbot.sort(key=lambda v: v[0][1], reverse=True)
    target_edge=[[left_side_of_Ttop,top_of_Ttop-0.5],[right_side_of_Ttop,top_of_Ttop-0.5]]
    
    V_new=perform_horizontal_commutation(horizontals_in_Tbot,target_edge,V)
    
    #print('This is the push T after the full isotopy')
    #draw_virtual_type2_boxes_diagram(Ttop, Tbot, V_new, where1='std', where2='horiz-infty',color1='purple')
    
    
    return V_new




def perform_upper_hinge_T_isotopy(hinge_T,V):
    
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
    
    
    #Now we perform the same isotopy: Shrink the wings of Ttop, then perform a series of "commutations".  This will not be valid commutations but will be a series of hinges. 

    vertices_crossing_b_arc_region = find_vertices_in_box(Ttop, V, where='horiz-infty')
   
    

    verticals_in_left_wing = [
        v for v in verticals
        if v[0] in vertices_crossing_b_arc_region
        and v[1] in vertices_crossing_b_arc_region
        and v[0][0] < left_side_of_Ttop]
    
    
    #to perform the series of commutations there need to be vertices under the left wing, otherwise we will have to change the boundary of the Ttop. 
    vertices_under_wings = find_vertices_in_box(Ttop, V, where='horiz-vert-infty') #this will capture everything under the wings on both sides
    vertices_under_left_wing=[v for v in vertices_under_wings if v[0]<left_side_of_Ttop]
    vertices_under_right_wing=[v for v in vertices_under_wings if v[0]>right_side_of_Ttop]
    
    verticals_in_right_wing = [
        v for v in verticals
        if v[0] in vertices_crossing_b_arc_region
        and v[1] in vertices_crossing_b_arc_region
        and v[0][0] > right_side_of_Ttop]
    
    
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
            
           # print('This is the T after the right wing is shrunk')
           # draw_virtual_type2_boxes_diagram(Ttop, Tmid, V, where1='horiz-infty', where2='std',color1='deeppink')
       
    
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
    #print('This is the hinge T after the full isotopy')
    #draw_virtual_type2_boxes_diagram(Ttop, Tmid, V, where1='horiz-infty', where2='std',color1='deeppink')
    
    
    return V




def perform_lower_hinge_T_isotopy(hinge_T,V):
     
    
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
    
    
    #Now we perform the same isotopy: Shrink the wings of Tbot, then perform a series of "commutations".  This will not be valid commutations but will be a series of hinges. 

    vertices_crossing_b_arc_region = find_vertices_in_box(Tbot, V, where='horiz-infty')
   
    

    verticals_in_left_wing = [
        v for v in verticals
        if v[0] in vertices_crossing_b_arc_region
        and v[1] in vertices_crossing_b_arc_region
        and v[0][0] < left_side_of_Ttop]
    
    
    #to perform the series of commutations there need to be vertices under the left wing, otherwise we will have to change the boundary of the Tbot. 
    vertices_above_wings = find_vertices_in_box(Tbot, V, where='horiz-vert-infty') #this will capture everything above the wings on both sides
    vertices_above_left_wing=[v for v in vertices_above_wings if v[0]<left_side_of_Tbot]
    vertices_above_right_wing=[v for v in vertices_above_wings if v[0]>right_side_of_Tbot]
    
    verticals_in_right_wing = [
        v for v in verticals
        if v[0] in vertices_crossing_b_arc_region
        and v[1] in vertices_crossing_b_arc_region
        and v[0][0] > right_side_of_Tbot]
    
    
    #Now we perform a series of commutations that push in these verticals:
    #Step 1: Commute the verticals in the left wing to the right past the left side of Ttop
    
    #The verticals need to be sorted correctly so the pushing occurs in the correct order:
    if verticals_in_left_wing:
        print('There are no verticals in left wing')
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
            print('This is the T after the left wing is shrunk')
            draw_virtual_type2_boxes_diagram(Tbot, Tmid, V, where1='horiz-infty', where2='std',color1='deeppink')
    
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
            
            print('This is the T after the right wing is shrunk')
            draw_virtual_type2_boxes_diagram(Tbot, Tmid, V, where1='horiz-infty', where2='std',color1='deeppink')
       
    
    #Uncomment for Debugging
    print('This is the T after the wings are shrunk')
    draw_virtual_type2_boxes_diagram(Tbot, Tmid, V, where1='horiz-infty', where2='std',color1='deeppink')
    
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
    print('This is the hinge T after the full isotopy')
    draw_virtual_type2_boxes_diagram(Tbot, Tmid, V, where1='horiz-infty', where2='std',color1='deeppink')
    
    
    return V





def generate_all_cyclic_permutations_matrix(R):
    n = len(R) // 2
    #print('The complexity of the diagram is:', n)

    # initialize empty n x n matrix
    R_matrix = [[None for _ in range(n)] for _ in range(n)]

    for i in range(n):
        for j in range(n):
            R_ij = perform_cyclic_permutations(R,
                number_of_vertical=i,
                number_of_horizontal=j,
                which_vertical='left-to-right',
                which_horizontal='top-to-bottom')
            R_matrix[i][j] = R_ij

    return R_matrix

def perform_vertical_commutation(vertical_edges,target_edge,V):
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
            
    return V_new


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
            
    return V_new


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
    # First convert tuples as shift_vertex_set expects tuples
    V_tuple = [tuple(v) for v in V_new_rest]
    V_shifted = shift_vertex_set(V_tuple)
    V_shifted=[list(v) for v in V_shifted]
    # Anchor topmost y-value at -1
    max_y = max(v[1] for v in V_shifted)
    delta = max_y + 1

    V_shifted = [[x, y - delta] for [x, y] in V_shifted]
    
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
    V_shifted = shift_vertex_set_simpler(V_tuple)
    V_shifted=[list(v) for v in V_shifted]
    # Anchor topmost y-value at -1
    max_y = max(v[1] for v in V_shifted)
    delta = max_y + 1

    V_shifted = [[x, y - delta] for [x, y] in V_shifted]
    
    return V_shifted


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
def check_for_simplifications_and_Ts(V1):
    rotation_count = 0

    while True:
        simplified = False
        complexity = len(V1)//2
        if complexity==2:
            print('The diagram is unknotted!')
            return V1
        print('Checking for virtual box simplications')
        VS = get_v1b_reduced_diagram(V1)
        V_new = VS[-1]
        if len(V_new)//2 < complexity:
            V1 = V_new
            rotation_count = 0
            simplified = True
            continue

        print('Checking for valid and essential push Ts')
        upper_push_Ts,lower_push_Ts =find_all_essential_push_Ts(V1)
        #Ensure the are not through infinity on the original diagram
        push_Ts_not_through_infinity=[]
        for upper_push_T in upper_push_Ts:
            if check_if_T_through_infinity(upper_push_T,[0,0],whichT='upper'):
                push_Ts_not_through_infinity.append(upper_push_T)

        push_Ts=push_Ts_not_through_infinity   #these are now valid and essential and not through infinity         
        if push_Ts:
            for T in push_Ts:
                print('This is a valid and essential push T')
                draw_virtual_type2_boxes_diagram(T[0], T[1], V1, where1='horiz-infty', where2='std',color1='purple')
                V_new=perform_upper_push_T_isotopy([T[0], T[1]],V1) 
                print('This is the diagram after the push T isotopy')
                draw_rectangular_diagram(V_new)        
                #JUST BEING CAREFUL!
                #if not verify_unknot_boolean(V_new):
                #    raise TypeError("The last simplification changed knot type!")                         
                print('Checking for virtual box simplifications now')
                complexity1=len(V_new)//2
                VS=get_v1b_reduced_diagram(V_new)
                V_new1=VS[-1]
                if len(V_new1)//2<complexity1:
                    V1=V_new1
                    rotation_count = 0
                    simplified=True
                    break

            if simplified:
                continue

        push_Ts_not_through_infinity=[]
        for lower_push_T in lower_push_Ts:
             if check_if_T_through_infinity(lower_push_T,[0,0],whichT='lower'):
                    push_Ts_not_through_infinity.append(lower_push_T)

        push_Ts=push_Ts_not_through_infinity   #these are now valid and essential and not through infinity         
        if push_Ts:
            for T in push_Ts:
                print('This is a valid and essential push T')
                draw_virtual_type2_boxes_diagram(T[0], T[1], V1, where1='horiz-infty', where2='std',color1='purple')
                V_new=perform_lower_push_T_isotopy([T[0], T[1]],V1) 
                print('This is the diagram after the push T isotopy')
                draw_rectangular_diagram(V_new)

                #JUST BEING CAREFUL!
                #if not verify_unknot_boolean(V_new):
                #    raise TypeError("The last simplification changed knot type!")

                print('Checking for virtual box simplifications now')
                complexity1=len(V_new)//2
                VS=get_v1b_reduced_diagram(V_new)
                V_new1=VS[-1]
                if len(V_new1)//2<complexity1:
                    V1=V_new1
                    rotation_count = 0
                    simplified=True
                    break
            if simplified:
                continue               
        else: 
            print('This diagram has no valid and essential push Ts')

        print('Checking for valid and essential hinge Ts')
        upper_hinge_Ts,lower_hinge_Ts=find_all_essential_hinge_Ts(V1)

        #Ensure the are not through infinity on the original diagram
        hinge_Ts_not_through_infinity=[]
        for hinge_T in upper_hinge_Ts:
             if check_if_T_through_infinity(hinge_T,[0,0],whichT='upper'):
                    hinge_Ts_not_through_infinity.append(hinge_T)  
        hinge_Ts=hinge_Ts_not_through_infinity   #these are now valid and essential and not through infinity 

        if hinge_Ts:
            for T in hinge_Ts:
                print('This is a valid and essential hinge T')
                draw_virtual_type2_boxes_diagram(T[0], T[1], V1, where1='horiz-infty', where2='std',color1='deeppink')
                V_new=perform_upper_hinge_T_isotopy([T[0], T[1]],V1) 
                print('This is the diagram after the hinge T isotopy')
                draw_rectangular_diagram(V_new)

                #JUST BEING CAREFUL!
                #if not verify_unknot_boolean(V_new):
                #    raise TypeError("The last simplification changed knot type!")

                print('Checking for virtual box simplifications now')
                complexity1=len(V_new)//2
                VS=get_v1b_reduced_diagram(V_new)
                V_new1=VS[-1]
                if len(V_new1)//2<complexity1:
                    V1=V_new1
                    rotation_count = 0
                    simplified=True
                    break

            if simplified:
                continue

        #Ensure the are not through infinity on the original diagram
        hinge_Ts_not_through_infinity=[]
        for hinge_T in lower_hinge_Ts:
             if check_if_T_through_infinity(hinge_T,[0,0],whichT='lower'):
                    hinge_Ts_not_through_infinity.append(hinge_T)

        hinge_Ts=hinge_Ts_not_through_infinity   #these are now valid and essential and not through infinity 

        if hinge_Ts:
            for T in hinge_Ts:
                print('This is a valid and essential hinge T')
                draw_virtual_type2_boxes_diagram(T[0], T[1], V1, where1='horiz-infty', where2='std',color1='deeppink')
                V_new=perform_lower_hinge_T_isotopy([T[0], T[1]],V1) 
                print('This is the diagram after the hinge T isotopy')
                draw_rectangular_diagram(V_new)

                #JUST BEING CAREFUL!
                #if not verify_unknot_boolean(V_new):
                #    raise TypeError("The last simplification changed knot type!")

                print('Checking for virtual box simplifications now')
                complexity1=len(V_new)//2
                VS=get_v1b_reduced_diagram(V_new)
                V_new1=VS[-1]
                if len(V_new1)//2<complexity1:
                    V1=V_new1
                    rotation_count = 0
                    simplified=True
                    break

            if simplified:
                continue

        else: 
            print('This diagram has no valid and essential hinge Ts')

        ##################### ROTATE AND RESTART ##########################################

        if rotation_count == 3:
            print('3 Rotations have been attempted. Returning current diagram.')
            return V1

        print('No simplification found. Rotating diagram and restarting search.')
        V1 = rotate_vertex_set_90_ccw(V1)
        rotation_count += 1
        continue

##############################################################################################






def check_for_simplifications_across_cyclic_permutations(V):
    while True:
        n = len(V)//2
        simplified = False
        for i in range(n):          # horizontal cyclic permutations
            for j in range(n):      # vertical cyclic permutations
                print('Checking cyclic permutation',[j,i])
                # Generate this cyclic permutation
                V1 = perform_cyclic_permutations(V,
                    number_of_vertical=j,
                    number_of_horizontal=i,
                    which_vertical='left-to-right',
                    which_horizontal='top-to-bottom')
                #draw_rectangular_diagram(V1)
                complexity = len(V1)//2
                print('Checking for virtual box simplications')
                VS = get_v1b_reduced_diagram(V1)
                V_new = VS[-1]
                if len(V_new)//2 < complexity:
                    V = V_new
                    rotation_count = 0
                    simplified = True
                    break
                print('Checking for valid and essential push Ts')
                upper_push_Ts,lower_push_Ts =find_all_essential_push_Ts(V1)
                #Ensure the are not through infinity on the original diagram
                push_Ts_not_through_infinity=[]
                for upper_push_T in upper_push_Ts:
                     if check_if_T_through_infinity(upper_push_T,[j,i],whichT='upper'):
                            push_Ts_not_through_infinity.append(upper_push_T)
                
                push_Ts=push_Ts_not_through_infinity   #these are now valid and essential and not through infinity         
                if push_Ts:
                    for T in push_Ts:
                        print('This is a valid and essential push T')
                        draw_virtual_type2_boxes_diagram(T[0], T[1], V1, where1='horiz-infty', where2='std',color1='purple')
                        V_new=perform_upper_push_T_isotopy([T[0], T[1]],V1) 
                        print('This is the diagram after the push T isotopy')
                        draw_rectangular_diagram(V_new)        
                        #JUST BEING CAREFUL!
                        #if not verify_unknot_boolean(V_new):
                        #    raise TypeError("The last simplification changed knot type!")                         
                        print('Checking for virtual box simplifications now')
                        complexity1=len(V_new)//2
                        VS=get_v1b_reduced_diagram(V_new)
                        V_new1=VS[-1]
                        if len(V_new1)//2<complexity1:
                            V=V_new1
                            rotation_count = 0
                            simplified=True
                            break

                    if simplified:
                        break
                    
                push_Ts_not_through_infinity=[]
                for lower_push_T in lower_push_Ts:
                     if check_if_T_through_infinity(lower_push_T,[j,i],whichT='lower'):
                            push_Ts_not_through_infinity.append(lower_push_T)
                
                push_Ts=push_Ts_not_through_infinity   #these are now valid and essential and not through infinity         
                if push_Ts:
                    for T in push_Ts:
                        print('This is a valid and essential push T')
                        draw_virtual_type2_boxes_diagram(T[0], T[1], V1, where1='horiz-infty', where2='std',color1='purple')
                        V_new=perform_lower_push_T_isotopy([T[0], T[1]],V1) 
                        print('This is the diagram after the push T isotopy')
                        draw_rectangular_diagram(V_new)
                        
                        #JUST BEING CAREFUL!
                        #if not verify_unknot_boolean(V_new):
                        #    raise TypeError("The last simplification changed knot type!")
                            
                        print('Checking for virtual box simplifications now')
                        complexity1=len(V_new)//2
                        VS=get_v1b_reduced_diagram(V_new)
                        V_new1=VS[-1]
                        if len(V_new1)//2<complexity1:
                            V=V_new1
                            rotation_count = 0
                            simplified=True
                            break
                    if simplified:
                        break               
                else: 
                    print('This cyclic permutation has no valid and essential push Ts')
                print('Checking for valid and essential hinge Ts')
                upper_hinge_Ts,lower_hinge_Ts=find_all_essential_hinge_Ts(V1)
                
                #Ensure the are not through infinity on the original diagram
                hinge_Ts_not_through_infinity=[]
                for hinge_T in upper_hinge_Ts:
                     if check_if_T_through_infinity(hinge_T,[j,i],whichT='upper'):
                            hinge_Ts_not_through_infinity.append(hinge_T)  
                hinge_Ts=hinge_Ts_not_through_infinity   #these are now valid and essential and not through infinity 
                
                if hinge_Ts:
                    for T in hinge_Ts:
                        print('This is a valid and essential hinge T')
                        draw_virtual_type2_boxes_diagram(T[0], T[1], V1, where1='horiz-infty', where2='std',color1='deeppink')
                        V_new=perform_upper_hinge_T_isotopy([T[0], T[1]],V1) 
                        print('This is the diagram after the hinge T isotopy')
                        draw_rectangular_diagram(V_new)
                        
                        #JUST BEING CAREFUL!
                        #if not verify_unknot_boolean(V_new):
                        #    raise TypeError("The last simplification changed knot type!")
                            
                        print('Checking for virtual box simplifications now')
                        complexity1=len(V_new)//2
                        VS=get_v1b_reduced_diagram(V_new)
                        V_new1=VS[-1]
                        if len(V_new1)//2<complexity1:
                            V=V_new1
                            rotation_count = 0
                            simplified=True
                            break
                            
                    if simplified:
                        #rotation_count = 0
                        break
               
                #Ensure the are not through infinity on the original diagram
                hinge_Ts_not_through_infinity=[]
                for hinge_T in lower_hinge_Ts:
                     if check_if_T_through_infinity(hinge_T,[j,i],whichT='lower'):
                            hinge_Ts_not_through_infinity.append(hinge_T)
                
                hinge_Ts=hinge_Ts_not_through_infinity   #these are now valid and essential and not through infinity 
                
                if hinge_Ts:
                    for T in hinge_Ts:
                        print('This is a valid and essential hinge T')
                        draw_virtual_type2_boxes_diagram(T[0], T[1], V1, where1='horiz-infty', where2='std',color1='deeppink')
                        V_new=perform_lower_hinge_T_isotopy([T[0], T[1]],V1) 
                        print('This is the diagram after the hinge T isotopy')
                        draw_rectangular_diagram(V_new)
                        
                        #JUST BEING CAREFUL!
                        #if not verify_unknot_boolean(V_new):
                        #    raise TypeError("The last simplification changed knot type!")
                            
                        print('Checking for virtual box simplifications now')
                        complexity1=len(V_new)//2
                        VS=get_v1b_reduced_diagram(V_new)
                        V_new1=VS[-1]
                        if len(V_new1)//2<complexity1:
                            V=V_new1
                            rotation_count = 0
                            simplified=True
                            break
                            
                    if simplified:
                        break
                        
                else: 
                    print('This cyclic permutation has no valid and essential hinge Ts')

                ##################### BEGIN ROTATION CHECKING ########################################## 

                # Rotate the diagram and check for push and hinge T's that simplify
                V1 = rotate_vertex_set_90_ccw(V1)
                
                print('Checking for valid and essential push Ts in rotated diagram')
                upper_push_Ts,lower_push_Ts=find_all_essential_push_Ts(V1)
                if upper_push_Ts:
                    for T in upper_push_Ts:
                        print('This is a valid and essential push T')
                        draw_virtual_type2_boxes_diagram(T[0], T[1], V1, where1='horiz-infty', where2='std',color1='purple')
                        V_new=perform_upper_push_T_isotopy([T[0], T[1]],V1) 
                        print('This is the diagram after the push T isotopy')
                        draw_rectangular_diagram(V_new)
                        
                        #JUST BEING CAREFUL!
                        #if not verify_unknot_boolean(V_new):
                        #    raise TypeError("The last simplification changed knot type!")
                            
                        print('Checking for virtual box simplifications now')
                        complexity1=len(V_new)//2
                        VS=get_v1b_reduced_diagram(V_new)
                        V_new1=VS[-1]
                        if len(V_new1)//2<complexity1:
                            V=V_new1
                            rotation_count = 0
                            simplified=True
                            break

                    if simplified:
                        break

                if lower_push_Ts:
                    for T in lower_push_Ts:
                        print('This is a valid and essential push T')
                        draw_virtual_type2_boxes_diagram(T[0], T[1], V1, where1='horiz-infty', where2='std',color1='purple')
                        V_new=perform_lower_push_T_isotopy([T[0], T[1]],V1) 
                        print('This is the diagram after the push T isotopy')
                        draw_rectangular_diagram(V_new)
                        
                        #JUST BEING CAREFUL!
                        #if not verify_unknot_boolean(V_new):
                        #    raise TypeError("The last simplification changed knot type!")
                            
                        print('Checking for virtual box simplifications now')
                        complexity1=len(V_new)//2
                        VS=get_v1b_reduced_diagram(V_new)
                        V_new1=VS[-1]
                        if len(V_new1)//2<complexity1:
                            V=V_new1
                            simplified=True
                            break
                            
                if simplified:
                    break
                        
                else: 
                    print('This cyclic permutation has no valid and essential push Ts')
                
                print('Checking for valid and essential hinge Ts in rotated diagram')
                upper_hinge_Ts,lower_hinge_Ts=find_all_essential_hinge_Ts(V1)
                if upper_hinge_Ts:
                    for T in upper_hinge_Ts:
                        print('This is a valid and essential hinge T')
                        draw_virtual_type2_boxes_diagram(T[0], T[1], V1, where1='horiz-infty', where2='std',color1='deeppink')
                        V_new=perform_upper_hinge_T_isotopy([T[0], T[1]],V1) 
                        print('This is the diagram after the hinge T isotopy')
                        draw_rectangular_diagram(V_new)
                        
                        #JUST BEING CAREFUL!
                        #if not verify_unknot_boolean(V_new):
                        #    raise TypeError("The last simplification changed knot type!")
                            
                        print('Checking for virtual box simplifications now')
                        complexity1=len(V_new)//2
                        VS=get_v1b_reduced_diagram(V_new)
                        V_new1=VS[-1]
                        if len(V_new1)//2<complexity1:
                            V=V_new1
                            simplified=True
                            break

                if simplified:
                    break

                if lower_hinge_Ts:
                    for T in lower_hinge_Ts:
                        print('This is a valid and essential hinge T')
                        draw_virtual_type2_boxes_diagram(T[0], T[1], V1, where1='horiz-infty', where2='std',color1='deeppink')
                        V_new=perform_lower_hinge_T_isotopy([T[0], T[1]],V1) 
                        print('This is the diagram after the hinge T isotopy')
                        draw_rectangular_diagram(V_new)
                        
                        #JUST BEING CAREFUL!
                        #if not verify_unknot_boolean(V_new):
                        #    raise TypeError("The last simplification changed knot type!")
                            
                        print('Checking for virtual box simplifications now')
                        complexity1=len(V_new)//2
                        VS=get_v1b_reduced_diagram(V_new)
                        V_new1=VS[-1]
                        if len(V_new1)//2<complexity1:
                            V=V_new1
                            simplified=True
                            break
                            
                if simplified:
                    break
                    
                else: 
                    print('The rotation of this cyclic permutation has no valid and essential hinge Ts')

                ##################### END ROTATION CHECKING ##########################################       

        # If a simplification was found, restart the cyclic permutation
        # search on the new diagram.
        if simplified:
            continue

        # No simplification found anywhere in the entire sweep.
        return []


def fully_simplify_via_cyclic_permutations(V, verbose=True):
    current_V = V
    current_complexity = len(current_V) // 2
    while True:
        if verbose:
            print("\nCurrent complexity:", current_complexity)
        # Stop if trivial
        if current_complexity == 2:
            if verbose:
                print("Reached complexity 2 (trivial unknot).")
            return current_V
        # Try one full pass of cyclic permutations
        V_new = check_for_simplifications_across_cyclic_permutations(current_V)

        # No simplification found anywhere
        if V_new == []:
            if verbose:
                print("No further simplifications found across all cyclic permutations.")
            return current_V

        # A strict simplification was found
        new_complexity = len(V_new) // 2

        if new_complexity >= current_complexity:
            # This should never happen, but we guard anyway
            if verbose:
                print("Warning: non-decreasing complexity detected. Stopping.")
            return current_V

        # Accept the simplification and continue
        current_V = V_new
        current_complexity = new_complexity
        
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
       
         #We need to find the dimensions of the T in the diagram V, and compare it to the i,j values
        y_values = [y for _, y in box_2] #look at the y_values of the neck
        max_y = max(y_values)
        top_of_T=max_y

        if -top_of_T<phi_infinity: 
            #If you have a downward T at the bottom of some phi_infinity diagram then the top of the T
            #cannot be at the bottom of the orginal diagram otherwise the neck will go through infinity.  That means that     
            # if the top of the T has a -y-value smaller than the number of vertical perms then it began at the top.  
            return True
        return False  
        #y_values = [y for _, y in box_2] #look at the y_values of the neck
        #max_y = max(y_values)
        #Top_of_T=max_y
        #if not -top_of_T>phi_infinity: 
            #If you have an downward T (so that the exit disk is the maximal y-value of the T) then the top of the T
            #moves up after each phi-cyclic permuation. 
            # If the top of the T has a -(y-value) smaller than the number of vertical perms then it was pushed to the bottom of the diagram.  I am checking this does not happen
        #    return True
        #return False  
        
        
        
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
    B = Link(braid_closure=braid)
    # Return True if seifert_genus is 0, else False
    return B.knot_floer_homology()['seifert_genus'] == 0

        
############################################### END FUNCTIONS NEEDED FOR T'S ##############################################        
        
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