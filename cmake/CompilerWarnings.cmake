# cmake/CompilerWarnings.cmake
#
# Centralised compiler warning management for LuisaCompute.
#
# Usage:
#
# cmake-format: off
#   include(cmake/CompilerWarnings.cmake)
#   luisa_set_compiler_warnings(<target>)                   # standard warnings
#   luisa_set_compiler_warnings(<target> WARNINGS_AS_ERRORS) # warnings = errors
# cmake-format: on
#
# The WARNINGS_AS_ERRORS keyword promotes all warnings to errors (-Werror /
# /WX).  It is intentionally opt-in so that dependent projects that consume
# LuisaCompute as a sub-project are not forced to compile with -Werror.
#
# All flags are applied as PRIVATE so they do not leak into consumers.
#
# Note: Warnings that produce false positives in generated or third-party code
# (e.g. -Wshadow, -Wconversion) are listed but commented out.  Enable them
# per-target as needed once the existing codebase is clean.

cmake_minimum_required(VERSION 3.23)

# Guard against multiple inclusion.
if(DEFINED _LUISA_COMPILER_WARNINGS_INCLUDED)
  return()
endif()
set(_LUISA_COMPILER_WARNINGS_INCLUDED TRUE)

# ──────────────────────────────────────────────────────────────────────────────
# Internal helpers — build warning flag lists per compiler family.
# ──────────────────────────────────────────────────────────────────────────────

function(_luisa_warnings_msvc OUT_VAR)
  set(${OUT_VAR}
      /W4 # Highest practical MSVC warning level
      /w14242 # Possible loss of data: conversion from 'type1' to 'type2'
      /w14254 # Larger bit field assigned to smaller bit field
      /w14263 # 'function': member function does not override base class virtual
              # member function
      /w14265 # 'class': class has virtual functions, but destructor is not
              # virtual
      /w14287 # 'operator': unsigned/negative constant mismatch
      /we4289 # Non-standard extension: loop control variable used outside the
              # for-loop scope
      /w14296 # 'operator': expression is always 'boolean_value'
      /w14311 # 'variable': pointer truncation from 'type1' to 'type2'
      /w14545 # Expression before comma evaluates to a function which is missing
              # an argument list
      /w14546 # Function call before comma missing argument list
      /w14547 # 'operator': operator before comma has no effect; expected
              # operator with side-effect
      /w14549 # 'operator': operator before comma has no effect; did you intend
              # 'operator'?
      /w14555 # Expression has no effect; expected expression with side-effect
      /w14619 # Pragma warning: there is no warning number 'number'
      /w14640 # Enable warning on thread-unsafe static member initialisation
      /w14826 # Conversion from 'type1' to 'type2' is sign-extended
      /w14905 # Wide string literal cast to 'LPSTR'
      /w14906 # String literal cast to 'LPWSTR'
      /w14928 # Illegal copy-initialisation; more than one user-defined
              # conversion applied
      PARENT_SCOPE)
endfunction()

function(_luisa_warnings_clang OUT_VAR)
  set(${OUT_VAR}
      -Wall
      -Wextra
      -Wpedantic
      -Wnon-virtual-dtor
      -Wold-style-cast
      -Wcast-align
      -Wunused
      -Woverloaded-virtual
      -Wnull-dereference
      -Wformat=2
      -Wimplicit-fallthrough
      # cmake-format: off
      # -Wshadow           # Often noisy in template-heavy code; enable per target
      # -Wconversion       # Can be noisy with GPU numeric types; enable per target
      # -Wsign-conversion  # Same as above
      # -Wdouble-promotion # Useful for GPU shaders; can be noisy elsewhere
      # cmake-format: on
      PARENT_SCOPE)
endfunction()

function(_luisa_warnings_gcc OUT_VAR)
  set(${OUT_VAR}
      -Wall
      -Wextra
      -Wpedantic
      -Wnon-virtual-dtor
      -Wold-style-cast
      -Wcast-align
      -Wunused
      -Woverloaded-virtual
      -Wnull-dereference
      -Wformat=2
      -Wimplicit-fallthrough
      -Wmisleading-indentation
      -Wduplicated-cond
      -Wduplicated-branches
      -Wlogical-op
      -Wuseless-cast
      # cmake-format: off
      # -Wshadow           # Often noisy in template-heavy code; enable per target
      # -Wconversion       # Can be noisy with GPU numeric types; enable per target
      # -Wsign-conversion  # Same as above
      # -Wdouble-promotion # Useful for GPU shaders; can be noisy elsewhere
      # cmake-format: on
      PARENT_SCOPE)
endfunction()

# ──────────────────────────────────────────────────────────────────────────────
# luisa_set_compiler_warnings(<target> [WARNINGS_AS_ERRORS])
#
# Apply the standard LuisaCompute warning set to <target>. Pass
# WARNINGS_AS_ERRORS to also promote all warnings to errors.
# ──────────────────────────────────────────────────────────────────────────────
function(luisa_set_compiler_warnings TARGET)
  cmake_parse_arguments(ARG "WARNINGS_AS_ERRORS" "" "" ${ARGN})

  if(CMAKE_CXX_COMPILER_ID MATCHES "MSVC")
    _luisa_warnings_msvc(_FLAGS)
    if(ARG_WARNINGS_AS_ERRORS)
      list(APPEND _FLAGS /WX)
    endif()
  elseif(CMAKE_CXX_COMPILER_ID MATCHES "Clang" OR CMAKE_CXX_COMPILER_ID MATCHES
                                                  "AppleClang")
    _luisa_warnings_clang(_FLAGS)
    if(ARG_WARNINGS_AS_ERRORS)
      list(APPEND _FLAGS -Werror)
    endif()
  elseif(CMAKE_CXX_COMPILER_ID MATCHES "GNU")
    _luisa_warnings_gcc(_FLAGS)
    if(ARG_WARNINGS_AS_ERRORS)
      list(APPEND _FLAGS -Werror)
    endif()
  else()
    message(
      WARNING
        "[CompilerWarnings] Unrecognised compiler '${CMAKE_CXX_COMPILER_ID}'; "
        "no warning flags applied.")
    return()
  endif()

  target_compile_options(${TARGET} PRIVATE ${_FLAGS})
endfunction()
