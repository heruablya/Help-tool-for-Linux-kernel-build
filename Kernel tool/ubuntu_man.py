#!/usr/bin/env python3
import os
import re

GRUB_CFG = "/boot/grub/grub.cfg"

def list_installed_kernels():
    kernels = []
    if os.path.exists(GRUB_CFG):
        with open(GRUB_CFG, 'r') as grub_file:
            for line in grub_file:
                match = re.search(r'vmlinuz-(\S+)', line)
                if match:
                    kernels.append(match.group(1))
    if not kernels:
        print("Ни одного ядра не установлено.")
    else:
        print("Установленные ядра:")
        for idx, kernel in enumerate(kernels, start=1):
            print(f"{idx}. {kernel}")
    return kernels

def rename_kernel(kernels):
    list_installed_kernels()
    try:
        idx = int(input("Введите номер ядра, чтобы переименовать: ")) - 1
        if idx < 0 or idx >= len(kernels):
            print("Ядро под выбранным номером отсутсвует.")
            return

        old_name = kernels[idx]
        new_name = input(f"Введите новое имя для ядра {old_name}: ")
        old_vmlinuz = f"/boot/vmlinuz-{old_name}"
        new_vmlinuz = f"/boot/vmlinuz-{new_name}"
        if os.path.exists(old_vmlinuz):
            os.rename(old_vmlinuz, new_vmlinuz)
            print(f"Переименованно с {old_name} на {new_name}.")
        else:
            print(f"{old_vmlinuz} не существует.")
    except (ValueError, IndexError):
        print("Ядро под выбранным номером отсутвует.")

def delete_kernel(kernels):
    list_installed_kernels()
    try:
        idx = int(input("Введите номер ядра для удалания: ")) - 1
        if idx < 0 or idx >= len(kernels):
            print("Ядра с выбранным номером не существует.")
            return

        kernel_name = kernels[idx]
        confirm = input(f"Вы уверенны, что хотите удалить  {kernel_name}? (y/N): ")
        if confirm.lower() == 'y':
            vmlinuz = f"/boot/vmlinuz-{kernel_name}"
            initrd = f"/boot/initrd.img-{kernel_name}"
            os.remove(vmlinuz)
            os.remove(initrd)
            print(f"Удалено {kernel_name}.")
        else:
            print("Отмена удаления.")
    except (ValueError, IndexError):
        print("Ядра под выбранным номером не существует.")
    except FileNotFoundError as e:
        print(f"Ошибка удаления файла: {e}")

def manage_kernels():
    kernels = list_installed_kernels()
    if not kernels:
        return

    print("/nУправление загруженными ядрами:")
    print("1. Переименовать ядро")
    print("2. Удалить ядро")
    choice = input("Введите ваш выбор: ")

    if choice == '1':
        rename_kernel(kernels)
    elif choice == '2':
        delete_kernel(kernels)
    else:
        print("Выбранного пункта не существует введите 1 или 2.")
