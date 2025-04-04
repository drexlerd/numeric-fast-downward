#include "numeric_task_proxy.h"

#include "numeric_helper.h"

using namespace std;

namespace numeric_pdb_helper {
const std::string &ResNumericVariableProxy::get_name() const {
    return task->get_numeric_variable_name(var_id);
}

numType ResNumericVariableProxy::get_var_type() const {
    return task->get_numeric_var_type(var_id);
}

ap_float ResNumericVariableProxy::get_initial_state_value() const {
    return task->get_initial_state_numeric_values()[var_id];
}

std::size_t ResNumericVariablesProxy::size() const {
    return task->get_num_numeric_variables();
}

ResNumericVariableProxy ResNumericVariablesProxy::operator[](std::size_t index) const {
    assert(index < size());
    return {*task, static_cast<int>(index)};
}

size_t NumericPreconditionsProxy::size() const {
    return task->get_operator(op_index).numeric_preconditions.size();
}

std::shared_ptr<numeric_condition::RegularNumericCondition> NumericPreconditionsProxy::operator[](std::size_t fact_index) const {
    assert(fact_index < size());
    return task->get_operator(op_index).numeric_preconditions[fact_index];
}

size_t PropositionalPreconditionsProxy::size() const {
    return task->get_operator(op_index).preconditions.size();
}

FactProxy PropositionalPreconditionsProxy::operator[](std::size_t fact_index) const {
    assert(fact_index < size());
    return task->get_operator(op_index).preconditions[fact_index];
}

size_t AssignEffectsProxy::size() const {
    return task->get_operator(op_index).asgn_effs.size();
}

const std::pair<int, ap_float> & AssignEffectsProxy::operator[](std::size_t fact_index) const {
    assert(fact_index < size());
    return task->get_operator(op_index).asgn_effs[fact_index];
}

size_t AdditiveEffectsProxy::size() const {
    return task->get_operator(op_index).eff_list.size();
}

std::pair<int, ap_float> AdditiveEffectsProxy::operator[](std::size_t fact_index) const {
    assert(fact_index < size());
    return {task->get_global_var_id(fact_index),
            task->get_operator(op_index).eff_list[fact_index]};
}

EffectsProxy NumericOperatorProxy::get_propositional_effects() const {
    return {*(task->task), index, false};
}

ap_float NumericOperatorProxy::get_cost() const {
    return task->get_operator_cost(index);
}

const string &NumericOperatorProxy::get_name() const {
    return task->get_operator_name(index);
}

size_t NumericOperatorsProxy::size() const {
    return task->get_num_operators();
}
}