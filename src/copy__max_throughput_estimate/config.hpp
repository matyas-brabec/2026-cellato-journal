#ifndef COPY_MAX_THROUGHPUT_ESTIMATE_CONFIG_HPP
#define COPY_MAX_THROUGHPUT_ESTIMATE_CONFIG_HPP

#include <array>
#include <string_view>
#include "./algorithm.hpp"
#include "./pretty_print.hpp"
#include "./data_init.hpp"
#include "./reference_implementation.hpp"
#include "memory/state_dictionary.hpp"

namespace copy_max_throughput_estimate {

namespace detail {
    constexpr std::size_t num_digits(unsigned n) {
        return n < 10 ? 1 : 1 + num_digits(n / 10);
    }

    template <int BITS>
    constexpr auto build_name() {
        constexpr std::string_view prefix = "copy--max-throughput-estimate--";
        constexpr std::string_view suffix = "-bit";
        constexpr std::size_t digits = num_digits(BITS);
        
        std::array<char, prefix.size() + digits + suffix.size() + 1> arr{};
        std::size_t idx = 0;
        
        for (char c : prefix) arr[idx++] = c;
        
        unsigned temp = BITS;
        for (std::size_t i = 0; i < digits; ++i) {
            arr[idx + digits - 1 - i] = '0' + (temp % 10);
            temp /= 10;
        }
        idx += digits;
        
        for (char c : suffix) arr[idx++] = c;
        
        // Null terminator
        arr[idx] = '\0';
        return arr;
    }
}

template <int BITS>
struct variant {
    
    struct config {
        static constexpr auto name_arr = detail::build_name<BITS>();
        static constexpr const char* name = name_arr.data();
        static constexpr double average_halo_radius = 1.0;

        using algorithm = copy_algorithm;

        using cell_state = copy_cell_state;
        using state_dictionary = cellato::memory::grids::int_based_state_dictionary<BITS>;

        using pretty_print = copy_pretty_print;

        using reference_implementation = reference::runner;

        struct input {
            using random = copy_random_init;
        };
    };
};

} // namespace copy_max_throughput_estimate

#endif // COPY_MAX_THROUGHPUT_ESTIMATE_CONFIG_HPP