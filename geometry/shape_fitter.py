


from bisect import bisect, bisect_left, bisect_right, insort_left
from functools import cmp_to_key
from math import inf
import math
from abstract.rect import Rect
from geometry.coords import Coords
from geometry.curve import PolyCurve, Line
from abstract.vector import Vector

#compare: a function which should return true if the compared element is less than the search value, when sorted ascending.
#for e
def bisect_compare(a,compare=None, lo=0, hi=None):
    """Return the index where to insert item x in list a, assuming a is sorted.

    If sorted ascending, the return value i is such that all e in a[:i] have e < x, and all e in
    a[i:] have e >= x.  So if x already appears in the list, a.insert(i, x) will
    insert just before the leftmost x already there.
    
    in that case, an example of a compare function could be lambda arg:arg < x

    Optional args lo (default 0) and hi (default len(a)) bound the
    slice of a to be searched.
    """
    if hi is None:
        hi = len(a)
    while lo < hi:
        mid = (lo+hi)//2
        result = compare(a[mid])
        #search higher
        if result: lo = mid + 1
        #search lower
        else: hi = mid
    return lo

def try_perfect_fit_2d(parents:list[tuple[int, Rect]], move_slices_to:list[tuple[int, Rect]], child:tuple[int,Coords], padding:float, allowed_error:float) -> tuple[int, Coords] | None:

    vector_cmp_desc = lambda elem, search_for: (search_for[0] - elem[0]) if (elem[0] != search_for[0]) else (search_for[1] - elem[1])
    rect_order = cmp_to_key(lambda elem, search_for: elem[1].size.compare(search_for[1].size))
    rect_order_size = cmp_to_key(lambda elem, search_for: vector_cmp_desc(elem[1].size, search_for))
    contains = lambda rect1, rect2: rect1[0] == rect2[0] and rect1[1].contains(rect2[1])
    
    #the smallest parent that can fit this child
    best_fit_index = bisect_left(parents, rect_order_size(child[1]), key=rect_order_size)
    while best_fit_index > 0:
        best_fit_index -= 1
        best_rect = parents[best_fit_index][1]
        #check if the rectangle isn't too big, that would be such a waste.
        if best_rect.size.x > child[1].x + allowed_error:
            #we went past the list of rectangles which aren't too big.
            return None
        #check if y falls in range too
        if best_rect.size.y >= child[1].y:
            if best_rect.size.y <= child[1].y + allowed_error:
                # found a parent which can contain this child and isn't too big
                best_parent_index = parents[best_fit_index][0]

                #substract padding from rectangles already, so we don't have to bother about it later.
                padded_child_rect = Rect(best_rect.p0, child[1]).expanded(padding)
                
                right_padded_size = child[1] + padding

                #slice the parent rectangle in three: this child and two leftover rectangles.
                sliced_rects:list[tuple[int,Rect]] = []
                #sliced on x
                if best_rect.size.x > right_padded_size.x:
                    sliced_rects.append((best_parent_index, Rect(Coords(best_rect.p0.x + right_padded_size.x, best_rect.p0.y), Coords(best_rect.size.x - right_padded_size.x, best_rect.size.y))))
                #sliced on y
                if best_rect.size.y > right_padded_size.y:
                    sliced_rects.append((best_parent_index, Rect(Coords(best_rect.p0.x, best_rect.p0.y + right_padded_size.y), Coords(best_rect.size.x, best_rect.size.y - right_padded_size.y))))
                parents.pop(best_fit_index)

                if parents == move_slices_to:

                    #loop over the other rectangles and slice everything which collides with this rectangle.
                    #loop reversed, because else we're sawing off the branch we're sitting on
                    cutting_index = len(parents) - 1
                    while cutting_index >= 0:
                        rect_ref = parents[cutting_index]
                        rect_to_slice = rect_ref[1]
                        if rect_ref[0] == best_parent_index and rect_to_slice.collides(padded_child_rect):
                            parents.pop(cutting_index)
                            pieces:list[Rect] = padded_child_rect.substractFrom(rect_to_slice)
                            for piece in pieces:
                                sliced_rects.append((rect_ref[0], piece))
                        cutting_index -= 1
                                
                    #now loop over the slices and see if they contain or are contained. in that case, remove the smallest element.
                    while len(sliced_rects) > 0:
                        sliced_rect = sliced_rects.pop(0)
                        for slice in sliced_rects:
                            #there's a bigger slice
                            if contains(slice, sliced_rect):
                                break
                        #not broken out of loop
                        else:
                            for rect2 in parents:
                                if contains(rect2, sliced_rect):
                                    break
                            #not broken out of loop
                            else:
                                #now we know for sure to 'approve' this piece. don't add it yet!
                                #the slice might contain an existing or sliced rectangle
                                #first slice other pieces
                                #for other_slice_index in reversed(range(len(sliced_rects))):
                                #    if contains(sliced_rect,sliced_rects[other_slice_index]):
                                #        sliced_rects.pop(other_slice_index)
                                #check if existing rectangles are contained by this slice
                                for contained_rect_index in reversed(range(len(parents))):
                                    if contains(sliced_rect, parents[contained_rect_index]):
                                        parents.pop(contained_rect_index)

                                #move slices to the move_slices_to array
                                insort_left(move_slices_to, sliced_rect, key=rect_order)
                else:
                    for sliced_rect in sliced_rects:
                        insort_left(move_slices_to, sliced_rect, key=rect_order)

                #for sliced_rect in sliced_rects:
                #    insort_left(left_over_parent_rects, sliced_rect,key=rect_order)
                return (best_parent_index, best_rect.p0)

class FitResult2D:
    def __init__(self, fitted_boxes:list[tuple[int,Coords]|None], leftovers: list[tuple[int,Rect]|None]):
        self.fitted_boxes = fitted_boxes
        self.leftovers = leftovers

def fit_boxes_2d(parent_shapes:list[Coords], child_shapes: list[Coords], padding: float, allowed_error: float)->FitResult2D:
    """this function tries to use the fewest base shapes possible when trying to fit child shapes inside them

    Args:
        parent_shapes (list[Coords]): the shapes in which we will try to fit the child shapes
        child_shapes (list[Coords]): 
        padding (float): the padding between the shapes
    """
    
    #first, order them by x size. then, by y size.
    #order from biggest to smallest
    size_order = cmp_to_key(lambda elem, search_for: elem[1].compare(search_for[1]))

    children = sorted(enumerate(child_shapes),key=size_order)
    parents = sorted(enumerate(parent_shapes),key=size_order)
    
    
    unused_parents:list[tuple[int, Rect]] = []
    #these are slices of used parents which could still be used
    used_parents:list[tuple[int, Rect]] = []

    fitted_children:list[tuple[int,Coords]|None] = [None] * len(child_shapes)
    #convert all parents to rects
    for parent in parents:
        unused_parents.append((parent[0], Rect(Coords(0,0), parent[1])))
        
    #now try to use as few rectangles as possible, by checking if each new rect fits in a used rect first.
    
    for child in children:
        #find a good parent in the list of used parents
        fit = try_perfect_fit_2d(used_parents, used_parents, child, padding, allowed_error)
        
        if fit == None:
            #else, use a new parent of the remaining parents

            fit = try_perfect_fit_2d(unused_parents, used_parents, child, padding, allowed_error)
            if fit == None:
                fit = try_perfect_fit_2d(used_parents,used_parents, child, padding,inf)
                if fit == None:
                    fit = try_perfect_fit_2d(unused_parents, used_parents, child, padding, inf)
        
        fitted_children[child[0]] = fit
        
    return FitResult2D(fitted_children, used_parents)
        
    

#this function modifies the parents list!
def try_perfect_fit(parents:list[tuple[int,float]], move_leftovers_to:list[tuple[int,float]], child: tuple[int,float], allowed_error:float) -> tuple[int,float] | None:
    """this function modifies the parents list!

    Args:
        parents (list[tuple[int,float]]): a list of parent indexes and sizes
        move_leftovers_to (list[tuple[int,float]]): to which array we should move any leftovers
        child (tuple[int,float]): the child to try fitting

    Returns:
        tuple[int,float] | None: the resulting fit position. cutting from the back to the front so if there's a parent with length 300, the first child cut from it will have an offset of 300!
    """
    #reverse the order: sorted from high to low
    order = cmp_to_key(lambda elem, search_for:search_for[1] - elem[1])
    #check if the parent with the most remaining length can contain this child.
    if len(parents) > 0 and parents[0][1] >= child[1]:
        #find a parent in use which fits perfectly.
        perfect_fit_index = bisect_left(parents, order(child),key=order)
        if perfect_fit_index <= len(parents) and perfect_fit_index > 0:
            perfect_fit_index -= 1
            #copy reference
            perfect_fit_parent = parents[perfect_fit_index]
            difference = perfect_fit_parent[1] - child[1]
            if difference < allowed_error:
                if difference == 0:
                    #remove parent from array. we no longer need it.
                    del parents[perfect_fit_index]
                    return (perfect_fit_parent[0], perfect_fit_parent[1])
                else:
                    #move reference to result
                    result = perfect_fit_parent

                    modified_parent = (perfect_fit_parent[0], perfect_fit_parent[1] - child[1])
                    #move the used parent to a new place in the array
                    parents.pop(perfect_fit_index)
                    insort_left(move_leftovers_to, modified_parent, key=order)
                    return result
    return None

def fit_lengths_1d(parent_lengths:list[float], child_lengths: list[float], padding: float, allowed_error:float)->list[tuple[int,float] | None]:
    """this function tries to use the fewest base shapes possible when trying to fit child shapes inside them.
    as second priority, you can provide a cost function to optimize the amount of loss.

    Args:
        parent_lengths (list[float]): the shapes in which we will try to fit the child shapes
        child_lengths (list[float]): 
        padding (float): the padding between the shapes
        allowed_error (float): the amount of wood per beam allowed to be chopped off
        
    Returns:
        a list of tuples containing the parent index and the parent offset for each child
    """
    #order by size
    #a sorted array, containing which parents are in use.
    #each parent in use contains a parent index and a remaining length.
    used_parents:list[tuple[int,float] | None] = []
    unused_parents = sorted(enumerate(parent_lengths), key=lambda x:x[1], reverse=True)
    children = sorted(enumerate(child_lengths), key=lambda x:x[1],reverse=True)
    #parent index, offset
    fitted_children:list[tuple[int,float]|None] = [None] * len(child_lengths)
    #child index, length
    #children_to_fit:list[tuple[int,float]|None]
    #first, fit the longest children. then, fit shorter children
    for child in children:
        padded_child = (child[0],child[1] + padding)
        #find a good parent in the list of used parents
        fit = try_perfect_fit(used_parents, used_parents, padded_child, allowed_error)
        
        if fit != None:
            fit = (fit[0], fit[1] - padding)
        else:
            #else, use a new parent of the remaining parents

            fit = try_perfect_fit(unused_parents, used_parents, child, allowed_error)
            if fit == None:
                fit = try_perfect_fit(used_parents,used_parents, padded_child,inf)
                if fit != None:
                    fit = (fit[0], fit[1] - padding)
                else:
                    fit = try_perfect_fit(unused_parents, used_parents, child, inf)
        
        if fit != None:
            #reverse offset in parent
            fitted_children[child[0]] = (fit[0], parent_lengths[fit[0]] - fit[1])
            
    #moving items around will rarely do much. it'd take a whole load of performance, though.

    #finally, return the list
    return fitted_children

class _SortedLineElement:
    angle: float
    child_index:int
    fit_group_index:int
    line: Line
    def __init__(self, angle, child_index, fit_group_index, line) -> None:
        self.angle = angle
        self.child_index = child_index
        self.fit_group_index = fit_group_index
        self.line = line

class _PolygonFitGroup:
    parent_index: int
    child_indexes: list[int]
    relative_child_offsets:list[Vector]
    bounds: Rect
    lines: list[_SortedLineElement]
    def __init__(self, parent_index,child_indexes: list[int], relative_child_offsets:list[Vector], lines: list[_SortedLineElement], bounds: Rect) -> None:
        self.parent_index = parent_index
        self.child_indexes = child_indexes
        self.relative_child_offsets = relative_child_offsets
        self.bounds = bounds
        self.lines = lines
    
class PolygonFitResult2D:
    
    fitted_children: list[tuple[int, Vector | None]] = []
    """a list of parent indexes and offsets from the 00 corner of the specified parent, ordered like the order of child_polygons"""
    grouped_polygons: list[_PolygonFitGroup] = []
    """a list of grouped polygons: these polygons are grouped because they fit into eachother nicely."""
    ordered_parents: list[Vector] = []
    
    box_result:FitResult2D = None

def fit_polygons_2d(parent_sizes:list[Vector], child_polygons: list[PolyCurve], allowed_error) -> PolygonFitResult2D:
    """fits polygons in a list of parent rectangles.<br>
    will not rotate the polygons, only move them!
    we expect the polygons to be closed.

    Args:
        parent_sizes (list[Vector]): the rectangles to fit the polygons in
        child_polygons (list[PolyCurve]): the polygons to fit. we expect the 00 corner of the bounds of the child polygons to be aligned to 0 0.
    """
    
    line_list: list[_SortedLineElement] = []
    
    fit: PolygonFitResult2D = PolygonFitResult2D()
    
    line_key = lambda elem: elem.angle
    
    
    #first, order them by x size. then, by y size.
    #order from biggest to smallest
    size_order = cmp_to_key(lambda elem, search_for: elem[1].compare(search_for[1]))

    parents = sorted(enumerate(parent_sizes),key=size_order)    
    
    #create a list of irregular lines and order them by angle and length
    
    child_index = 0
    for poly in child_polygons:
        group = _PolygonFitGroup(None, [child_index], [Vector(0,0)], [],poly.bounds)
        for line in poly.curves:
            angle = line.angle
            line_elem = _SortedLineElement(angle, child_index, child_index, line)
            group.lines.append(line_elem)
            insort_left(line_list, line_elem, key=line_key)
        
        #convert all children to polygonfitgroups
        fit.grouped_polygons.append(group)
            
        #try fitting as many polygons as possible
        child_index += 1
    
    #now try to group polygons based on their fitting.
    
    #loop over half of the lines, and compare the other half
    for sorted_line_index in range(len(line_list)):
        
        elem_a = line_list[sorted_line_index]
        line_a = elem_a.line
        #find lines with the opposite angle
        
        group_a = fit.grouped_polygons[elem_a.fit_group_index]
        
        target_angle = elem_a.angle + math.pi
        opposite_angle_index = bisect_left(line_list, target_angle,key=line_key)
        if opposite_angle_index < len(line_list):
            elem_b = line_list[opposite_angle_index]
            if(elem_b.angle == target_angle):
                line_b = elem_b.line
                group_b = fit.grouped_polygons[elem_b.fit_group_index]
                #loop over all lines with the opposite angle and check polygon collision and bounds

                #try merging at line_a.start and line_b.end
                offset = line_b.end - line_a.start
                relative_b_bounds = Rect(offset, group_b.bounds.size)
                merged_bounds_relative_to_a = Rect.outer([group_a.bounds, relative_b_bounds])

                #check if the biggest parent available can contain the merged rectangle
                if parent_sizes[0].x >= merged_bounds_relative_to_a.size.x and parent_sizes[0].y >= merged_bounds_relative_to_a.size.y:

                    #merge group b into group a

                    translate_a = -merged_bounds_relative_to_a.p0
                    translate_b = translate_a + offset
                    
                    for group, translation in zip([group_a,group_b], [translate_a, translate_b]):
                        for line_elem in group.lines:
                            line_elem.line.translate(translation)
                        for i in range(len(group.relative_child_offsets)):
                            group.relative_child_offsets[i] += translation

                    group_a.lines.extend(group_b.lines)
                    group_a.child_indexes.extend(group_b.child_indexes)
                    group_a.relative_child_offsets.extend(group_b.relative_child_offsets)

                    
                    group_a.bounds = merged_bounds_relative_to_a
                    group_a.bounds.p0 = Vector([0] * 2)
                    
    #finally, when done grouping, try fitting as many groups as possible into the rectangles provided using their bounding boxes.
    child_sizes = [group.bounds.size for group in fit.grouped_polygons]
    fit.box_result = fit_boxes_2d(parent_sizes, child_sizes, 0, allowed_error)
    
    fit.fitted_children = [None] * len(child_polygons)
    for fitted_box, group in zip(fit.box_result.fitted_boxes, fit.grouped_polygons):
        if fitted_box != None:
            for group_child_index, fitted_child_index in enumerate(group.child_indexes):
                fit.fitted_children[fitted_child_index] = (fitted_box[0], fitted_box[1] + group.relative_child_offsets[group_child_index])

    return fit