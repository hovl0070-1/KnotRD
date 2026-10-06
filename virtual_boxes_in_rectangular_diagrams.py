
#### Begin Section 1: General Functions for Rectangular Diagrams######### 
###### This function puts the vertcial edges paired in paired in pairedx_V and the horizontal edges  in pairedy_V ####
def sort_vertices_into_verticals_and_horizontals(V):
    V.sort() #This sorts on x-values we will be sorting into tuples the pairs of vertices that share the same x-values 
    it = iter(V)
    pairedx_V=list(list(zip(it, it))) #this gives the vertices of each vertical edge
    pairedx_V.sort() #each vertical edge is a tuple below we change it to a list
    templist=[]
    for vert in pairedx_V:
        vert=list(vert)
        templist.append(vert)
    pairedx_V=templist    
    V = sorted(V, key= lambda elem : elem[1], reverse=True)
    it = iter(V)
    # zip the iterator with itself
    pairedy_V=list(list(zip(it, it))) #this gives the vertices of each horizontal edge
    pairedy_V.sort() 
    templist=[]
    for vert in pairedy_V:
        vert=list(vert)
        templist.append(vert)
    pairedy_V=templist  
    return[pairedy_V,pairedx_V]

### The function below finds vertices in a virtual box ########
def find_vertices_in_box(box,V,where):
    vertices_in_box=[]
    for v in V: 
        if check_if_vertex_in_box(v,box,where)==True:
            vertices_in_box.append(v)
    return vertices_in_box

### This does exactly what it says### 

def check_if_vertex_in_box(vertex,box,where):
    import math as m
   
        
    if where == 'std':
        min_x = min(v[0] for v in box)
        max_x = max(v[0] for v in box)
        min_y = min(v[1] for v in box)
        max_y = max(v[1] for v in box)
        
        if min_x <= vertex[0] <= max_x and min_y <= vertex[1] <= max_y:
            return True
        else:
            return False  
    #when doing type 2 boxes this is needed    
    elif where == 'std-no-boundary':
        min_x = min(v[0] for v in box)
        max_x = max(v[0] for v in box)
        min_y = min(v[1] for v in box)
        max_y = max(v[1] for v in box)
        
        if min_x < vertex[0] < max_x and min_y < vertex[1] < max_y:
            return True
        else:
            return False  
        

    elif where=='horiz-infty':
        min_x=min(v[0] for v in box)
        max_x=max(v[0] for v in box)
        min_y=min(v[1] for v in box)
        max_y=max(v[1] for v in box)
       
        if (min_x >= vertex[0] or vertex[0] >= max_x) and min_y <= vertex[1] <= max_y:
            return True
        else:
            return False 
     #when doing type 2 boxes this is needed      
    elif where=='horiz-infty-no-boundary':
        min_x=min(v[0] for v in box)
        max_x=max(v[0] for v in box)
        min_y=min(v[1] for v in box)
        max_y=max(v[1] for v in box)
        #IS IT LEQ OR JUST LT???
        if (min_x > vertex[0] or vertex[0] > max_x) and min_y < vertex[1] < max_y:
            return True
        else:
            return False 
        

    elif where=='vert-infty':
        min_x=min(v[0] for v in box)
        max_x=max(v[0] for v in box)
        min_y=min(v[1] for v in box)
        max_y=max(v[1] for v in box)
        
        if min_x <= vertex[0] <= max_x  and (max_y <= vertex[1] or vertex[1] <= min_y):
            return True
        else:
            return False 
        
    elif where=='vert-infty-no-boundary':
        min_x=min(v[0] for v in box)
        max_x=max(v[0] for v in box)
        min_y=min(v[1] for v in box)
        max_y=max(v[1] for v in box)
        
        if min_x < vertex[0] < max_x  and (max_y < vertex[1] or vertex[1] < min_y):
            return True
        else:
            return False     
            
    
    elif where=='horiz-vert-infty':
        min_x=min(v[0] for v in box)
        max_x=max(v[0] for v in box)
        min_y=min(v[1] for v in box)
        max_y=max(v[1] for v in box)
        
        
        if (min_x >= vertex[0] or vertex[0] >= max_x) and (max_y <= vertex[1] or vertex[1] <= min_y):
            return True
        else:
            return False
        
    elif where=='horiz-vert-infty-no-boundary':
        min_x=min(v[0] for v in box)
        max_x=max(v[0] for v in box)
        min_y=min(v[1] for v in box)
        max_y=max(v[1] for v in box)
        
        
        if (min_x > vertex[0] or vertex[0] > max_x) and (max_y < vertex[1] or vertex[1] < min_y):
            return True
        else:
            return False    



    else: raise TypeError("where input not recognized")
    
    
def find_all_virtual_boxes(V):
    
    [horizontals,verticals]=sort_vertices_into_verticals_and_horizontals(V) 
    type1_virtual_boxes=[];
    
    for pair in verticals: #for a vertical edge in the rectangular diagram
        first_yval=pair[0][1] #this is the first y-value of the vertical edge
        second_yval=pair[1][1] #this is the second y-value of the vertical edge
        point_with_first_yval = [i for i in V if i[1] == first_yval and i[0] !=pair[0][0]]  #find the other vertex with shared 1st y-value 
        point_with_second_yval = [i for i in V if i[1] == second_yval and i[0] !=pair[0][0]] #find the other vertex with shared 2nd y-value 
        point_with_first_yval=point_with_first_yval[0] #this is flattening
        point_with_second_yval=point_with_second_yval[0] #this is flattening

        first_added_point=[point_with_first_yval[0],second_yval] #these are the points that will be added to the virtual type 1 box
        second_added_point=[point_with_second_yval[0],first_yval]
        
        first_box=pair+[point_with_first_yval]+[first_added_point] 
        second_box=pair+[point_with_second_yval]+[second_added_point]
        
        type1_virtual_boxes.append(first_box)
        type1_virtual_boxes.append(second_box)
        
#Note: there is some ambiguity here.  Each virtual box is just a triple of vertices, so for a simplification it will need to be checked two ways. 1) standard 2) through infinity
    
    #These boxes will correspond to our general type 2 virtual boxes
    type2_virtual_boxes=[]
    
    for pair in horizontals: #along a horizontal   
        first_xval=pair[0][0] #this is the first x-value of the horizontal edge
        second_xval=pair[1][0] #this is the second x-value of the horizontal edge
        
        point_with_first_xval = [i for i in V if i[0] == first_xval and i[1] !=pair[1][1]] #find the other vertex with the same 1st x-value
        point_with_second_xval = [i for i in V if i[0] == second_xval and i[1] !=pair[0][1]] #find the vertex with the same 2nd x-value
        point_with_first_xval=point_with_first_xval[0] #this is just flattening
        point_with_second_xval=point_with_second_xval[0] #this is just flattening
        range_of_x_vals=list(range(first_xval,second_xval))
        #range_of_x_vals=list(range(pair[0][0]+1,pair[1][0])) NOTE: CHANGED 6/1/2025 #The y-values between the 1st y-val of the vert and the 2nd y-val of the vert
        for x in range_of_x_vals: #these are the places where our type 2 box may be ''cut''
            new_vertex_1=[x+0.5,point_with_first_xval[1]]
            new_vertex_2=[x+0.5,point_with_second_xval[1]] 
            
            box=pair+[point_with_first_xval]+[point_with_second_xval]+[new_vertex_1]+[new_vertex_2]
            type2_virtual_boxes.append(box)
            
    for pair in verticals:   
        first_yval=pair[0][1] #this is the first y-value of the vertical edge
        second_yval=pair[1][1] #this is the second y-value of the vertical edge
        
        point_with_first_yval = [i for i in V if i[1] == first_yval and i[0] !=pair[0][0]] #find the other vertex with the same 1st y-value
        point_with_second_yval = [i for i in V if i[1] == second_yval and i[0] !=pair[0][0]] #find the vertex with the same 2nd y-value
        
        point_with_first_yval=point_with_first_yval[0] #this is just flattening
        point_with_second_yval=point_with_second_yval[0] #this is just flattening
        #TROUBLESHOOTING
        #range_of_y_vals=list(range(pair[0][1]+1,pair[1][1])) #The y-values between the 1st y-val of the vert and the 2nd y-val of the vert
        #range_of_y_vals=list(range(pair[0][1]+1,pair[1][1]))
        range_of_y_vals=list(range(pair[0][1],pair[1][1]))
        for y in range_of_y_vals: #these are the places where our type 2 box may be ''cut''
            new_vertex_1=[point_with_first_yval[0],y-0.5]
            new_vertex_2=[point_with_second_yval[0],y-0.5] 
            
            box=pair+[point_with_first_yval]+[point_with_second_yval]+[new_vertex_1]+[new_vertex_2]
            type2_virtual_boxes.append(box)
            
    #non_std_type2=find_all_non_std_type_2_boxes(V) #this fixes an issue with type 2 boxes with edges flipped out to infty
    #type2_virtual_boxes=type2_virtual_boxes+non_std_type2
    
    return [type1_virtual_boxes,type2_virtual_boxes]

def find_all_non_std_type_2_boxes(V):
    
    #These boxes will correspond to our non-std type 2 virtual boxes
    type2_virtual_boxes=[]
    [horizontals,verticals]=sort_vertices_into_verticals_and_horizontals(V)
    for pair in horizontals: #along a horizontal   
        number_of_edges=len(V)//2
        number_of_edges=list(range(0,number_of_edges+1))
        first_xval=pair[0][0] #this is the first x-value of the horizontal edge
        second_xval=pair[1][0] #this is the second x-value of the horizontal edge
        
        x_start,x_end=sorted([pair[0][0],pair[1][0]])
        max_x = len(V) // 2
        all_half_x_vals = [x + 0.5 for x in range(0, max_x+1)]  # Gives: 0.5, 1.5, ..., max_x + 0.5

        # Exclude the values that lie strictly between x_start and x_end
        range_of_x_vals = [x for x in all_half_x_vals if not (x_start < x < x_end)]
        
        point_with_first_xval = [i for i in V if i[0] == first_xval and i[1] !=pair[1][1]] #find the other vertex with the same 1st x-value
        point_with_second_xval = [i for i in V if i[0] == second_xval and i[1] !=pair[0][1]] #find the vertex with the same 2nd x-value
        
        point_with_first_xval=point_with_first_xval[0] #this is just flattening
        point_with_second_xval=point_with_second_xval[0] #this is just flattening

        for x in range_of_x_vals: #these are the places where our type 2 box may be ''cut''
            new_vertex_1=[x,point_with_first_xval[1]]
            new_vertex_2=[x,point_with_second_xval[1]] 
            
            box=pair+[point_with_first_xval]+[point_with_second_xval]+[new_vertex_1]+[new_vertex_2]
            type2_virtual_boxes.append(box)
            
    for pair in verticals:   
        first_yval=pair[0][1] #this is the first y-value of the vertical edge
        second_yval=pair[1][1] #this is the second y-value of the vertical edge
        y_start,y_end=sorted([pair[0][1],pair[1][1]])
        min_y = -len(V) // 2
        all_half_y_vals = [y + 0.5 for y in range(min_y-1, 0)]  # Gives:  min_y - 0.5, ... ,-0.5

        # Exclude the values that lie strictly between x_start and x_end
        range_of_y_vals = [y for y in all_half_y_vals if not (y_start < y < y_end)]
        
        
        
        point_with_first_yval = [i for i in V if i[1] == first_yval and i[0] !=pair[0][0]] #find the other vertex with the same 1st y-value
        point_with_second_yval = [i for i in V if i[1] == second_yval and i[0] !=pair[0][0]] #find the vertex with the same 2nd y-value
        
        point_with_first_yval=point_with_first_yval[0] #this is just flattening
        point_with_second_yval=point_with_second_yval[0] #this is just flattening
        
        
        for y in range_of_y_vals: #these are the places where our type 2 box may be ''cut''
            new_vertex_1=[point_with_first_yval[0],y]
            new_vertex_2=[point_with_second_yval[0],y] 
            
            box=pair+[point_with_first_yval]+[point_with_second_yval]+[new_vertex_1]+[new_vertex_2]
            type2_virtual_boxes.append(box)
            
    return type2_virtual_boxes
        