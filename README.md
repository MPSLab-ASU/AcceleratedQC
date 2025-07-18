# AcceleratedQC

This repository contains the main codebase for the AcceleratedQC project, including the `catalyst` component and a submodule reference to the official LLVM project.

## Repository Structure

- `catalyst/` — Main project code and scripts
- `llvm-project/` — LLVM project (added as a submodule)

## Setup Instructions

### 1. Clone the Repository

Clone this repository and initialize submodules:

```bash
git clone --recurse-submodules https://github.com/MPSLab-ASU/AcceleratedQC.git
cd AcceleratedQC
```

If you already cloned without `--recurse-submodules`, run:

```bash
git submodule update --init --recursive
```

### 2. Install Dependencies

Navigate to the `catalyst` directory and install Python dependencies:

```bash
cd catalyst
pip install -r requirements.txt
```

### 3. Building LLVM (Optional)

If you need to build LLVM from source, follow the instructions in `llvm-project/README.md`.

### 4. Additional Information

- For more details, see the `catalyst/README.md` and `llvm-project/README.md` files.
- If you encounter issues, please open an issue on this repository.

---

**Maintained by MPSLab-ASU** 