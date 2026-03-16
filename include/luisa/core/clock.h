#pragma once

#include <chrono>

namespace luisa {

/**
 * @brief High-resolution wall-clock timer.
 *
 * Typical usage:
 * @code
 *   Clock clk;
 *   // ... do work ...
 *   double ms = clk.toc();  // milliseconds elapsed since construction or last tic()
 * @endcode
 */
class Clock {

    using SystemClock = std::chrono::high_resolution_clock;
    using Tick = std::chrono::high_resolution_clock::time_point;

private:
    Tick _last;

public:
    /**
     * @brief Construct and start the clock (equivalent to calling tic() immediately).
     */
    Clock() noexcept : _last{SystemClock::now()} {}

    /**
     * @brief Reset the clock start point to the current time.
     */
    void tic() noexcept { _last = SystemClock::now(); }

    /**
     * @brief Return elapsed time in milliseconds since the last tic() (or construction).
     * @return elapsed time in milliseconds
     */
    [[nodiscard]] double toc() const noexcept {
        auto curr = SystemClock::now();
        using namespace std::chrono_literals;
        return static_cast<double>((curr - _last) / 1ns) * 1e-6;
    }

    /**
     * @brief Alias for toc(). Returns elapsed time in milliseconds.
     * @return elapsed time in milliseconds
     */
    [[nodiscard]] double elapsed_ms() const noexcept { return toc(); }
};

}// namespace luisa

