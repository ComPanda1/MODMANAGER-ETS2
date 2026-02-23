import os
import re
import sys
import time
import shutil
import zipfile
import datetime
import threading
import subprocess
import urllib.request

# Attempt to import colorama for better colors
# When compiled with PyInstaller, this will be bundled.
try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    HAS_COLORAMA = True
except ImportError:
    HAS_COLORAMA = False

# ---------------------------------------------------------------------------
# COLORS (Soft Palette)
# ---------------------------------------------------------------------------

class Color:
    INFO  = Fore.CYAN if HAS_COLORAMA else ""           # Info / Header
    OK    = Fore.GREEN if HAS_COLORAMA else ""          # Success
    ERROR = Fore.LIGHTRED_EX if HAS_COLORAMA else ""    # Error
    WARN  = Fore.YELLOW if HAS_COLORAMA else ""         # Warning / Backup
    BLUE  = Fore.BLUE if HAS_COLORAMA else ""           # Details
    GRAY  = Fore.WHITE + Style.DIM if HAS_COLORAMA else "" # Gray / Secondary
    RESET = Style.RESET_ALL if HAS_COLORAMA else ""     # Reset
    BOLD  = Style.BRIGHT if HAS_COLORAMA else ""        # Bold

# ---------------------------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------------------------

# Use a strategy to find the base directory that works both in script and EXE mode
if getattr(sys, 'frozen', False):
    # If running as EXE
    BASE_DIR = os.path.dirname(sys.executable)
else:
    # If running as script
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SII_DECRYPT_EXE = os.path.join(BASE_DIR, "SII_Decrypt.exe")
SII_ZIP         = os.path.join(BASE_DIR, "SII_Decrypt.zip")
LIST_FILE       = os.path.join(BASE_DIR, "list.txt")
ETS2_PROFILES_DIR = os.path.join(os.path.expanduser("~"), "Documents", "Euro Truck Simulator 2", "profiles")

SII_TOOLS_URL = (
    "https://www.dropbox.com/scl/fi/95lxm718dh54fgbth3gkn/sii_tools.zip"
    "?rlkey=05hnsrgz1txfj1l3wdh1q47x1&st=sgmls9ar&dl=1"
)

GAME_PROCESS_NAME = "eurotrucks2.exe"

# ---------------------------------------------------------------------------
# BILINGUAL TEXTS
# ---------------------------------------------------------------------------

LOCALIZATION = {
    "es": {
        "title"              : "ETS2 - Gestor de Mods",
        "option_extract"     : "1. Extraer lista de Mods",
        "option_apply"       : "2. Aplicar lista de Mods",
        "option_backups"     : "3. Eliminar todos los Backups",
        "option_exit"        : "4. Salir",
        "choose"             : "Elige una opción: ",
        "invalid_choice"     : "Opción no válida. Elige 1, 2, 3 o 4.",
        "setting_up"         : "Configurando entorno",
        "game_running"       : "ETS2 está abierto. Ciérralo antes de continuar.",
        "list_not_found"     : "No se encontró list.txt en la carpeta del script.",
        "tools_ready"        : "Herramientas de descifrado listas.",
        "downloading_tools"  : "Descargando herramientas...",
        "extracting_files"   : "Extrayendo archivos...",
        "invalid_zip"        : "El archivo descargado no es válido.",
        "sii_error"          : "No se pudo preparar SII_Decrypt.exe.",
        "download_error"     : "Error al descargar herramientas.",
        "profiles_not_found" : "No se encontró la carpeta de perfiles de ETS2.",
        "no_profiles"        : "No se encontró ningún perfil de usuario.",
        "no_sii_file"        : "El perfil seleccionado no tiene profile.sii.",
        "profile_loaded"     : "Perfil cargado con éxito",
        "backup_created"     : "Copia de seguridad creada",
        "already_editable"   : "El archivo ya es editable directamente.",
        "decrypting_profile" : "Descifrando perfil para edición...",
        "decrypted_ok"       : "Perfil descifrado.",
        "decrypt_failed"     : "Error crítico al usar SII_Decrypt.exe.",
        "mods_extracted_count": "mods detectados en lista",
        "mods_applied_count" : "mods aplicados al perfil.",
        "no_mods_found"      : "No hay mods válidos en la lista.",
        "format_error"       : "Error de formato en profile.sii.",
        "profile_saved"      : "Perfil optimizado y guardado.",
        "changes_saved"      : "Cambios guardados correctamente.",
        "success_apply"      : "¡ORDEN DE MODS ACTUALIZADO!",
        "backup_info"        : "Se ha guardado un backup en",
        "unexpected_error"   : "Error inesperado. Restaurando copia de seguridad...",
        "restore_ok"         : "Perfil restaurado al estado original.",
        "extract_success"    : "LISTA GENERADA CON ÉXITO",
        "mods_exported"      : "mods exportados a list.txt",
        "finalizing"         : "Finalizando proceso...",
        "press_enter"        : "\nPresiona [Enter] para continuar...",
        "goodbye"            : "Cerrando gestor. ¡Buen viaje!",
        "fatal_error"        : "HA OCURRIDO UN PROBLEMA",
        "ask_close_game"     : "ETS2 está abierto. ¿Quieres cerrarlo ahora? (s/n): ",
        "closing_game"       : "Cerrando el juego",
        "game_closed_ok"     : "Juego cerrado con éxito.",
        "game_close_failed"  : "No se pudo cerrar el juego. Por favor, ciérralo manualmente.",
        "confirm_delete"     : "¿Estás seguro de que quieres eliminar TODOS los backups? (s/n): ",
        "deleting_backups"   : "Borrando copias de seguridad",
        "backups_deleted"    : "Backups eliminados correctamente.",
        "no_backups"         : "No se encontraron backups para eliminar."
    },
    "en": {
        "title"              : "ETS2 - Mod Manager",
        "option_extract"     : "1. Extract Mod List",
        "option_apply"       : "2. Apply Mod List",
        "option_backups"     : "3. Delete all Backups",
        "option_exit"        : "4. Exit",
        "choose"             : "Choose an option: ",
        "invalid_choice"     : "Invalid option. Choose 1, 2, 3 or 4.",
        "setting_up"         : "Setting up environment",
        "game_running"       : "ETS2 is running. Please close it first.",
        "list_not_found"     : "list.txt not found in folder.",
        "tools_ready"        : "Decryption tools are ready.",
        "downloading_tools"  : "Downloading tools...",
        "extracting_files"   : "Extracting files...",
        "invalid_zip"        : "Downloaded file is invalid.",
        "sii_error"          : "Could not set up SII_Decrypt.exe.",
        "download_error"     : "Error downloading tools.",
        "profiles_not_found" : "ETS2 profiles folder not found.",
        "no_profiles"        : "No user profile found.",
        "no_sii_file"        : "Selected profile has no profile.sii.",
        "profile_loaded"     : "Profile loaded successfully",
        "backup_created"     : "Backup copy created",
        "already_editable"   : "File is already editable.",
        "decrypting_profile" : "Decrypting profile for editing...",
        "decrypted_ok"       : "Profile decrypted.",
        "decrypt_failed"     : "Critical error with SII_Decrypt.exe.",
        "mods_extracted_count": "mods detected in list",
        "mods_applied_count" : "mods applied to profile.",
        "no_mods_found"      : "No valid mods found in the list.",
        "format_error"       : "Format error in profile.sii.",
        "profile_saved"      : "Profile optimized and saved.",
        "changes_saved"      : "Changes saved successfully.",
        "success_apply"      : "MOD ORDER UPDATED!",
        "backup_info"        : "A backup has been saved at",
        "unexpected_error"   : "Unexpected error. Restoring backup...",
        "restore_ok"         : "Profile restored to original state.",
        "extract_success"    : "LIST GENERATED SUCCESSFULLY",
        "mods_exported"      : "mods exported to list.txt",
        "finalizing"         : "Wrapping up...",
        "press_enter"        : "\nPress [Enter] to continue...",
        "goodbye"            : "Closing manager. Enjoy the road!",
        "fatal_error"        : "A PROBLEM OCCURRED",
        "ask_close_game"     : "ETS2 is running. Do you want to close it now? (y/n): ",
        "closing_game"       : "Closing the game",
        "game_closed_ok"     : "Game closed successfully.",
        "game_close_failed"  : "Could not close the game. Please close it manually.",
        "confirm_delete"     : "Are you sure you want to delete ALL backups? (y/n): ",
        "deleting_backups"   : "Deleting backup copies",
        "backups_deleted"    : "Backups deleted successfully.",
        "no_backups"         : "No backups found to delete."
    },
}

current_lang = "es"

# ---------------------------------------------------------------------------
# CONSOLE HELPERS
# ---------------------------------------------------------------------------

def translate(key):
    return LOCALIZATION[current_lang][key]

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def draw_separator(width=60, color=Color.GRAY):
    print(f"{color}" + "─" * width + f"{Color.RESET}")

def draw_title_box(text):
    width = 60
    print(f"{Color.INFO}╔" + "═" * (width - 2) + "╗")
    padding = width - 2 - len(text)
    left_pad = padding // 2
    right_pad = padding - left_pad
    print(f"{Color.INFO}║{Color.BOLD}{' ' * left_pad}{text.upper()}{' ' * right_pad}{Color.RESET}{Color.INFO}║")
    print(f"{Color.INFO}╚" + "═" * (width - 2) + "╝" + f"{Color.RESET}")

def print_ok(msg):
    print(f"  {Color.OK}✓  {Color.RESET}{msg}")

def print_info(msg):
    print(f"  {Color.INFO}→  {Color.RESET}{msg}")

def print_warn(msg):
    print(f"  {Color.WARN}⚠  {Color.RESET}{msg}")

def print_error_msg(msg):
    print(f"\n  {Color.ERROR}✗  {msg}{Color.RESET}")

def handle_fatal(key_or_msg):
    msg = translate(key_or_msg) if key_or_msg in LOCALIZATION[current_lang] else key_or_msg
    print(f"\n  {Color.ERROR}[ {translate('fatal_error')} ]{Color.RESET}")
    print(f"  {Color.ERROR}» {msg}{Color.RESET}")
    input(f"{Color.GRAY}{translate('press_enter')}{Color.RESET}")
    sys.exit(1)

# ---------------------------------------------------------------------------
# LOADING SPINNER
# ---------------------------------------------------------------------------

class LoadingSpinner:
    FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

    def __init__(self, text):
        self.text    = text
        self._active  = False
        self._thread  = None

    def _animate(self):
        i = 0
        while self._active:
            frame = self.FRAMES[i % len(self.FRAMES)]
            sys.stdout.write(f"\r  {Color.INFO}{frame}{Color.RESET}  {Color.GRAY}{self.text}...{Color.RESET}")
            sys.stdout.flush()
            time.sleep(0.08)
            i += 1
        sys.stdout.write("\r" + " " * 65 + "\r")
        sys.stdout.flush()

    def __enter__(self):
        self._active = True
        self._thread = threading.Thread(target=self._animate, daemon=True)
        self._thread.start()
        return self

    def __exit__(self, *args):
        self._active = False
        self._thread.join()

# ---------------------------------------------------------------------------
# INITIAL PHASE
# ---------------------------------------------------------------------------

def select_language():
    global current_lang
    clear_screen()
    print()
    print(f"  {Color.INFO}╔═════════════════════════════════╗")
    print(f"  ║ {Color.BOLD}SELECT LANGUAGE / ELIGE IDIOMA {Color.RESET}{Color.INFO} ║")
    print(f"  ╚═════════════════════════════════╝{Color.RESET}")
    print()
    print(f"    {Color.INFO}[1]{Color.RESET} Español")
    print(f"    {Color.INFO}[2]{Color.RESET} English")
    print()

    while True:
        choice = input(f"    {Color.BOLD}>> {Color.RESET}").strip().lower()
        if choice in ("1", "es", "esp", "español"):
            current_lang = "es"
            break
        elif choice in ("2", "en", "eng", "english"):
            current_lang = "en"
            break

def initial_setup():
    clear_screen()
    draw_title_box(translate("title"))
    print()

    profile_file = None
    errors = []

    with LoadingSpinner(translate("setting_up")):
        if not os.path.isfile(SII_DECRYPT_EXE):
            _download_tools(errors)
            _extract_tools(errors)

        if not errors:
            profile_file = _find_active_profile(errors)
        time.sleep(4)

    if errors:
        for e in errors:
            print_error_msg(e)
        input(translate("press_enter"))
        sys.exit(1)

    print_ok(translate("tools_ready"))
    print_info(f"{translate('profile_loaded')}: {Color.BOLD}{os.path.basename(os.path.dirname(profile_file))}{Color.RESET}")
    print()
    time.sleep(0.5)
    return profile_file

def _download_tools(errors):
    try:
        urllib.request.urlretrieve(SII_TOOLS_URL, SII_ZIP)
    except Exception:
        errors.append(translate("download_error"))
    if not os.path.isfile(SII_ZIP):
        errors.append(translate("download_error"))

def _extract_tools(errors):
    if errors or not os.path.isfile(SII_ZIP): return
    try:
        with zipfile.ZipFile(SII_ZIP, "r") as zf:
            zf.extractall(BASE_DIR)
    except zipfile.BadZipFile:
        errors.append(translate("invalid_zip"))
    finally:
        if os.path.isfile(SII_ZIP): os.remove(SII_ZIP)
    if not os.path.isfile(SII_DECRYPT_EXE):
        errors.append(translate("sii_error"))

def _find_active_profile(errors):
    if not os.path.isdir(ETS2_PROFILES_DIR):
        errors.append(translate("profiles_not_found"))
        return None
    folders = [e.path for e in os.scandir(ETS2_PROFILES_DIR) if e.is_dir()]
    if not folders:
        errors.append(translate("no_profiles"))
        return None
    # Just take the first profile found for now
    file_path = os.path.join(folders[0], "profile.sii")
    if not os.path.isfile(file_path):
        errors.append(translate("no_sii_file"))
        return None
    return file_path

# ---------------------------------------------------------------------------
# MAIN MENU
# ---------------------------------------------------------------------------

def main_menu(profile_file):
    while True:
        clear_screen()
        draw_title_box(translate("title"))
        print()
        print(f"  {Color.INFO}[1]{Color.RESET} {translate('option_extract')}")
        print(f"  {Color.INFO}[2]{Color.RESET} {translate('option_apply')}")
        print(f"  {Color.WARN}[3]{Color.RESET} {translate('option_backups')}")
        print(f"  {Color.ERROR}[4]{Color.RESET} {translate('option_exit')}")
        print()
        draw_separator()
        choice = input(f"  {Color.BOLD}{translate('choose')}{Color.RESET}").strip()

        if choice == "1":
            action_extract(profile_file)
        elif choice == "2":
            action_apply(profile_file)
        elif choice == "3":
            action_clean_backups(profile_file)
        elif choice == "4":
            clear_screen()
            print(f"\n  {Color.OK}{translate('goodbye')}{Color.RESET}\n")
            time.sleep(1)
            break
        else:
            print_warn(translate("invalid_choice"))
            time.sleep(1)

# ---------------------------------------------------------------------------
# ACTIONS
# ---------------------------------------------------------------------------

def action_extract(profile_file):
    clear_screen()
    draw_title_box(translate("option_extract").split(". ")[1])
    print()

    if not _handle_game_running():
        return

    _create_profile_backup(profile_file)
    was_encrypted = _decrypt_if_needed(profile_file)
    mods = _get_mods_from_profile(profile_file)

    if was_encrypted:
        _run_sii_decrypt(profile_file)

    with open(LIST_FILE, "w", encoding="utf-8") as f:
        for line in mods: f.write(line + "\n")

    with LoadingSpinner(translate("option_extract").split(". ")[1]):
        time.sleep(4)

    if was_encrypted:
        print_ok(translate("decrypted_ok"))
        print_ok(translate("profile_saved")) # Reuse key if available
    else:
        print_ok(translate("changes_saved"))

    print()
    draw_separator()
    print(f"  {Color.OK}{translate('extract_success')}{Color.RESET}")
    print_info(f"{Color.BOLD}{len(mods)}{Color.RESET} {translate('mods_exported')}")
    draw_separator()
    input(translate("press_enter"))

def action_apply(profile_file):
    clear_screen()
    draw_title_box(translate("option_apply").split(". ")[1])
    print()

    if not _handle_game_running():
        return

    if not os.path.isfile(LIST_FILE):
        print_error_msg(translate("list_not_found"))
        input(translate("press_enter"))
        return

    backup_path = _create_profile_backup(profile_file)
    was_encrypted = _decrypt_if_needed(profile_file)
    new_mods = _load_mods_from_list_file()
    print_info(f"{translate('mods_extracted_count')}: {Color.BOLD}{len(new_mods)}{Color.RESET}")

    try:
        content = _read_file_lines(profile_file)
        new_content = _replace_mod_block(content, new_mods)
        _write_file_lines(profile_file, new_content)
    except Exception as exc:
        print_error_msg(f"{translate('unexpected_error')} ({exc})")
        shutil.copy2(backup_path, profile_file)
        print_ok(translate("restore_ok"))
        if was_encrypted: _run_sii_decrypt(profile_file)
        input(translate("press_enter"))
        return

    if was_encrypted:
        _run_sii_decrypt(profile_file)
    
    with LoadingSpinner(translate("option_apply").split(". ")[1]):
        time.sleep(4)

    if was_encrypted:
        print_ok(translate("decrypted_ok"))
        print_ok(translate("profile_saved"))
    else:
        print_ok(translate("changes_saved"))

    print()
    draw_separator()
    print(f"  {Color.OK}{translate('success_apply')}{Color.RESET}")
    print_info(f"{Color.BOLD}{len(new_mods)}{Color.RESET} {translate('mods_applied_count')}")
    print(f"  {Color.GRAY}{translate('backup_info')}: {os.path.basename(backup_path)}{Color.RESET}")
    draw_separator()
    input(translate("press_enter"))

def action_clean_backups(profile_file):
    clear_screen()
    draw_title_box(translate("option_backups").split(". ")[1])
    print()

    profile_dir = os.path.dirname(profile_file)
    backups = [f for f in os.listdir(profile_dir) if f.startswith("profile_backup_") and f.endswith(".sii")]

    if not backups:
        print_info(translate("no_backups"))
        input(translate("press_enter"))
        return

    print_warn(f"Found {len(backups)} backup copies.")
    confirm = input(f"  {Color.BOLD}{translate('confirm_delete')}{Color.RESET}").strip().lower()

    if confirm in ("s", "si", "y", "yes"):
        with LoadingSpinner(translate("deleting_backups")):
            for b in backups:
                try:
                    os.remove(os.path.join(profile_dir, b))
                except:
                    pass
            time.sleep(4)
        print_ok(translate("backups_deleted"))
    
    input(translate("press_enter"))

# ---------------------------------------------------------------------------
# CORE LOGIC
# ---------------------------------------------------------------------------

def _get_mods_from_profile(profile_file):
    pattern = re.compile(r"^\s*active_mods\[\d+\]:\s*(.+)")
    mods = []
    with open(profile_file, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            m = pattern.match(line)
            if m:
                val = m.group(1).strip()
                mods.append(f" active_mods[{len(mods)}]: {val}")
    if not mods: handle_fatal("no_mods_found")
    return mods

def _load_mods_from_list_file():
    pattern = re.compile(r"active_mods\[\d+\]:\s*(.+)")
    mods = []
    with open(LIST_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith(("#", "::")): continue
            m = pattern.match(line)
            if m:
                val = m.group(1).strip()
                mods.append(f" active_mods[{len(mods)}]: {val}")
    if not mods: handle_fatal("no_mods_found")
    return mods

def _replace_mod_block(content, new_mods):
    entry_pattern = re.compile(r"^\s*active_mods\[\d+\]")
    count_pattern = re.compile(r"^\s*active_mods:\s*\d+")
    result, inserted = [], False
    for line in content:
        if entry_pattern.match(line): continue
        if count_pattern.match(line):
            result.append(f" active_mods: {len(new_mods)}\n")
            for mod in new_mods: result.append(mod + "\n")
            inserted = True
            continue
        result.append(line)
    if not inserted: handle_fatal("format_error")
    return result

def _is_game_running():
    res = subprocess.run(["tasklist", "/FI", f"IMAGENAME eq {GAME_PROCESS_NAME}"], capture_output=True, text=True)
    return GAME_PROCESS_NAME.lower() in res.stdout.lower()

def _handle_game_running():
    if not _is_game_running():
        return True
    
    print_warn(translate("game_running"))
    confirm = input(f"  {Color.BOLD}{translate('ask_close_game')}{Color.RESET}").strip().lower()
    
    if confirm in ("s", "si", "y", "yes"):
        with LoadingSpinner(translate("closing_game")):
            subprocess.run(["taskkill", "/F", "/IM", GAME_PROCESS_NAME], capture_output=True)
            time.sleep(2)
        
        if not _is_game_running():
            print_ok(translate("game_closed_ok"))
            return True
        else:
            print_error_msg(translate("game_close_failed"))
            input(translate("press_enter"))
            return False
    else:
        return False

def _create_profile_backup(profile_file):
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    name = f"profile_backup_{ts}.sii"
    path = os.path.join(os.path.dirname(profile_file), name)
    shutil.copy2(profile_file, path)
    print_ok(translate("backup_created"))
    return path

def _decrypt_if_needed(profile_file):
    encrypted = _is_encrypted(profile_file)
    if encrypted:
        print_info(translate("decrypting_profile"))
        _run_sii_decrypt(profile_file)
        # We don't print "Decryption complete" here to avoid line conflicts with Spinner later, 
        # or we print it after the spinner finishes.
    else:
        print_ok(translate("already_editable"))
    return encrypted

def _is_encrypted(file_path):
    with open(file_path, "rb") as f: return f.read(8) != b"SiiNunit"

def _run_sii_decrypt(file_path):
    if subprocess.run([SII_DECRYPT_EXE, file_path], capture_output=True).returncode != 0: handle_fatal("decrypt_failed")

def _read_file_lines(file_path):
    with open(file_path, "r", encoding="utf-8", errors="replace") as f: return f.readlines()

def _write_file_lines(file_path, lines):
    with open(file_path, "w", encoding="utf-8", newline="\n") as f: f.writelines(lines)

def main():
    select_language()
    profile_file = initial_setup()
    main_menu(profile_file)

if __name__ == "__main__":
    main()
