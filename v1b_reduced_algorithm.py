from drawing_rectangular_diagrams_src.draw_rectangular_diagram import *
from drawing_rectangular_diagrams_src.draw_type_2_boxes import *
from virtual_boxes_in_rectangular_diagrams import *
from rechoosing_infinity import find_boxes_from_corner_positions, generate_corner_diagrams 
from topological_ordering import *
import math as m
from collections import deque
import copy
from GridPyM import *
from snappy import *


## 9/27/2026 Seth you have two things that need changing. One is checking all infinities in the check for type 1 simplifications and the other is the unknot verification in the last function both are commented on.

def check_type_1_box_for_simplification(box,V,where):
    if where=='std':
        where1='std-no-boundary'
    elif where=='horiz-infty':
        where1='horiz-infty-no-boundary'
    elif where=='vert-infty':
        where1='vert-infty-no-boundary'
    #elif where=='horiz-vert-infty':
        #where1='horiz-vert-infty'
    #    where1='horiz-vert-infty-no-boundary'   
    else: where1=where
    #if where=='std-no-boundary':
    #    where1='std' 
    
        
    [horizontals,verticals]=sort_vertices_into_verticals_and_horizontals(V)
    vertices_in_box=[v for v in V if check_if_vertex_in_box(v,box,where1)==True] #these are vertices in the interior of the box
    #print('These are the vertices in the box',vertices_in_box)
    if not vertices_in_box: #empty box! do the simplification
        return True
    
    strands=build_strands_graph(vertices_in_box) #this builds strands out of only vertices contained entirely in box
    #print('These are the strands',strands)
    vertical_strands=[]
    horizontal_strands=[]
    for strand in strands:
        if len(strand)==1: #this strand hooks the box
            return False
        else:
             #Update 6/18: There was an issue about whether to view the boundary of the box as inside or outside the virtual box.  This is dealt with by considering strands that have an endpoint on the boundary-- those strands will have that edge added this should not interfere with anything else
            type_of_strand = [None, None]
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
                
            elif check_if_vertex_in_box(z,box,where1)==False and check_if_vertex_in_box(z,box,where)==True :#this vertex is on the boundary   
                 #in this case the strand will start with the vertex on the box 
                strand.insert(0,z) #add this vertex to the strand
                type_of_strand[0]='H'  #the beginning of this strand crosses a vertical on the boundary which is adjacent to a horizontal
            else: #this vertex is out of the box
                #strand.insert(-1,z) #add this vertex to the strand
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
                type_of_strand[1]='H' #the beginning of this strand crosses a horizontal
                
            elif check_if_vertex_in_box(z,box,where1)==False and check_if_vertex_in_box(z,box,where)==True :#this vertex is on the boundary   
                strand.insert(-1,z) #add this vertex to the strand
                type_of_strand[1]='H'  #the beginning of this strand crosses a horizontal on the boundary which is adjacent to a vertical
            else: #this vertex is out of the box
                type_of_strand[1]='V' #otherwise the strand crosses a vertical
            
            if len(set(type_of_strand))==2: #the strand enters on a V and leaves on a H or vice versa
                return False #There is a strand that enters and leaves on V and H 
            if set(type_of_strand)== {'H'}:
                horizontal_strands.append(strand)
            else:
                vertical_strands.append(strand)

    #if we have come this far without breaking out we have sorted all the strands into verticals and horizontals
    flattened = [point for strand in horizontal_strands for point in strand]
    vertical_segments = [
        [group[i], group[i+1]]
        for x in set(p[0] for p in flattened)
        for group in [sorted([p for p in flattened if p[0] == x], key=lambda p: p[1])]
        for i in range(0, len(group) - 1, 2)] 
    #vertical_segments are the vertical edges of the horizonal strands

    flattened = [point for strand in vertical_strands for point in strand]
    horizontal_segments = [
    [group[i], group[i+1]]
    for y in set(p[1] for p in flattened)
    for group in [sorted([p for p in flattened if p[1] == y], key=lambda p: p[0])]
    for i in range(0, len(group) - 1, 2)]
    #now check the crossing of the vertical segements against the vertical segments
    #now we have to break into different subcases depending on 'where' and if the edges leave the box 
    
    if not (vertical_segments and horizontal_segments): #one of these is empty
        return True
    
    if where=='std' or where=='std-no-boundary':
        return  check_no_crossings(vertical_segments, horizontal_segments,where='std')
    
    
    elif where=='horiz-infty':
     #the horizontal part of a vertical strand
        for horizontal_edge in horizontal_segments: #these are the horizontal parts of the vertical strands
            left_vertex_x_value=horizontal_edge[0][0]
            right_vertex_x_value=horizontal_edge[1][0]
            horizontal_height=horizontal_edge[0][1] #both vertices share same y-val
            for vertical_edge in vertical_segments: #these are the vertical parts of horizontal strands
                x_value_of_vertical_edge=vertical_edge[0][0] #vertices share x-val 
                min_y=min(v[1] for v in vertical_edge)
                max_y=max(v[1] for v in vertical_edge)
                min_box_x=min(v[0] for v in box)
                max_box_x=max(v[0] for v in box)
                if min_box_x<=left_vertex_x_value<=right_vertex_x_value<=max_box_x: #the horiz edge is in the box w/o flipping through infty
                    if left_vertex_x_value<=x_value_of_vertical_edge<=right_vertex_x_value and min_y<=horizontal_height<=max_y: #this virt. box has linking
                        return False #we have linking_inside.  This box will not work to simplify
                else: #the horizontal edge was flipped through infty
                    if min_y<=horizontal_height<=max_y: #the horizontal egde will be flipped and hit an x-value of vertical edge
                         return False

        return True #if you make it to here then you are unlinked
    
    
    elif where=='vert-infty': 
        for horizontal_edge in horizontal_segments: #these are the horizontal parts of the vertical strands
            left_vertex_x_value=horizontal_edge[0][0]
            right_vertex_x_value=horizontal_edge[1][0]
            horizontal_height=horizontal_edge[0][1] #both vertices share same y-val
            for vertical_edge in vertical_segments: #these are the vertical parts of horizontal strands
                x_value_of_vertical_edge=vertical_edge[0][0] #vertices share x-val 
                min_y=min(v[1] for v in vertical_edge)
                max_y=max(v[1] for v in vertical_edge)
                min_box_y=min(v[1] for v in box)
                max_box_y=max(v[1] for v in box)
                if min_box_y<=min_y<=max_y<=max_box_y:
                    if left_vertex_x_value<=x_value_of_vertical_edge<=right_vertex_x_value and min_y<=horizontal_height<=max_y: #this virt. box has linking
                        return False #we have linking_inside.  This box will not work to simplify
                else:
                    if left_vertex_x_value<=x_value_of_vertical_edge<=right_vertex_x_value: #this vertical egde will be flipped to remain in the box and will link
                         return False
        return True #if you make it to here then you are unlinked


## This is a general hooked box check for infty=std #########################################################
def check_type_1_box_hooked(box,V):
    where='std'
    where1='std-no-boundary'
    [horizontals,verticals]=sort_vertices_into_verticals_and_horizontals(V)
    vertices_in_box=[v for v in V if check_if_vertex_in_box(v,box,where1)==True] #these are vertices in the interior of the box
    if not vertices_in_box: #empty box! do the simplification
        return False
    
    strands=build_strands_graph(vertices_in_box) #this builds strands out of only vertices contained entirely in box
    vertical_strands=[]
    horizontal_strands=[]
    for strand in strands:
        if len(strand)==1: #this strand hooks the box
            return True
        else:
            type_of_strand = [None, None] #initization
            
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
                
            elif check_if_vertex_in_box(z,box,where1)==False and check_if_vertex_in_box(z,box,where)==True :#this vertex is on the boundary   
                 #in this case the strand will start with the vertex on the box 
                strand.insert(0,z) #add this vertex to the strand
                type_of_strand[0]='H'  #the beginning of this strand crosses a vertical on the boundary which is adjacent to a horizontal
            else: #this vertex is out of the box
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
                type_of_strand[1]='H' #the beginning of this strand crosses a horizontal
                
            elif check_if_vertex_in_box(z,box,where1)==False and check_if_vertex_in_box(z,box,where)==True :#this vertex is on the boundary   
                strand.insert(-1,z) #add this vertex to the strand
                type_of_strand[1]='H'  #the beginning of this strand crosses a horizontal on the boundary which is adjacent to a vertical
            else: #this vertex is out of the box
                type_of_strand[1]='V' #otherwise the strand crosses a vertical
            
            if len(set(type_of_strand))==2: #the strand enters on a V and leaves on a H or vice versa
                return True #There is a strand that enters and leaves on V and H 
   
       
#################################################

def check_for_type_1_simplifications(V):
    
    type1,_=find_all_virtual_boxes(V)
    n=len(V)//2
    for box in type1:
        
        #9/27/2026 Code verification: I have commented out bool0, bool1 and bool2 I want to only look at horiz-vert-infty
        bool0=check_type_1_box_for_simplification(box,V,where='std')
        
        if bool0:
            print('The box below has a generalized v1b simplification')
            draw_virtual_box_diagram(box,V,where='std')
            return box
        bool1=check_type_1_box_for_simplification(box,V,where='horiz-infty')
        if bool1:
            print('The box below has a generalized v1b simplification')
            draw_virtual_box_diagram(box,V,where='horiz-infty')
            return box
        bool2=check_type_1_box_for_simplification(box,V,where='vert-infty')
        if bool2:
            print('The box below has a generalized v1b simplification')
            draw_virtual_box_diagram(box,V,where='vert-infty')
            return box

        #Rechoose the point at infinity and see if in the 'std' there is a simplification.  This will correspond to a horiz-vert-infty type simplification
        #draw_virtual_box_diagram(box,V,where='std')
        #Determine where the real vertex is
        virtual_vertex=[v for v in box if v not in V]

        if not virtual_vertex:
            if len(V)//2>2:
                print('This diagram has a split link component')
                draw_virtual_box_diagram(box,V,where='std')
                print('This component will be removed and the simplification process will continue')
                return box #it should be removed from the diagram
            else:
                print('The diagram is unknotted')
                return box

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

        bool1=check_type_1_box_for_simplification(NW_box,NW,where='std')
        bool2=check_type_1_box_for_simplification(NE_box,NE,where='std')
        bool3=check_type_1_box_for_simplification(SW_box,SW,where='std')
        bool4=check_type_1_box_for_simplification(SE_box,SE,where='std')
        if bool1 or bool2 or bool3 or bool4:
            #if bool1:
            #    print('its NW')
            #    draw_virtual_box_diagram(NW_box,NW,where='std')
            #if bool2:
            #    print('its NE')
            #    draw_virtual_box_diagram(NE_box,NE,where='std')
            #if bool3:
            #    print('its SW')
            #    draw_virtual_box_diagram(SW_box,SW,where='std')    
            #if bool4:
            #    print('its SE')
            #    draw_virtual_box_diagram(SE_box,SE,where='std')    
            
            #9/27/2026 I am drawing it now!
            print('The box below has a generalized v1b simplification')
            draw_virtual_box_diagram(box,V,where='horiz-vert-infty')
            return box
    return []   

#This code is needed if being used in other functions and you do not want all the printing
def check_for_type_1_simplifications_not_verbose(V):
    
    from rechoosing_infinity import find_boxes_from_corner_positions, generate_corner_diagrams 
    type1,_=find_all_virtual_boxes(V)
    n=len(V)//2
    for box in type1:
        bool0=check_type_1_box_for_simplification(box,V,where='std')
        if bool0:
            return box
        bool1=check_type_1_box_for_simplification(box,V,where='horiz-infty')
        if bool1:
            return box
        bool2=check_type_1_box_for_simplification(box,V,where='vert-infty')
        if bool2:
            return box
        #Determine where the real vertex is
        virtual_vertex=[v for v in box if v not in V]
        if virtual_vertex:
            virtual_vertex=virtual_vertex[0]
            real_corner_vertex=[v for v in box if v[0]!=virtual_vertex[0] and v[1]!=virtual_vertex[1]]
            real_corner_vertex=real_corner_vertex[0]
        else:
            print('There is an unlinked component in the diagram!')
            V_new=[v for v in V if v not in box]
            V_new=shift_vertex_set(V_new)
            V_new=shift_vertex_set(V_new)
            print('This is the new diagram with the unlinked component removed')
            draw_rectangular_diagram(V_new)
            #I have not returned it yet though
            return box
        #Generate the corner diagrams
        [NW, NE, SW, SE]=generate_corner_diagrams(V,box)

        # The box has now been moved to a corner we want to keep track of that as well.
        NW_box=find_boxes_from_corner_positions(NW,V_type='NW')
        NE_box=find_boxes_from_corner_positions(NE,V_type='NE')
        SW_box=find_boxes_from_corner_positions(SW,V_type='SW')
        SE_box=find_boxes_from_corner_positions(SE,V_type='SE')

        bool1=check_type_1_box_for_simplification(NW_box,NW,where='std')
        bool2=check_type_1_box_for_simplification(NE_box,NE,where='std')
        bool3=check_type_1_box_for_simplification(SW_box,SW,where='std')
        bool4=check_type_1_box_for_simplification(SE_box,SE,where='std')
        if bool1 or bool2 or bool3 or bool4:
            return box
    return []    
            
def perform_destabilization(V,box):
    if box==[]: #there were no simplifications found
        return [] # the function returns [] which will terminate the loop made below. 
    virtual_vertex=[v for v in box if v not in V]
    #IF AN UNKNOTTED COMPONENT 
    if not virtual_vertex:
        V_new=[v for v in V if v not in box]
        if not V_new:
            #print('Unknotted!')
            return []
        #fix the gaps in V_new now
        #Now I will shift V_new so that the x-values do not have a gap
        V_new=shift_vertex_set(V_new)
        V_new=shift_vertex_set(V_new)
        return V_new
    
    else:
        new_vertex=[v for v in box if v not in V]
        if new_vertex: #If it is just a 
            new_vertex=new_vertex[0] #flattening
        else:     
            return []
        old_vertices=[v for v in box if v != new_vertex]
        V_new=[v for v in V if v not in old_vertices]
        V_new.append(new_vertex)
        #Now I will shift V_new so that the x-values do not have a gap
        first_elements = [t[0] for t in V_new]
        max_value = max(first_elements)

            # Identify gap
        gap = []
        for value in range(1, max_value + 1):
            if value not in first_elements:
                gap.append(value)

            #Fix the gaps
        if gap:
            modified_V_new = [
            (first_entry - 1, second_entry) if first_entry > gap[0] else (first_entry, second_entry)
                for first_entry, second_entry in V_new
            ]
            V_new=modified_V_new

            #Now we do the same thing for the missing y-value
        second_elements = [t[1] for t in V_new]
        min_value = min(second_elements)
        max_value = -1

            # Identify gap
        gap = []
        for value in range(min_value, max_value + 1):
            if value not in second_elements:
                gap.append(value)

            #Fix the gaps
        if gap:
            modified_V_new = [
                (first_entry, second_entry+1) if second_entry < gap[0] else (first_entry, second_entry)
            for first_entry, second_entry in V_new
            ]
            V_new=modified_V_new

        V_new.sort()
        temp=[]
        for v in V_new:
            temp.append(list(v))

        V_new=temp
        return V_new           
        
def perform_all_type_1_box_simplifications_updated(V):
    Vertex_Sets=[]
    Vertex_Sets.append(V)
    simplification_box=check_for_type_1_simplifications(V)
    while simplification_box: #there is a box that can simplify
        V_new=perform_destabilization(V,simplification_box)
        if V_new: #maybe V was a simple box, if so V_new=[] and the while loop breaks
            Vertex_Sets.append(V_new)
            #draw_rectangular_diagram(V_new)
            simplification_box=check_for_type_1_simplifications(V_new)
            V=V_new
        else:
            break
    #print('There are no type 1 v_1^b simplifications')         
    return Vertex_Sets[-1] 
        
############################### NOW TYPE 2 BOXES #####################################
    
###This function takes all type_2_virtual boxes and splits them into two type_1 virtual boxes.  We will perform the check on each type_1 box to decide if there is a simplification
def split_type_2_virtual_box(box):
    sub_box_1 = box[0:4]
    sub_box_2 = box[2:6]
    for vertex in box:
        for coord in vertex:
            if coord != int(coord):
                determining_vertex=vertex
                break  # Exit the inner loop once a non-integer is found   
            else:
                continue  # If the inner loop completes without finding a non-integer, skip to the next tuple
            break # Exit the outer loop once a tuple with a non-integer is found     
    # We need to determine if the subboxes are to be split along the horizontal or the vertical 
    if int(determining_vertex[0]) != determining_vertex[0]:
        half_val = determining_vertex[0]
        half_vertices = [v for v in box if v[0] == half_val]
        horiz, vert = sort_vertices_into_verticals_and_horizontals(sub_box_1)
        v_right=[v for v in vert if v[0]==max(v[0] for v in vert)]
        v_right=v_right[0]
        v_left=[v for v in vert if v[0]==min(v[0] for v in vert)]
        v_left=v_left[0]
        new_sub_box_1 = [v_left[0], v_left[1], [half_val, v_left[0][1]], [half_val, v_left[1][1]]]
        new_sub_box_2 = [v_right[0], v_right[1], [half_val, v_right[0][1]], [half_val, v_right[1][1]]]
    else:
        half_val = determining_vertex[1]
        half_vertices = [v for v in box if v[0] == half_val]
        horiz, vert = sort_vertices_into_verticals_and_horizontals(sub_box_1)
        h_top=[v for v in horiz if v[1]==max(v[1] for v in horiz)]
        h_top=h_top[0]
        h_bot=[v for v in horiz if v[1]==min(v[1] for v in horiz)]
        h_bot=h_bot[0]
        new_sub_box_1 = [h_top[0], h_top[1], [h_top[0][0], half_val], [h_top[1][0], half_val]]
        new_sub_box_2 = [h_bot[0], h_bot[1], [h_bot[0][0], half_val], [h_bot[1][0], half_val]]
            
    return [new_sub_box_1, new_sub_box_2]


## Note: You do not need to put into normal position for type 2 boxes because you can not do a where='horiz-vert-infty' simplification on a type 2 box
def check_type_2_box_for_simplification(box,V,where):
   #troubleshooting 6/16- Type 2 boxes need to be checked not including the boundary    
    splitbox1,splitbox2=split_type_2_virtual_box(box)
    if check_type_1_box_for_simplification(splitbox1,V,where) and check_type_1_box_for_simplification(splitbox2,V,where='std')==True:
        #print('There is',where,'v1^b type 2 simplification:')
        #draw_virtual_type2_boxes_diagram(splitbox1,splitbox2, V,where1=where,where2='std',color1='green')
        #draw the subboxes as type 1 guys with the correct 'where' but in green with different opacity
        return True
    if check_type_1_box_for_simplification(splitbox1,V,where='std') and check_type_1_box_for_simplification(splitbox2,V,where)==True:
        #print('There is',where,'v1^b type 2 simplification:')
        #draw_virtual_type2_boxes_diagram(splitbox1,splitbox2, V,where1='std',where2=where,color1='green')
        #draw the subboxes as type 1 guys with the correct 'where' but in green with different opacity
        return True
  
    return False

def check_type_2_box_for_simplification_not_verbose(box,V,where):   
    splitbox1,splitbox2=split_type_2_virtual_box(box)
    if check_type_1_box_for_simplification(splitbox1,V,where) and check_type_1_box_for_simplification(splitbox2,V,where='std')==True:
        #draw the subboxes as type 1 guys with the correct 'where' but in green with different opacity
        return True
    if check_type_1_box_for_simplification(splitbox1,V,where='std') and check_type_1_box_for_simplification(splitbox2,V,where)==True:
        return True
  
    return False


    
def perform_type_2_destabilization(V,box):
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
    #V_new has two gaps now so I will shift the vertex set twice so this is fixed
    V_new=shift_vertex_set(V_new)
    V_new=shift_vertex_set(V_new)
    V_new.sort()
    temp=[]
    for v in V_new:
        temp.append(list(v))

    V_new=temp
    return V_new
##########################################################
## Auxillary functions


def shift_vertex_set(V_new):
    #Now I will shift V_new so that the x-values do not have a gap
    first_elements = [t[0] for t in V_new]
    max_value = len(V_new)//2
    min_value=1

        # Identify gap
    gap = []
    for value in range(min_value, max_value + 1):
        if value not in first_elements:
            gap.append(value)

        #Fix the gaps
    if gap:
        modified_V_new = [
        (first_entry - 1, second_entry) if first_entry > gap[0] else (first_entry, second_entry)
            for first_entry, second_entry in V_new
        ]
        V_new=modified_V_new

        #Now we do the same thing for the missing y-value
    second_elements = [t[1] for t in V_new]
    min_value = min(second_elements)
    max_value = -1

        # Identify gap
    gap = []
    for value in range(min_value, max_value + 1):
        if value not in second_elements:
            gap.append(value)

        #Fix the gaps
    if gap:
        modified_V_new = [
            (first_entry, second_entry+1) if second_entry < gap[0] else (first_entry, second_entry)
        for first_entry, second_entry in V_new
        ]
        V_new=modified_V_new

    V_new.sort()
    """temp=[]
    for v in V_new:
        temp.append(list(v))
    tempp=[]
    if min(v[0] for v in temp)!=1: # This happens with a commutation all the way to the left of the diagram
        for v in temp:
            tempp.append([v[0]+1,v[1]])
    elif max(v[0] for v in temp)!=len(temp)//2: # This happens with a commutation all the way to the right of the diagram
        for v in temp:
            tempp.append([v[0]-1,v[1]]) 
    elif max(v[1] for v in temp)!=-1: # This happens with a commutation all the way to the top of the diagram
        for v in temp:
            tempp.append([v[0],v[1]-1])
    elif min(v[1] for v in temp)!=-len(temp)//2: # This happens with a commutation all the way to the bot of the diagram
        for v in temp:
            tempp.append([v[0],v[1]+1])
    else:
        tempp=temp
    
    V_new=tempp"""
    
    # Anchor leftmost x-value at 1
    min_x = min(v[0] for v in V_new)
    epsilon = min_x -1 
    
    # Anchor topmost y-value at -1
    max_y = max(v[1] for v in V_new)
    delta = max_y + 1

    V_new = [[x-epsilon, y - delta] for [x, y] in V_new]
    
    
    return V_new
    
def check_for_type_2_simplifications(V):
    _,type2=find_all_virtual_boxes(V)
    nonstdtype2=find_all_non_std_type_2_boxes(V)
    type2=type2+nonstdtype2
    where1= 'std'
    where2='horiz-infty'
    where3='vert-infty'
    for box in type2: 
        Bool=check_type_2_box_for_simplification(box,V,where1)
        if Bool==True:
            V_new=perform_type_2_destabilization(V,box)
            return V_new  
    #print('There are no standard type 2 v_1^b simplifications') 
    for box in type2: 
        Bool=check_type_2_box_for_simplification(box,V,where2)
        if Bool==True:
            V_new=perform_type_2_destabilization(V,box)
            return V_new  
    #print('There are no horizontal infty type 2 v_1^b simplifications') 
    
    for box in type2: 
        Bool=check_type_2_box_for_simplification(box,V,where3)
        if Bool==True:
            V_new=perform_type_2_destabilization(V,box)
            return V_new  
    #print('There are no vertical infty type 2 v_1^b simplifications') 
    #print('All type_2 virtual boxes are hooked or linked. Further testing is needed.')
    return []

def check_for_type_2_simplifications_not_verbose(V):
    _,type2=find_all_virtual_boxes(V)
    nonstdtype2=find_all_non_std_type_2_boxes(V)
    type2=type2+nonstdtype2
   #where1='std'
    #troubleshooting
    where1= 'std'
    where2='horiz-infty'
    where3='vert-infty'
    for box in type2: 
        Bool=check_type_2_box_for_simplification(box,V,where1)
        if Bool==True:
            V_new=perform_type_2_destabilization(V,box)
            return V_new  
    #print('There are no standard type 2 v_1^b simplifications') 
    for box in type2: 
        Bool=check_type_2_box_for_simplification(box,V,where2)
        if Bool==True:
            V_new=perform_type_2_destabilization(V,box)
            return V_new  
    #print('There are no horizontal infty type 2 v_1^b simplifications') 
    
    for box in type2: 
        Bool=check_type_2_box_for_simplification(box,V,where3)
        if Bool==True:
            V_new=perform_type_2_destabilization(V,box)
            return V_new  
    #print('There are no vertical infty type 2 v_1^b simplifications') 
    return []
        
###################################################    #6/18/2025 Something needs to be done here### 
def check_for_non_standard_type_2_simplifications(V,where):
    type2=find_all_non_std_type_2_boxes(V) #the point here is that these are type2 boxes that need to be checked through an infinity
    for box in type2:
        if int(box[-1][0])!= box[-1][0] and where=='vert-infty': #you split along a horizontal, you cannot check then horiz infty
            return False
        if int(box[-1][1])!= box[-1][1] and where=='horiz-infty': #you split along a vertical, you cannot check then vert infty
            return False
        if check_type_2_box_for_simplification(box,V,where)==True:
            #print('A',where,'type 2 box admits a simplification')
            #draw_virtual_box_diagram(box,V,where='std')
            return box  #it returns the type2 box
    #print('There are no',where,'type 2 simplifications. Further testing is needed.')        
    return [] #there is no type2 box with simplification    
    
    
    

def get_v1b_reduced_diagram(V):
# Step 1: Perform all type 1 simplifications

    Vertex_Sets=[] #after each simplification the new vertex set will be added here
    Vertex_Sets.append(V) #add the initial vertex set

    switch1=1 #intialize the while loop
    while switch1==1:
        switch1=0
        switch2=1
        box1 = check_for_type_1_simplifications(V)
        if box1==[]: #there were no type 1 simplifications
            box1 = 0 #this will break the first while loop
            box2 = 1 #look for type 2 then 
        if box1: #there was a type 1 simplifcation
            V_new=perform_destabilization(V, box1)
            #9/27/2026 Code verification
            #if not verify_unknot_boolean(V_new):
            #    print('this is the box',box1)
            #    print('This is the vertex set',V)
            #    return V
            switch1=1
            switch2=0
            if V_new==[]: #it was the last simplification of the unknot
                break
            Vertex_Sets.append(V_new)
            #if not verify_unknot_boolean(V_new):
            #    print('this is the box',box1)
            #    print('This is the vertex set',V)
            #    return V
            V=V_new #resets V for above
          
            
        # Step 2: Perform type 2 simplifications
        while switch2==1:
            switch2=0
            V_new=check_for_type_2_simplifications(V) #this is either a simplified vertex set or empty
            if V_new:
                Vertex_Sets.append(V_new)
                #if not verify_unknot_boolean(V_new):
                #    print('this is the box',box1)
                #    print('This is the vertex set',V)
                #    return V
                V=V_new
                switch1=1            
    #draw_rectangular_diagram(Vertex_Sets[-1])            
    return Vertex_Sets 


def get_v1b_reduced_diagram_not_verbose(V):
# Step 1: Perform all type 1 simplifications

    Vertex_Sets=[] #after each simplification the new vertex set will be added here
    Vertex_Sets.append(V) #add the initial vertex set

    switch1=1 #intialize the while loop
    while switch1==1:
        switch1=0
        switch2=1
        box1 = check_for_type_1_simplifications_not_verbose(V)
        if box1==[]: #there were no type 1 simplifications
            box1 = 0 #this will break the first while loop
            box2 = 1 #look for type 2 then 
        if box1: #there was a type 1 simplifcation
            V_new=perform_destabilization(V, box1)
            switch1=1
            switch2=0
            if V_new==[]: #it was the last simplification of the unknot
                break
            Vertex_Sets.append(V_new)
            V=V_new #resets V for above
            
        # Step 2: Perform type 2 simplifications
      
        while switch2==1:
            switch2=0
            V_new=check_for_type_2_simplifications(V) #this is either a simplified vertex set or empty
            if V_new:
                Vertex_Sets.append(V_new)
                V=V_new
                switch1=1                       
    return Vertex_Sets 

def verify_unknot_boolean(V):
    G = vertexset_to_XOGrid(V)
    braid = convert_to_braid(G, optimized='Y', verbose=False)
    try:
        B = Link(braid_closure=braid)
        B.simplify('global')
        if len(B.link_components)==1 and len(B.crossings)==0:
            return True
        elif len(B.link_components)==0:
            print('Could not verify')
            return True  
        else:
            print(B)
            return False
    except ValueError:
        print('Could not verify')
        return True    