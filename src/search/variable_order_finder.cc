#include "variable_order_finder.h"

#include "causal_graph.h"
#include "globals.h"

#include "../numeric_pdbs/numeric_helper.h"

#include "../utils/system.h"

#include <algorithm>
#include <cassert>
#include <cstdlib>
#include <iostream>
#include <vector>

using namespace std;
using utils::ExitCode;


VariableOrderFinder::VariableOrderFinder(const shared_ptr<AbstractTask> task, VariableOrderType variable_order_type, bool is_pdb)
    : task(task),
      task_proxy(*task),
      variable_order_type(variable_order_type), 
      is_pdb(is_pdb) {
    int var_count = task_proxy.get_variables().size();
    if (variable_order_type == REVERSE_LEVEL) {
        for (int i = 0; i < var_count; ++i)
            remaining_vars.push_back(i);
    } else {
        for (int i = var_count - 1; i >= 0; --i)
            remaining_vars.push_back(i);
    }

    if (variable_order_type == CG_GOAL_RANDOM ||
        variable_order_type == RANDOM)
        random_shuffle(remaining_vars.begin(), remaining_vars.end());

    numeric_pdb_helper::NumericTaskProxy num_proxy(task);
    is_causal_predecessor.resize(var_count, false);
    is_goal_variable.resize(var_count, false);
    for (FactProxy goal : num_proxy.get_propositional_goals())
        is_goal_variable[goal.get_variable().get_id()] = true;
}

void VariableOrderFinder::select_next(int position, int var_no) {
    assert(remaining_vars[position] == var_no);
    remaining_vars.erase(remaining_vars.begin() + position);
    selected_vars.push_back(var_no);
    const CausalGraph &cg = task_proxy.get_causal_graph();
    const vector<int> &new_vars = cg.get_eff_to_pre(var_no);
    for (int new_var : new_vars)
        is_causal_predecessor[new_var] = true;
}

bool VariableOrderFinder::done() const {
    return remaining_vars.empty();
}

int VariableOrderFinder::next() {
    assert(!done());
    if (variable_order_type == CG_GOAL_LEVEL || variable_order_type
        == CG_GOAL_RANDOM) {
        // First run: Try to find a causally connected variable.
        for (size_t i = 0; i < remaining_vars.size(); ++i) {
            int var_no = remaining_vars[i];
            if (is_causal_predecessor[var_no]) {
                select_next(i, var_no);
                return var_no;
            }
        }
        // Second run: Try to find a goal variable.
        for (size_t i = 0; i < remaining_vars.size(); ++i) {
            int var_no = remaining_vars[i];
            if (is_goal_variable[var_no]) {
                select_next(i, var_no);
                return var_no;
            }
        }
    } else if (variable_order_type == GOAL_CG_LEVEL) {
        // First run: Try to find a goal variable.
        for (size_t i = 0; i < remaining_vars.size(); ++i) {
            int var_no = remaining_vars[i];
            if (is_goal_variable[var_no]) {
                select_next(i, var_no);
                return var_no;
            }
        }
        // Second run: Try to find a causally connected variable.
        for (size_t i = 0; i < remaining_vars.size(); ++i) {
            int var_no = remaining_vars[i];
            if (is_causal_predecessor[var_no]) {
                select_next(i, var_no);
                return var_no;
            }
        }
    } else if (variable_order_type == RANDOM ||
               variable_order_type == LEVEL ||
               variable_order_type == REVERSE_LEVEL) {
        int var_no = remaining_vars[0];
        select_next(0, var_no);
        return var_no;
    }
    if (is_pdb) {
        return -1; // Avoiding derived variables in PDB, as they are not causaly conneted.
    }
    cerr << "Relevance analysis has not been performed." << endl;
    utils::exit_with(ExitCode::INPUT_ERROR);
}

void VariableOrderFinder::dump() const {
    cout << "Variable order type: ";
    switch (variable_order_type) {
    case CG_GOAL_LEVEL:
        cout << "CG/GOAL, tie breaking on level (main)";
        break;
    case CG_GOAL_RANDOM:
        cout << "CG/GOAL, tie breaking random";
        break;
    case GOAL_CG_LEVEL:
        cout << "GOAL/CG, tie breaking on level";
        break;
    case RANDOM:
        cout << "random";
        break;
    case LEVEL:
        cout << "by level";
        break;
    case REVERSE_LEVEL:
        cout << "by reverse level";
        break;
    default:
        ABORT("Unknown variable order type.");
    }
    cout << endl;
}
