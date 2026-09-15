import parser_utils as pu
import utils as u
import cost_processor as cp
import copy

def print_optimised_query(db):
    """function used to print the opt process

    Args:
        db (database): db to use
    """

    # copy the last query 
    obj = copy.deepcopy(db.queries[-1])

    # flatten the query
    obj = u.query_flattener(db, obj)

    # check for valid structure
    u.check_structure(db, copy.deepcopy(obj));

    print("")
    print("--------------------")
    print("Flattened last query:")
    print(obj)
    print("--------------------")
    print("")
    
    # run the optimisation algo
    obj = full_optimisation(db, obj)

    print("--------------------")
    print("Final optimised query:")
    print(obj)
    print("--------------------")
    print("")

def opt_generator(db, obj, rejected_opts):
    """recursive function used to simplify every query

    Args:
        db (database): db to use
        obj (query): any query obj
        rejected_opts (list): list of rejected operations

    Returns:
        obj: the intermediate optimised query obj
        bool: if obj was changed
        tracker: tuple to track latest change and possibly reject it
    """

    # simplify the child queries
    if hasattr(obj, "relvar"):
        changed_obj, modified, tracker = opt_generator(db, obj.relvar, rejected_opts)
        if modified:
            obj.relvar = changed_obj
            return obj, True, tracker
    
    if hasattr(obj, "relvar1"):
        changed_obj, modified, tracker = opt_generator(db, obj.relvar1, rejected_opts)
        if modified:
            obj.relvar1 = changed_obj
            return obj, True, tracker
    
    if hasattr(obj, "relvar2"):
        changed_obj, modified, tracker = opt_generator(db, obj.relvar2, rejected_opts)
        if modified:
            obj.relvar2 = changed_obj
            return obj, True, tracker

    # perform unary optimisations
    opt_obj = unary_simplification(db, obj)
    if opt_obj:
        tracker = (str(obj), str(opt_obj))
        if tracker not in rejected_opts:
            return opt_obj, True, tracker
        else:
            print("Rejected previously computed optimisation")

    # try to perform selection pushdown
    opt_obj = selection_pushdown(db, obj)
    if opt_obj:
        tracker = (str(obj), str(opt_obj))
        if tracker not in rejected_opts:
            return opt_obj, True, tracker
        else:
            print("Rejected previously computed optimisation")

    # try to perform projection pushdown
    opt_obj = projection_pushdown(db, obj)
    if opt_obj:
        tracker = (str(obj), str(opt_obj))
        if tracker not in rejected_opts:
            return opt_obj, True, tracker
        else:
            print("Rejected previously computed optimisation")

    # no opt can be done
    return obj, False, None

def full_optimisation(db, obj):
    """function used to perform full optimisation on a query

    Args:
        db (database): db to use
        obj (query): any query obj

    Returns:
        obj: optimised query obj
    """

    counter = 0

    # keep track of rejected opts
    rejected_opts = []

    # keep on running until no more optimisations can be done
    while True:

        counter += 1
        
        obj_original = copy.deepcopy(obj)
        cost_original = cp.total_cost_calc(db, obj_original)

        opt_obj, modified, tracker = opt_generator(db, obj, rejected_opts)
        cost_optimised = cp.total_cost_calc(db, opt_obj)

        print("Previous query:  |", obj_original, "| cost:", cost_original)
        print("Generated query: |", opt_obj, "| cost:", cost_optimised)

        # check if there is no change
        if modified == False:
            print("---> No more optimisations available")
            print("")
            break

        # check if there is no cost improvement
        elif cost_optimised < cost_original:
            obj = opt_obj
            print("---> Change accepted")
            print("")
            print(f"----- Intermediate step {counter}:")
            print(obj)
            print("")
            rejected_opts.clear()

        else:
            obj = obj_original
            print("---> Change rejected")
            print("")
            rejected_opts.append(tracker)

    return obj

def selection_pushdown(db, obj):
    """function used to perform selection push down 

    Args:
        db (database): db to use
        obj (query object): query object

    Returns:
        obj: the optimised query obj
    """

    if not isinstance(obj, pu.Select):
        return None

    # try to swap selections if it reduces cost
    if isinstance(obj.relvar, pu.Select):

        inside_select_obj = obj.relvar
        out_predicate = obj.predicate
        in_predicate = inside_select_obj.predicate

        print("Applied: selection push down")
        print("Optimised using formula: σθ1(σθ2(r)) ≡ σθ2(σθ1(r))")
        return pu.Select(pu.Select(inside_select_obj.relvar, out_predicate), in_predicate)
    
    # push selection inside projection
    elif isinstance(obj.relvar, pu.Project):

        project_obj = obj.relvar
        new_select = pu.Select(project_obj.relvar, obj.predicate)

        print("Applied: selection push down")
        print("Optimised using formula: σθ(πA(r)) ≡ πA(σθ(r))")
        return pu.Project(new_select, project_obj.attrlist)
    
    # push selection inside union
    elif isinstance(obj.relvar, pu.Union):

        union_obj = obj.relvar
        new_select1 = pu.Select(union_obj.relvar1, obj.predicate)
        new_select2 = pu.Select(union_obj.relvar2, obj.predicate)

        print("Applied: selection push down")
        print("Optimised using formula: σθ(r ∪ s) ≡ σθ(r) ∪ σθ(s)")
        return pu.Union(new_select1, new_select2)

    # push selection inside difference
    elif isinstance(obj.relvar, pu.Difference):

        diff_obj = obj.relvar
        new_select1 = pu.Select(diff_obj.relvar1, obj.predicate)
        new_select2 = pu.Select(diff_obj.relvar2, obj.predicate)

        print("Applied: selection push down")
        print("Optimised using formula: σθ(r − s) ≡ σθ(r) − σθ(s)")
        return pu.Difference(new_select1, new_select2)
    
    # push selection inside rename
    elif isinstance(obj.relvar, pu.Rename):

        rename_obj = obj.relvar
        left = obj.predicate.left

        original_schema = u.single_relation_finder(db, rename_obj.relvar).schema
        
        index = 0

        # get the updated attribute name
        for attr in rename_obj.attrlist:
            if attr == left:
                break
            index += 1

        left = original_schema[index]
        right = obj.predicate.right
        index = 0

        # get the updated right if needed
        if isinstance(right, str) and right[0] != '"':
            for temp in rename_obj.attrlist:
                if temp == right:
                    break
                index += 1
            right = original_schema[index]

        new_select = pu.Select(rename_obj.relvar, pu.Predicate(left, obj.predicate.operator, right))

        print("Applied: selection push down")
        print("Optimised using formula: σθ(ρa(r)) ≡ ρa(σθ′(r))")
        return pu.Rename(new_select, rename_obj.attrlist)
    
    # push selection inside join
    elif isinstance(obj.relvar, pu.Join):
        join_obj = obj.relvar
        predicate = obj.predicate

        new_select1 = join_obj.relvar1
        new_select2 = join_obj.relvar2

        temp_1, temp_2 = u.double_relation_finder(db, join_obj.relvar1, join_obj.relvar2)
        
        # check for joined selection
        if predicate.left in temp_1.schema and predicate.right in temp_2.schema or predicate.right in temp_1.schema and predicate.left in temp_2.schema:
            return None
        
        # find individual selection
        if predicate.left in temp_1.schema:
            new_select1 = pu.Select(join_obj.relvar1, obj.predicate)
        
        # find individual selection
        if predicate.left in temp_2.schema:
            new_select2 = pu.Select(join_obj.relvar2, obj.predicate)

        print("Applied: selection push down")
        print("Optimised using formula: σθ1∧θ2∧θ3(r ▷◁ s) ≡ σθ1(σθ2(r) ▷◁ σθ3(s))")
        return pu.Join(new_select1, new_select2)

    return None

def projection_pushdown(db, obj):
    """function used to perform projection push down 

    Args:
        db (database): db to use
        obj (query object): query object

    Returns:
        obj: the optimised query obj
    """

    if not isinstance(obj, pu.Project):
        return None

    # push projection inside union
    if isinstance(obj.relvar, pu.Union):

        union_obj = obj.relvar
        new_project1 = pu.Project(union_obj.relvar1, obj.attrlist)
        new_project2 = pu.Project(union_obj.relvar2, obj.attrlist)

        print("Applied: projection push down")
        print("Optimised using formula: πA(r ∪ s) ≡ πA(r) ∪ πA(s)")

        return pu.Union(new_project1, new_project2)
    
    # push projection inside rename
    elif isinstance(obj.relvar, pu.Rename):
        
        rename_obj = obj.relvar
        attrlist = obj.attrlist
        original_schema = u.single_relation_finder(db, rename_obj.relvar).schema

        new_projectors = []

        # get the updated attribute names
        for attr in attrlist:

            index = 0
            for renamed in rename_obj.attrlist:
                if attr == renamed:
                    new_projectors.append(original_schema[index])
                    break
                index += 1

        new_project = pu.Project(rename_obj.relvar, new_projectors)

        print("Applied: projection push down")
        print("Optimised using formula: πA(ρa(r)) ≡ ρa(πA′ (r))")

        return pu.Rename(new_project, attrlist)
    
    # push projection inside join
    elif isinstance(obj.relvar, pu.Join):

        join_obj = obj.relvar
        temp_1, temp_2 = u.double_relation_finder(db, join_obj.relvar1, join_obj.relvar2)
            
        # perform the algo from the lectures
        alpha = obj.attrlist
        r = temp_1.schema
        s = temp_2.schema
        alpha_s = list(alpha)
        alpha_r = list(alpha)

        for attr in s:
            if attr not in alpha_s:
                alpha_s.append(attr)

        for attr in r:
            if attr not in alpha_r:
                alpha_r.append(attr)
        
        r_prime = []
        for attr in r:
            if attr in alpha_s:
                r_prime.append(attr)
        
        s_prime = []
        for attr in s:
            if attr in alpha_r:
                s_prime.append(attr)

        # terminate if no change and all columns needed
        if r_prime == r and s_prime == s:
            return None

        new_project1 = None
        new_project2 = None

        # avoid empty attrs, dont add redundant node
        if r_prime and r_prime != r:
            new_project1 = pu.Project(join_obj.relvar1, r_prime)
        else:
            new_project1 = join_obj.relvar1
        
        if s_prime and s_prime != s:
            new_project2 = pu.Project(join_obj.relvar2, s_prime)
        else:
            new_project2 = join_obj.relvar2

        new_join = pu.Join(new_project1, new_project2)

        print("Applied: projection push down")
        print("Optimised using formula: πα(r ▷◁ s) ≡ πα(πR′ (r) ▷◁ πS′ (s))")

        return pu.Project(new_join, alpha)

    return None

def unary_simplification(db, obj):
    """function used to perform unary simplifications

    Args:
        db (database): db to use
        obj (obj): query obj

    Returns:
        obj: optimised query object
    """

    # simplify join
    if isinstance(obj, pu.Join):

        if obj.relvar1 == obj.relvar2:

            print("Applied: unary simplification")
            print("Optimised using formula: r ▷◁ r ≡ r")
            return obj.relvar1

    # simplify union
    elif isinstance(obj, pu.Union):

        if obj.relvar1 == obj.relvar2:

            print("Applied: unary simplification")
            print("Optimised using formula: r ∪ r ≡ r")
            return obj.relvar1
    
    # simplify project
    elif isinstance(obj, pu.Project):

        if isinstance(obj.relvar, pu.Project):

            print("Applied: unary simplification")
            print("Optimised using formula: πA1(πA2(r)) ≡ πA1(r)")
            return pu.Project(obj.relvar.relvar, obj.attrlist)

    # simplify rename
    elif isinstance(obj, pu.Rename):

        if isinstance(obj.relvar, pu.Rename):

            print("Applied: unary simplification")
            print("Optimised using formula: ρa1(ρa2(r)) ≡ ρa3(r)")
            return pu.Rename(obj.relvar.relvar, obj.attrlist)

    return None
