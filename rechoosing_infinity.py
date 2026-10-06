## This file contains the helper functions for rechoosing the points at infinity on a rectangular diagram###

from virtual_boxes_in_rectangular_diagrams import * 
from drawing_rectangular_diagrams_src import *


#This is another long function that returns which subcase box is in after it has been moved to a corner.  This will help us determine where the exit disk lives.
#from determine_cases_of_sorted_diagrams import *
import copy
from itertools import combinations

## This function generates and returns the 4 corner positions of a virtual box. 
def generate_corner_diagrams(V,box):
        n=len(V)//2
        virtual_vertex=[v for v in box if v not in V]
        virtual_vertex=virtual_vertex[0]
        real_corner_vertex=[v for v in box if v[0]!=virtual_vertex[0] and v[1]!=virtual_vertex[1]]
        real_corner_vertex=real_corner_vertex[0]
        
        #the corner is top left of box
        if real_corner_vertex[0]<virtual_vertex[0] and real_corner_vertex[1]>virtual_vertex[1]:
            choice_of_infty=[real_corner_vertex[0],-real_corner_vertex[1]] #this tuple tells you how many cyclic perms are needed to put the real vertex in top left of RD
            
            #the new vertex set will place the real_corner_vertex at the vertex [1,-1] on the RD.
            NW=perform_cyclic_permutations(V,choice_of_infty[0]-1,choice_of_infty[1]-1,which_vertical='left-to-right',which_horizontal='top-to-bottom')
             #the vertex set below places the real_corner_vertex at the [n,-1] on the RD.
            #print('Trying for NE corner')
            #NE=perform_cyclic_permutations(V,n-1,0,which_vertical='right-to-left',which_horizontal='top-to-bottom')
            NE=perform_cyclic_permutations(NW,n-1,0,which_vertical='right-to-left',which_horizontal='top-to-bottom')
            #the vertex set below places the real_corner_vertex at the [1,-n] on the RD.
            SW=perform_cyclic_permutations(NW,0,n-1,which_vertical='left-to-right',which_horizontal='bottom-to-top')
            
            #the vertex set below places the real_corner_vertex at the [n,-n] on the RD.
            SE=perform_cyclic_permutations(NW,n-1,n-1,which_vertical='right-to-left',which_horizontal='bottom-to-top')
            
            return[NW, NE, SW, SE]


        elif real_corner_vertex[0]>virtual_vertex[0] and real_corner_vertex[1]>virtual_vertex[1]: #the corner is top right of box
            choice_of_infty=[n-real_corner_vertex[0],-real_corner_vertex[1]] #this tuple tells you how many cyclic perms are needed to put the real vertex in top left of RD
            #the new vertex set will place the real_corner_vertex at the vertex [n,-1] on the RD.
            NE=perform_cyclic_permutations(V,choice_of_infty[0],choice_of_infty[1]-1,which_vertical='right-to-left',which_horizontal='top-to-bottom')
             #the vertex set below places the real_corner_vertex at the [1,-1] on the RD.
            NW=perform_cyclic_permutations(NE,n-1,0,which_vertical='left-to-right',which_horizontal='top-to-bottom')
            #the vertex set below places the real_corner_vertex at the [n,-n] on the RD.
            SE=perform_cyclic_permutations(NE,0,n-1,which_vertical='left-to-right',which_horizontal='bottom-to-top')
            #the vertex set below places the real_corner_vertex at the [1,-n] on the RD.
            SW=perform_cyclic_permutations(NE,n-1,n-1,which_vertical='left-to-right',which_horizontal='bottom-to-top')
        
            return[NW, NE, SW, SE]
           

        elif real_corner_vertex[0]<virtual_vertex[0] and real_corner_vertex[1]<virtual_vertex[1]: #the corner is bottom left of box

            choice_of_infty=[real_corner_vertex[0],-real_corner_vertex[1]] #this tuple tells you how many cyclic perms are needed to put the real vertex in top left of RD
            
            #the new vertex set will place the real_corner_vertex at the vertex [1,-n] on the RD.
            SW=perform_cyclic_permutations(V,choice_of_infty[0]-1,n-choice_of_infty[1],which_vertical='left-to-right',which_horizontal='bottom-to-top') 
            #the vertex set below places the real_corner_vertex at the [n,-n] on the RD.
            SE=perform_cyclic_permutations(SW,n-1,0,which_vertical='right-to-left',which_horizontal='top-to-bottom')
            #the vertex set below places the real_corner_vertex at the [1,-1] on the RD.
            
            NW=perform_cyclic_permutations(SW,0,n-1,which_vertical='left-to-right',which_horizontal='top-to-bottom')
           
            #the vertex set below places the real_corner_vertex at the [n,-1] on the RD.
            NE=perform_cyclic_permutations(SW,n-1,n-1,which_vertical='right-to-left',which_horizontal='top-to-bottom')
            
            
            return[NW, NE, SW, SE]
            

        elif real_corner_vertex[0]>virtual_vertex[0] and real_corner_vertex[1]<virtual_vertex[1]: #the corner is bottom right of box
            choice_of_infty=[n-real_corner_vertex[0],-real_corner_vertex[1]] #this tuple tells you how many cyclic perms are needed to put the real vertex in top left of RD
            #the new vertex set will place the real_corner_vertex at the vertex [n,-n] on the RD.
            SE=perform_cyclic_permutations(V,choice_of_infty[0],n-choice_of_infty[1],which_vertical='right-to-left',which_horizontal='bottom-to-top')   
            
            #the vertex set below places the real_corner_vertex at the [n,-n] on the RD.
            SW=perform_cyclic_permutations(SE,n-1,0,which_vertical='left-to-right',which_horizontal='top-to-bottom')
            #the vertex set below places the real_corner_vertex at the [n,-1] on the RD.
            NE=perform_cyclic_permutations(SE,0,n-1,which_vertical='left-to-right',which_horizontal='top-to-bottom')
            #the vertex set below places the real_corner_vertex at the [1,-1] on the RD.
            NW=perform_cyclic_permutations(SE,n-1,n-1,which_vertical='left-to-right',which_horizontal='top-to-bottom')
            
            return[NW, NE, SW, SE]

#######################################################

def find_boxes_from_corner_positions(V_in_corner_position,V_type):
    if V_type=='NW':
        #now isolate the box
        [horizontals,verticals]=sort_vertices_into_verticals_and_horizontals(V_in_corner_position)
        horizontals.sort(key=lambda l: l[0][1],reverse=True)
        box1=[v for v in V_in_corner_position if v in horizontals[0] or v in verticals[0]]
        x = [p[0] for p in box1]
        y = [p[1] for p in box1]
        mx = [i for i in x if x.count(i) == 1][0]
        my = [i for i in y if y.count(i) == 1][0]
        newvert=[mx, my]
        box1.append(newvert)
        box1.sort(key=lambda l: l[0],reverse=True) #required for drawing.... sorry
        return box1
    
    elif V_type=='NE':
        [horizontals,verticals]=sort_vertices_into_verticals_and_horizontals(V_in_corner_position)
        horizontals.sort(key=lambda l: l[0][1],reverse=True)
        box1=[v for v in V_in_corner_position if v in horizontals[0] or v in verticals[-1]]
        x = [p[0] for p in box1]
        y = [p[1] for p in box1]
        mx = [i for i in x if x.count(i) == 1][0]
        my = [i for i in y if y.count(i) == 1][0]
        newvert=[mx, my]
        box1.append(newvert)
        box1.sort(key=lambda l: l[0],reverse=True) #required for drawing.... sorry
        return box1
    
    elif V_type=='SW':
        #now isolate the box
        [horizontals,verticals]=sort_vertices_into_verticals_and_horizontals(V_in_corner_position)
        horizontals.sort(key=lambda l: l[0][1],reverse=True)
        box1=[v for v in V_in_corner_position if v in horizontals[-1] or v in verticals[0]]
        x = [p[0] for p in box1]
        y = [p[1] for p in box1]
        mx = [i for i in x if x.count(i) == 1][0]
        my = [i for i in y if y.count(i) == 1][0]
        newvert=[mx, my]
        box1.append(newvert)
        box1.sort(key=lambda l: l[0],reverse=True) #required for drawing.... sorry
        return box1
        
    elif V_type=='SE':    
        #now isolate the box
        [horizontals,verticals]=sort_vertices_into_verticals_and_horizontals(V_in_corner_position)
        horizontals.sort(key=lambda l: l[0][1],reverse=True)
        box1=[v for v in V_in_corner_position if v in horizontals[-1] or v in verticals[-1]]
        x = [p[0] for p in box1]
        y = [p[1] for p in box1]
        mx = [i for i in x if x.count(i) == 1][0]
        my = [i for i in y if y.count(i) == 1][0]
        newvert=[mx, my]
        box1.append(newvert)
        box1.sort(key=lambda l: l[0],reverse=True) #required for drawing.... sorry
        return box1

## Helper function for fixing the vertex set after a cyclic perm
def shift_vertex_set_cyclic_perm(V_new):
    #Now I will shift V_new so that the x-values do not have a gap
    first_elements = [t[0] for t in V_new]
    max_value = max(max(first_elements),len(V_new)//2)
    min_value=min(min(first_elements),1)

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
    temp=[]
    for v in V_new:
        temp.append(list(v))
    tempp=[]
    if min(v[0] for v in temp)==0: # This happens with a commutation all the way to the left of the diagram
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
    
    V_new=tempp
    return V_new

def vertical_cyclic_permutation_1(V,which):
    # This will move the left vertical edge to the right side of the diagram
    if which=='left-to-right':
        V.sort()
        rightmost_vertical=V[-1][0]
        top_left=V[0]
        bot_left=V[1]
        V_new=[v for v in V if v!= top_left and v!= bot_left]
        new_vertices=[[rightmost_vertical+1,top_left[1]],[rightmost_vertical+1,bot_left[1]]]
        V_new=V_new+new_vertices
        V_new=shift_vertex_set_cyclic_perm(V_new)
        return V_new
    elif which=='right-to-left':
        V.sort()
        leftmost_vertical=V[0][0]
        top_right=V[-1]
        bot_right=V[-2]
        V_new=[v for v in V if v!= top_right and v!= bot_right]
        new_vertices=[[leftmost_vertical-1,top_right[1]],[leftmost_vertical-1,bot_right[1]]]
        V_new=V_new+new_vertices
        V_new=shift_vertex_set_cyclic_perm(V_new)
        return V_new 


def horizontal_cyclic_permutation_1(V,which):
    if which=='top-to-bottom':
        V.sort(key=lambda x: x[1])
        bottom_horizontal=V[0][1]
        top_right=V[-1][0]
        top_left=V[-2][0]
        V_new=V[:-2]
        new_vertices=[[top_left,bottom_horizontal-1],[top_right,bottom_horizontal-1]]
        V_new=V_new+new_vertices
        V_new=shift_vertex_set_cyclic_perm(V_new)
        return V_new
    elif which=='bottom-to-top':
        V.sort(key=lambda x: x[1])
        top_horizontal=V[-1][1]
        bot_right=V[0][0]
        bot_left=V[1][0]
        V_new=V[2:]
        new_vertices=[[bot_left,top_horizontal+1],[bot_right,top_horizontal+1]]
        V_new=V_new+new_vertices
        V_new=shift_vertex_set_cyclic_perm(V_new)
        return V_new

def perform_cyclic_permutations(V,number_of_vertical,number_of_horizontal,which_vertical,which_horizontal):
    for i in range(number_of_vertical):
        V=vertical_cyclic_permutation_1(V,which=which_vertical) 
    for j in range(number_of_horizontal): 
        V=horizontal_cyclic_permutation_1(V,which=which_horizontal) 
    return V    



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
            print('perform_horizontal_commutation error the file is rechoosing infinity')
            print('this x value is not seen',x)
            raise TypeError('Theres an x gap')
    for y in range(-n,0):
        if y not in ys:
            print('this y value is not seen',y)
            raise TypeError('Theres an y gap')        
    return V_new

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
    
    # 9/15/26 There has been some trouble with hinge T's leaving gaps I am troubleshooting
    n=len(V_new)//2
    xs=[v[0] for v in V_new]
    ys=[v[1] for v in V_new]
    for x in range(1,n+1):
        if x not in xs:
            print('perform_vertical_commutation error the file is rechoosing infinity')
            print('this x value is not seen',x)
            raise TypeError('Theres an x gap')
    for y in range(-n,0):
        if y not in ys:
            print('this y value is not seen',y)
            raise TypeError('Theres an y gap')        
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


##########################################################
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
    temp=[]
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
    
    V_new=temp
    return V_new        

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