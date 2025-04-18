#ifndef NUMERIC_PDBS_PATTERN_COLLECTION_INFORMATION_H
#define NUMERIC_PDBS_PATTERN_COLLECTION_INFORMATION_H

#include "numeric_helper.h"
#include "types.h"

#include <memory>

namespace numeric_pdbs {
/*
  This class contains everything we know about a pattern collection. It will
  always contain patterns, but can also contain the computed PDBs and maximal
  additive subsets of the PDBs. If one of the latter is not available, then
  this information is created when it is requested.
  Ownership of the information is shared between the creators of this class
  (usually PatternCollectionGenerators), the class itself, and its users
  (consumers of pattern collections like heuristics).
*/
class PatternCollectionInformation {
    std::shared_ptr<numeric_pdb_helper::NumericTaskProxy> task_proxy;
    std::shared_ptr<PatternCollection> patterns;
    std::shared_ptr<PDBCollection> pdbs;
    std::shared_ptr<MaxAdditivePDBSubsets> max_additive_subsets;

    // approximate upper bound on the number of abstract states per PDB possibly reachable within the pattern
    size_t max_number_pdb_states;

    void create_pdbs_if_missing();
    void create_max_additive_subsets_if_missing();

    bool information_is_valid() const;
public:
    PatternCollectionInformation(
            std::shared_ptr<numeric_pdb_helper::NumericTaskProxy> task_proxy,
            std::shared_ptr<PatternCollection> patterns,
            size_t max_number_pdb_states);
    ~PatternCollectionInformation() = default;

    void set_pdbs(std::shared_ptr<PDBCollection> pdbs);
    void set_max_additive_subsets(
        std::shared_ptr<MaxAdditivePDBSubsets> max_additive_subsets);

    std::shared_ptr<PatternCollection> get_patterns();
    std::shared_ptr<PDBCollection> get_pdbs();
    std::shared_ptr<MaxAdditivePDBSubsets> get_max_additive_subsets();
};
}

#endif
