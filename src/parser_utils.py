
class Domain:
    """
    This class is used to represent a domain object extracted 
    during parsing

    it has name and type
    """

    def __init__(self, name, type):
        self.name = name
        self.type = type 
    
    def __repr__(self):
        return f"Domain ({self.name} is {self.type})"

class Type:
    """
    This class is used to represent a type object extracted 
    during parsing

    it has an attribute and a domain
    """

    def __init__(self, attribute, domain):
        self.attribute = attribute
        self.domain = domain
    
    def __repr__(self):
        return f"Type ({self.attribute} as {self.domain})"

class Schema:
    """
    This class is used to represent a schema object extracted 
    during parsing

    it has name and a list of attributes
    """

    def __init__(self, name, attrlist):
        self.name = name
        self.attrlist = attrlist
    
    def __eq__(self, other):
        if not isinstance(other, Schema):
            return False

        compare = set(self.attrlist) == set(other.attrlist)
        return compare
    
    def __repr__(self):
        return f"Schema for relation ({self.name} with attributes {self.attrlist})"

class FunctionalDep:
    """
    This class is used to represent a functional dependency object extracted 
    during parsing

    it has relvar, determinants and a dependents
    """

    def __init__(self, relvar, determinants, dependents):
        self.relvar = relvar
        self.determinants = determinants
        self.dependents = dependents
    
    def __repr__(self):
        return f"FD on {self.relvar} ({self.determinants} -> {self.dependents})"

class Load:
    """
    This class is used to represent a load object extracted 
    during parsing

    it has file path and relation name
    """

    def __init__(self, path, relvar):
        self.path = path
        self.relvar = relvar
    
    def __repr__(self):
        return f"Load ({self.path} into {self.relvar})"

class Let:
    """
    This class is used to represent a let query object extracted 
    during parsing

    it has a variable and a query
    """

    def __init__(self, relvar, query):
        self.relvar = relvar
        self.query = query
    
    def __repr__(self):
        return f"Let ({self.relvar} be {self.query})"

class Predicate:
    """
    This class is used to represent a predicate object extracted 
    during parsing

    it has a left var, operator, right var
    """

    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right
    
    def __eq__(self, other):
        if not isinstance(other, Predicate):
            return False

        compare = self.left == other.left and self.operator == other.operator and self.right == other.right
        return compare
    
    def __repr__(self):
        return f"Predicate ({self.left} {self.operator} {self.right})"

class Select:
    """
    This class is used to represent a select query object extracted 
    during parsing

    it has relvar and predicate
    """

    def __init__(self, relvar, predicate):
        self.relvar = relvar
        self.predicate = predicate
    
    def __eq__(self, other):
        if not isinstance(other, Select):
            return False

        compare = self.relvar == other.relvar and self.predicate == other.predicate
        return compare
    
    def __repr__(self):
        return f"Select ({self.relvar} where {self.predicate})"

class Project:
    """
    This class is used to represent a project query object extracted 
    during parsing

    it has relvar and list of attributes
    """

    def __init__(self, relvar, attrlist):
        self.relvar = relvar
        self.attrlist = attrlist
    
    def __eq__(self, other):
        if not isinstance(other, Project):
            return False

        compare = self.relvar == other.relvar and self.attrlist == other.attrlist
        return compare
    
    def __repr__(self):
        return f"Project ({self.relvar} on {self.attrlist})"

class Union:
    """
    This class is used to represent a union query object extracted 
    during parsing

    it has two relvars
    """

    def __init__(self, relvar1, relvar2):
        self.relvar1 = relvar1
        self.relvar2 = relvar2
    
    def __eq__(self, other):
        if not isinstance(other, Union):
            return False

        compare = self.relvar1 == other.relvar1 and self.relvar2 == other.relvar2
        return compare
    
    def __repr__(self):
        return f"Union ({self.relvar1} and {self.relvar2})"

class Difference:
    """
    This class is used to represent a difference query object extracted 
    during parsing

    it has two relvars
    """

    def __init__(self, relvar1, relvar2):
        self.relvar1 = relvar1
        self.relvar2 = relvar2
    
    def __eq__(self, other):
        if not isinstance(other, Difference):
            return False

        compare = self.relvar1 == other.relvar1 and self.relvar2 == other.relvar2
        return compare
    
    def __repr__(self):
        return f"Difference ({self.relvar1} and {self.relvar2})"

class Join:
    """
    This class is used to represent a join query object extracted 
    during parsing

    it has two relvars
    """

    def __init__(self, relvar1, relvar2):
        self.relvar1 = relvar1
        self.relvar2 = relvar2
    
    def __eq__(self, other):
        if not isinstance(other, Join):
            return False

        compare = self.relvar1 == other.relvar1 and self.relvar2 == other.relvar2
        return compare
    
    def __repr__(self):
        return f"Join ({self.relvar1} and {self.relvar2})"

class Rename:
    """
    This class is used to represent a rename query object extracted 
    during parsing

    it has relvar and list of attributes
    """

    def __init__(self, relvar, attrlist):
        self.relvar = relvar
        self.attrlist = attrlist
    
    def __eq__(self, other):
        if not isinstance(other, Rename):
            return False

        compare = self.relvar == other.relvar and self.attrlist == other.attrlist
        return compare
    
    def __repr__(self):
        return f"Rename ({self.relvar} on {self.attrlist})"
    
class Database:
    """class to represent a database object
    """

    def __init__(self):

        # dict: name -> type
        self.domains = {}

        # dict: attribute -> domain
        self.types = {}

        # dict: name -> attrlist
        self.relations = {}

        # dict: name -> [FD]
        self.fds = {}

        # dict: name -> [[first fd], [], ...]
        self.loaded_fds = {}

        # [load]
        self.loads = []

        # dict: name -> query
        self.vars = {}

        # dict: name -> relation
        self.loaded_relations = {}

        # [queries]
        self.queries = []

        # [results]
        self.query_results = []

class Relation:
    """
    This class is used to represent a relation with schema and tuples 
    """

    def __init__(self, schema, tuples):
        self.schema = schema
        self.tuples = tuples
    
    def __repr__(self):
        return f"Relation ({self.schema} with tuples {self.tuples})"
    
    def __eq__(self, other):
        if not isinstance(other, Relation):
            return False

        compare = self.schema == other.schema and len(self.tuples) == len(other.tuples)
        if compare == False:
            return False
        
        for i in range(len(self.tuples)):
            if self.tuples[i] not in other.tuples:
                return False
            
        return True