#include "task_tools.h"

#include "../utils/system.h"

#include <iostream>

using namespace std;
using utils::ExitCode;


bool is_unit_cost(TaskProxy task) {
    for (OperatorProxy op : task.get_operators()) {
        if (op.get_cost() != 1)
            return false;
    }
    return true;
}

bool has_axioms(TaskProxy task) {
    return !task.get_axioms().empty();
}

void verify_no_axioms(TaskProxy task) {
    if (has_axioms(task)) {
        cerr << "This configuration does not support axioms!"
             << endl << "Terminating." << endl;
        utils::exit_with(ExitCode::UNSUPPORTED);
    }
}

void verify_no_non_numeric_axioms(TaskProxy task) {
    if (has_axioms(task)) {
        if (task.get_axioms().size() > 2) {
            cerr << "This configuration does not support non-numeric axioms, "
                 << "but there are " << task.get_axioms().size() << " axioms. " << endl
                 << "Terminating." << endl;
            utils::exit_with(utils::ExitCode::UNSUPPORTED);
        }
        // reconstruct regular numeric goals
        for (auto axiom : task.get_axioms()) {
            if (!axiom.get_preconditions().empty() && axiom.get_effects().size() > 1){
                cerr << "This configuration does not support non-numeric axioms."
                     << "Axiom " << axiom.get_name() << " does not look like a numeric goal axiom. " << endl
                     << "Terminating." << endl;
                utils::exit_with(utils::ExitCode::UNSUPPORTED);
            }
        }
    }
}

static int get_first_conditional_effects_op_id(TaskProxy task) {
    for (OperatorProxy op : task.get_operators()) {
        for (EffectProxy effect : op.get_effects()) {
            if (!effect.get_conditions().empty())
                return op.get_id();
        }
    }
    return -1;
}

bool has_conditional_effects(TaskProxy task) {
    return get_first_conditional_effects_op_id(task) != -1;
}

void verify_no_conditional_effects(TaskProxy task) {
    int op_id = get_first_conditional_effects_op_id(task);
    if (op_id != -1) {
        OperatorProxy op = task.get_operators()[op_id];
        cerr << "This configuration does not support conditional effects "
             << "(operator " << op.get_name() << ")!" << endl
             << "Terminating." << endl;
        utils::exit_with(ExitCode::UNSUPPORTED);
    }
}

ap_float get_average_operator_cost(TaskProxy task_proxy) {
    double average_operator_cost = 0;
    for (OperatorProxy op : task_proxy.get_operators()) {
        average_operator_cost += op.get_cost();
    }
    average_operator_cost /= task_proxy.get_operators().size();
    return average_operator_cost;
}
