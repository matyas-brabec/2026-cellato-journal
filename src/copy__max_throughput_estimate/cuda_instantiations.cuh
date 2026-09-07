#ifndef COPY_CUDA_INSTANTIATIONS_CUH
#define COPY_CUDA_INSTANTIATIONS_CUH

// == 1 ==

#define AUTOMATON_NAMESPACE copy_max_throughput_estimate::variant<1>

#include "./config.hpp"
#include "../_shared/cuda_instantiation_template.cuh"

#undef AUTOMATON_NAMESPACE

// == 2 ==

#define AUTOMATON_NAMESPACE copy_max_throughput_estimate::variant<2>
#define SKIP_STANDARD_GRID_CUDA_TRAVERSER_INSTANTIATIONS

#include "./config.hpp"
#include "../_shared/cuda_instantiation_template.cuh"

#undef SKIP_STANDARD_GRID_CUDA_TRAVERSER_INSTANTIATIONS
#undef AUTOMATON_NAMESPACE

// == 3 ==

#define AUTOMATON_NAMESPACE copy_max_throughput_estimate::variant<3>
#define SKIP_STANDARD_GRID_CUDA_TRAVERSER_INSTANTIATIONS

#include "./config.hpp"
#include "../_shared/cuda_instantiation_template.cuh"

#undef SKIP_STANDARD_GRID_CUDA_TRAVERSER_INSTANTIATIONS
#undef AUTOMATON_NAMESPACE

// == 4 ==

#define AUTOMATON_NAMESPACE copy_max_throughput_estimate::variant<4>
#define SKIP_STANDARD_GRID_CUDA_TRAVERSER_INSTANTIATIONS

#include "./config.hpp"
#include "../_shared/cuda_instantiation_template.cuh"

#undef SKIP_STANDARD_GRID_CUDA_TRAVERSER_INSTANTIATIONS
#undef AUTOMATON_NAMESPACE

// == 5 ==

#define AUTOMATON_NAMESPACE copy_max_throughput_estimate::variant<5>
#define SKIP_STANDARD_GRID_CUDA_TRAVERSER_INSTANTIATIONS

#include "./config.hpp"
#include "../_shared/cuda_instantiation_template.cuh"

#undef SKIP_STANDARD_GRID_CUDA_TRAVERSER_INSTANTIATIONS
#undef AUTOMATON_NAMESPACE


#endif // COPY_CUDA_INSTANTIATIONS_CUH