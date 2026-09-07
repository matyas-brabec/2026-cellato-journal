#ifndef COPY_MAX_THROUGHPUT_ESTIMATE_INIT_HPP
#define COPY_MAX_THROUGHPUT_ESTIMATE_INIT_HPP

#include <vector>
#include <tuple>
#include "memory/grid_utils.hpp"
#include "experiments/run_params.hpp"
#include "./algorithm.hpp"

namespace copy_max_throughput_estimate {

struct copy_random_init {
    static std::vector<copy_cell_state> init(cellato::run::run_params& params) {

        std::vector<copy_cell_state> initial_state(params.x_size * params.y_size);

        return initial_state;
    }
};

}

#endif // COPY_MAX_THROUGHPUT_ESTIMATE_INIT_HPP