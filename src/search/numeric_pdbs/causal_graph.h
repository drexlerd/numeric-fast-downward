#ifndef NUMERIC_PDBS_CAUSAL_GRAPH
#define NUMERIC_PDBS_CAUSAL_GRAPH

/*
  TODO: Perform some memory profiling on this class.

  This implementation precomputes some information (in particular the
  "predecessor" and "successor" information) that could also be
  computed on the fly. Is this a good time/memory tradeoff? We usually
  expect causal graphs to be rather small, but we have some planning
  tasks with huge numbers of variables.

  In the other direction, it might also be useful to have even more
  causal graph variants directly available, e.g. a "get_neighbors"
  method that is the union of pre->eff, eff->pre and eff->eff arcs.
  Before doing this, we should check that they are useful somewhere
  and do the memory profiling.
*/


/*
  An IntRelation represents a relation on a set {0, ..., K - 1} as an
  adjacency list, encoded as a vector<vector<int> >. For example, the
  relation { (0, 1), (0, 3), (1, 3), (3, 0), (3, 1), (3, 2) } over the
  set {0, 1, 3, 4} would be represented as

  [
    [1, 3],       # representing (0, 1), (0, 3)
    [3],          # representing (1, 3)
    [],           # there are no pairs of the form (2, v)
    [0, 1, 2],    # representing (3, 0), (3, 1), (3, 2)
    []            # there are no pairs of the form (4, v)
  ]

  The number K is called the range of the relation.

  The individual lists are guaranteed to be sorted and free of
  duplicates.

  TODO: IntRelations, along with the efficient way of constructing
  them in causal_graph.cc, could be useful for other parts of the
  planner, too. If this is the case, they should be moved to a
  different source file.

  TODO: IntRelations currently only work for relations on {0, ..., K -
  1}^2. They could easily be generalized to relations on {0, ..., K -
  1 } x S for arbitrary sets S. Our current code only requires that S
  is hashable and sortable, and we have one assertion that checks that
  S = {0, ..., K - 1}. This could easily be changed if such a
  generalization is useful anywhere in the code.
*/

#include "numeric_helper.h"

#include <vector>

namespace numeric_pdbs {
typedef std::vector<std::vector<int>> IntRelation;
class CausalGraph {
    std::vector<int> prop_var_id_to_glob_var_id;
    std::vector<int> num_var_id_to_glob_var_id;
    std::vector<int> glob_var_id_to_var_id;
    int first_num_var_index;

    IntRelation pre_to_eff;
    IntRelation eff_to_pre;
    IntRelation eff_to_eff;

    IntRelation successors;
    IntRelation predecessors;

    void dump(const numeric_pdb_helper::NumericTaskProxy &task_proxy) const;

public:
    /* Use the factory function get_causal_graph to create causal graphs
       to avoid creating more than one causal graph per AbstractTask. */
    explicit CausalGraph(const numeric_pdb_helper::NumericTaskProxy &num_task);

    /*
      All below methods querying neighbors (of some sort or other) of
      var guarantee that:
      - the return vertex list is sorted
      - var itself is not in the returned list

      "Successors" and "predecessors" are w.r.t. the common definition
      of causal graphs, which have pre->eff and eff->eff arcs.

      Note that axioms are treated as operators in the causal graph,
      i.e., their condition variables are treated as precondition
      variables and the derived variable is treated as an effect
      variable.

      For effect conditions, we only add pre->eff arcs for the respective
      conditional effect.
    */

    const std::vector<int> &get_pre_to_eff(int var) const {
        std::cerr << "ERROR: not implemented in numeric CG" << std::endl;
        utils::exit_with(utils::ExitCode::CRITICAL_ERROR);
        return pre_to_eff[var];
    }

    std::vector<int> get_prop_eff_to_prop_pre(int prop_var) const;

    std::vector<int> get_prop_eff_to_num_pre(int prop_var) const;

    std::vector<int> get_num_eff_to_prop_pre(int num_var) const;

    std::vector<int> get_num_eff_to_num_pre(int num_var) const;

    std::vector<int> get_num_eff_to_num_eff(int num_var) const;

    std::vector<int> get_prop_predecessors_of_prop_var(int prop_var) const;

    std::vector<int> get_prop_predecessors_of_num_var(int num_var) const;

    std::vector<int> get_num_predecessors_of_prop_var(int prop_var) const;

    std::vector<int> get_num_predecessors_of_num_var(int num_var) const;

    void to_dot(const numeric_pdb_helper::NumericTaskProxy &task_proxy, const std::string &file_name) const;
};
}
/* Create or retrieve a causal graph from cache. If causal graphs are created
   with this function, we build at most one causal graph per AbstractTask. */
extern const numeric_pdbs::CausalGraph &get_numeric_causal_graph(
        const numeric_pdb_helper::NumericTaskProxy *num_proxy);

#endif
