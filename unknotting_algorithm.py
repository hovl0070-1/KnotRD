from push_Ts import *
from hinge_Ts import *
from snowplow_gates_sorting_simplifications import *


def simplify_v1b_T_and_rotate(V):
     ############################################################
    # SIMPLIFICATION CYCLE:
    #
    # Repeatedly performs:
    #   1. V1b simplifications
    #   2. ALL possible push T moves
    #   3. ONE hinge T move
    #   4. Returns to step 1
    #
    # A hinge T move is deliberately NOT exhausted before
    # returning to V1b and push T simplifications. This allows
    # newly created V1b and push T opportunities to be exploited
    # between individual hinge T moves.
    #
    # If no hinge T is available, the algorithm attempts rotations.
    ############################################################
     #
    # NOTE: IF YOU RUN THIS YOU CAN GET STUCK IN A CYCLE. IT COULD GO HINGE -> PUSH -> PUSH -> HINGE (ORIGINAL DIAGRAM) AND STUCK
    # THE FIX WILL BE PASSING THE SEEN DIAGRAMS BETWEEN PUSH AND HINGE T'S
    ##
    
    rotations = 0

    while True:
        complexity = len(V) // 2

        if complexity == 2:
            #print('The diagram has been unknotted!')
            return V

        # computationally expensive but covers a lot of bases
        V = perform_v1b_corner_rigid_simplifications(V)

        # easier computationally
        # VS = get_v1b_reduced_diagram(V)
        # V = VS[-1]

        if len(V) // 2 < complexity:
            rotations = 0
            continue

        print('The above diagram is v1b reduced. Attempting push T moves')

        V, seen_diagrams, invalid_exit_disks = \
            perform_push_T_move_and_v1b_reduce(V)

        if len(V) // 2 < complexity:
            rotations = 0
            continue
            
        print(
            'The above diagram is v1b reduced and all push T moves '
            'attempted. Attempting hinge T moves'
        )

        V, exit_disk = \
            perform_single_hinge_T_and_simplify(
                V,
                seen_diagrams,
                invalid_exit_disks
            )

        if exit_disk:
            invalid_exit_disks.append(exit_disk)
            rotations = 0
            continue

        if len(V) // 2 < complexity:
            rotations = 0
            continue

        if rotations <= 3:
            print(
                'Performing a 90 degree rotation of diagram '
                'and attempting all moves again'
            )

            V = rotate_vertex_set_90_ccw(V)
            rotations = rotations + 1
            continue

        else:
            print('The diagram is still knotted.')
            return V
        

        
def simplify_v1b_pushT_hingeT_and_rotate(V):
    
    ############################################################
    # FULL SIMPLIFICATION CYCLE:
    #
    # Repeatedly performs:
    #   1. V1b simplifications
    #   2. ALL possible push T moves
    #   3. ALL possible hinge T moves
    #   4. A 90-degree rotation if no further simplification
    #      is found
    #
    # The push T and hinge T stages are each exhausted before
    # moving to the next stage.
    #
    ############################################################
    
    rotations1 = 0
    rotations0 = 0
    while True:
        complexity = len(V) // 2
 
        if complexity == 2:
            print('The diagram has been unknotted!')
            return V

        # V1b simplification
        #rotations get all the gates and snowplows so we rotate here at this step 4 times first. We do it agian later too
        V = perform_v1b_corner_rigid_simplifications(V)
        if rotations0 <=3:
            V = rotate_vertex_set_90_ccw(V)
            rotations0 = rotations0 + 1
            continue
        # easier computationally
        # VS = get_v1b_reduced_diagram(V)
        # V = VS[-1]

        if len(V) // 2 < complexity:
            rotations1 = 0
            continue

        print(
            'The above diagram is v1b reduced. '
            'Attempting push T moves'
        )

        # Perform ALL push T moves
        V, seen_diagrams, invalid_exit_disks = perform_push_T_move_and_v1b_reduce(V)

        if len(V) // 2 < complexity:
            rotations1 = 0
            rotations0=0
            continue

        print(
            'The above diagram is v1b reduced and all push T moves '
            'attempted. Attempting hinge T moves'
        )

        # Perform ALL hinge T moves
        V = perform_hinge_Ts_and_simplify(V)

        if len(V) // 2 < complexity:
            rotations1 = 0
            rotations0=0
            continue

        if rotations1 <= 3:
            print(
                'Performing a 90 degree rotation of diagram '
                'and attempting all moves again'
            )

            V = rotate_vertex_set_90_ccw(V)
            rotations1 = rotations1 + 1
            continue

        else:
            print('The diagram is still knotted.')
            return V