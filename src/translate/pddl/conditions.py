

#from . import pddl_types
from . import f_expression # NFD

DEBUG = False

# Conditions (of any type) are immutable, because they need to
# be hashed occasionally. Immutability also allows more efficient comparison
# based on a precomputed hash value.
#
# Careful: Most other classes (e.g. Effects, Axioms, Actions) are not!

class Condition:
    def __init__(self, parts):
        self.parts = tuple(parts)
        self.hash = hash((self.__class__, self.parts))
        if DEBUG: print("Initialized %s Condition with the following %d parts:" % (self.__class__,len(parts)))
        if DEBUG: 
            for p in parts:
                print (p)
    def __hash__(self):
        return self.hash
    def __ne__(self, other):
        return not self == other
    def __lt__(self, other):
        return self.hash < other.hash
    def __le__(self, other):
        return self.hash <= other.hash
    def __repr__(self, *args, **kwargs):
        return "Condition %s" % [str(p) for p in self.parts]
    def dump(self, indent="  "):
        print("%s%s" % (indent, self._dump()))
        for part in self.parts:
            part.dump(indent + "  ")
    def _dump(self):
        return self.__class__.__name__
    def _postorder_visit(self, method_name, *args):
        part_results = [part._postorder_visit(method_name, *args)
                        for part in self.parts]
        method = getattr(self, method_name, self._propagate)
        return method(part_results, *args)
    def _propagate(self, parts, *args):
        return self.change_parts(parts)
    def simplified(self):
        return self._postorder_visit("_simplified")
    def relaxed(self):
        return self._postorder_visit("_relaxed")
    def untyped(self):
        return self._postorder_visit("_untyped")

    def uniquify_variables(self, type_map, renamings={}):
        # Cannot used _postorder_visit because this requires preorder
        # for quantified effects.
        if not self.parts:
            return self
        else:
            return self.__class__([part.uniquify_variables(type_map, renamings)
                                   for part in self.parts])
    def to_untyped_strips(self):
        raise ValueError("Not a STRIPS condition: %s" % self.__class__.__name__)
    def instantiate(self, var_mapping, init_facts, fluent_facts, init_function_vals,
                    fluent_functions, task, new_axiom, new_modules, result):
        raise ValueError("Cannot instantiate condition: not normalized")   
    def free_variables(self):
        result = set()
        for part in self.parts:
            result |= part.free_variables()
        return result
    def has_disjunction(self):
        for part in self.parts:
            if part.has_disjunction():
                return True
        return False
    def has_existential_part(self):
        for part in self.parts:
            if part.has_existential_part():
                return True
        return False
    def has_universal_part(self):
        for part in self.parts:
            if part.has_universal_part():
                return True
        return False

class ConstantCondition(Condition):
    # Defining __eq__ blocks inheritance of __hash__, so must set it explicitly.
    __hash__ = Condition.__hash__
    parts = ()
    def __init__(self):
        self.hash = hash(self.__class__)
    def change_parts(self, parts):
        return self
    def __eq__(self, other):
        return self.__class__ is other.__class__

class Impossible(Exception):
    pass

class Falsity(ConstantCondition):
    def instantiate(self, var_mapping, init_facts, fluent_facts, init_function_vals,
                    fluent_functions, task, new_axiom, new_modules, result):
        raise Impossible()
    def negate(self):
        return Truth()

class Truth(ConstantCondition):
    def to_untyped_strips(self):
        return []
    def instantiate(self, var_mapping, init_facts, fluent_facts, init_function_vals,
                    fluent_functions, task, new_axiom, new_modules, result):        
        pass
    def negate(self):
        return Falsity()

class JunctorCondition(Condition):
    # Defining __eq__ blocks inheritance of __hash__, so must set it explicitly.
    __hash__ = Condition.__hash__
    def __eq__(self, other):
        # Compare hash first for speed reasons.
        return (self.hash == other.hash and
                self.__class__ is other.__class__ and
                self.parts == other.parts)
    def change_parts(self, parts):
        return self.__class__(parts)

class Conjunction(JunctorCondition):
    def _simplified(self, parts):
        result_parts = []
        for part in parts:
            if isinstance(part, Conjunction):
                result_parts += part.parts
            elif isinstance(part, Falsity):
                return Falsity()
            elif not isinstance(part, Truth):
                result_parts.append(part)
        if not result_parts:
            return Truth()
        if len(result_parts) == 1:
            return result_parts[0]
        return Conjunction(result_parts)
    def to_untyped_strips(self):
        result = []
        for part in self.parts:
            result += part.to_untyped_strips()
        return result
    def instantiate(self, var_mapping, init_facts, fluent_facts, init_function_vals,
                    fluent_functions, task, new_axiom, new_modules, result):                       
        assert not result, "Condition not simplified"
        for part in self.parts:
            part.instantiate(var_mapping, init_facts, fluent_facts, init_function_vals,
                    fluent_functions, task, new_axiom, new_modules, result)
    def negate(self):
        return Disjunction([p.negate() for p in self.parts])

class Disjunction(JunctorCondition):
    def _simplified(self, parts):
        result_parts = []
        for part in parts:
            if isinstance(part, Disjunction):
                result_parts += part.parts
            elif isinstance(part, Truth):
                return Truth()
            elif not isinstance(part, Falsity):
                result_parts.append(part)
        if not result_parts:
            return Falsity()
        if len(result_parts) == 1:
            return result_parts[0]
        return Disjunction(result_parts)
    def negate(self):
        return Conjunction([p.negate() for p in self.parts])
    def has_disjunction(self):
        return True

class QuantifiedCondition(Condition):
    # Defining __eq__ blocks inheritance of __hash__, so must set it explicitly.
    __hash__ = Condition.__hash__
    def __init__(self, parameters, parts):
        self.parameters = tuple(parameters)
        self.parts = tuple(parts)
        self.hash = hash((self.__class__, self.parameters, self.parts))
    def __eq__(self, other):
        # Compare hash first for speed reasons.
        return (self.hash == other.hash and
                self.__class__ is other.__class__ and
                self.parameters == other.parameters and
                self.parts == other.parts)
    def _dump(self, indent="  "):
        arglist = ", ".join(map(str, self.parameters))
        return "%s %s" % (self.__class__.__name__, arglist)
    def _simplified(self, parts):
        if isinstance(parts[0], ConstantCondition):
            return parts[0]
        else:
            return self._propagate(parts)

    def uniquify_variables(self, type_map, renamings={}):
        renamings = dict(renamings) # Create a copy.
        new_parameters = [par.uniquify_name(type_map, renamings)
                          for par in self.parameters]
        new_parts = (self.parts[0].uniquify_variables(type_map, renamings),)
        return self.__class__(new_parameters, new_parts)

    def free_variables(self):
        result = Condition.free_variables(self)
        for par in self.parameters:
            result.discard(par.name)
        return result
    def change_parts(self, parts):
        return self.__class__(self.parameters, parts)

class UniversalCondition(QuantifiedCondition):
    def _untyped(self, parts):
        type_literals = [par.get_atom().negate() for par in self.parameters]
        return UniversalCondition(self.parameters,
                                  [Disjunction(type_literals + parts)])
    def negate(self):
        return ExistentialCondition(self.parameters, [p.negate() for p in self.parts])
    def has_universal_part(self):
        return True

class ExistentialCondition(QuantifiedCondition):
    def _untyped(self, parts):
        type_literals = [par.get_atom() for par in self.parameters]
        return ExistentialCondition(self.parameters,
                                    [Conjunction(type_literals + parts)])
    def negate(self):
        return UniversalCondition(self.parameters, [p.negate() for p in self.parts])
    def instantiate(self, var_mapping, init_facts, fluent_facts, init_function_vals,
                    fluent_functions, task, new_axiom, new_modules, result):
        assert not result, "ExistentialCondition not simplified"
        self.parts[0].instantiate(var_mapping, init_facts, fluent_facts, init_function_vals,
                                  fluent_functions, task, new_axiom, new_modules, result)
    def has_existential_part(self):
        return True

class Literal(Condition):
    # Defining __eq__ blocks inheritance of __hash__, so must set it explicitly.
    __hash__ = Condition.__hash__
    parts = []
    def __init__(self, predicate, args):
        self.predicate = predicate
        self.args = tuple(args)
        self.hash = hash((self.__class__, self.predicate, self.args))
    def __eq__(self, other):
        # Compare hash first for speed reasons.
        return (self.hash == other.hash and
                self.__class__ is other.__class__ and
                self.predicate == other.predicate and
                self.args == other.args)
    def __ne__(self, other):
        return not self == other
    @property
    def key(self):
        return str(self.predicate), self.args
    ## NFD: sort by hash value (__lt__ and __le__ methods of Condition instead don't know if this might have unintended implications) 
#    def __lt__(self, other):    
#        return self.key < other.key
#    def __le__(self, other):
#        return self.key <= other.key
    def __str__(self):
        return "%s %s(%s)" % (self.__class__.__name__, self.predicate,
                              ", ".join(map(str, self.args)))
    def __repr__(self):
        return '<%s>' % self
    def _dump(self):
        return str(self)
    def change_parts(self, parts):
        return self
    def uniquify_variables(self, type_map, renamings={}):
        return self.rename_variables(renamings)
    def rename_variables(self, renamings):
        new_args = tuple(renamings.get(arg, arg) for arg in self.args)
        return self.__class__(self.predicate, new_args)
    def replace_argument(self, position, new_arg):
        new_args = list(self.args)
        new_args[position] = new_arg
        return self.__class__(self.predicate, new_args)
    def free_variables(self):
        return set(arg for arg in self.args if arg[0] == "?")

class Atom(Literal):
    negated = False
    def to_untyped_strips(self):
        return [self]    
    def instantiate(self, var_mapping, init_facts, fluent_facts, init_function_vals,
                    fluent_functions, task, new_axiom, new_modules, result):
        args = [var_mapping.get(arg, arg) for arg in self.args]
        atom = Atom(self.predicate, args)
        if atom in fluent_facts:
            result.append(atom)
        elif atom not in init_facts:
            raise Impossible()
    def negate(self):
        return NegatedAtom(self.predicate, self.args)
    def positive(self):
        return self

class NegatedAtom(Literal):
    negated = True
    def _relaxed(self, parts):
        return Truth()
    def instantiate(self, var_mapping, init_facts, fluent_facts, init_function_vals,
                    fluent_functions, task, new_axiom, new_modules, result):
        args = [var_mapping.get(arg, arg) for arg in self.args]
        atom = Atom(self.predicate, args)
        if atom in fluent_facts:
            result.append(NegatedAtom(self.predicate, args))
        elif atom in init_facts:
            raise Impossible()
    def negate(self):
        return Atom(self.predicate, self.args)
    positive = negate
    
class FunctionComparison(Condition): # NFD class yielding the truth value of a function comparison
    negated = False
    def _relaxed(self, parts):
        return Truth()
    def __init__(self, comparator, parts, compare_to_zero = False):
        self.comparator = comparator
        assert len(parts) == 2
        if compare_to_zero:
            self.parts = (f_expression.Difference(parts), f_expression.NumericConstant(0.0))
        else:
            self.parts = tuple(parts)
        self.hash = hash((self.__class__, self.comparator, self.parts))
    def _dump(self, indent="  "):
        return "%s %s" % (self.__class__.__name__, self.comparator)
    def __eq__(self, other):
        # Compare hash first for speed reasons.
        return (self.hash == other.hash and
                self.__class__ == other.__class__ and
                self.comparator == other.comparator and
                self.parts == other.parts)
    def __hash__(self):
        return self.hash
    def __str__(self):
        return "%s (%s %s)" % (self.__class__.__name__, self.comparator,
                              ", ".join(map(str, self.parts)))
    def __repr__(self, *args, **kwargs):
        return self.__str__
    def uniquify_variables(self, type_map, renamings={}):
        return self.__class__(self.comparator,[part.rename_variables(renamings)
                                   for part in self.parts])
    def has_disjunction(self):
        return False
    def has_universal_part(self):
        return False
    def has_existential_part(self):
        return False
    def negate(self):
        return NegatedFunctionComparison(self.comparator, self.parts)
    def change_parts(self, parts):
        return self.__class__(self.comparator,parts)
    def primitive_numeric_expressions(self):
        result = set()
        for part in self.parts:
            result |= part.primitive_numeric_expressions()           
        return result
    def instantiate(self, var_mapping, init_facts, fluent_facts, init_function_vals,
                    fluent_functions, task, new_axiom, new_modules, result):
        instantiated_parts = [part.instantiate(var_mapping, fluent_functions, 
                                               init_function_vals, task, new_axiom) 
                                               for part in self.parts]
        # future work: eliminate non-fluent functions
        result.append(self.__class__(self.comparator,instantiated_parts))
    def positive(self):
        return self
        
    
class NegatedFunctionComparison(FunctionComparison): # NFD
    negated = True
    def negate(self):
        return FunctionComparison(self.comparator, self.parts)
    positive = negate
