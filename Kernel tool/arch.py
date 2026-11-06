#!/usr/bin/env python3
import os
import requests
import subprocess
import sys
import tarfile



class colors:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

KERNEL_BASE_URL = "https://www.kernel.org"

def get_available_versions(debug=False):
    print("ARCH")
    url = f"{KERNEL_BASE_URL}/releases.json"
    if debug:
        print(f"{colors.DARKCYAN}Получение доступных версий с {url}{colors.END}")
    response = requests.get(url)
    if response.status_code == 200:
        versions = response.json().get('releases')
        if debug:
            print(f"{colors.GREEN}Получено {len(versions)} версий{colors.END}")
        return versions
    else:
        print(f"{colors.RED}{colors.END}")
        return []

def format_version_info(version_info):
    version = version_info.get('version', 'Unknown Version')
    released_date = version_info.get('released', {}).get('isodate', 'Unknown Date')
    source_url = version_info.get('source', 'Unknown Source')
    return f"{colors.BOLD}{version}{colors.END} - Выпущено: {released_date}\n   Источник: {source_url}"

def choose_kernel_version(versions, debug=False):
    print(f"{colors.PURPLE}Доступные версии ядра Linux:{colors.END}")
    for idx, version_info in enumerate(versions, start=1):
        formatted_info = format_version_info(version_info)
        print(f"{idx}. {formatted_info}")

    while True:
        try:
            selection = input("Введите номер версии ядра Linux для сборки: ")
            index = int(selection) - 1
            if 0 <= index < len(versions):
                if debug:
                    print(f"{colors.GREEN}Выбранная версия: {versions[index].get('version')}{colors.END}")
                return versions[index].get('version')
            else:
                print(f"{colors.RED}Неверное значение. Пожалуйста, выберите номер из списка{colors.END}")
        except ValueError:
            print(f"{colors.RED}Неверное значение. Пожалуйста, введите число (номер из списка).{colors.END}")

def download_kernel(version, debug=False):
    filename = f"linux-{version}.tar.xz"
    if os.path.exists(filename):
        print(f"{colors.GREEN}Ядро {filename} уже загруженно. Пропуск загрузки.{colors.END}")
        return

    url = f"{KERNEL_BASE_URL}/pub/linux/kernel/v{version.split('.')[0]}.x/linux-{version}.tar.xz"
    if debug:
        print(f"{colors.CYAN}Загрузка ядра с {url}{colors.END}")
    response = requests.get(url, stream=True)

    if response.status_code == 200:
        total_size = int(response.headers.get('content-length', 0))
        downloaded_size = 0
        with open(filename, 'wb') as file:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    file.write(chunk)
                    downloaded_size += len(chunk)
                    print_progress_bar(downloaded_size, total_size, prefix=f"{colors.BLUE}Загрузка:{colors.END}", suffix=f"{colors.GREEN}Завершено{colors.END}", length=50)
        print(f"\nDownloaded {filename}")
        if debug:
            print(f"{colors.GREEN}Ядро загружено в: {filename}{colors.END}")
    else:
        print(f"{colors.RED}Ошибка загрузки ядра. Проверьте версию и попробуйте ещё раз.{colors.END}")


def extract_kernel(version, debug=False):
    dirname = f"linux-{version}"
    if os.path.exists(dirname):
        print(f"{colors.GREEN}Ядро уже извлечено в {dirname}. Пропуск распаковки архива.{colors.END}")
        return

    if debug:
        print(f"{colors.CYAN}Распаковка linux-{version}.tar.xz{colors.END}")
    with tarfile.open(f"linux-{version}.tar.xz", 'r:xz') as tar:
        total_files = len(tar.getmembers())
        extracted_files = 0
        for member in tar.getmembers():
            tar.extract(member)
            extracted_files += 1
            print_progress_bar(extracted_files, total_files, prefix=f"{colors.BLUE}Распаковка:{colors.END}", suffix=f"{colors.GREEN}Завершено{colors.END}", length=50)
    print(f"\nИзвлечено linux-{version}")
    if debug:
        print(f"{colors.GREEN}Ядро распоковано в {dirname}{colors.END}")


def apply_patch(version, debug=False):
    apply_patch = input(f"{colors.YELLOW}У вас есть patch-файл? (yes/no): {colors.END}").strip().lower()
    if apply_patch == 'yes':
        patch_in_current_dir = input(f"{colors.YELLOW}Patch-файл в данной директории? (yes/no): {colors.END}").strip().lower()
        if patch_in_current_dir == 'yes':
            patch_files = [f for f in os.listdir('.') if f.endswith('.patch')]
            if patch_files:
                patch_file = patch_files[0]
            else:
                print(f"{colors.RED}Не надено файлов с расширением .patch в данной директории.{colors.END}")
                return
        else:
            patch_dir = input(f"{colors.YELLOW}Введите директорию в которой находиться patch-файл: {colors.END}").strip()
            patch_files = [f for f in os.listdir(patch_dir) if f.endswith('.patch')]
            if patch_files:
                patch_file = os.path.join(patch_dir, patch_files[0])
            else:
                print(f"{colors.RED}Не надено файлов с расширением .patch в директории {patch_dir}.{colors.END}")
                return
        if debug:
            print(f"{colors.CYAN}Применение .patch {patch_file}{colors.END}")
        os.system(f"patch -p1 < {patch_file}")
        print(f"{colors.GREEN}Задача выполнена успешно.{colors.END}")

def print_progress_bar(iteration, total, prefix='', suffix='', decimals=1, length=100, fill='█'):
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + '-' * (length - filled_length)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end='\r')
    if iteration == total:
        print()

def install_packages(debug):
    packages = [
    "base-devel",
    "xmlto",
    "kmod",
    "inetutils",
    "bc",
    "libelf",
    "git",
    "cpio",
    "perl",
    "tar",
    "xz"
    ]
    package_list = ' '.join(packages)
    print(f"{colors.CYAN}Установка необходимых зависимостей: {package_list}{colors.END}")
    if debug:
        print(f"{colors.CYAN}Выполнение 'sudo pacman -Syu --needed {package_list}'{colors.END}")
    subprocess.run(["sudo", "pacman", "-Syu", "--needed", *packages])
    print(f"{colors.GREEN}Утсановка пакетов  завершена{colors.END}")

def configure_kernel(version, debug=False):
    os.chdir(f"linux-{version}")
    print(f"{colors.PURPLE}Опции:{colors.END}")
    print(f"{colors.BOLD}1.{colors.END} Использование стандартной конфигурации")
    print(f"{colors.BOLD}2.{colors.END} Использование конфигурации из scratch")
    print(f"{colors.BOLD}3.{colors.END} Настрорйка стандартной конфигурации")
    while True:
        config_option = input(f"{colors.YELLOW}Введите номер (1/2/3): {colors.END}")
        if config_option == '1':
            if debug:
                print(f"{colors.CYAN}Выполнение 'zcat /proc/config.gz > .config'{colors.END}")
            os.system("zcat /proc/config.gz > .config")
            print(f"{colors.GREEN}Ядро настроено с текущей конфигурацией запуска ядра{colors.END}")
            break
        elif config_option == '2':
            if debug:
                print(f"{colors.CYAN}Выполнение 'make menuconfig'{colors.END}")
            os.system("make menuconfig")
            print(f"{colors.GREEN}Настройка ядра из scratch завершена{colors.END}")
            break
        elif config_option == '3':
            if debug:
                print(f"{colors.CYAN}Выполнение 'zcat /proc/config.gz > .config' следует из 'make menuconfig'{colors.END}")
            os.system("zcat /proc/config.gz > .config")
            os.system("make menuconfig")
            print(f"{colors.GREEN}Ядро настроено с изменением текущей конфигурацией запуска ядра{colors.END}")
            break
        else:
            print(f"{colors.RED}Неверный выбор. Пожалуйста, введите 1, 2 или 3.{colors.END}")
    os.chdir("..")

def compile_kernel(version, debug=False):
    os.chdir(f"linux-{version}")
    print(f"{colors.CYAN}Сборка ядра{colors.END}")
    if debug:
        print(f"{colors.CYAN}Выполнение 'make -j$(nproc)'{colors.END}")
    subprocess.run(["make", "-j20",])
    subprocess.run(["make", "bzImage",])
    print(f"{colors.GREEN}Сборка ядра завершена{colors.END}")
    os.chdir("..")

def install_kernel(version, debug=False):
    os.chdir(f"linux-{version}")
    print(f"{colors.CYAN}Установка модулей ядра{colors.END}")
    if debug:
        print(f"{colors.CYAN}Выполнение 'sudo make modules_install'{colors.END}")
    subprocess.run(["sudo", "make", "modules_install"])
    print(f"{colors.CYAN}Установка ядра{colors.END}")
    if debug:
         print(f"{colors.CYAN}Выполнение 'sudo make modules'{colors.END}")
         subprocess.run(["sudo", "make", "modules"])
    if debug:
        print(f"{colors.CYAN}Выполнение 'sudo make install'{colors.END}")
    subprocess.run(["sudo", "make", "install"])
    print(f"{colors.GREEN}Установка ядра завершена{colors.END}")
    os.chdir("..")
    bzImage_path = f"linux-{version}/arch/x86/boot/bzImage"
    target_path = f"/boot/vmlinuz-linux-{version}"

    # Ensure bzImage exists
    if os.path.exists(bzImage_path):
        print(f"{colors.CYAN}Копирование bzImage в {target_path}{colors.END}")
        if debug:
            print(f"{colors.CYAN}Выполнение 'sudo cp -v {bzImage_path} {target_path}'{colors.END}")
        subprocess.run(["sudo", "cp", "-v", bzImage_path, target_path])
        print(f"{colors.GREEN}bzImage скопировано в {target_path}{colors.END}")
    else:
        print(f"{colors.RED}Ошибка: bzImage не найдено в {bzImage_path}{colors.END}")
        return

def create_initramfs(version, debug=False):
    version_parts = version.split('.')
    if len(version_parts) == 2:
        version = f"{version}.0"

    print(f"{colors.CYAN}Создание initramfs{colors.END}")
    if debug:
        print(f"{colors.CYAN}Выполнение 'sudo mkinitcpio -k {version} -c /etc/mkinitcpio.conf -g /boot/initramfs-linux-{version}.img'{colors.END}")
    subprocess.run(["sudo", "mkinitcpio", "-k", version, "-c", "/etc/mkinitcpio.conf", "-g", f"/boot/initramfs-linux-{version}.img"])
    print(f"{colors.GREEN}создание Initramfs завершено{colors.END}")


def update_bootloader(version, debug=False):
    bootloader = check_bootloader()
    if bootloader == 'grub':
        print(f"{colors.CYAN}Обновление конфигурации GRUB{colors.END}")
        os.system("sudo grub-mkconfig -o /boot/grub/grub.cfg")
        print(f"{colors.GREEN}Конфигурация GRUB обновлена{colors.END}")
    elif bootloader == 'systemd-boot':
        print(f"{colors.CYAN}Обновление конфигурации systemd-boot{colors.END}")
        os.system("sudo bootctl update")
        print(f"{colors.GREEN}Конфигурация systemd-boot обновлена{colors.END}")
    else:
        print(f"{colors.RED}Поддерживаемые загрузчики не найдены.{colors.END}")

def check_bootloader(debug=False):
    if debug:
        print(f"{colors.CYAN}Проверка загрузчика{colors.END}")
    try:
        bootctl_output = subprocess.run(['bootctl', 'status'], capture_output=True, text=True)
        if 'Systemd' in bootctl_output.stdout:
            if debug:
                print(f"{colors.GREEN}Загрузчик systemd найден{colors.END}")
            return 'systemd-boot'
    except FileNotFoundError:
        pass

    try:
        grub_output = subprocess.run(['grub-install', '--version'], capture_output=True, text=True)
        if 'GRUB' in grub_output.stdout:
            if debug:
                print(f"{colors.GREEN}Загрузчик GRUB найден{colors.END}")
            return 'grub'
    except FileNotFoundError:
        pass

    if debug:
        print(f"{colors.RED}Поддерживаемые загрузчики не найдены.{colors.END}")
    return None

def disable_secureboot_keyrings():
    disable_keyrings = input(f"{colors.YELLOW}Вы хотите отключить Secure Boot keyrings? (yes/no): {colors.END}").strip().lower()
    if disable_keyrings == 'yes':
        os.system("sudo scripts/config --disable SYSTEM_TRUSTED_KEYS")
        os.system("sudo scripts/config --disable SYSTEM_REVOCATION_KEYS")
        os.system("sudo scripts/config --set-str CONFIG_SYSTEM_TRUSTED_KEYS ''")
        os.system("sudo scripts/config --set-str CONFIG_SYSTEM_REVOCATION_KEYS ''")
        print(f"{colors.GREEN}Secure Boot keyrings disabled successfully.{colors.END}")
    else:
        print(f"{colors.YELLOW}Secure Boot keyrings не были модифицированы.{colors.END}")
packages = [
    "base-devel",
    "xmlto",
    "kmod",
    "inetutils",
    "bc",
    "libelf",
    "git",
    "cpio",
    "perl",
    "tar",
    "xz"
]

if __name__ == "__main__":
    debug = input(f"{colors.YELLOW}Включить режим отладки? (yes/no): {colors.END}").strip().lower() == 'yes'

    versions = get_available_versions(debug)
    if not versions:
        print(f"{colors.RED}Не получено ни одной версии. Выход.{colors.END}")
        sys.exit(1)

    version = choose_kernel_version(versions, debug)
    download_kernel(version, debug)
    extract_kernel(version, debug)
    install_packages(packages, debug)
    apply_patch(version, debug)
    configure_kernel(version, debug)
    disable_secureboot_keyrings()
    compile_kernel(version, debug)
    install_kernel(version, debug)
    create_initramfs(version, debug)
    update_bootloader(version, debug)
    check_bootloader(debug)
