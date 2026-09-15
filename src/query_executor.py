import os
import parser_utils as pu
import utils as u
import csv

def execute_query(db, obj):
    """function used to dispatch the correct query executor 

    Args:
        db (database): database to use
        obj (query): query object to execute

    Raises:
        RuntimeError: if no matching object found

    Returns:
        relation: the relation object created after execution
    """

    result = None

    # dispatch the correct executor function
    if isinstance(obj, pu.Select):
        result = execute_select(db, obj)

    elif isinstance(obj, pu.Project):
        result = execute_project(db, obj)

    elif isinstance(obj, pu.Let):
        result = execute_let(db, obj)

    elif isinstance(obj, pu.Rename):
        result = execute_rename(db, obj)

    elif isinstance(obj, pu.Difference):
        result = execute_diff(db, obj)

    elif isinstance(obj, pu.Union):
        result = execute_union(db, obj)

    elif isinstance(obj, pu.Join):
        result = execute_join(db, obj)

    else:
        raise RuntimeError("Unrecognized query")

    return result

def execute_load(db, obj):
    """function used to load data from a csv file into a relation

    Args:
        db (database): it is the database we are using
        obj (Load): load query obj
    """

    relation_name = obj.relvar
    path = obj.path

    # check the relation exists in the db
    if relation_name not in db.relations:
        raise RuntimeError("Schema", relation_name, "has not been initialised yet")
    
    attrlist = db.relations[relation_name]

    # initialise an empty relation
    if relation_name not in db.loaded_relations:
        db.loaded_relations[relation_name] = pu.Relation(attrlist, [])

    # check the file exists
    if not os.path.isfile(path):
        raise RuntimeError("The path", path, "does not exist or does not point to a file")

    # check that it is a csv file
    if not os.path.splitext(path)[-1] == ".csv":
        raise RuntimeError("The path", path, "does not point to csv file")

    # populate with empty lists the db for the fds
    if relation_name in db.fds and relation_name not in db.loaded_fds:
        db.loaded_fds[relation_name] = []
        
        for fd in db.fds[relation_name]:
            db.loaded_fds[relation_name].append([])

    # process the csv file
    with open(path, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')

        # check each row
        for row in reader:

            # length of elements must match the schema
            if len(row) != len(attrlist):
                raise RuntimeError("Mismatch in row length and size of attribute list specified")

            temp_dict = {}

            # iterate through each row element
            for i in range(len(attrlist)):
                elem = row[i]
                attribute = attrlist[i]

                att_type = db.types[attribute]
                d_type = db.domains[att_type]

                # if an attribute is an int try to convert it
                if d_type == "Int":
                    try:
                        int_elem = int(elem)  
                        temp_dict[attribute] = int_elem
                    
                    except:
                        raise RuntimeError("The file has a row with an attribute that cannot be converted to int")
                
                else:
                    temp_dict[attribute] = elem
            
            # check for fds
            if relation_name in db.fds:

                index = 0

                # iterate through all the fds for a given relation
                for fd in db.fds[relation_name]:

                    # get all the determinants
                    determinant_vals = []
                    determinants = fd.determinants
                    for deter in determinants:
                        determinant_vals.append(temp_dict[deter])
                    
                    # get all the dependents
                    dependent_vals = []
                    dependents = fd.dependents
                    for dep in dependents:
                        dependent_vals.append(temp_dict[dep])

                    found = False

                    # check if there exists already a populated fd with the given determinants
                    for pop_fd in db.loaded_fds[relation_name][index]:
                        if tuple(determinant_vals) in pop_fd:
                            found = True
                            break
                    
                    # add a new fd if there is not a populated one
                    if found == False:
                        new_fd = {}
                        new_fd[tuple(determinant_vals)] = dependent_vals
                        db.loaded_fds[relation_name][index].append(new_fd)
                    
                    # if there is a populated fd check if that the dependents match
                    else:

                        for pop_fd in db.loaded_fds[relation_name][index]:

                            # check for match
                            if tuple(determinant_vals) in pop_fd.keys():
                                if dependent_vals != pop_fd[tuple(determinant_vals)]:
                                    raise RuntimeError(f"The fd {fd} given {tuple(determinant_vals)} has been corrupted")

                    index += 1

            # disallow duplicates
            if temp_dict not in db.loaded_relations[relation_name].tuples:
                db.loaded_relations[relation_name].tuples.append(temp_dict)

def execute_select(db, obj):
    """function used to perform select

    Args:
        db (database): db to use
        obj (select): select query obj

    Returns:
        relation: result relation generated
    """

    # get the relation object
    temp = u.single_relation_finder(db, obj.relvar)
    result = []

    left = obj.predicate.left
    right = obj.predicate.right

    # check if valid selection
    if left not in temp.schema:
        raise RuntimeError(f"{left} does not exist in relation schema")

    # iterate through each tuple of the relation
    for tuple in temp.tuples:

        # check for correct selection
        if obj.predicate.operator == "=":

            # check for constants or attributes
            if isinstance(right, int):
                if tuple[left] == right:
                    result.append(dict(tuple))

            elif right[0] != '"':
                if right in temp.schema:
                    if tuple[left] == tuple[right]:
                        result.append(dict(tuple))
                else:
                    raise RuntimeError(f"{right} does not exist in relation schema")

            else:
                temp_right = right.strip('"')
                if tuple[left] == temp_right:
                    result.append(dict(tuple))
                
        else:

            # check for constants or attributes
            if isinstance(right, int):
                if tuple[left] != right:
                    result.append(dict(tuple))

            elif right[0] != '"':
                if right in temp.schema:
                    if tuple[left] != tuple[right]:
                        result.append(dict(tuple))
                else:
                    raise RuntimeError(f"{right} does not exist in relation schema")

            else:
                temp_right = right.strip('"')
                if tuple[left] != temp_right:
                    result.append(dict(tuple))

    return pu.Relation(temp.schema, result)

def execute_project(db, obj):
    """function used to perform project

    Args:
        db (database): db to use
        obj (project): project query obj

    Raises:
        RuntimeError: if a project attr does not exist in the schema

    Returns:
        relation: result relation generated
    """

    # get the relation object
    temp = u.single_relation_finder(db, obj.relvar)
    result = []
    
    relvar = obj.relvar
    attrlist = obj.attrlist

    # iterate through each tuple of the relation
    for tuple in temp.tuples:

        temp_dict = {}

        # iterate through each attribute of project attrlist
        for attr in attrlist:

            # project
            if attr in tuple.keys():
                temp_dict[attr] = tuple[attr]
            else:
                raise RuntimeError(f"{attr} not in relation schema")
        
        # disallow duplicates
        if temp_dict not in result:
            result.append(temp_dict)

    return pu.Relation(attrlist, result)

def execute_let(db, obj):

    # update the db
    relvar = obj.relvar
    db.vars[relvar] = obj.query

    return relvar

def execute_rename(db, obj):
    """function used to perform rename

    Args:
        db (database): db to use
        obj (rename): rename query obj

    Raises:
        RuntimeError: if there is mismatch in number of renamed attr and schema

    Returns:
        relation: result relation generated
    """

    # get the relation object
    temp = u.single_relation_finder(db, obj.relvar)

    result = []
    attrlist = obj.attrlist

    # check same number of attrs
    if len(attrlist) != len(temp.schema):
        raise RuntimeError("Mismatch in length of renamed attributes and schema")
    
    # check renamed attrs exist
    for attr in attrlist:
        if attr not in db.types.keys():
            raise RuntimeError(f"{attr} does not exist in the set of known types")
        
    # iterate through each tuple of the relation
    for tuple in temp.tuples:
        temp_dict = {}
        i = 0

        # iterate through each attribute of the tuples
        for key in tuple.keys():
            attribute = attrlist[i]
            temp_dict[attribute] = tuple[key]
            i += 1

        result.append(temp_dict)

    return pu.Relation(attrlist, result)

def execute_diff(db, obj):
    """function used perform difference

    Args:
        db (database): db to use
        obj (difference): difference query obj

    Raises:
        RuntimeError: if there is a mismatch of attributes

    Returns:
        relation: result relation generated
    """

    # get the relation objects
    temp_1, temp_2 = u.double_relation_finder(db, obj.relvar1, obj.relvar2)
    result = []

    # check both relations have the same attributes
    if set(temp_1.schema) != set(temp_2.schema):
        raise RuntimeError(f"Incompatible schemas")

    # iterate through each tuple
    for tuple in temp_1.tuples:

        # remove tuples in intersection
        if tuple not in temp_2.tuples:
            result.append(dict(tuple))

    return pu.Relation(temp_1.schema, result)

def execute_union(db, obj):
    """function used perform union

    Args:
        db (database): db to use
        obj (union): union query obj

    Raises:
        RuntimeError: if there is a mismatch of attributes

    Returns:
        relation: result relation generated
    """

    # get the relation objects
    temp_1, temp_2 = u.double_relation_finder(db, obj.relvar1, obj.relvar2)
    result = []

    # check both relations have the same attributes
    if set(temp_1.schema) != set(temp_2.schema):
        raise RuntimeError(f"Incompatible schemas")

    result = list(temp_1.tuples)

    # iterate through each tuple
    for tuple in temp_2.tuples:

        # append if not in original
        if tuple not in result:
            result.append(u.reorder_tuple(temp_1.schema, tuple))    

    return pu.Relation(temp_1.schema, result)

def execute_join(db, obj):
    """function used to perform join

    Args:
        db (database): db to use
        obj (join): join query obj

    Returns:
        relation: result relation generated
    """

    # get the relation objects
    temp_1, temp_2 = u.double_relation_finder(db, obj.relvar1, obj.relvar2)
    result = []

    shared_keys = []
    found = False

    # check if there are any matching attributes
    for key in temp_1.schema:
        if key in temp_2.schema:
            found = True
            shared_keys.append(key)
    
    # if no attributes in common perform cartesian product
    if found == False:

        for tuple1 in temp_1.tuples:
            for tuple2 in temp_2.tuples:
                temp_dict = dict(tuple1)
                temp_dict.update(tuple2)
                result.append(temp_dict)
    
    # otherwise perform join on common attributes
    else:

        # iterate through each tuple in the relations
        for tuple1 in temp_1.tuples: 

            for tuple2 in temp_2.tuples:

                # check if all common attrs match
                satisfied = True

                for attr in shared_keys:

                    if tuple2[attr] != tuple1[attr]:
                        satisfied = False
                        break
                
                # if we have full match create the joined tuple
                if satisfied:

                    temp_tuple = dict(tuple1)

                    # add the new attributes
                    for key in tuple2.keys():
                        if key not in tuple1.keys():
                            temp_tuple[key] = tuple2[key]

                    # do not allow duplicates
                    if temp_tuple not in result:
                        result.append(temp_tuple)

    # create the updated schema
    new_schema = list(temp_1.schema)

    for key in temp_2.schema:
        if key not in temp_1.schema:
            new_schema.append(key)

    return pu.Relation(new_schema, result)