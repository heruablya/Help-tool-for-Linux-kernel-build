
🐧 Linux Kernel Builder Helper

A console-based Python application designed to automate and simplify the processes of compiling, installing, and managing different versions of the Linux operating system kernel. The program handles routine system operations, minimizing the risks of human error during manual compilation.

🛠 Project Architecture

The application is divided into 5 main modules:
• main.py — The single entry point; automatically detects the current distribution and initializes the interactive menu.
• arch.py / ubuntu.py — Contain the core logic for automated kernel compilation and installation tailored to the respective OS.
• arch_man.py / ubuntu_man.py — Responsible for auditing, renaming, and removing kernels currently installed on the system.

🔄 Main Workflow

The application workflow is divided into two main scenarios: Installing a New Kernel and Managing Existing Kernels.

1. New Kernel Installation and Compilation Scenario

1. Environment Check: main.py utilizes the distro library to automatically detect the OS type (Arch or Ubuntu) to apply distribution-specific package managers and commands.
2. Fetching Versions: The application makes an HTTP request to the kernel.org API, retrieves the up-to-date JSON list of available kernels (mainline, stable, longterm, linux-next), and displays a formatted, numbered list to the user.
3. Download and Extraction: Once a version is selected, the source code archive (.tar.xz) is downloaded and extracted, featuring an interactive visual progress bar.
4. Dependency Installation: Depending on the detected system, the utility automatically invokes pacman or apt to install essential compilation packages (base-devel, libelf, bc, git, etc.).
5. Patching and Configuration:
	• The program prompts the user to apply custom .patch files if available.
	• It offers 3 configuration modes using the menuconfig interface: using the current system configuration, configuring from scratch, or a hybrid configuration method.
6. Compilation: Parallel compilation of the kernel components is triggered along with compressed image generation using make -j and make bzImage commands.
7. Final Integration: The utility installs the compiled modules, copies the compressed image to the /boot directory, generates the initramfs file system (to prevent boot errors), and automatically updates the system bootloader configuration (e.g., GRUB).

2. Managing Installed Kernels Scenario

1. System Audit: The program scans the bootloader configuration files (e.g., /boot/grub/grub.cfg) looking for signatures of installed vmlinuz-* kernels.
2. List Output: The user is presented with an ordered list of all kernels discovered on the system.
3. Modification Options:
	• Renaming: Safely renames the kernel file inside the /boot directory while keeping track of system naming conventions.
	• Deletion: Performs a cascading deletion of all files associated with the chosen kernel (including vmlinuz-*, initrd.img-*, and initramfs-* files) to free up storage space.

📦 Project Dependencies

For the script to operate correctly and compile the kernel successfully, specific external libraries and system utilities are required. The application automatically installs the kernel compilation packages when the compilation option is selected from the menu, using your OS package manager (pacman or apt).

1. Python Packages

Ensure the following Python modules are installed on your system (they can be installed via your system package manager or pip):
• requests — Used for making synchronous HTTP requests to the kernel.org API.
• distro — Used for precise identification of the current Linux distribution during the initialization phase.
• Built-in modules (require no separate installation): os, sys, tarfile, subprocess, argparse, re, time.

2. System Packages for Kernel Compilation (Auto-Installed)

Below is the list of low-level utilities required to compile and integrate a new kernel into your system:
• Core Build Tools:
	• base-devel (or build-essential in Ubuntu) — Includes compilers, the make utility, and fundamental developer tools.
	• git — Required for version control operations and handling kernel repositories.
• Archivers and File Handling:
	• tar and xz — Required for decompressing downloaded kernel source archives.
	• cpio — An archiving utility used for creating file system archive files.
• Kernel-Specific Utilities:
	• kmod — Utilities for managing Linux kernel modules.
	• bc — An arbitrary-precision calculator language used inside kernel configuration scripts.
	• libelf — A library for parsing and handling ELF files (crucial for module compilation).
	• perl — A scripting language required by internal kernel automation scripts.
• Network and Documentation Utilities:
	• inetutils — Base network clients.
	• xmlto — A tool for converting XML files to other formats (needed for generating manuals and documentation).

🛠 Debug Mode and usage
For use just jump into the project folder, and run ./main.py
When launching the script with the --debug (or -d) flag:
python3 main.py --debug
The console will display extended technical information, including the exact URLs of system HTTP requests, the number of fetched versions, and the full text of background bash terminal commands being executed. The application is also protected against network failures (ConnectionError) using built-in try-except exception handling blocks.
