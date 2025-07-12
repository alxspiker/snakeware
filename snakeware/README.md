# snakeware build docs

The snakeware build system is based on Buildroot 2021.08 and the process is almost entirely automated. Note that this project hasn't been actively maintained since 2021, so some fixes are required for compatibility with modern systems (e.g., newer Meson for GLib builds, line ending fixes in WSL). We've included troubleshooting steps below based on common issues.

The build will take quite a long time the first time (1-2 hours or more, depending on hardware), but subsequent builds are faster due to caching (unless you run `make clean` in the buildroot directory).

Currently supported platforms:
* x86-64 (tested on PCs/VMs)
* rpi4 (Raspberry Pi 4)

## Build Process

### Prerequisites
- **Linux Host**: Use a GNU/Linux distribution like Ubuntu. Tested on Ubuntu 22.04+.
- **Dependencies**: Install these packages before building (on Ubuntu/Debian):  
  ```
  sudo apt update && sudo apt upgrade -y
  sudo apt install -y which sed make binutils build-essential diffutils gcc g++ bash patch gzip bzip2 perl tar cpio unzip rsync file bc findutils gawk wget git python3 ncurses-base libncurses5-dev libncursesw5-dev flex bison libssl-dev libelf-dev curl mercurial subversion cvs graphviz libglib2.0-dev libexpat1-dev autopoint gettext docbook2x lzop gengetopt zlib1g-dev dos2unix
  ```
- **Windows/WSL Setup**: If building on Windows, use WSL 2 with Ubuntu. Install WSL via PowerShell (as admin): `wsl --install`. Then install dependencies as above in the WSL terminal. Clone/move the repo to your WSL home directory (`~`) to avoid path issues:  
  ```
  mv /mnt/c/path/to/snakeware ~
  cd ~/snakeware
  ```
- **Fix Line Endings**: If cloning/editing on Windows, convert files to Unix LF:  
  ```
  dos2unix build.sh
  find external -name "Config.in" -exec dos2unix {} \;
  dos2unix external/external.desc
  chmod +x build.sh
  ```

### 1. Run `./build.sh <platform>`
`<platform>` should be one of the supported platforms from the above list (e.g., `x86-64`).

This script clones Buildroot 2021.08, configures it with your platform's defconfig, and builds the image. It may fail due to outdated components—see Troubleshooting below for fixes.

### 2. Done!
If successful, a `snakeware_<platform>.iso` or `.img` file will be generated in this directory (e.g., `snakeware_x86-64.iso`).

You can run this in QEMU:  
```
qemu-system-x86_64 -cdrom snakeware_x86-64.iso -m 2G -cpu host -machine type=q35,accel=kvm -smp $(nproc) -audiodev pa,id=snd -device ich9-intel-hda -device hda-output,audiodev=snd
```
Or dd it to a USB/SD for real hardware:  
```
sudo dd if=snakeware_x86-64.iso of=/dev/sdX bs=4M status=progress && sync
```
(Replace `/dev/sdX` with your device; use `lsblk` to check.)

## Customizations and Updates
We've updated the build for modern graphics acceleration (e.g., using Mesa and SDL2 with KMS/DRM for faster Pygame rendering) and fixed compatibility issues. These are optional but recommended for better performance.

### Adding Hardware Graphics Acceleration
To enable GPU acceleration (fixes slow framebuffer graphics), append these to your platform's defconfig (e.g., `external/configs/x86-64_defconfig`):  
```
# Hardware Acceleration for Graphics
BR2_PACKAGE_MESA3D=y
BR2_PACKAGE_MESA3D_OPENGL_GL=y
BR2_PACKAGE_MESA3D_OPENGL_ES=y
BR2_PACKAGE_MESA3D_OPENGL_ES2=y
BR2_PACKAGE_MESA3D_OPENGL_EGL=y
BR2_PACKAGE_MESA3D_DRI_DRIVER=y
BR2_PACKAGE_MESA3D_GALLIUM_DRIVER_I915=y  # Add others like radeonsi for AMD
BR2_PACKAGE_LIBDRM=y
BR2_PACKAGE_LIBEGL=y
BR2_PACKAGE_LIBGLES=y
BR2_PACKAGE_LIBGBM=y
BR2_PACKAGE_SDL2=y
BR2_PACKAGE_SDL2_KMSDRM=y
```
For rpi4, use VC4 driver: `BR2_PACKAGE_MESA3D_GALLIUM_DRIVER_VC4=y`.

After updating, rerun `./build.sh <platform>`.

In `snakewm/wm.py`, enable acceleration:  
```
import os
os.environ['SDL_VIDEODRIVER'] = 'kmsdrm'
os.environ['SDL_VIDEO_GL_DRIVER'] = 'libGL.so'  # Or libGLESv2.so
import pygame
pygame.init()
screen = pygame.display.set_mode((info.current_w, info.current_h), pygame.FULLSCREEN | pygame.OPENGL)
```

For ModernGL (advanced OpenGL): Add a custom package in `external/package/python-moderngl/` with Config.in and python-moderngl.mk as described in conversation, then add `BR2_PACKAGE_PYTHON_MODERNGL=y` to defconfig.

### Troubleshooting Common Build Errors
If the build fails, apply these fixes step-by-step in the `buildroot_<platform>` directory (e.g., `cd buildroot_x86-64`).

- **Legacy Config Errors**:  
  ```
  make menuconfig  # Disable legacy options (e.g., old GCC), save/exit
  make olddefconfig
  make savedefconfig DEF_CONFIG=../external/configs/x86-64_defconfig
  make
  ```

- **Meson Version Mismatch (e.g., for GLib)**:  
  Edit `package/meson/meson.mk`:  
  ```
  MESON_VERSION = 1.4.1
  MESON_SITE = https://github.com/mesonbuild/meson/releases/download/$(MESON_VERSION)
  MESON_SOURCE = meson-$(MESON_VERSION).tar.gz
  ```
  Edit `package/meson/meson.hash`:  
  ```
  sha256  1b8aad738a5f6ae64294cc8eaba9a82988c1c420204484ac02ef782e5bba5f49  meson-1.4.1.tar.gz
  ```
  Manually download if 404:  
  ```
  cd dl
  wget https://github.com/mesonbuild/meson/releases/download/1.4.1/meson-1.4.1.tar.gz
  cd ..
  ```
  Clean/rebuild:  
  ```
  make host-meson-dirclean
  make host-meson
  make
  ```

- **GLib gspawn.c Compilation Error**:  
  Edit `output/build/host-libglib2-2.68.2/glib/gspawn.c`: Change `close_range (lowfd, G_MAXUINT)` to `close_range (lowfd, G_MAXUINT, 0)`.  
  Then `make`.

- **Meson Patch Failures**:  
  Remove outdated patches:  
  ```
  rm package/meson/0001-Prefer-ext-static-libs-when-default-library-static.patch
  rm package/meson/0002-mesonbuild-dependencies-base.py-add-pkg_config_stati.patch
  make host-meson-dirclean
  make host-meson
  make
  ```

- **Meson ImportError (HoldableObject)**:  
  ```
  make host-meson-dirclean
  rm -rf output/host/lib/python3.9/site-packages/mesonbuild
  make host-meson
  make
  ```

- **Force Fresh Clone**: If version mismatches persist:  
  ```
  rm -rf buildroot_x86-64
  ./build.sh x86-64
  ```

- **Manual ISO Copy (if Script Fails)**:  
  ```
  cp buildroot_x86-64/output/images/rootfs.iso9660 snakeware_x86-64.iso
  ```

If issues continue, check Buildroot docs or search for the error—project is old, so manual tweaks are common.

## Other Info
- **Testing in VM**: Use QEMU script above. For persistence, add partitions as in original docs.
- **Custom Python Userspace**: snakeware boots to a Python shell with snakewm (Pygame-based WM). Customize in `snakewm/` and rebuild.
- **Upgrades**: We've tested with modern Ubuntu/WSL as of July 2025. For newer Buildroot (e.g., 2025.05), expect more legacy fixes—edit `build.sh` to change `BUILDROOT_VERSION`.
- **Performance Tips**: Use `-j$(nproc)` in `make` for parallel builds (edit script or run manually).

## Ports
snakeware will always be primarily focused on x86-64, but buildroot makes it possible to build for other platforms.

You can try porting snakeware to other platforms by creating a kernel config and a buildroot config that both match the platform you're targeting. For example, if you were making an ARM port, you will add the files `config/arm-buildroot-config` and `config/arm-kernel-config` and then run `./build.sh arm`.

It may be very difficult to create configs that work for the platform you're targeting, and this is not a task for inexperienced Linux users. I do not guarantee that cross-building will work because I haven't tried it, and you shouldn't try it unless you're pretty knowledgeable about the Linux kernel and about buildroot.

I would be interested to hear your results if you try this, and please send a PR if you get some working configs.