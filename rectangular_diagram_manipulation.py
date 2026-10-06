def flip_vertex_set(V):
    n=len(V)//2
    V_flip=[]
    for v in V:
        v_flip=[v[0],-n-v[1]-1]
        V_flip.append(v_flip)
    return V_flip



def rotate_vertex_set_90_ccw(V):
    # Step 1: Rotate each vertex (x, y) -> (-y, x)
    rotated = [[-y, x] for x, y in V]

    # Step 2: Normalize the x and y coordinates
    min_x = min(v[0] for v in rotated)
    min_y = min(v[1] for v in rotated)

    # Shift so that x starts at 1 and y ends at -1 (standard rectangular diagram convention)
    x_shift = 1 - min_x
    y_shift = -1 - max(v[1] for v in rotated)

    rotated_shifted = [[x + x_shift, y + y_shift] for x, y in rotated]
   
    # Optional: sort to return in consistent order
    rotated_shifted.sort()
    return rotated_shifted

def reflect_vertex_set(V):
    n=len(V)//2
    V_reflect=[]
    for v in V:
        v_reflect=[n-v[0]+1,v[1]]
        V_reflect.append(v_reflect)
    return V_reflect