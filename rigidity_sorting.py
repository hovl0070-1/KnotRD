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

#########################################################################################
        
def verticals_rigid(V,where):
    horizontals,verticals=sort_vertices_into_verticals_and_horizontals(V)
    sawtooth=0
    if where=='W':
        while sawtooth==0:
            for i in range(len(verticals)-1):
                if (verticals[i][0][1]<verticals[i+1][0][1] and verticals[i][1][1]>verticals[i+1][1][1]): #interleaved and smaller to right 
                    temp=verticals[i]
                    verticals[i]=[[verticals[i][0][0],verticals[i+1][0][1]],[verticals[i][1][0],verticals[i+1][1][1]]]
                    verticals[i+1]=[[verticals[i+1][0][0],temp[0][1]],[verticals[i+1][1][0],temp[1][1]]]
                    sawtooth=0
                    break
                else:
                    sawtooth=1
    elif where=='E':
        while sawtooth==0:
            for i in range(len(verticals)-1):
                if verticals[i][0][1]>verticals[i+1][0][1] and verticals[i][1][1]<verticals[i+1][1][1]:#interleaved and smaller to left 
                    temp=verticals[i]
                    verticals[i]=[[verticals[i][0][0],verticals[i+1][0][1]],[verticals[i][1][0],verticals[i+1][1][1]]]
                    verticals[i+1]=[[verticals[i+1][0][0],temp[0][1]],[verticals[i+1][1][0],temp[1][1]]]
                    sawtooth=0
                    break
                else:
                    sawtooth=1
    else: raise TypeError("where input not recognized")           
        
    newvertexset=[]
    for v in verticals:
        for i in range(len(v)):
            newvertexset.append(v[i]) 
    return newvertexset 


def horizontals_rigid(V,where):
    horizontals,verticals=sort_vertices_into_verticals_and_horizontals(V)
    horizontals.sort(key=lambda x:x[0][1])
    sawtooth=0
    if where=='N':
        while sawtooth==0:
            for i in range(len(horizontals)-1):
                if (horizontals[i+1][0][0]>horizontals[i][0][0] and horizontals[i+1][1][0]<horizontals[i][1][0]):
                    temp=horizontals[i]
                    horizontals[i]=[[horizontals[i+1][0][0],horizontals[i][0][1]],[horizontals[i+1][1][0],horizontals[i][1][1]]]
                    horizontals[i+1]=[[temp[0][0],horizontals[i+1][0][1]],[temp[1][0],horizontals[i+1][1][1]]]
                    sawtooth=0
                    break
                else:
                    sawtooth=1  
    elif where=='S':
        for i in range(len(horizontals)-1):
            if (horizontals[i+1][0][0]<horizontals[i][0][0] and horizontals[i+1][1][0]>horizontals[i][1][0]):
                temp=horizontals[i]
                horizontals[i]=[[horizontals[i+1][0][0],horizontals[i][0][1]],[horizontals[i+1][1][0],horizontals[i][1][1]]]
                horizontals[i+1]=[[temp[0][0],horizontals[i+1][0][1]],[temp[1][0],horizontals[i+1][1][1]]]
                sawtooth=0
                break
            else:
                sawtooth=1  
    else: raise TypeError("where input not recognized")           
        
    newvertexset=[]
    for h in horizontals:
        for i in range(len(h)):
            newvertexset.append(h[i])
    return newvertexset        

def top_left_rigid(V):
    horizontals,verticals=sort_vertices_into_verticals_and_horizontals(V)
    horizontals.sort(key=lambda x:x[0][1],reverse=True) #sorts from -1 to -n
    rigid=0
    while rigid==0:
        for i in range(1,len(horizontals)-1):
            h1=horizontals[i]
            h2=horizontals[i+1]
            widthh1=list(range(h1[0][0],h1[1][0]+1))
            widthh2=list(range(h2[0][0],h2[1][0]+1))
            leftmosthorizontal = h1 if h1[0][0] < h2[0][0] else h2
            rightmosthorizontal= h2 if leftmosthorizontal==h1 else h1
            intersectionh1h2 = list(set(widthh1) & set(widthh2))
            
            if (horizontals[i+1][0][0]>horizontals[i][0][0] and horizontals[i+1][1][0]<horizontals[i][1][0]): #interleaved and smaller below
                #swap
                temp=horizontals[i]
                horizontals[i]=[[horizontals[i+1][0][0],horizontals[i][0][1]],[horizontals[i+1][1][0],horizontals[i][1][1]]]
                horizontals[i+1]=[[temp[0][0],horizontals[i+1][0][1]],[temp[1][0],horizontals[i+1][1][1]]]
                rigid=0
                break
                
            elif intersectionh1h2==[] and h2==leftmosthorizontal: #disjoint and leftmost horizontal is below the other 
                temp=horizontals[i]
                horizontals[i]=[[horizontals[i+1][0][0],horizontals[i][0][1]],[horizontals[i+1][1][0],horizontals[i][1][1]]]
                horizontals[i+1]=[[temp[0][0],horizontals[i+1][0][1]],[temp[1][0],horizontals[i+1][1][1]]]
                rigid=0
                break
                    
           
            else:
                rigid=1  
    #Now push the verticals correctly. top left
    sawtooth=0
    while sawtooth==0:
        for i in range(len(verticals)-1):
            v1=verticals[i]
            topofv1 = v1[0][1] if v1[0][1] > v1[1][1] else v1[1][1]
            botofv1=v1[0][1] if v1[1][1]==topofv1 else v1[1][1]
            
            v2=verticals[i+1]
            topofv2 = v2[0][1] if v2[0][1] > v2[1][1] else v2[1][1]
            botofv2=v2[0][1] if v2[1][1]==topofv2 else v2[1][1]
            
            
            if topofv1>topofv2 and botofv1<botofv2: #interleaved and smaller to right
            #if verticals[i][0][1]<verticals[i+1][0][1] and verticals[i][1][1]>verticals[i+1][1][1]:#interleaved and smaller to right
                #exchange
                temp=verticals[i]
                verticals[i]=[[verticals[i][0][0],verticals[i+1][0][1]],[verticals[i][1][0],verticals[i+1][1][1]]]
                verticals[i+1]=[[verticals[i+1][0][0],temp[0][1]],[verticals[i+1][1][0],temp[1][1]]]
                sawtooth=0
                break
            elif botofv2>topofv1: #disjoint with top vertical to the right
            #elif verticals[i][1][1]>verticals[i+1][0][1]: #disjoint with top vertical to the right
                temp=verticals[i]
                verticals[i]=[[verticals[i][0][0],verticals[i+1][0][1]],[verticals[i][1][0],verticals[i+1][1][1]]]
                verticals[i+1]=[[verticals[i+1][0][0],temp[0][1]],[verticals[i+1][1][0],temp[1][1]]]
                sawtooth=0
                break

            else:
                sawtooth=1
    
        
    newvertexset=[]
    for h in horizontals:
        for i in range(len(h)):
            newvertexset.append(h[i])
    return newvertexset  

def top_right_rigid(V):
    horizontals,verticals=sort_vertices_into_verticals_and_horizontals(V)
    horizontals.sort(key=lambda x:x[0][1],reverse=True) #sorts from -1 to -n
    rigid=0
    while rigid==0:
        for i in range(1,len(horizontals)-1):
            h1=horizontals[i]
            h2=horizontals[i+1]
            widthh1=list(range(h1[0][0],h1[1][0]+1))
            widthh2=list(range(h2[0][0],h2[1][0]+1))
            leftmosthorizontal = h1 if h1[0][0] < h2[0][0] else h2
            rightmosthorizontal= h2 if leftmosthorizontal==h1 else h1
            intersectionh1h2 = list(set(widthh1) & set(widthh2))
            
            if (horizontals[i+1][0][0]>horizontals[i][0][0] and horizontals[i+1][1][0]<horizontals[i][1][0]): #interleaved and smaller below
                #swap
                temp=horizontals[i]
                horizontals[i]=[[horizontals[i+1][0][0],horizontals[i][0][1]],[horizontals[i+1][1][0],horizontals[i][1][1]]]
                horizontals[i+1]=[[temp[0][0],horizontals[i+1][0][1]],[temp[1][0],horizontals[i+1][1][1]]]
                rigid=0
                break
                
            elif intersectionh1h2==[] and h2==rightmosthorizontal: #disjoint and rightmost horizontal is below the other 
                temp=horizontals[i]
                horizontals[i]=[[horizontals[i+1][0][0],horizontals[i][0][1]],[horizontals[i+1][1][0],horizontals[i][1][1]]]
                horizontals[i+1]=[[temp[0][0],horizontals[i+1][0][1]],[temp[1][0],horizontals[i+1][1][1]]]
                rigid=0
                break
                    
           
            else:
                rigid=1  
                
    #Now push the verticals correctly   top right

    sawtooth=0
    while sawtooth==0:
        for i in range(len(verticals)-1):
            v1=verticals[i]
            topofv1 = v1[0][1] if v1[0][1] > v1[1][1] else v1[1][1]
            botofv1=v1[0][1] if v1[1][1]==topofv1 else v1[1][1]
            
            v2=verticals[i+1]
            topofv2 = v2[0][1] if v2[0][1] > v2[1][1] else v2[1][1]
            botofv2=v2[0][1] if v2[1][1]==topofv2 else v2[1][1]
            
            
            if topofv1<topofv2 and botofv1>botofv2: #interleaved and smaller to left
            #if verticals[i][0][1]<verticals[i+1][0][1] and verticals[i][1][1]>verticals[i+1][1][1]:#interleaved and smaller to right
                #exchange
                temp=verticals[i]
                verticals[i]=[[verticals[i][0][0],verticals[i+1][0][1]],[verticals[i][1][0],verticals[i+1][1][1]]]
                verticals[i+1]=[[verticals[i+1][0][0],temp[0][1]],[verticals[i+1][1][0],temp[1][1]]]
                sawtooth=0
                break
            elif botofv1>topofv2: #disjoint with top vertical to the left
            #elif verticals[i][1][1]>verticals[i+1][0][1]: #disjoint with top vertical to the right
                temp=verticals[i]
                verticals[i]=[[verticals[i][0][0],verticals[i+1][0][1]],[verticals[i][1][0],verticals[i+1][1][1]]]
                verticals[i+1]=[[verticals[i+1][0][0],temp[0][1]],[verticals[i+1][1][0],temp[1][1]]]
                sawtooth=0
                break

           
            else:
                sawtooth=1
                    
    newvertexset=[]
    for h in horizontals:
        for i in range(len(h)):
            newvertexset.append(h[i])
    return newvertexset  

def bottom_left_rigid(V):
    horizontals,verticals=sort_vertices_into_verticals_and_horizontals(V)
    horizontals.sort(key=lambda x:x[0][1],reverse=True) #sorts from -1 to -n
    rigid=0
    while rigid==0:
        for i in range(len(horizontals)-2):
            h1=horizontals[i]
            h2=horizontals[i+1]
            widthh1=list(range(h1[0][0],h1[1][0]+1))
            widthh2=list(range(h2[0][0],h2[1][0]+1))
            leftmosthorizontal = h1 if h1[0][0] < h2[0][0] else h2
            rightmosthorizontal= h2 if leftmosthorizontal==h1 else h1
            intersectionh1h2 = list(set(widthh1) & set(widthh2))
            
            if (horizontals[i+1][0][0]<horizontals[i][0][0] and horizontals[i+1][1][0]>horizontals[i][1][0]): #interleaved and smaller above
                #swap
                temp=horizontals[i]
                horizontals[i]=[[horizontals[i+1][0][0],horizontals[i][0][1]],[horizontals[i+1][1][0],horizontals[i][1][1]]]
                horizontals[i+1]=[[temp[0][0],horizontals[i+1][0][1]],[temp[1][0],horizontals[i+1][1][1]]]
                rigid=0
                break
                
            elif intersectionh1h2==[] and h1==leftmosthorizontal: #disjoint and leftmost horizontal is below the other 
                temp=horizontals[i]
                horizontals[i]=[[horizontals[i+1][0][0],horizontals[i][0][1]],[horizontals[i+1][1][0],horizontals[i][1][1]]]
                horizontals[i+1]=[[temp[0][0],horizontals[i+1][0][1]],[temp[1][0],horizontals[i+1][1][1]]]
                rigid=0
                break
                    
           
            else:
                rigid=1  
                
                
    #Now push the verticals correctly. bottom left 
    sawtooth=0
    while sawtooth==0:
        for i in range(len(verticals)-1):
            v1=verticals[i]
            topofv1 = v1[0][1] if v1[0][1] > v1[1][1] else v1[1][1]
            botofv1=v1[0][1] if v1[1][1]==topofv1 else v1[1][1]
            
            v2=verticals[i+1]
            topofv2 = v2[0][1] if v2[0][1] > v2[1][1] else v2[1][1]
            botofv2=v2[0][1] if v2[1][1]==topofv2 else v2[1][1]
            
            
            if topofv2<topofv1 and botofv2>botofv1: #interleaved and smaller to right
            #if verticals[i][0][1]<verticals[i+1][0][1] and verticals[i][1][1]>verticals[i+1][1][1]:#interleaved and smaller to right
                #exchange
                temp=verticals[i]
                verticals[i]=[[verticals[i][0][0],verticals[i+1][0][1]],[verticals[i][1][0],verticals[i+1][1][1]]]
                verticals[i+1]=[[verticals[i+1][0][0],temp[0][1]],[verticals[i+1][1][0],temp[1][1]]]
                sawtooth=0
                break
            elif botofv1>topofv2: #disjoint with bottom vertical to the right
            #elif verticals[i][1][1]>verticals[i+1][0][1]: #disjoint with top vertical to the right
                temp=verticals[i]
                verticals[i]=[[verticals[i][0][0],verticals[i+1][0][1]],[verticals[i][1][0],verticals[i+1][1][1]]]
                verticals[i+1]=[[verticals[i+1][0][0],temp[0][1]],[verticals[i+1][1][0],temp[1][1]]]
                sawtooth=0
                break

            else:
                sawtooth=1        
       
        
    newvertexset=[]
    for h in horizontals:
        for i in range(len(h)):
            newvertexset.append(h[i])
    return newvertexset  

def bottom_right_rigid(V):
    horizontals,verticals=sort_vertices_into_verticals_and_horizontals(V)
    horizontals.sort(key=lambda x:x[0][1],reverse=True) #sorts from -1 to -n
    rigid=0
    while rigid==0:
        for i in range(len(horizontals)-2):
            h1=horizontals[i]
            h2=horizontals[i+1]
            widthh1=list(range(h1[0][0],h1[1][0]+1))
            widthh2=list(range(h2[0][0],h2[1][0]+1))
            leftmosthorizontal = h1 if h1[0][0] < h2[0][0] else h2
            rightmosthorizontal= h2 if leftmosthorizontal==h1 else h1
            intersectionh1h2 = list(set(widthh1) & set(widthh2))
            
            if (horizontals[i+1][0][0]<horizontals[i][0][0] and horizontals[i+1][1][0]>horizontals[i][1][0]): #interleaved and smaller above
                #swap
                temp=horizontals[i]
                horizontals[i]=[[horizontals[i+1][0][0],horizontals[i][0][1]],[horizontals[i+1][1][0],horizontals[i][1][1]]]
                horizontals[i+1]=[[temp[0][0],horizontals[i+1][0][1]],[temp[1][0],horizontals[i+1][1][1]]]
                rigid=0
                break
                
            elif intersectionh1h2==[] and h1==rightmosthorizontal: #disjoint and t=rightmost horizontal is below the other 
                temp=horizontals[i]
                horizontals[i]=[[horizontals[i+1][0][0],horizontals[i][0][1]],[horizontals[i+1][1][0],horizontals[i][1][1]]]
                horizontals[i+1]=[[temp[0][0],horizontals[i+1][0][1]],[temp[1][0],horizontals[i+1][1][1]]]
                rigid=0
                break
                    
            else:
                rigid=1  
       
    sawtooth=0
    while sawtooth==0:
        for i in range(len(verticals)-1):
            v1=verticals[i]
            topofv1 = v1[0][1] if v1[0][1] > v1[1][1] else v1[1][1]
            botofv1=v1[0][1] if v1[1][1]==topofv1 else v1[1][1]
            
            v2=verticals[i+1]
            topofv2 = v2[0][1] if v2[0][1] > v2[1][1] else v2[1][1]
            botofv2=v2[0][1] if v2[1][1]==topofv2 else v2[1][1]
            
            
            if topofv1<topofv2 and botofv1>botofv2: #interleaved and smaller to right
            #if verticals[i][0][1]<verticals[i+1][0][1] and verticals[i][1][1]>verticals[i+1][1][1]:#interleaved and smaller to right
                #exchange
                temp=verticals[i]
                verticals[i]=[[verticals[i][0][0],verticals[i+1][0][1]],[verticals[i][1][0],verticals[i+1][1][1]]]
                verticals[i+1]=[[verticals[i+1][0][0],temp[0][1]],[verticals[i+1][1][0],temp[1][1]]]
                sawtooth=0
                break
            elif botofv2>topofv1: #disjoint with top vertical to the right
            #elif verticals[i][1][1]>verticals[i+1][0][1]: #disjoint with top vertical to the right
                temp=verticals[i]
                verticals[i]=[[verticals[i][0][0],verticals[i+1][0][1]],[verticals[i][1][0],verticals[i+1][1][1]]]
                verticals[i+1]=[[verticals[i+1][0][0],temp[0][1]],[verticals[i+1][1][0],temp[1][1]]]
                sawtooth=0
                break

            else:
                sawtooth=1
                    
                    
    newvertexset=[]
    for h in horizontals:
        for i in range(len(h)):
            newvertexset.append(h[i])
    return newvertexset  
