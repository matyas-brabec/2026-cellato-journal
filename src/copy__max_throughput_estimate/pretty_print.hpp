#ifndef COPY_MAX_THROUGHPUT_ESTIMATE_PRETTY_PRINT_HPP
#define COPY_MAX_THROUGHPUT_ESTIMATE_PRETTY_PRINT_HPP

#include "memory/standard_grid.hpp"
#include "./algorithm.hpp"

namespace copy_max_throughput_estimate {

using print_config = cellato::memory::grids::standard::print_config<copy_cell_state>;

struct copy_pretty_print {
    static print_config get_config() {
        return print_config();
    }
};

} // namespace copy_max_throughput_estimate

#endif // COPY_MAX_THROUGHPUT_ESTIMATE_PRETTY_PRINT_HPP