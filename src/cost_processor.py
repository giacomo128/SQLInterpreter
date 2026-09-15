import parser_utils as pu
import utils as u

def distinct_val_calc(attr, relation):
    """function used to find the number of distinct values of A in R

    Args:
        attr (str): attribute to look for
        relation (relation): relation obj

    Returns:
        int: number of distinct vals
    """

    distinct_list = []

    if attr not in relation.schema:
        raise RuntimeError(f"{attr} does not exist in the relation schema")
    
    # check for distinct values
    for tuple in relation.tuples:
        if tuple[attr] not in distinct_list:
            distinct_list.append(tuple[attr])
    
    return len(distinct_list)

def individual_cost_calc(db, obj):
    """function used to get the individual cost of a query

    Args:
        db (database): db to use
        obj (obj): query obj

    Returns:
        int: cost
    """

    # find the size of the relation 
    if isinstance(obj, str):
        temp = u.single_relation_finder(db, obj)
        return len(temp.tuples)

    # find the size of the relation 
    if isinstance(obj, pu.Relation):
        return len(obj.tuples)
    
    # find the size of the union
    if isinstance(obj, pu.Union):
        temp_1 = individual_cost_calc(db, obj.relvar1)
        temp_2 = individual_cost_calc(db, obj.relvar2)
        return temp_1 + temp_2

    # find the size of the difference
    if isinstance(obj, pu.Difference):
        temp_1 = individual_cost_calc(db, obj.relvar1)
        return temp_1

    # find the size of the projection
    if isinstance(obj, pu.Project):

        # must have attributes
        if not obj.attrlist:
            return 0
        
        temp_cost = []
        rel_obj = u.single_relation_finder(db, obj.relvar)

        for attr in obj.attrlist:
            temp_cost.append(distinct_val_calc(attr, rel_obj))

        return max(temp_cost)

    # find the size of the selection
    if isinstance(obj, pu.Select):
        rel_obj = u.single_relation_finder(db, obj.relvar)
        temp_cost = individual_cost_calc(db, obj.relvar)

        distinct = distinct_val_calc(obj.predicate.left, rel_obj)

        # must have value
        if distinct == 0:
            return temp_cost

        # return correct cost
        if obj.predicate.operator == "=":
            return temp_cost / distinct
        else:
            return temp_cost - (temp_cost / distinct)

    # find the size of the rename
    if isinstance(obj, pu.Rename):
        temp_1 = individual_cost_calc(db, obj.relvar)
        return temp_1

    # find the size of the join
    if isinstance(obj, pu.Join):
        temp_1, temp_2 = u.double_relation_finder(db, obj.relvar1, obj.relvar2)

        # find common values
        found = False
        shared_keys = []
        for key in temp_1.schema:
            if key in temp_2.schema:
                found = True
                shared_keys.append(key)
        
        # return size of cartesian
        if found == False:
            return len(temp_1.tuples) * len(temp_2.tuples)
        
        product = len(temp_1.tuples) * len(temp_2.tuples)

        # calculate the min attribute cost
        distinct_list = []
        for key in shared_keys:
            distinct_1 = distinct_val_calc(key, temp_1)
            distinct_2 = distinct_val_calc(key, temp_2)

            # disallow empty
            if distinct_1 == 0 or distinct_2 == 0:
                return 0
            
            val = min(product/distinct_1, product/distinct_2)
            distinct_list.append(val)

        return min(distinct_list)

def total_cost_calc(db, obj):
    """function used to return the total cost of a query

    Args:
        db (database): db to use
        obj (query): obj for a query

    Returns:
        int: total cost
    """

    # find the individual cost of the operation
    cost = individual_cost_calc(db, obj)

    # find the cumulative cost
    if hasattr(obj, "relvar"):
        cost += total_cost_calc(db, obj.relvar)

    if hasattr(obj, "relvar1"):
        cost += total_cost_calc(db, obj.relvar1)

    if hasattr(obj, "relvar2"):
        cost += total_cost_calc(db, obj.relvar2)

    return cost

