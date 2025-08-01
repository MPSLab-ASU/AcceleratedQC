PYTHON ?= $(shell which python3)
PYTHON_PREFIX := $(shell $(PYTHON) -c "import sys; print(sys.prefix)")
PYTHON_VERSION := $(shell $(PYTHON) -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
C_COMPILER ?= $(shell which clang)
CXX_COMPILER ?= $(shell which clang++)
COMPILER_LAUNCHER ?= $(shell which ccache)
NPROC ?= $(shell python3 -c "import os; print(os.cpu_count())")

MK_ABSPATH := $(abspath $(lastword $(MAKEFILE_LIST)))
MK_DIR := $(dir $(MK_ABSPATH))
RT_BUILD_DIR ?= $(MK_DIR)/build
CODE_COVERAGE ?= OFF
BUILD_TYPE ?= RelWithDebInfo
ENABLE_OPENQASM ?= ON
ENABLE_OQD ?= OFF
ENABLE_ASAN ?= OFF
STRICT_WARNINGS ?= ON
LLVM_DIR ?= $(MK_DIR)/../../llvm-project/

PLATFORM := $(shell uname -s)

# Since we build executables for all test targets in this file, there is no reason to preload.
# Preloading while the ASAN RT is already embedded in the executable can lead to the "incompatible
# ASAN runtimes detected" error, at least on Linux (macOS seemed okay with it).
# If necessary, add ASAN flags here to fine-tune behaviour (e.g. ASAN_OPTIONS="...").
ASAN_COMMAND :=

# Note: ASAN replaces dlopen calls, which means that when we open other libraries via dlopen that
#       relied on the parent's library's RPATH, these libraries are no longer found.
#         e.g. `dlopen(openqasm_python_module.so)` from OpenQASMRunner.hpp
#       We can fix this using LD_LIBRARY_PATH (for dev builds).
ifeq ($(PLATFORM), Linux)
ASAN_FLAGS = LD_LIBRARY_PATH="$(RT_BUILD_DIR)/lib:$(LD_LIBRARY_PATH)"
# Python tests can generally produce leaks, here observed on Linux. OpenQASM tests call into Python.
PY_ASAN_OPTIONS := ASAN_OPTIONS="detect_leaks=0"
endif

# Deferred assignment since RT_BUILD_DIR can be modified by the targets.
ifeq ($(ENABLE_ASAN), ON)
ASAN_COMMAND = $(ASAN_FLAGS)
endif

BUILD_TARGETS := rt_capi rtd_null_qubit rtd_custom_device
TEST_TARGETS := runner_tests_qir_runtime runner_tests_mbqc_runtime

ifeq ($(ENABLE_OPENQASM), ON)
	BUILD_TARGETS += rtd_openqasm
	TEST_TARGETS += runner_tests_openqasm
endif

ifeq ($(ENABLE_OQD), ON)
	BUILD_TARGETS += rt_OQD_capi rtd_oqd_device
	TEST_TARGETS += runner_tests_oqd
endif

.PHONY: help
help:
	@echo "Please use \`make <target>' where <target> is one of"
	@echo "  all                to build Catalyst Runtime"
	@echo "  coverage           to generate a coverage report using lcov"
	@echo "  clean              to delete all temporary, cache, and build files"
	@echo "  test               to run the Catalyst runtime test suite"
	@echo "  format [check=1]   to apply C++ formatter; use with 'check=1' to check instead of modify (requires clang-format)"
	@echo "  format [version=?] to apply C++ formatter; use with 'version={version}' to run clang-format-{version} instead of clang-format"
	@echo "  check-tidy         to build Catalyst Runtime with RUNTIME_CLANG_TIDY=ON (requires clang-tidy)"

.PHONY: configure
configure:
	@echo "Configure Catalyst Runtime"

	cmake -G Ninja -B $(RT_BUILD_DIR) . \
		-DCMAKE_BUILD_TYPE=$(BUILD_TYPE) \
		-DCMAKE_LIBRARY_OUTPUT_DIRECTORY=$(RT_BUILD_DIR)/lib \
		-DCMAKE_C_COMPILER=$(C_COMPILER) \
		-DMLIR_INCLUDE_DIRS=$(LLVM_DIR)/mlir/include \
		-DCMAKE_CXX_COMPILER=$(CXX_COMPILER) \
		-DCMAKE_C_COMPILER_LAUNCHER=$(COMPILER_LAUNCHER) \
		-DCMAKE_CXX_COMPILER_LAUNCHER=$(COMPILER_LAUNCHER) \
		-DENABLE_OPENQASM=$(ENABLE_OPENQASM) \
		-DENABLE_OQD=$(ENABLE_OQD) \
		-DENABLE_CODE_COVERAGE=$(CODE_COVERAGE) \
		-DPython_EXECUTABLE=$(PYTHON) \
		-DENABLE_ADDRESS_SANITIZER=$(ENABLE_ASAN) \
		-DRUNTIME_ENABLE_WARNINGS=$(STRICT_WARNINGS)

.PHONY: runtime
runtime: configure
	cmake --build $(RT_BUILD_DIR) --target $(BUILD_TARGETS) -j$(NPROC)

.PHONY: test_runner
test_runner: configure
	cmake --build $(RT_BUILD_DIR) --target $(TEST_TARGETS) -j$(NPROC)

.PHONY: test
test: CODE_COVERAGE=OFF
test: BUILD_TYPE?=RelWithDebInfo
test: test_runner
	@echo "Catalyst runtime test suite - NullQubit"
	$(ASAN_COMMAND) $(RT_BUILD_DIR)/tests/runner_tests_qir_runtime
	@echo "Catalyst MBQC runtime test suite"
	$(ASAN_COMMAND) $(RT_BUILD_DIR)/tests/runner_tests_mbqc_runtime
ifeq ($(ENABLE_OPENQASM), ON)
	# Test the OpenQasm devices C++ tests
	$(ASAN_COMMAND) $(PY_ASAN_OPTIONS) $(RT_BUILD_DIR)/tests/runner_tests_openqasm
endif
ifeq ($(ENABLE_OQD), ON)
	# Test the OQD devices C++ tests
	$(ASAN_COMMAND) $(RT_BUILD_DIR)/tests/runner_tests_oqd
endif

.PHONY: coverage
coverage: RT_BUILD_DIR := $(RT_BUILD_DIR)_cov
coverage: CODE_COVERAGE=ON
coverage: BUILD_TYPE=Debug
coverage: C_COMPILER=$(shell which gcc)
coverage: CXX_COMPILER=$(shell which g++)
coverage: export LLVM_PROFILE_FILE := $(RT_BUILD_DIR)/tests/%m.profraw
coverage: test_runner
	@echo "check C++ code coverage"
	$(ASAN_COMMAND) $(RT_BUILD_DIR)/tests/runner_tests_qir_runtime
	$(ASAN_COMMAND) $(RT_BUILD_DIR)/tests/runner_tests_mbqc_runtime
ifeq ($(ENABLE_OPENQASM), ON)
	$(ASAN_COMMAND) $(PY_ASAN_OPTIONS) $(RT_BUILD_DIR)/tests/runner_tests_openqasm
endif
ifeq ($(ENABLE_OQD), ON)
	$(ASAN_COMMAND) $(RT_BUILD_DIR)/tests/runner_tests_oqd
endif
ifeq ($(PLATFORM),Linux)
	lcov --directory $(RT_BUILD_DIR) -b $(MK_DIR)/lib --capture --output-file $(RT_BUILD_DIR)/coverage.info
	lcov --remove $(RT_BUILD_DIR)/coverage.info '/usr/*' '*/_deps/*' '*/envs/*' '*/mlir/*' --output-file $(RT_BUILD_DIR)/coverage.info -q
	genhtml $(RT_BUILD_DIR)/coverage.info --output-directory $(RT_BUILD_DIR)/cov -t "Catalyst Runtime C++ Coverage" --num-spaces 4  -q
else
	xcrun llvm-profdata merge $(RT_BUILD_DIR)/tests/*.profraw -o $(RT_BUILD_DIR)/tests/rt_test_coverage.profdata
	xcrun llvm-cov show -instr-profile $(RT_BUILD_DIR)/tests/rt_test_coverage.profdata \
		-object $(RT_BUILD_DIR)/tests/runner_tests_openqasm \
		$(RT_BUILD_DIR)/tests/runner_tests_qir_runtime \
		$(RT_BUILD_DIR)/tests/runner_tests_mbqc_runtime \
		-format=html -output-dir=$(RT_BUILD_DIR)/coverage_html \
		$(MK_DIR)/include $(MK_DIR)/lib $(MK_DIR)/tests
endif

.PHONY: clean
clean:
	@echo "clean build files"
	rm -rf $(RT_BUILD_DIR) $(RT_BUILD_DIR)_cov cov coverage.info $(MK_DIR)/BuildTidy

.PHONY: format
format:
ifdef check
	$(PYTHON) ../bin/format.py --check $(if $(version:-=),--cfversion $(version)) .
else
	$(PYTHON) ../bin/format.py $(if $(version:-=),--cfversion $(version)) .
endif

.PHONY: check-tidy
check-tidy:
	@echo "build Catalyst Runtime with RUNTIME_CLANG_TIDY=ON"
	cmake -G Ninja -B $(MK_DIR)/BuildTidy . \
		-DCMAKE_BUILD_TYPE=$(BUILD_TYPE) \
		-DCMAKE_C_COMPILER=$(C_COMPILER) \
		-DCMAKE_CXX_COMPILER=$(CXX_COMPILER) \
		-DMLIR_INCLUDE_DIRS="$(abspath $(LLVM_DIR))/mlir/include" \
		-DRUNTIME_CLANG_TIDY=ON

	cmake --build $(MK_DIR)/BuildTidy --target rt_capi -j$(NPROC)
