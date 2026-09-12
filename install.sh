#!/usr/bin/bash

CYAN='\033[0;36m'
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
RESET='\033[0m'

USERNAME="axellpemula"
REPO="Generator-id"
BRANCH="main"

clear
echo -e "${CYAN}=========================================${RESET}"
echo -e "${GREEN}    AUTO INSTALLER XLOOP TOOLS    ${RESET}"
echo -e "${CYAN}=========================================${RESET}"
echo ""

echo -e "${YELLOW}[+] Memperbarui sistem Termux...${RESET}"
pkg update -y && pkg upgrade -y

echo -e "${YELLOW}[+] Memasang dependensi dasar...${RESET}"
pkg install python clang make git libcrypt curl -y

echo -e "${YELLOW}[+] Memasang modul Python...${RESET}"
python -m pip install --upgrade pip
pip install colorama requests urllib3 pycryptodome pyTelegramBotAPI

echo -e "${YELLOW}[+] Membuat struktur folder...${RESET}"
mkdir -p XLOOP_GEN/NORMAL \
         XLOOP_GEN/GHOST \
         XLOOP_GEN/COUPLE \
         XLOOP_GEN/RATE \
         XLOOP_GEN/RATE/LEGENDARY \
         XLOOP_GEN/RATE/MYTHIC \
         XLOOP_GEN/RATE/EPIC \
         XLOOP_GEN/RATE/RARE \
         XLOOP_GEN/TOKENS

echo -e "${YELLOW}[+] Mengunduh file terbaru...${RESET}"
curl -sL -o id.py "https://raw.githubusercontent.com/${USERNAME}/${REPO}/${BRANCH}/XLOOP_GEN.py"

echo ""
echo -e "${GREEN}===========================================${RESET}"
echo -e "${GREEN}[✔] Pemasangan Selesai!${RESET}"
echo -e "${CYAN}Jalankan skrip dengan perintah:${RESET} ${YELLOW}python XLOOP_GEN.py${RESET}"
echo -e "${GREEN}===========================================${RESET}"
