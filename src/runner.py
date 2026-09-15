import parser as p
import parser_utils as pu
import utils as u
import optimiser as o
import query_executor as qe
import os

def execute(path, optimised):
    """function used to execute each line from a given usql file

    Args:
        path (string): it is the path to an usql file to process
        optimised (bool): if we need to optimise the execution
    """

    # parse the file and initialise an empty database
    if not os.path.isfile(path):
        raise RuntimeError(f"The path {path} does not exist or does not point to a file")
    
    # check the file is an usql file
    if not os.path.splitext(path)[-1] == ".usql":
        raise RuntimeError("The path", path, "does not point to usql file")
    
    # parse the text and create a database object
    parsed_text = p.start_parser(path)
    db = pu.Database()

    last_query_let = False

    # get each object from the parsed text
    for obj in parsed_text:

        # add domains to the db
        if isinstance(obj, pu.Domain):
            db.domains[obj.name] = obj.type

        # add types to the db
        elif isinstance(obj, pu.Type):

            # the linked domain must exist
            if obj.domain not in db.domains:
                raise RuntimeError(f"Type: The domain for {obj.attribute} is not in the list of known domains")
            
            db.types[obj.attribute] = obj.domain

        # add relations to the db
        elif isinstance(obj, pu.Schema):

            # check all attributes exist
            for attr in obj.attrlist:
                if attr not in db.types:
                    raise RuntimeError(f"Attribute: {attr} for {obj.name} is not in the list of known types")

            db.relations[obj.name] = obj.attrlist
            
        # add functional dependencies to the db
        elif isinstance(obj, pu.FunctionalDep):

            # check the relation exists
            if obj.relvar not in db.relations:
                raise RuntimeError(f"FD: The relation {obj.relvar} is not in the list of known relations")
            
            # instantiate empty list
            if obj.relvar not in db.fds:
                db.fds[obj.relvar] = []

            # check that the fd does not exist yet
            if obj not in db.fds[obj.relvar]:
                db.fds[obj.relvar].append(obj)

        # add load instructions
        elif isinstance(obj, pu.Load):

            db.loads.append(obj)

            # load the info from a file
            qe.execute_load(db, obj)
        
        # add query instructions to db
        else:

            db.queries.append(obj)

            # check if the query is let
            if isinstance(obj, pu.Let):
                last_query_let = True
            else:
                last_query_let = False
            
            if not optimised:

                # execute the queries and store the results
                res = qe.execute_query(db, obj)

                if last_query_let == False:
                    db.query_results.append(res)
            
            elif isinstance(obj, pu.Let):

                qe.execute_query(db, obj)

    if not optimised:

        # print the result from the last query
        if not last_query_let:
            u.pretty_print(db.query_results[-1])

    else:

        # optimise and print
        o.print_optimised_query(db)
