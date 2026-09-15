
import query_executor as qe
import parser_utils as pu

def pretty_print(query_result):
    """function used to print a relation: its schema and content

    Args:
        query_result (Relation): it is the object to be printed
    """

    # print the schema
    print(", ".join(query_result.schema) + ";")

    # print the tuples
    for tuple in query_result.tuples:
        strs = [str(val) for val in tuple.values()]
        print(", ".join(strs) + ";")

def single_relation_finder(db, relvar):
    """function used to retrieve a relation object given a relvar

    Args:
        db (database): database to iterate
        relvar (String): the name of the relation

    Raises:
        RuntimeError: if the relation could not be found

    Returns:
        Relation: the relation object given its relvar name
    """

    # if nested query object get the result
    if not isinstance(relvar, str):
        return qe.execute_query(db, relvar)

    temp = None

    # check if it is loaded
    if relvar in db.loaded_relations:
        temp = db.loaded_relations[relvar]

    # check if it needs to be executed and then loaded
    elif relvar in db.vars:
        temp = qe.execute_query(db, db.vars[relvar])

    # check if no such relation exists
    else:
        raise RuntimeError(f"{relvar} cannot be found or has not been populated")
    
    return temp

def double_relation_finder(db, relvar1, relvar2):
    """function used to retrieve two relation objects given two relvars

    Args:
        db (Database): database to iterate
        relvar1 (String): the name of the first relation
        relvar2 (String): the name of the second relation

    Raises:
        RuntimeError: if the first relation could not be found
        RuntimeError: if the second relation could not be found

    Returns:
        Relation: returns two relation objects
    """

    temp_1 = single_relation_finder(db, relvar1)
    temp_2 = single_relation_finder(db, relvar2)
    
    return temp_1, temp_2

def reorder_tuple(schema, tuple):
    """function used to reorder a tuple given a schema

    Args:
        schema (list): list of attrs in order
        tuple (dict): tuple

    Returns:
        dict: ordered tuple
    """
    
    original_tuple = dict(tuple)
    new_tuple = {}

    for attr in schema:
        new_tuple[attr] = original_tuple[attr]

    return new_tuple

def query_flattener(db, obj):
    """function used to flatten a query by tracing all the let statements

    Args:
        db (database): db to use
        obj (query): any query object 

    Returns:
        obj: an object
    """

    if isinstance(obj, pu.Select):
        if obj.relvar in db.vars:
            obj.relvar = query_flattener(db, db.vars[obj.relvar])

    elif isinstance(obj, pu.Let):
        return obj.query
    
    elif isinstance(obj, pu.Project):
        if obj.relvar in db.vars:
            obj.relvar = query_flattener(db, db.vars[obj.relvar])
    
    elif isinstance(obj, pu.Rename):
        if obj.relvar in db.vars:
            obj.relvar = query_flattener(db, db.vars[obj.relvar])

    elif isinstance(obj, pu.Difference):
        if obj.relvar1 in db.vars:
            obj.relvar1 = query_flattener(db, db.vars[obj.relvar1])

        if obj.relvar2 in db.vars:
            obj.relvar2 = query_flattener(db, db.vars[obj.relvar2])

    elif isinstance(obj, pu.Union):
        if obj.relvar1 in db.vars:
            obj.relvar1 = query_flattener(db, db.vars[obj.relvar1])

        if obj.relvar2 in db.vars:
            obj.relvar2 = query_flattener(db, db.vars[obj.relvar2])

    elif isinstance(obj, pu.Join):
        if obj.relvar1 in db.vars:
            obj.relvar1 = query_flattener(db, db.vars[obj.relvar1])

        if obj.relvar2 in db.vars:
            obj.relvar2 = query_flattener(db, db.vars[obj.relvar2])

    return obj

def check_structure(db, obj):
    """check if nested queries are valid

    Args:
        db (database): db to use
        obj (obj): query obj

    Raises:
        RuntimeError: invalid structure

    Returns:
        schema (list): schema of query
    """

    # check for relation
    if isinstance(obj, str):
        if obj not in db.loaded_relations:
            raise RuntimeError(f"Relation {obj} has not been loaded")
        
        return list(db.loaded_relations[obj].schema)

    # check for select
    elif isinstance(obj, pu.Select):
        schema = check_structure(db, obj.relvar)
        left = obj.predicate.left
        right = obj.predicate.right

        if left not in schema:
            raise RuntimeError(f"{left} does not exist in relation schema")
        
        if isinstance(right, str) and right[0] != '"':
            if right not in schema:
                raise RuntimeError(f"{right} does not exist in relation schema")

        return schema

    # check for project
    elif isinstance(obj, pu.Project):
        schema = check_structure(db, obj.relvar)

        for attr in obj.attrlist:
            if attr not in schema:
                raise RuntimeError(f"Attribute {attr} not in {schema}")
            
        return list(obj.attrlist)

    # check for rename
    elif isinstance(obj, pu.Rename):
        schema = check_structure(db, obj.relvar)
        if len(obj.attrlist) != len(schema):
            raise RuntimeError("Mismatch in length of renamed attributes and schema")
        
        for attr in obj.attrlist:
            if attr not in db.types:
                raise RuntimeError(f"Attribute {attr} does not exist in the set of known types")
        
        return list(obj.attrlist)

    # check diff
    elif isinstance(obj, pu.Difference):
        schema1 = check_structure(db, obj.relvar1)
        schema2 = check_structure(db, obj.relvar2)

        if set(schema1) != set(schema2):
            raise RuntimeError(f"Difference: incompatible schemas")
        
        return schema1

    # check union
    elif isinstance(obj, pu.Union):
        schema1 = check_structure(db, obj.relvar1)
        schema2 = check_structure(db, obj.relvar2)

        if set(schema1) != set(schema2):
            raise RuntimeError(f"Union: incompatible schemas")

        return schema1

    # check join
    elif isinstance(obj, pu.Join):
        schema1 = check_structure(db, obj.relvar1)
        schema2 = check_structure(db, obj.relvar2)
        res = schema1

        for attr in schema2:
            if attr not in schema1:
                res.append(attr)

        return res
    
    # check let
    elif isinstance(obj, pu.Let):
        return check_structure(db, obj.query)

    else:
        raise RuntimeError(f"unknown error")
