#ifndef COPY_MAX_THROUGHPUT_ESTIMATE_ALGORITHM_HPP
#define COPY_MAX_THROUGHPUT_ESTIMATE_ALGORITHM_HPP

#include "core/ast.hpp"

namespace copy_max_throughput_estimate {
using namespace cellato::ast;

using copy_cell_state = int;

// Next state is just a copy of the current state
using copy_algorithm = current_state; 

}

#endif // COPY_MAX_THROUGHPUT_ESTIMATE_ALGORITHM_HPP