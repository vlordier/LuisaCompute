# cmake/Sanitizers.cmake
#
# Centralised sanitizer support for LuisaCompute.
#
# Usage (from CMakeLists.txt or a sub-CMakeLists):
#
# cmake-format: off
#   include(cmake/Sanitizers.cmake)
#   luisa_enable_sanitizers(<target>)      # apply flags to a specific target
#   luisa_enable_sanitizers_global()       # apply via luisa-compute-include INTERFACE
# cmake-format: on
#
# Controlled by the CMake option LUISA_COMPUTE_ENABLE_SANITIZERS (default OFF).
# On MSVC only AddressSanitizer is supported; on Clang/GCC we also enable
# LeakSanitizer and UndefinedBehaviorSanitizer.
#
# Note: Do NOT enable sanitizers in release / shipping builds. Use them only in
# developer or CI debug builds. They carry significant runtime overhead and are
# incompatible with certain optimisations.

cmake_minimum_required(VERSION 3.23)

# Guard against multiple inclusion.
if(DEFINED _LUISA_SANITIZERS_INCLUDED)
  return()
endif()
set(_LUISA_SANITIZERS_INCLUDED TRUE)

# ──────────────────────────────────────────────────────────────────────────────
# Internal helper — build the sanitizer flag list for the current compiler.
# ──────────────────────────────────────────────────────────────────────────────
function(_luisa_compute_sanitizer_flags OUT_VAR)
  if(CMAKE_CXX_COMPILER_ID MATCHES "MSVC")
    # MSVC: only ASan is available via /fsanitize=address
    set(${OUT_VAR}
        "/fsanitize=address"
        PARENT_SCOPE)
  else()
    # Clang / GCC: ASan + LSan + UBSan. TSan is mutually exclusive with ASan;
    # enable it separately if needed.
    set(${OUT_VAR}
        "-fsanitize=address" "-fsanitize=leak" "-fsanitize=undefined"
        # Improve UBSan diagnostics
        "-fno-omit-frame-pointer"
        PARENT_SCOPE)
  endif()
endfunction()

# ──────────────────────────────────────────────────────────────────────────────
# luisa_enable_sanitizers(<target>)
#
# Apply sanitizer compile/link options to an individual CMake target. Safe to
# call from any CMakeLists; does nothing when the option is OFF.
# ──────────────────────────────────────────────────────────────────────────────
function(luisa_enable_sanitizers TARGET)
  if(NOT LUISA_COMPUTE_ENABLE_SANITIZERS)
    return()
  endif()

  _luisa_compute_sanitizer_flags(_FLAGS)

  target_compile_options(${TARGET} PRIVATE ${_FLAGS})

  if(NOT CMAKE_CXX_COMPILER_ID MATCHES "MSVC")
    target_link_options(${TARGET} PRIVATE ${_FLAGS})
  endif()

  message(STATUS "[Sanitizers] Enabled on target '${TARGET}': ${_FLAGS}")
endfunction()

# ──────────────────────────────────────────────────────────────────────────────
# luisa_enable_sanitizers_global()
#
# Propagate sanitizer flags through the luisa-compute-include INTERFACE target
# so that ALL targets that link to it inherit the flags automatically. This is
# equivalent to the inline block previously in CMakeLists.txt.
# ──────────────────────────────────────────────────────────────────────────────
function(luisa_enable_sanitizers_global)
  if(NOT LUISA_COMPUTE_ENABLE_SANITIZERS)
    return()
  endif()

  if(NOT TARGET luisa-compute-include)
    message(
      WARNING
        "[Sanitizers] luisa-compute-include not yet defined; "
        "call luisa_enable_sanitizers_global() after the target is created.")
    return()
  endif()

  _luisa_compute_sanitizer_flags(_FLAGS)

  target_compile_options(luisa-compute-include INTERFACE ${_FLAGS})

  if(NOT CMAKE_CXX_COMPILER_ID MATCHES "MSVC")
    target_link_options(luisa-compute-include INTERFACE ${_FLAGS})
  endif()

  mark_as_advanced(LUISA_COMPUTE_SANITIZER_FLAGS)
  message(STATUS "[Sanitizers] Global sanitizer flags applied: ${_FLAGS}")
endfunction()
