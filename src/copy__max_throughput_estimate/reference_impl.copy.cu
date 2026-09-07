#include "./reference_implementation.hpp"
#include <cuda_runtime.h>
#include "traversers/cuda_utils.cuh"
#include "../_shared/indexing.hpp"

namespace copy_max_throughput_estimate::reference {
using namespace ::reference::indexing;

// CUDA kernel for Game of Life (single step)
__global__ void copy_kernel(const copy_cell_state* current, copy_cell_state* next, 
                           int width, int height) {
    // Calculate thread indices, adjusting for margins
    int x = blockIdx.x * blockDim.x + threadIdx.x + indexer::x_margin;
    int y = blockIdx.y * blockDim.y + threadIdx.y + indexer::y_margin;

    indexer idx(width, height);
    const int center_idx = idx.at(x, y);
    
    // Just copy the current state to the next state
    next[center_idx] = current[center_idx];
}

void runner::run_kernel(int steps) {
    if (!d_current || !d_next) {
        init_cuda();
    }
    
    // Set up grid and block dimensions, accounting for margins
    dim3 block_size(_block_size_x, _block_size_y);

    constexpr std::size_t x_margin = indexer::x_margin;
    constexpr std::size_t y_margin = indexer::y_margin;

    auto _x_size_threads = _x_size - 2 * x_margin; // Adjust for margins
    auto _y_size_threads = _y_size - 2 * y_margin; // Adjust for margins

    dim3 grid_dim((_x_size_threads + block_size.x - 1) / block_size.x, 
                 (_y_size_threads + block_size.y - 1) / block_size.y);
    
    // Run steps iterations
    for (int i = 0; i < steps; i++) {
        // Launch kernel for one step
        copy_kernel<<<grid_dim, block_size>>>(d_current, d_next, _x_size, _y_size);

        // Swap pointers for next iteration
        copy_cell_state* temp = d_current;
        d_current = d_next;
        d_next = temp;
    }
}

} // namespace copy_max_throughput_estimate::reference
