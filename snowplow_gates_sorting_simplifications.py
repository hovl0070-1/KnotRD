from rigidity_sorting import *
from virtual_boxes_in_rectangular_diagrams import *
from  rechoosing_infinity import *
from v1b_reduced_algorithm import *
import copy
import math as m


def perform_v1b_corner_rigid_simplifications(V):
    while True:
        # --- 1. V1b simplifications ---
        VS=get_v1b_reduced_diagram(V)
        V = VS[-1]

        # --- Check if unknotted ---
        if len(V) // 2 == 2:
            #print("The rectangular diagram has been unknotted.")
            return V

        # --- Single hooked box simplifications ---
        V_new = simple_commutation_check(V)
        if V_new != V:
            V = V_new
            if len(V) // 2 == 2:
                #print("The rectangular diagram has been unknotted.")
                return V
            continue

        # --- Corner rigidity simplifications ---
        #print("No single hooked box simplifications. Testing for corner rigidity now.")
        V_new = corner_rigidity_simplification(V)
        if V_new != V:
            print("A corner rigid simplification was found.")
            draw_rectangular_diagram(V_new)
            V = V_new
            if len(V) // 2 == 2:
                #print("The rectangular diagram has been unknotted.")
                return V
            continue
        else:
            print("No generalized destabilizations or corner rigidity simplifications.")
            #draw_rectangular_diagram(V)
            
            #This is commented out when gates and snowplows are checked
            #return V
            #Comment out all the other lines to turn off gate snowplow type simplifications
            # --- Gate → Snowplow simplifications ---
            #print("Checking for Gate → Snowplow simplifications")
            V_new = gate_snowplow_move_simplification(V)
            if V_new != V:
                print("Gate → Snowplow combo modified the diagram.")
                V = V_new
                if len(V) // 2 == 2:
                    #print("The rectangular diagram has been unknotted.")
                    return V
                continue

            ## --- Snowplow → Gate simplifications ---
            print("Checking for Snowplow → Gate simplifications")
            V_new = snowplow_gate_move_simplification(V)
            if V_new != V:
                print("Snowplow → Gate combo modified the diagram.")
                V = V_new
                if len(V) // 2 == 2:
                    #print("The rectangular diagram has been unknotted.")
                    return V
                continue

            ## --- No further simplifications ---
            ##print("No further simplifications possible.")
            #return V
            ##Seth when you uncomment the rigidity delete the return V below
            return V

def simple_commutation_check(V):
    type1,type2=find_all_virtual_boxes(V)
    for box in type1:
        if is_type_1_virtual_box_single_hooked_q(box,V,where='std')==True:
            box.sort()
            left_edge_of_box=box[0][0]
            right_edge_of_box=box[3][0]
            top_edge_of_box=box[1][1]
            bot_edge_of_box=box[0][1]
            vertical_entering=find_vertical_edges_entering_box(box,V,where='std')
            vertical_entering=vertical_entering[0]
            x_val_vert_edge=vertical_entering[0][0]
            left_check=x_val_vert_edge-left_edge_of_box
            right_check=right_edge_of_box-x_val_vert_edge
            horizontal_entering=find_horizontal_edges_entering_box(box,V,where='std')
            horizontal_entering=horizontal_entering[0]
            y_val_horiz_edge=horizontal_entering[0][1]
            top_edge_check=top_edge_of_box-y_val_horiz_edge
            bot_edge_check=y_val_horiz_edge-bot_edge_of_box
            horiz_com_count=count_edge_commutation(horizontal_entering,V)
            vert_com_count=count_edge_commutation(vertical_entering,V)
            if horiz_com_count[0]>top_edge_check:
                print('The horizontal edge of the hook commutes out the top')
                draw_virtual_box_diagram(box,V,where='std')
                new_edge=[[horizontal_entering[0][0],top_edge_of_box+0.5],[horizontal_entering[1][0],top_edge_of_box+0.5]]
                #print('the horizontal edge',horizontal_entering,' is being replaced with',new_edge)
                V=[v for v in V if v!=horizontal_entering[0] and v!=horizontal_entering[1]]
                V_new=commute_vertex_set(V,new_edge,direction='up')
                return V_new
            if horiz_com_count[1]>bot_edge_check:
                print('The horizontal edge of the hook commutes out the bottom')
                draw_virtual_box_diagram(box,V,where='std')
                new_edge=[[horizontal_entering[0][0],bot_edge_of_box-0.5],[horizontal_entering[1][0],bot_edge_of_box-0.5]]
                #print('the horizontal edge',horizontal_entering,' is being replaced with',new_edge)
                V=[v for v in V if v!=horizontal_entering[0] and v!=horizontal_entering[1]]
                V_new=commute_vertex_set(V,new_edge,direction='down')
                return V_new
            if vert_com_count[0]>left_check:
                print('The vertical edge of the hook commutes out the left side')
                draw_virtual_box_diagram(box,V,where='std')
                new_edge=[[left_edge_of_box-0.5,vertical_entering[0][1]],[left_edge_of_box-0.5,vertical_entering[1][1]]]
                #print('the vertical edge',vertical_entering,' is being replaced with',new_edge)
                V=[v for v in V if v!=vertical_entering[0] and v!=vertical_entering[1]]
                V_new=commute_vertex_set(V,new_edge,direction='left')
                return V_new
            if vert_com_count[1]>right_check:
                print('The vertical edge of the hook commutes out the right side')
                draw_virtual_box_diagram(box,V,where='std')
                new_edge=[[right_edge_of_box+0.5,vertical_entering[0][1]],[right_edge_of_box+0.5,vertical_entering[1][1]]]
                #print('the vertical edge',vertical_entering,' is being replaced with',new_edge)
                V=[v for v in V if v!=vertical_entering[0] and v!=vertical_entering[1]]
                V_new=commute_vertex_set(V,new_edge,direction='right')
                return V_new
    #print('There are no single commutations that simplify a type 1 box.')        
    return V   

#################################### Begin Auxillary Functions for simple commutation check box #############################
def is_type_1_virtual_box_single_hooked_q(box,V,where):
    #check for a strand that enters by crossing a vertical then leaves by crossing a horizontal.
    [horizontals,verticals]=sort_vertices_into_verticals_and_horizontals(V)
    horizontals_entering=find_horizontal_edges_entering_box(box,V,where)
    verticals_entering=find_vertical_edges_entering_box(box,V,where)
    if len(horizontals_entering)==1 and len(verticals_entering)==1: #there is a single horizontal and leaving vert the virtual box
        return True
    return False

##### The function finds horizontal edges that intersect the vertical edges of the virtual box.
# These edges have a vertex that will be in a strand through the box
def find_horizontal_edges_entering_box(box,V,where):
    [horizontals,verticals]=sort_vertices_into_verticals_and_horizontals(V)
    horizontals_entering=[]
    for horizontal in horizontals:
        left_vertex_in_box_q=check_if_vertex_in_box(horizontal[0],box,where)
        right_vertex_in_box_q=check_if_vertex_in_box(horizontal[1],box,where) 
        if left_vertex_in_box_q+right_vertex_in_box_q==1:
            horizontals_entering.append(horizontal)
    return horizontals_entering


##### The function finds vertical edges that intersect the horizontal edges of the virtual box.
# These edges have a vertex that will be in a strand through the box
def find_vertical_edges_entering_box(box,V,where):
    [horizontals,verticals]=sort_vertices_into_verticals_and_horizontals(V)
    verticals_entering=[]
    for vertical in verticals:
        bottom_vertex_in_box_q=check_if_vertex_in_box(vertical[0],box,where)
        top_vertex_in_box_q=check_if_vertex_in_box(vertical[1],box,where) 
        if top_vertex_in_box_q+bottom_vertex_in_box_q==1:
             verticals_entering.append(vertical)
    return verticals_entering


########################################################
def commute_vertex_set(V,new_edge,direction):
    
    def ceil_of_vertices(box):
            import math as m
            ceil_box= [[int(m.ceil(num)) for num in sublist] for sublist in box]
            return ceil_box
    def floor_of_vertices(box):
            import math as m
            floor_box= [[int(m.floor(num)) for num in sublist] for sublist in box]
            return floor_box 
    #the input is an edge that has half values but is the same width or height as some edge in V
    V_new=[]
    new_vertices=new_edge
    shift_by_x=0
    shift_by_y=0
    if new_vertices[0][0]==new_vertices[1][0]: #the new vertices form a new vertical edge
        shift_by_x=1
    else: #the new vertices form a new horizontal edge
        shift_by_y=1
    if shift_by_x==1 and direction=='right':
        for v in V:
            if v[0]>new_vertices[0][0]:
                V_new.append([v[0]+1,v[1]])
            else:
                V_new.append(v)
        rounded_verts=ceil_of_vertices(new_vertices) #this rounds the half values up
    elif shift_by_x==1 and direction =='left':
        for v in V:
            if v[0]<new_vertices[0][0]:
                V_new.append([v[0]-1,v[1]])
            else:
                V_new.append(v)
        rounded_verts=floor_of_vertices(new_vertices) #this rounds the half values down
      
    elif shift_by_y==1 and direction=='up':   
        for v in V:
            if v[1]>new_vertices[0][1]:
                v1=[v[0],v[1]+1]
            else:
                v1=v
            V_new.append(v1)  
        rounded_verts= ceil_of_vertices(new_vertices) #this rounds the half values up    
    elif shift_by_y==1 and direction=='down':   
        for v in V:
            if v[1]<new_vertices[0][1]:
                v1=[v[0],v[1]-1]
            else:
                v1=v
            V_new.append(v1)      
        rounded_verts=floor_of_vertices(new_vertices)
         
    new_vertices=rounded_verts  
    V_new=V_new+new_vertices
    #V_new has two gaps now so I will shift the vertex set twice so this is fixed
    V_new=shift_vertex_set(V_new)
    V_new=shift_vertex_set(V_new)
    V_new.sort()
    temp=[]
    for v in V_new:
        temp.append(list(v))    

    tempp=[]
    if min(v[0] for v in temp)==0: # This happens with a commutation all the way to the left of the diagram
        for v in temp:
            tempp.append([v[0]+1,v[1]])
    elif max(v[0] for v in temp)==len(temp)//2+1: # This happens with a commutation all the way to the right of the diagram
        for v in temp:
            tempp.append([v[0]-1,v[1]]) 
    elif max(v[1] for v in temp)==0: # This happens with a commutation all the way to the top of the diagram
        for v in temp:
            tempp.append([v[0],v[1]-1])
    elif min(v[1] for v in temp)==-len(temp)//2-1: # This happens with a commutation all the way to the bot of the diagram
        for v in temp:
            tempp.append([v[0],v[1]+1])
    else:
        tempp=temp
        
    V_new=tempp    
    return V_new
################################ END Auxillary Functions for simple commutation check box #############################


### Begin function for corner rigidity simplification ###########
#### The idea is that maybe a virtual box can be simplified by a prescribed normal form.
# Step 1: By cyclic permutations put the box into a corner of the diagram (NW NE SW SE)
# Step 2: See if this creates a simplification if so return this simplifed diagram
# Step 3: See if by performing a rigidity sort on the diagram it simplifies the box 
        # A rigidity sort tries to push all horizontals up (down) as high as possible and all verticals right (left) in the case #         of ties the longer horizontal is pushed above the shorter. etc. obtaining this sorted diagram is n^3 worst case senario
# Step 4: There is sometimes a ``slip knot'' or a crochet stitch made this appears as a tangle being pushed through the virtual box by entering a side and then leaving the bottom.  The tangle can then be pushed up into the virtual box and then out the side.  This is performed by looking for a T move and is the last case treated by the below function. 
    
def corner_rigidity_simplification(V):
    from push_Ts import find_all_valid_Ts,perform_T_move_isotopy,draw_virtual_T_diagram
    type1,_=find_all_virtual_boxes(V)
    n=len(V)//2
    for box in type1:
        #draw_virtual_box_diagram(box,V,where='std')
        #Determine where the real vertex is
        virtual_vertex=[v for v in box if v not in V]
        #if not virtual_vertex: #This occurs when you have a simple unknotted loop component!
        #    print('The diagram has an unknotted link component. It will be removed now.')
         #   V_new=perform_destabilization(V,box)
         #   return V_new
        
        virtual_vertex=virtual_vertex[0]
        real_corner_vertex=[v for v in box if v[0]!=virtual_vertex[0] and v[1]!=virtual_vertex[1]]
        real_corner_vertex=real_corner_vertex[0]
        
        #Generate the corner diagrams
        [NW, NE, SW, SE]=generate_corner_diagrams(V,box)
        
        # The box has now been moved to a corner we want to keep track of that as well.
        NW_box=find_boxes_from_corner_positions(NW,V_type='NW')
        NE_box=find_boxes_from_corner_positions(NE,V_type='NE')
        SW_box=find_boxes_from_corner_positions(SW,V_type='SW')
        SE_box=find_boxes_from_corner_positions(SE,V_type='SE')
        
        NW1=top_left_rigid(NW)
        box1=find_boxes_from_corner_positions(NW1,V_type='NW')
        bool1=check_type_1_box_for_simplification(box1,NW1,where='std')
        bool2=check_type_1_box_for_simplification(box1,NW1,where='vert-infty')
        if bool1 or bool2:
            print('The box below has a NW rigid simplification')
            draw_virtual_box_diagram(box,V,where='std')
            
            print('This is the diagram in NW position')
            draw_virtual_box_diagram(NW_box,NW,where='std')
            
            print('This is the diagram after the top_left_rigid isotopy')  
            draw_virtual_box_diagram(box1,NW1,where='std')
            
            V_new=perform_destabilization(NW1,box1)
            return V_new
        
        corner_type2_boxes=find_type2_boxes_from_corner_positions(NW1,V_type='NW')
        for box1 in corner_type2_boxes:
            bool1=check_type_2_box_for_simplification(box1,NW1,where='std')
            bool2=check_type_2_box_for_simplification(box1,NW1,where='vert-infty')
            if bool1 or bool2:
                
                print('The box below has a NW rigid simplification')
                draw_virtual_box_diagram(box,V,where='std')
            
                print('This is the diagram in NW position')
                draw_virtual_box_diagram(NW_box,NW,where='std')

                print('This is the diagram after the top_left_rigid isotopy')  
                draw_virtual_box_diagram(box1,NW1,where='std')
            
                V_new=perform_type_2_destabilization(NW1,box1)
                return V_new

        
        NE1=top_right_rigid(NE)
        box1=find_boxes_from_corner_positions(NE1,V_type='NE')
        bool1=check_type_1_box_for_simplification(box1,NE1,where='std')
        bool2=check_type_1_box_for_simplification(box1,NE1,where='vert-infty')
        if bool1 or bool2:
            print('The box below has a NE rigid simplification')
            draw_virtual_box_diagram(box,V,where='std')
            
            print('This is the diagram in NE position')
            draw_virtual_box_diagram(NE_box,NE,where='std')
            
            print('This is the diagram after the top_right_rigid isotopy')  
            draw_virtual_box_diagram(box1,NE1,where='std')
            
            V_new=perform_destabilization(NE1,box1)
            return V_new
        
        corner_type2_boxes=find_type2_boxes_from_corner_positions(NE1,V_type='NE')
        for box1 in corner_type2_boxes:
            bool1=check_type_2_box_for_simplification(box1,NE1,where='std')
            bool2=check_type_2_box_for_simplification(box1,NE1,where='vert-infty')
            if bool1 or bool2:
                print('The box below has a NE rigid simplification')
                draw_virtual_box_diagram(box,V,where='std')

                print('This is the diagram in NE position')
                draw_virtual_box_diagram(NE_box,NE,where='std')

                print('This is the diagram after the top_right_rigid isotopy')  
                draw_virtual_box_diagram(box1,NE1,where='std')

                V_new=perform_type_2_destabilization(NE1,box1)
                return V_new
        
        SW1=bottom_left_rigid(SW)
        box1=find_boxes_from_corner_positions(SW1,V_type='SW')
        bool1=check_type_1_box_for_simplification(box1,SW1,where='std')
        bool2=check_type_1_box_for_simplification(box1,SW1,where='vert-infty')
        if bool1 or bool2:
            print('The box below has a SW rigid simplification')
            draw_virtual_box_diagram(box,V,where='std')

            print('This is the diagram in SW position')
            draw_virtual_box_diagram(SW_box,SW,where='std')

            print('This is the diagram after the bottom_left_rigid isotopy')  
            draw_virtual_box_diagram(box1,SW1,where='std')

            V_new=perform_destabilization(SW1,box1)
            return V_new
        
        corner_type2_boxes=find_type2_boxes_from_corner_positions(SW1,V_type='SW')
        for box1 in corner_type2_boxes:
            bool1=check_type_2_box_for_simplification(box1,SW1,where='std')
            bool2=check_type_2_box_for_simplification(box1,SW1,where='vert-infty')
            if bool1 or bool2:
                print('The box below has a SW rigid simplification')
                draw_virtual_box_diagram(box,V,where='std')

                print('This is the diagram in SW position')
                draw_virtual_box_diagram(SW_box,SW,where='std')

                print('This is the diagram after the bottom_left_rigid isotopy')  
                draw_virtual_box_diagram(box1,SW1,where='std')
                
                V_new=perform_type_2_destabilization(SW1,box1)
                return V_new
        
        SE1=bottom_right_rigid(SE)
        box1=find_boxes_from_corner_positions(SE1,V_type='SE')
        bool1=check_type_1_box_for_simplification(box1,SE1,where='std')
        bool2=check_type_1_box_for_simplification(box1,SE1,where='vert-infty')
        if bool1 or bool2:
            print('The box below has a SE rigid simplification')
            draw_virtual_box_diagram(box,V,where='std')

            print('This is the diagram in SE position')
            draw_virtual_box_diagram(SE_box,SE,where='std')
            print('This is the diagram after the bottom_right_rigid isotopy')  
            draw_virtual_box_diagram(box1,SE1,where='std')
            
       
            V_new=perform_destabilization(SE1,box1)
            return V_new
        
        corner_type2_boxes=find_type2_boxes_from_corner_positions(SE1,V_type='SE')
        for box1 in corner_type2_boxes:
            bool1=check_type_2_box_for_simplification(box1,SE1,where='std')
            bool2=check_type_2_box_for_simplification(box1,SE1,where='vert-infty')
            if bool1 or bool2:
                print('The box below has a SE rigid simplification')
                draw_virtual_box_diagram(box,V,where='std')

                print('This is the diagram in SE position')
                draw_virtual_box_diagram(SE_box,SE,where='std')

                print('This is the diagram after the bottom_right_rigid isotopy')  
                draw_virtual_box_diagram(box1,SE1,where='std')
                
                V_new=perform_type_2_destabilization(SE1,box1)
                return V_new
        
        
        
        #Draw these virtual boxes
        #print('The NW diagram')
        #draw_virtual_box_diagram(NW_box,NW,where='vert-infty')
        #print('The NE diagram')
        #draw_virtual_box_diagram(NE_box,NE,where='vert-infty')
        #print('The SW diagram')
        #draw_virtual_box_diagram(SW_box,SW,where='vert-infty')
        #print('The SE diagram')
        #draw_virtual_box_diagram(SE_box,SE,where='vert-infty')
        
        #Now for each diagram we find the horizontal y-value of the mouths of the T.  This is the virtual horizontal edge of each box.
        NW_exit_disks=find_exit_disks(NW,NW_box) 
        NE_exit_disks=find_exit_disks(NE,NE_box) 
        SW_exit_disks=find_exit_disks(SW,SW_box) 
        SE_exit_disks=find_exit_disks(SE,SE_box) 
        
        #Next we find all T regions 
        T_regions_NW=find_all_T_regions_snowplow(NW,NW_box,direction='down') 
        T_regions_NE=find_all_T_regions_snowplow(NE,NE_box,direction='down')
        T_regions_SW=find_all_T_regions_snowplow(SW,SW_box,direction='up')
        T_regions_SE=find_all_T_regions_snowplow(SE,SE_box,direction='up')
        
        #For each T region we want to find the valid ones only.  We use the T code for this
        valid_NW_Ts=find_all_valid_Ts(T_regions_NW,NW)
        valid_NE_Ts=find_all_valid_Ts(T_regions_NE,NE)
        valid_SW_Ts=find_all_valid_Ts(T_regions_SW,SW)
        valid_SE_Ts=find_all_valid_Ts(T_regions_SE,SE)
    
        if valid_NW_Ts:
            for valid_T in valid_NW_Ts:
                boundary_of_T=valid_T[0]
                exit_disk=[boundary_of_T[0],boundary_of_T[1]]
                #troubleshooting remove below after
                #draw_virtual_T_diagram(boundary_of_T, NW)
                V_pushed,_=perform_T_move_isotopy(valid_T,NW)
                #now we recheck the box for a v1b simplification
                box1=find_boxes_from_corner_positions(V_pushed,V_type='NW')
                
                bool1=check_type_1_box_for_simplification(box1,V_pushed,where='std')
                bool2=check_type_1_box_for_simplification(box1,V_pushed,where='vert-infty')
                if bool1 or bool2:
                    print('The box below has a NW gate/snowplow simplification')
                    draw_virtual_box_diagram(box,V,where='std')
                    draw_virtual_T_diagram(boundary_of_T, NW)
                    print('This is the diagram after the isotopy')
                    draw_rectangular_diagram(V_pushed)
                    V_new=perform_destabilization(V_pushed,box1)
                    return V_new
                corner_type2_boxes=find_type2_boxes_from_corner_positions(V_pushed,V_type='NW')
                for box1 in corner_type2_boxes:
                    bool1=check_type_2_box_for_simplification(box1,V_pushed,where='std')
                    bool2=check_type_2_box_for_simplification(box1,V_pushed,where='vert-infty')
                    if bool1 or bool2:
                        print('The box below has a NW gate/snowplow simplification')
                        draw_virtual_box_diagram(box,V,where='std')
                        draw_virtual_T_diagram(boundary_of_T, NW)
                        print('This is the diagram after the isotopy')
                        draw_rectangular_diagram(V_pushed)
                        V_new=perform_type_2_destabilization(V_pushed,box1)
                        return V_new
                    
        
        if valid_NE_Ts:
            for valid_T in valid_NE_Ts:
                boundary_of_T=valid_T[0]
                exit_disk=[boundary_of_T[0],boundary_of_T[1]]
                #draw_virtual_T_diagram(boundary_of_T, NE)
                V_pushed,_=perform_T_move_isotopy(valid_T,NE)
                #now we recheck the box for a v1b simplification
                box1=find_boxes_from_corner_positions(V_pushed,V_type='NE')
                bool1=check_type_1_box_for_simplification(box1,V_pushed,where='std')
                bool2=check_type_1_box_for_simplification(box1,V_pushed,where='vert-infty')
                if bool1 or bool2:
                    print('The box below has a NE gate/snowplow simplification')
                    draw_virtual_box_diagram(box,V,where='std')
                    draw_virtual_T_diagram(boundary_of_T, NE)
                    print('This is the diagram after the isotopy')
                    draw_rectangular_diagram(V_pushed)
                    V_new=perform_destabilization(V_pushed,box1)
                    return V_new
                corner_type2_boxes=find_type2_boxes_from_corner_positions(V_pushed,V_type='NE')
                for box1 in corner_type2_boxes:
                    bool1=check_type_2_box_for_simplification(box1,V_pushed,where='std')
                    bool2=check_type_2_box_for_simplification(box1,V_pushed,where='vert-infty')
                    if bool1 or bool2:
                        print('The box below has a NE gate/snowplow simplification')
                        draw_virtual_box_diagram(box,V,where='std')
                        draw_virtual_T_diagram(boundary_of_T, NE)
                        print('This is the diagram after the isotopy')
                        draw_rectangular_diagram(V_pushed)
                        V_new=perform_type_2_destabilization(V_pushed,box1)
                        return V_new
                
                
        if valid_SW_Ts:
            for valid_T in valid_SW_Ts:
                boundary_of_T=valid_T[0]
                exit_disk=[boundary_of_T[0],boundary_of_T[1]]
                #draw_virtual_T_diagram(boundary_of_T, SW)
                V_pushed,_=perform_T_move_isotopy(valid_T,SW)
                #now we recheck the box for a v1b simplification
                box1=find_boxes_from_corner_positions(V_pushed,V_type='SW')
                bool1=check_type_1_box_for_simplification(box1,V_pushed,where='std')
                bool2=check_type_1_box_for_simplification(box1,V_pushed,where='vert-infty')
                if bool1 or bool2:
                    print('The box below has a SW gate/snowplow simplification')
                    draw_virtual_box_diagram(box,V,where='std')
                    draw_virtual_T_diagram(boundary_of_T, SW)
                    V_new=perform_destabilization(V_pushed,box1)
                    return V_new
                corner_type2_boxes=find_type2_boxes_from_corner_positions(V_pushed,V_type='SW')
                for box1 in corner_type2_boxes:
                    bool1=check_type_2_box_for_simplification(box1,V_pushed,where='std')
                    bool2=check_type_2_box_for_simplification(box1,V_pushed,where='vert-infty')
                    if bool1 or bool2:
                        print('The box below has a SW gate/snowplow simplification')
                        draw_virtual_box_diagram(box,V,where='std')
                        draw_virtual_T_diagram(boundary_of_T, SW)
                        print('This is the diagram after the isotopy')
                        draw_rectangular_diagram(V_pushed)
                        V_new=perform_type_2_destabilization(V_pushed,box1)
                        return V_new
        
        if valid_SE_Ts:
            for valid_T in valid_SE_Ts:
                boundary_of_T=valid_T[0]
                exit_disk=[boundary_of_T[0],boundary_of_T[1]]
                #draw_virtual_T_diagram(boundary_of_T, SE)
                V_pushed,_=perform_T_move_isotopy(valid_T,SE)
                #now we recheck the box for a v1b simplification
                box1=find_boxes_from_corner_positions(V_pushed,V_type='SE')
                bool1=check_type_1_box_for_simplification(box1,V_pushed,where='std')
                bool2=check_type_1_box_for_simplification(box1,V_pushed,where='vert-infty')
                if bool1 or bool2:
                    print('The box below has a SE gate/snowplow simplification')
                    draw_virtual_box_diagram(box,V,where='std')
                    draw_virtual_T_diagram(boundary_of_T, SE)
                    V_new=perform_destabilization(V_pushed,box1)
                    return V_new
                
                corner_type2_boxes=find_type2_boxes_from_corner_positions(V_pushed,V_type='SE')
                for box1 in corner_type2_boxes:
                    bool1=check_type_2_box_for_simplification(box1,V_pushed,where='std')
                    bool2=check_type_2_box_for_simplification(box1,V_pushed,where='vert-infty')
                    if bool1 or bool2:
                        print('The box below has a SE gate/snowplow simplification')
                        draw_virtual_box_diagram(box,V,where='std')
                        draw_virtual_T_diagram(boundary_of_T, SE)
                        print('This is the diagram after the isotopy')
                        draw_rectangular_diagram(V_pushed)
                        V_new=perform_type_2_destabilization(V_pushed,box1)
                        return V_new
                
                
    #If you are here then there are no vaild snowplow moves that reveal a destabilization
    #print('There are no valid snowplow moves that reveal a destabilization. More testing required.')
    return V
        

def snowplow_simplification_type_2(V):
    _,type2=find_all_virtual_boxes(V)
    another_type2=find_all_non_std_type_2_boxes(V)
    type2=type2+another_type2
    n=len(V)//2
    for box in type2:
        subbox1,subbox2=split_type_2_virtual_box(box)
        real_vertices_of_subbox1=[v for v in subbox1 if v in V] #there should be two vertices in this list
        real_vertices_of_subbox2=[v for v in subbox2 if v in V] #there should be two vertices in this list
        #draw_virtual_box_diagram(box,V,where='std')
        #Determine where the real vertex is
        virtual_vertex=[v for v in box if v not in V]
        virtual_vertex=virtual_vertex[0]
        real_corner_vertex=[v for v in box if v[0]!=virtual_vertex[0] and v[1]!=virtual_vertex[1]]
        real_corner_vertex=real_corner_vertex[0]
        
        #Generate the corner diagrams
        [NW, NE, SW, SE]=generate_corner_diagrams(V,box)
        
        # The box has now been moved to a corner we want to keep track of that as well.
        NW_box=find_boxes_from_corner_positions(NW,V_type='NW')
        NE_box=find_boxes_from_corner_positions(NE,V_type='NE')
        SW_box=find_boxes_from_corner_positions(SW,V_type='SW')
        SE_box=find_boxes_from_corner_positions(SE,V_type='SE')
        
        #Draw these virtual boxes
        #print('The NW diagram')
        #draw_virtual_box_diagram(NW_box,NW,where='vert-infty')
        #print('The NE diagram')
        #draw_virtual_box_diagram(NE_box,NE,where='vert-infty')
        #print('The SW diagram')
        #draw_virtual_box_diagram(SW_box,SW,where='vert-infty')
        #print('The SE diagram')
        #draw_virtual_box_diagram(SE_box,SE,where='vert-infty')
        
        #Now for each diagram we find the horizontal y-value of the mouths of the T.  This is the virtual horizontal edge of each box.
        NW_exit_disks=find_exit_disks(NW,NW_box) 
        NE_exit_disks=find_exit_disks(NE,NE_box) 
        SW_exit_disks=find_exit_disks(SW,SW_box) 
        SE_exit_disks=find_exit_disks(SE,SE_box) 
        
        #Next we find all T regions 
        T_regions_NW=find_all_T_regions_snowplow(NW,NW_box,direction='down') 
        T_regions_NE=find_all_T_regions_snowplow(NE,NE_box,direction='down')
        T_regions_SW=find_all_T_regions_snowplow(SW,SW_box,direction='up')
        T_regions_SE=find_all_T_regions_snowplow(SE,SE_box,direction='up')
        
        #For each T region we want to find the valid ones only.  We use the T code for this
        valid_NW_Ts=find_all_valid_Ts(T_regions_NW,NW)
        valid_NE_Ts=find_all_valid_Ts(T_regions_NE,NE)
        valid_SW_Ts=find_all_valid_Ts(T_regions_SW,SW)
        valid_SE_Ts=find_all_valid_Ts(T_regions_SE,SE)
    
        if valid_NW_Ts:
            for valid_T in valid_NW_Ts:
                boundary_of_T=valid_T[0]
                exit_disk=[boundary_of_T[0],boundary_of_T[1]]
                #troubleshooting remove below after
                #draw_virtual_T_diagram(boundary_of_T, NW)
                V_pushed,_=perform_T_move_isotopy(valid_T,NW)
                #now we recheck the box for a v1b simplification
                box1=find_boxes_from_corner_positions(V_pushed,V_type='NW')
                bool1=check_type_1_box_for_simplification(box1,V_pushed,where='std')
                bool2=check_type_1_box_for_simplification(box1,V_pushed,where='vert-infty')
                if bool1 or bool2:
                    print('The box below has a NW gate/snowplow simplification')
                    draw_virtual_box_diagram(box,V,where='std')
                    draw_virtual_T_diagram(boundary_of_T, NW)
                    V_new=perform_destabilization(V_pushed,box1)
                    return V_new
        
        
        if valid_NE_Ts:
            for valid_T in valid_NE_Ts:
                boundary_of_T=valid_T[0]
                exit_disk=[boundary_of_T[0],boundary_of_T[1]]
                #draw_virtual_T_diagram(boundary_of_T, NE)
                V_pushed,_=perform_T_move_isotopy(valid_T,NE)
                #now we recheck the box for a v1b simplification
                box1=find_boxes_from_corner_positions(V_pushed,V_type='NE')
                bool1=check_type_1_box_for_simplification(box1,V_pushed,where='std')
                bool2=check_type_1_box_for_simplification(box1,V_pushed,where='vert-infty')
                if bool1 or bool2:
                    print('The box below has a NE gate/snowplow simplification')
                    draw_virtual_box_diagram(box,V,where='std')
                    draw_virtual_T_diagram(boundary_of_T, NE)
                    V_new=perform_destabilization(V_pushed,box1)
                    return V_new
                
                
        if valid_SW_Ts:
            for valid_T in valid_SW_Ts:
                boundary_of_T=valid_T[0]
                exit_disk=[boundary_of_T[0],boundary_of_T[1]]
                #draw_virtual_T_diagram(boundary_of_T, SW)
                V_pushed,_=perform_T_move_isotopy(valid_T,SW)
                #now we recheck the box for a v1b simplification
                box1=find_boxes_from_corner_positions(V_pushed,V_type='SW')
                bool1=check_type_1_box_for_simplification(box1,V_pushed,where='std')
                bool2=check_type_1_box_for_simplification(box1,V_pushed,where='vert-infty')
                if bool1 or bool2:
                    print('The box below has a SW gate/snowplow simplification')
                    draw_virtual_box_diagram(box,V,where='std')
                    draw_virtual_T_diagram(boundary_of_T, SW)
                    V_new=perform_destabilization(V_pushed,box1)
                    return V_new
        
        if valid_SE_Ts:
            for valid_T in valid_SE_Ts:
                boundary_of_T=valid_T[0]
                exit_disk=[boundary_of_T[0],boundary_of_T[1]]
                #draw_virtual_T_diagram(boundary_of_T, SE)
                V_pushed,_=perform_T_move_isotopy(valid_T,SE)
                #now we recheck the box for a v1b simplification
                box1=find_boxes_from_corner_positions(V_pushed,V_type='SE')
                bool1=check_type_1_box_for_simplification(box1,V_pushed,where='std')
                bool2=check_type_1_box_for_simplification(box1,V_pushed,where='vert-infty')
                if bool1 or bool2:
                    print('The box below has a SE gate/snowplow simplification')
                    draw_virtual_box_diagram(box,V,where='std')
                    draw_virtual_T_diagram(boundary_of_T, SE)
                    V_new=perform_destabilization(V_pushed,box1)
                    return V_new
                
                
    #If you are here then there are no vaild snowplow moves that reveal a destabilization
    #print('There are no valid snowplow moves that reveal a destabilization. More testing required.')
    return V
        

#######################################################

def find_type2_boxes_from_corner_positions(V_in_corner_position,V_type):
    n=len(V_in_corner_position)//2
    _,type2=find_all_virtual_boxes(V_in_corner_position)
    another_type2=find_all_non_std_type_2_boxes(V_in_corner_position)
    type2=type2+another_type2
    
    if V_type=='NW':
        #now isolate the box
        corner_type2_boxes=[]
        for box in type2:
            if [1,-1] in box:
                corner_type2_boxes.append(box)
        return corner_type2_boxes
    
    elif V_type=='NE':
        #now isolate the box
        corner_type2_boxes=[]
        for box in type2:
            if [n,-1] in box:
                corner_type2_boxes.append(box)
        return corner_type2_boxes
    
    elif V_type=='SW':
        #now isolate the box
        corner_type2_boxes=[]
        for box in type2:
            if [1,-n] in box:
                corner_type2_boxes.append(box)
        return corner_type2_boxes
    
        
    elif V_type=='SE':    
        #now isolate the box
        corner_type2_boxes=[]
        for box in type2:
            if [n,-n] in box:
                corner_type2_boxes.append(box)
        return corner_type2_boxes

    
    
    
######
def find_exit_disks(V,box):
    [horizontals,verticals]=sort_vertices_into_verticals_and_horizontals(V)
    
    #STEP 1) We will find all the strands crossing from the virtual box R into the region A which is the annulus-box.
    horizontals_of_box = [[p for p in box if p[1] == y] for y in sorted({p[1] for p in box}, reverse=True)]  #sorted by y-val top to bottom
    
    #A vertical edge that crosses a horizontal of R is the beginning of a strand in A. Because of the positioning one of the horizontals        will not be crossed by any strands. we need to decide which horizontal to look at.
    top_horizontal=horizontals_of_box[0] #checking the top edge of the box
    y_val_of_horizontal =top_horizontal[0][1] 
    x_start, x_end = sorted([top_horizontal[0][0], top_horizontal[1][0]])
    # We need to determine which type of diagram we have.  To do this we will see which horizontal gets crossed by strands in the RD.
    crossed = False
    number_of_crossings=0
    for vertical in verticals: 
        x_val_of_vertical = vertical[0][0]
        y_start, y_end = sorted([vertical[0][1], vertical[1][1]])
        if y_start < y_val_of_horizontal < y_end and x_start < x_val_of_vertical < x_end:
            crossed = True
            number_of_crossings=number_of_crossings+1 #counting the crossings of verticals on top horizontal
    if number_of_crossings!=0: #this is the horizontal we want to consider
        important_horizontal=top_horizontal #It is a SW or SE diagram 
        where_are_strands='above'  #we will be considering the strands above the top horizontal
    else: 
        important_horizontal=horizontals_of_box[1] #It is a NW or NE diagram
        where_are_strands='below'  #we will be considering the strands below the bottom horizontal
    
    #the important_horizontal tells us the y-value of the exit disks we will be checking, the where_are_strands tells us whether our T opens up or down.
    if where_are_strands=='below':
        #Then all strands need to be commuted above the important horizontal
        y_val_of_mouth=important_horizontal[0][1]+0.5
    else: #that is strands are above
        y_val_of_mouth=important_horizontal[0][1]-0.5
        
    
    n = len(V) // 2
    horizontals,verticals=sort_vertices_into_verticals_and_horizontals(V)
    half_x_val = [i + 0.5 for i in range(0,n)]  
    half_y_val=[y_val_of_mouth]
    # Build all possible vertex points
    all_vertices = [[x, y_val_of_mouth] for x in half_x_val]
    
    # Horizontal segments: y=y_val_of_mouth, different x
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
    #for T in horizontal_exit_disks:
    #    draw_T_and_rectangular_diagram(V, T)
    return horizontal_exit_disks  
   
#Now we must generate the T and decide if it is a valid T. We will use a lot of the T code already used for this. V is a NW,NE,SW,SE diagram. The box is the box in corner position.  The direction is which way to check for strands.  if V is a N_ then direction is down and if V is a S_ direction is up. 

def find_all_T_regions_snowplow(V,box,direction):
    from push_Ts import generate_full_T,upward_T_generation,downward_T_generation
    T_regions=[]
    mouths=find_exit_disks(V,box)
   
    for mouth in mouths:
        if direction=='up':
            [horizontal_disk_up,strands_in_T_up,strands_crossing_disk_up]=upward_T_generation(mouth,V)
            if horizontal_disk_up:
                boundary_of_T=generate_full_T(horizontal_disk_up,strands_in_T_up)
                #draw_virtual_T_diagram(boundary_of_T, V)
                T_regions.append([horizontal_disk_up,strands_in_T_up,strands_crossing_disk_up])
        else: 
            [horizontal_disk_down,strands_in_T_down,strands_crossing_disk_down]=downward_T_generation(mouth,V)    
            if horizontal_disk_down:
                boundary_of_T=generate_full_T(horizontal_disk_down,strands_in_T_down)
                #draw_virtual_T_diagram(boundary_of_T, V)
                T_regions.append([horizontal_disk_down,strands_in_T_down,strands_crossing_disk_down])
    return T_regions     


################ Begin Snowplow and Gate v1b simplifications ####################################
def perform_interior_gate_move(box, V):
    n = len(V) // 2
    top_of_box = max(v[1] for v in box)
    bot_of_box = min(v[1] for v in box)
    # draw_virtual_box_diagram(box, V, where='std')
    [horizontals, verticals] = sort_vertices_into_verticals_and_horizontals(V)
    verts_in_box = find_vertices_in_box(box, V, where='std')
    strict_inside_verts = [v for v in verts_in_box if v not in box]

    # Keep horizontals that have at least one strict-inside vertex,
    # but exclude horizontals lying exactly on the top or bottom of the virtual box.
    strict_horizontals_inside = [
        h for h in horizontals
        if any(v in h for v in strict_inside_verts) and h[0][1] not in (top_of_box, bot_of_box)
    ]

    # helper fcn
    def find_commutation_boxes_for_horizontal(horizontal, V):
        horizontal_commutation_boxes = []
        x_start, x_end = sorted([horizontal[0][0], horizontal[1][0]]) 
        y_val_of_horizontal=horizontal[0][1]
        for y in range(-n-1,0): 
            if y==y_val_of_horizontal or y==y_val_of_horizontal-1:
                continue #You can always commute + - 0.5 from current horizontal value
            new_horizontal_edge=[[x_start,y+0.5],[x_end,y+0.5]]
            commutation_box1=[horizontal[0],horizontal[1],new_horizontal_edge[0],new_horizontal_edge[1]]   
            #vertices_in_box=find_vertices_in_box(commutation_box1,V,where='std-no-boundary')
            where='std'
            #if vertices_in_box:
            if check_type_1_box_for_simplification(commutation_box1, V, where):
                horizontal_commutation_boxes.append(commutation_box1)
        return horizontal_commutation_boxes
    
    def perform_downward_interior_gate_move(strict_horizontals_inside, bot_of_box, V):
        strict_horizontals_inside.sort(key=lambda h: h[0][1]) #Now the first horizontal is nearest to the bottom of the box.
        for i, horizontal in enumerate(strict_horizontals_inside):
            horizontal_commutation_boxes=find_commutation_boxes_for_horizontal(horizontal, V)
            #Keep only the commutations that clear the bottom of the box
            commutation_boxes = [b for b in horizontal_commutation_boxes if b[2][1] < bot_of_box]
            if not commutation_boxes: #if this horizontal cannot commute out skip it.
                continue
            # pick the box with the smallest y among the filtered (the one furthest from bot_of_box)
            picked_box = min(commutation_boxes, key=lambda b: b[2][1])
            # perform the commutation
            V = perform_commutation(V, picked_box)
            bot_of_box=bot_of_box+1 #the commutation performed above shifted the bottom of the box up by 1.
            # Move horizontals up by 1 as well
            strict_horizontals_inside = [
                [[h[0][0], h[0][1] + 1], [h[1][0], h[1][1] + 1]]
                for h in strict_horizontals_inside
            ]
            #print('Working on downward gate cascade')
            #draw_rectangular_diagram(V)
        return V
    
    def perform_upward_interior_gate_move(strict_horizontals_inside, top_of_box, V):
        strict_horizontals_inside.sort(key=lambda h: h[0][1], reverse=True) #Now the first horizontal is nearest to the top of the box.
        for i, horizontal in enumerate(strict_horizontals_inside):
            horizontal_commutation_boxes=find_commutation_boxes_for_horizontal(horizontal, V)
            #Keep only the commutations that clear the top of the box
            commutation_boxes = [b for b in horizontal_commutation_boxes if b[2][1] > top_of_box]
            if not commutation_boxes: #if this horizontal cannot commute out skip it.
                continue
            # pick the box with the largest y among the filtered (the one furthest from top_of_box)
            picked_box = max(commutation_boxes, key=lambda b: b[2][1])
            #print('I am about to preform the following commutation')
            #draw_virtual_box_diagram(picked_box,V,where='std')
            # perform the commutation
            V = perform_commutation(V, picked_box)
            top_of_box=top_of_box-1 #the commutation performed above shifted the bottom of the box down by 1.
            # Move horizontals down by 1 as well
            strict_horizontals_inside = [
                [[h[0][0], h[0][1] - 1], [h[1][0], h[1][1] - 1]]
                for h in strict_horizontals_inside
            ]
            #print('Working on upward gate cascade')
            #draw_rectangular_diagram(V)
        return V
    
    V_down=perform_downward_interior_gate_move(strict_horizontals_inside, bot_of_box, V)
    #print('this is V now, see if this matches')
    #draw_rectangular_diagram(V)
    
    # Recompute strict horizontals inside for the upward pass
    # Important: do this using the original V
    [horizontals, verticals] = sort_vertices_into_verticals_and_horizontals(V)
    verts_in_box = find_vertices_in_box(box, V, where='std')
    strict_inside_verts = [v for v in verts_in_box if v not in box]

    strict_horizontals_inside = [
        h for h in horizontals
        if any(v in h for v in strict_inside_verts) and h[0][1] not in (top_of_box, bot_of_box)
    ]

    V_up = perform_upward_interior_gate_move(strict_horizontals_inside, top_of_box, V)
    return [V_down,V_up]
    
    
#Will need to update this for all the verticals that are inside the vertical annulus given by the box.
def perform_interior_snowplow_move(box, V):
    n = len(V) // 2
    left_of_box = min(v[0] for v in box)
    right_of_box = max(v[0] for v in box)
    # draw_virtual_box_diagram(box, V, where='std')
    [horizontals, verticals] = sort_vertices_into_verticals_and_horizontals(V)
    verts_in_box = find_vertices_in_box(box, V, where='std')
    strict_inside_verts = [v for v in verts_in_box if v not in box]
    #print('these are strict_inside_verts',strict_inside_verts)

    # Keep verticals that have at least one strict-inside vertex,
    # but exclude verticals lying exactly on the top or bottom of the virtual box.
    strict_verticals_inside = [
        v for v in verticals
        if any(vertex in v for vertex in strict_inside_verts) and v[0][0] not in (left_of_box, right_of_box)
    ]
    #print('these are the inside verticals')
    #print(strict_verticals_inside)

    def find_commutation_boxes_for_vertical(vertical, V):
        vertical_commutation_boxes = []
        y_start, y_end = sorted([vertical[0][1], vertical[1][1]]) 
        x_val_of_vertical=vertical[0][0]
        # search candidate integer x positions across the full horizonal range, excluding the interior of the box
        for x in range(0, n + 1):
            # don't pick x that would be the same or adjacent (these are not useful commutations)
            if x == x_val_of_vertical or x == x_val_of_vertical - 1:
                continue
            x_new = x + 0.5
            new_vertical_edge = [[x_new, y_start], [x_new, y_end]]
            commutation_box1 = [vertical[0], vertical[1], new_vertical_edge[0], new_vertical_edge[1]]
            where = 'std'
            if check_type_1_box_for_simplification(commutation_box1, V, where):
                vertical_commutation_boxes.append(commutation_box1)
        return vertical_commutation_boxes
    
    def perform_rightward_interior_snowplow_move(strict_verticals_inside, right_of_box, V):
        strict_verticals_inside.sort(key=lambda h: h[0][0], reverse=True) #Now the first vertical is nearest to the right of the box.
        for i, vertical in enumerate(strict_verticals_inside):
            vertical_commutation_boxes=find_commutation_boxes_for_vertical(vertical, V)
            #Keep only the commutations that clear the bottom of the box
            commutation_boxes = [b for b in vertical_commutation_boxes if b[2][0] > right_of_box]
            if not commutation_boxes: #if this horizontal cannot commute out skip it.
                continue
            # pick the box with the largest x-val among the filtered (the one rightmost from right_of_box)
            picked_box = max(commutation_boxes, key=lambda b: b[2][0])
            # perform the commutation
            #print('I am about to perform the following commutation')
            #draw_virtual_box_diagram(picked_box,V,where='std')
            V = perform_commutation(V, picked_box)
            right_of_box=right_of_box-1 #the commutation performed above shifted the right of the box up by -1.
            # Move verticals over by -1 as well
            strict_verticals_inside = [
                [[v[0][0]-1, v[0][1]], [v[1][0]-1, v[1][1]]]
                for v in strict_verticals_inside
            ]
            #print('Working on rightward snowplow cascade')
            #draw_rectangular_diagram(V)
        return V
    
    def perform_leftward_interior_snowplow_move(strict_verticals_inside, left_of_box, V):
        strict_verticals_inside.sort(key=lambda h: h[0][0]) #Now the first vertical is nearest to the left of the box.
        #print('this is the inside verticals from left to right')
        #print(strict_verticals_inside)
        for i, vertical in enumerate(strict_verticals_inside):
            vertical_commutation_boxes=find_commutation_boxes_for_vertical(vertical, V)
            #Keep only the commutations that clear the bottom of the box
            commutation_boxes = [b for b in vertical_commutation_boxes if b[2][0] < left_of_box]
            if not commutation_boxes: #if this horizontal cannot commute out skip it.
                continue
            # pick the box with the smallest x-val among the filtered (the one leftmost from left_of_box)
            picked_box = min(commutation_boxes, key=lambda b: b[2][0])
            # perform the commutation
            #print('I am about to perform the following commutation')
            #draw_virtual_box_diagram(picked_box,V,where='std')
            V = perform_commutation(V, picked_box)
            left_of_box=left_of_box+1 #the commutation performed above shifted the left of the box up by +1.
            # Move verticals over by +1 as well
            strict_verticals_inside = [
                [[v[0][0]+1, v[0][1]], [v[1][0]+1, v[1][1]]]
                for v in strict_verticals_inside
            ]
            #print('Working on leftward snowplow cascade')
            #draw_rectangular_diagram(V)
        return V
    
    V_right=perform_rightward_interior_snowplow_move(strict_verticals_inside, right_of_box, V)
    
    # Recompute verticals inside the box after rightward sweep altered them
    horizontals, verticals = sort_vertices_into_verticals_and_horizontals(V)
    verts_in_box = find_vertices_in_box(box, V, where='std')
    strict_inside_verts = [v for v in verts_in_box if v not in box]
    strict_verticals_inside = [
        v for v in verticals
        if any(vertex in v for vertex in strict_inside_verts) and v[0][0] not in (left_of_box, right_of_box)
    ]
    
    V_left=perform_leftward_interior_snowplow_move(strict_verticals_inside, left_of_box, V)
    return [V_right,V_left]


def gate_move_simplification(V):
    switch=1
    while switch==1:
        switch=0
        type1,_=find_all_virtual_boxes(V)
        for box in type1: 
            #draw_virtual_box_diagram(box,V,where='std')
            [V_down,V_up]=perform_interior_gate_move(box,V) #the point of the interior gate move is that the box does not change! 
            box1=check_for_type_1_simplifications_not_verbose(V_down)
            if box1:
                #print("A downward gate simplification was found")
                switch=1
                V=perform_destabilization(V_down,box1)
                #draw_rectangular_diagram(V)
                return V
            box2=check_for_type_1_simplifications_not_verbose(V_up)
            if box2:
                #print("An upward gate simplification was found")
                switch=1
                V=perform_destabilization(V_up,box2)
                #draw_rectangular_diagram(V)
                return V
    return V

def snowplow_move_simplification(V):
    switch=1
    while switch==1:
        switch=0
        type1,_=find_all_virtual_boxes(V)
        for box in type1: 
            #draw_virtual_box_diagram(box,V,where='std')
            [V_right,V_left]=perform_interior_snowplow_move(box,V)   #the point of the interior snowplow move is that the box does not change!
            box1=check_for_type_1_simplifications_not_verbose(V_right)
            if box1:
                switch=1
                V=perform_destabilization(V_right,box1)
                #draw_rectangular_diagram(V)
                return V 
            box2=check_for_type_1_simplifications_not_verbose(V_left)
            if box2:
                switch=1
                V=perform_destabilization(V_left,box2)
                #draw_rectangular_diagram(V)
                return V 
    return V

def snowplow_gate_move_simplification(V):
    switch=1
    while switch==1:
        switch=0
        type1,_=find_all_virtual_boxes(V)
        for box in type1: 
            #draw_virtual_box_diagram(box,V,where='std')
            [V_right,V_left]=perform_interior_snowplow_move(box,V)   #the point of the interior snowplow move is that the box does not change!
            box1=check_for_type_1_simplifications_not_verbose(V_right)
            if box1:
                print('A rightward snowplow move in the following virtual box revealed a simplification')
                draw_virtual_box_diagram(box,V,where='std')
                switch=1
                V=perform_destabilization(V_right,box1)
                draw_rectangular_diagram(V)
                return V 
            V_temp=check_for_type_2_simplifications_not_verbose(V_right)
            if V_temp:
                print('A rightward snowplow move in the following virtual box revealed a type 2 simplification')
                draw_virtual_box_diagram(box,V,where='std')
                V=V_temp
                switch=1
                return V
            box2=check_for_type_1_simplifications_not_verbose(V_left)
            if box2:
                print('A leftward snowplow move in the following virtual box revealed a simplification')
                draw_virtual_box_diagram(box,V,where='std')
                switch=1
                V=perform_destabilization(V_left,box2)
                draw_rectangular_diagram(V)
                return V               
            V_temp=check_for_type_2_simplifications_not_verbose(V_left)
            if V_temp:
                print('A leftward snowplow move in the following virtual box revealed a type 2 simplification')
                draw_virtual_box_diagram(box,V,where='std')
                V=V_temp
                switch=1
                return V   
            #if you have made it here you did not see a snowplow simplification
            [V_down,V_up]=perform_interior_gate_move(box,V_right)   #the point of the interior gate move is that the box does not change!
            box1=check_for_type_1_simplifications_not_verbose(V_down)
            if box1:
                print('A rightward snowplow then downward gate move in the following virtual box revealed a simplification')
                draw_virtual_box_diagram(box,V,where='std')
                switch=1
                V=perform_destabilization(V_down,box1)
                draw_rectangular_diagram(V)
                return V
            V_temp=check_for_type_2_simplifications_not_verbose(V_down)
            if V_temp:
                print('A rightward snowplow then downward move in the following virtual box revealed a type 2 simplification')
                draw_virtual_box_diagram(box,V,where='std')
                V=V_temp
                switch=1
                return V
            
            box2=check_for_type_1_simplifications_not_verbose(V_up)
            if box2:
                print('A rightward snowplow then upward gate move in the following virtual box revealed a simplification')
                draw_virtual_box_diagram(box,V,where='std')
                switch=1
                V=perform_destabilization(V_up,box2)
                draw_rectangular_diagram(V)
                return V
            V_temp=check_for_type_2_simplifications_not_verbose(V_up)
            if V_temp:
                print('A rightward snowplow then upward move in the following virtual box revealed a type 2 simplification')
                draw_virtual_box_diagram(box,V,where='std')
                V=V_temp
                switch=1
                return V
            
            #if you have made it here you did not see a snowplow gate simplification in V_right
            [V_down,V_up]=perform_interior_gate_move(box,V_left)   #the point of the interior gate move is that the box does not change!
            box1=check_for_type_1_simplifications_not_verbose(V_down)
            if box1:
                print('A leftward snowplow then downward gate move in the following virtual box revealed a simplification')
                draw_virtual_box_diagram(box,V,where='std')
                switch=1
                V=perform_destabilization(V_down,box1)
                draw_rectangular_diagram(V)
                return V
            
            V_temp=check_for_type_2_simplifications_not_verbose(V_down)
            if V_temp:
                print('A leftward snowplow then downward gate move in the following virtual box revealed a type 2 simplification')
                draw_virtual_box_diagram(box,V,where='std')
                V=V_temp
                switch=1
                return V
            
            box2=check_for_type_1_simplifications_not_verbose(V_up)
            if box2:
                print('A leftward snowplow then upward gate move in the following virtual box revealed a simplification')
                draw_virtual_box_diagram(box,V,where='std')
                switch=1
                V=perform_destabilization(V_up,box2)
                draw_rectangular_diagram(V)
                return V
            
            V_temp=check_for_type_2_simplifications_not_verbose(V_up)
            if V_temp:
                print('A leftward snowplow move then upward in the following virtual box revealed a type 2 simplification')
                draw_virtual_box_diagram(box,V,where='std')
                V=V_temp
                switch=1
                return V
    return V

def gate_snowplow_move_simplification(V):
    switch=1
    while switch==1:
        switch=0
        type1,_=find_all_virtual_boxes(V)
        for box in type1: 
            #draw_virtual_box_diagram(box,V,where='std')
            [V_down,V_up]=perform_interior_gate_move(box,V)   
            box1=check_for_type_1_simplifications_not_verbose(V_up)
            if box1:
                print('An upward gate move in the following virtual box revealed a simplification')
                draw_virtual_box_diagram(box,V,where='std')
                switch=1
                V=perform_destabilization(V_up,box1)
                draw_rectangular_diagram(V)
                return V 
            
            V_temp=check_for_type_2_simplifications_not_verbose(V_up)
            if V_temp:
                print('An upward gate move in the following virtual box revealed a type 2 simplification')
                draw_virtual_box_diagram(box,V,where='std')
                V=V_temp
                switch=1
                return V
            
            box2=check_for_type_1_simplifications_not_verbose(V_down)
            if box2:
                print('A downward gate move in the following virtual box revealed a simplification')
                draw_virtual_box_diagram(box,V,where='std')                         
                switch=1
                V=perform_destabilization(V_down,box2)
                draw_rectangular_diagram(V)
                return V 
            
            V_temp=check_for_type_2_simplifications_not_verbose(V_down)
            if V_temp:
                print('A downward gate move in the following virtual box revealed a type 2 simplification')
                draw_virtual_box_diagram(box,V,where='std')
                V=V_temp
                switch=1
                return V
            
            #if you have made it here you did not see a gate simplification
            [V_right,V_left]=perform_interior_snowplow_move(box,V_up)   #the point of the interior gate move is that the box does not change!
            box1=check_for_type_1_simplifications_not_verbose(V_right)
            if box1:
                print('An upward gate then rightward snowplow move in the following virtual box revealed a simplification')
                draw_virtual_box_diagram(box,V,where='std')
                switch=1
                V=perform_destabilization(V_right,box1)
                draw_rectangular_diagram(V)
                return V
            
            V_temp=check_for_type_2_simplifications_not_verbose(V_right)
            if V_temp:
                print('An upward gate then rightward snowplow move in the following virtual box revealed a type 2 simplification')
                draw_virtual_box_diagram(box,V,where='std')
                V=V_temp
                switch=1
                return V
 
            box2=check_for_type_1_simplifications_not_verbose(V_left)
            if box2:
                print('An upward gate then leftward snowplow move in the following virtual box revealed a simplification')
                draw_virtual_box_diagram(box,V,where='std')
                switch=1
                V=perform_destabilization(V_left,box2)
                draw_rectangular_diagram(V)
                return V
            V_temp=check_for_type_2_simplifications_not_verbose(V_left)
            if V_temp:
                print('An upward gate then leftward snowplow move in the following virtual box revealed a type 2 simplification')
                draw_virtual_box_diagram(box,V,where='std')
                V=V_temp
                switch=1
                return V
            
            #if you have made it here you did not see a snowplow gate simplification in V_up
            [V_right,V_left]=perform_interior_gate_move(box,V_down)   #the point of the interior gate move is that the box does not change!
            box1=check_for_type_1_simplifications_not_verbose(V_left)
            if box1:
                print('An downward gate then leftward snowplow move in the following virtual box revealed a simplification')
                draw_virtual_box_diagram(box,V,where='std')
                switch=1
                V=perform_destabilization(V_left,box1)
                draw_rectangular_diagram(V)
                return V
            V_temp=check_for_type_2_simplifications_not_verbose(V_left)
            
            if V_temp:
                print('An downward gate then leftward snowplow move in the following virtual box revealed a type 2 simplification')
                draw_virtual_box_diagram(box,V,where='std')
                V=V_temp
                switch=1
                return V
            
            box2=check_for_type_1_simplifications_not_verbose(V_right)
            if box2:
                print('An downward gate then rightward snowplow move in the following virtual box revealed a simplification')
                draw_virtual_box_diagram(box,V,where='std')
                switch=1
                V=perform_destabilization(V_right,box2)
                draw_rectangular_diagram(V)
                return V
            
            V_temp=check_for_type_2_simplifications_not_verbose(V_right)
            if V_temp:
                print('An downward gate then rightward snowplow move in the following virtual box revealed a type 2 simplification')
                draw_virtual_box_diagram(box,V,where='std')
                V=V_temp
                switch=1
                return V
    return V



################# End Snowplow and Gate v1b simplifications ######################################
### Auxillary for gates and snowplows
def perform_commutation(V,box):
    #this shifts the RD which needs to be fixed   
    #first have to round the half values and shift accordingly
    new_vertices = [v for v in box if v not in V]
    V=[v for v in V if v not in box]
    V_new=[]
    #if these new_vertices share an x-value then we need to shift all the vertices in V with x-value larger by 1
    #if these new_vertices share an y-value then we need to shift all the vertices in V with y-value larger by 1
    shift_by_x=0
    shift_by_y=0
    if new_vertices[0][0]==new_vertices[1][0]: #the new vertices form a new vertical edge
        shift_by_x=1
    else: #the new vertices form a new horizontal edge
        shift_by_y=1
    if shift_by_x==1:
        for v in V:
            if v[0]>new_vertices[0][0]:
                V_new.append([v[0]+1,v[1]])
            else:
                V_new.append(v)
        def ceil_of_vertices(box):
            import math as m
            ceil_box= [[int(m.ceil(num)) for num in sublist] for sublist in box]
            return ceil_box
        rounded_verts=ceil_of_vertices(new_vertices)
        new_vertices=rounded_verts  
        new_vertices            
    else:
        for v in V:
            if v[1]<new_vertices[0][1]:
                v1=[v[0],v[1]-1]
            else:
                v1=v
            V_new.append(v1)        
        def floor_of_vertices(box):
            import math as m
            floor_box= [[int(m.floor(num)) for num in sublist] for sublist in box]
            return floor_box
        rounded_verts=floor_of_vertices(new_vertices)
        new_vertices=rounded_verts  
    V_new=V_new+new_vertices
    #V_new has a gap now so I will shift the vertex set twice so this is fixed
    V_new=shift_vertex_set(V_new)
    #V_new=shift_vertex_set(V_new)
    V_new.sort()
    temp=[]
    for v in V_new:
        temp.append(list(v))

    V_new=temp
    return V_new
##########################################################


# This is very important to be sure a commutation can actually occur out of a box in a diagram.
def count_edge_commutation(edge,V):
    
    n=len(V)//2 #this is the furthest right the diagram goes!
    horiz,vert=sort_vertices_into_verticals_and_horizontals(V)
    all_horiz_ys = set()
    for e in horiz:
        all_horiz_ys.add(e[0][1])
        all_horiz_ys.add(e[1][1])
    all_vert_xs = set()
    for e in vert:
        all_vert_xs.add(e[0][0])
        all_vert_xs.add(e[1][0])    
    
    if edge in horiz: #its a horizontal edge
        x_start, x_end = sorted([edge[0][0], edge[1][0]])
        #width_of_edge=list(range(edge[0][0],edge[1][0]+1))
        y_val_of_edge=edge[0][1]
        commute=True
        commute_up_count=0
        while commute==True:
            next_y=((y_val_of_edge + 1 + n) % n) - n 
          
            immediate_above_horiz = [e for e in horiz if e[0][1] == next_y or e[1][1] == next_y]
            immediate_above_horiz=immediate_above_horiz[0]

            x_above_start,x_above_end= sorted([immediate_above_horiz[0][0], immediate_above_horiz[1][0]])

            if x_end<x_above_start or x_above_end<x_start: #disjoint
                commute_up_count+=1
                y_val_of_edge= next_y  

            elif x_start<x_above_start<x_above_end<x_end or x_above_start<x_start<x_end<x_above_end: #nested 
                commute_up_count+= 1
                y_val_of_edge= next_y    
            else: #interleaved
                commute=False
           
                
        commute=True
        commute_down_count=0
        y_val_of_edge=edge[0][1]
        while commute==True:
            next_y = ((y_val_of_edge-1+n) % n)-n
            
            immediate_below_horiz = [e for e in horiz if e[0][1] == next_y or e[1][1] == next_y]
            
            immediate_below_horiz=immediate_below_horiz[0]

            x_below_start,x_below_end= sorted([immediate_below_horiz[0][0], immediate_below_horiz[1][0]])

            if x_end<x_below_start or x_below_end<x_start: #disjoint
                commute_down_count+=1
                y_val_of_edge= next_y 

            elif x_start<x_below_start<x_below_end<x_end or x_below_start<x_start<x_end<x_below_end: #nested 
                commute_down_count+= 1
                y_val_of_edge= next_y    
            else: #interleaved
                commute=False
        
        return [commute_up_count, commute_down_count]          
    
    
    
    if edge in vert: #its a vertical edge
        y_start, y_end = sorted([edge[0][1], edge[1][1]]) #bottom to top
        #height_of_edge=list(range(edge[0][1],edge[1][1]+1))
        x_val_of_edge=edge[0][0]
        commute=True
        commute_right_count=0
        while commute==True:
           
            next_x = (x_val_of_edge) % n +1  # wrap right: n → 1
           
            immediate_right_vert = [e for e in vert if e[0][0] == next_x or e[1][0] == next_x]

            #immediate_right_vert=[edge for edge in vert if edge[0][0]==x_val_of_edge+1]
            
            immediate_right_vert=immediate_right_vert[0]

            y_right_start,y_right_end=sorted([immediate_right_vert[0][1], immediate_right_vert[1][1]]) #bottom to top
            #height_of_right_edge=list(range(immediate_right_vert[0][1],immediate_right_vert[1][1]+1))
            #intersection_set = set(height_of_edge).intersection(height_of_right_edge)
            #intersection_heights = list(intersection_set)
            if y_start>y_right_end or y_right_start>y_end: #disjoint
                commute_right_count+= 1
                x_val_of_edge= next_x  
            elif y_start<y_right_start<y_right_end<y_end or y_right_start<y_start<y_end<y_right_end:#nested
                commute_right_count+= 1
                x_val_of_edge=next_x
            else: #interleaved
                commute=False
           
        
        commute=True
        commute_left_count=0
        x_val_of_edge=edge[0][0]
        while commute==True:
            
            next_x = (x_val_of_edge - 2) % n + 1
           
            immediate_left_vert = [e for e in vert if e[0][0] == next_x or e[1][0] == next_x]
            
            immediate_left_vert=immediate_left_vert[0]
            y_left_start,y_left_end=sorted([immediate_left_vert[0][1], immediate_left_vert[1][1]]) #bottom to top
            if y_start>y_left_end or y_left_start>y_end: #disjoint
                commute_left_count+= 1
                x_val_of_edge= next_x  
            elif y_start<y_left_start<y_left_end<y_end or y_left_start<y_start<y_end<y_left_end:#nested
                commute_left_count+= 1
                x_val_of_edge= next_x
            else: #interleaved
                commute=False 
        return [commute_left_count,commute_right_count] 
    
    if edge not in vert and edge not in horiz:
        raise TypeError("edge is not in verticals or horizontals")