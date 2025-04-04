#ifndef PDBS_ZERO_ONE_PDBS_H
#define PDBS_ZERO_ONE_PDBS_H

#include "types.h"

#include "../globals.h"

class State;
class TaskProxy;

namespace pdbs {
class ZeroOnePDBs {
    PDBCollection pattern_databases;
public:
    ZeroOnePDBs(TaskProxy task_proxy, const PatternCollection &patterns);
    ~ZeroOnePDBs() = default;

    ap_float get_value(const State &state) const;
    /*
      Returns the sum of all mean finite h-values of every PDB.
      This is an approximation of the real mean finite h-value of the Heuristic,
      because dead-ends are ignored for the computation of the mean finite
      h-values for a PDB. As a consequence, if different PDBs have different
      states which are dead-end, we do not calculate the real mean h-value for
      these states.
    */
    ap_float compute_approx_mean_finite_h() const;
    void dump() const;
};
}

#endif
