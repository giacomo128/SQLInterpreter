from lark import Lark, Transformer, Token
import parser_utils as pu

usql_grammar = """
   start:program
   lend: ";"
   dname:  CNAME
   attr:   CNAME
   relvar: CNAME
   path:   ESCAPED_STRING
   
   const: INT | ESCAPED_STRING
   
   attrlist: attr ("," attr)*
   
   program: domain* type* relation* functional_dep* load* query+
   
   gtype: "String" | "Int"
   domain: "DOMAIN" dname "IS" gtype lend
   
   type: "TYPE" attr "AS" dname lend
   
   relation: "RELATION" relvar "WITH" attrlist lend

   functional_dep: "FD" "ON" relvar "WHERE" attrlist "->" attrlist lend
   
   load: "LOAD" path "INTO" relvar lend
   
   operator: "=" | "!="
   
   theta: attr operator attr
         | attr operator const
         
   query: "LET" relvar "BE" query
         | "SELECT" relvar "WHERE" theta lend
         | "PROJECT" relvar "ON" attrlist lend
         | "UNION" relvar "AND" relvar lend
         | "DIFFERENCE" relvar "AND" relvar lend
         | "JOIN" relvar "AND" relvar lend
         | "RENAME" relvar "ON" attrlist lend

   %import common.UCASE_LETTER
   %import common.CNAME
   %import common.WS
   %import common.ESCAPED_STRING
   %import common.INT
   %ignore WS
   """

class USQLTransformer(Transformer):
   """transformer class that returns the objects generated during parsing 

   Args:
      Transformer (transformer): the transformer responsible for returning the objects
   """
   
   def start(self, args):
      return args[0]
   
   def program(self, args):
      return args

   def lend(self, _):
      return None
   
   def dname(self, args):
      return str(args[0])

   def attr(self, args):
      return str(args[0])

   def relvar(self, args):
      return str(args[0])
   
   def ESCAPED_STRING(self, args):
      return str(args).strip()

   def INT(self, args):
      return int(args)

   def path(self, args):
      return args[0]

   def const(self, args):
      return args[0]

   def attrlist(self, args):
      # ignore commas
      return [x for x in args if not isinstance(x, Token)]

   def gtype(self, args):
      return str(args[0])
   
   def operator(self, args):
      return str(args[0])

   def domain(self, args):
      return pu.Domain(args[1], args[3])
   
   def type(self, args):
      return pu.Type(args[1], args[3])
   
   def relation(self, args):
      return pu.Schema(args[1], args[3])
   
   def functional_dep(self, args):
      return pu.FunctionalDep(args[2], args[4], args[6])
   
   def load(self, args):
      return pu.Load(args[1].strip('"'), args[3])
   
   def theta(self, args):
      return pu.Predicate(args[0], args[1], args[2])
   
   def query(self, args):

      # get the correct query operator
      query_op = str(args[0])

      if query_op == "LET":
         return pu.Let(args[1], args[3])
      
      elif query_op == "SELECT":
         return pu.Select(args[1], args[3])
      
      elif query_op == "PROJECT":
         return pu.Project(args[1], args[3])
      
      elif query_op == "UNION":
         return pu.Union(args[1], args[3])
      
      elif query_op == "DIFFERENCE":
         return pu.Difference(args[1], args[3])
      
      elif query_op == "JOIN":
         return pu.Join(args[1], args[3])
      
      elif query_op == "RENAME":
         return pu.Rename(args[1], args[3])

def start_parser(path):
   """function used to parse the text from a usql file

   Args:
      path (string): path to the usql file

   Returns:
      list of parsed objects: list of objects retrieved during parsing
   """

   # use larl for allowing transformers
   l = Lark(usql_grammar, parser = "lalr", keep_all_tokens = True, transformer = USQLTransformer())
   
   # read the file and parse
   with open(path, "r") as f:
      text = l.parse(f.read())
   return text
