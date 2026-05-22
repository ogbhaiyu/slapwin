"""SlapWin Production Build Script — Compiles SlapWin.exe and prank.exe for distribution."""

import os
import sys
import shutil
import subprocess
import tempfile


APP_NAME = "SlapWin"
APP_VERSION = "1.0.0"
COMPANY = "SlapWin"
COPYRIGHT = "Copyright © 2026 SlapWin. All rights reserved."
DESCRIPTION_MAIN = "SlapWin — Windows Charger Novelty Tool"
DESCRIPTION_PRANK = "SlapWin Prank Service"


def create_version_file(name, description, version, output_path):
    """Generate a Windows version-info file for PyInstaller."""
    parts = version.split(".")
    major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])

    content = f"""# UTF-8
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=({major}, {minor}, {patch}, 0),
    prodvers=({major}, {minor}, {patch}, 0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
        StringTable(
          u'040904B0',
          [
            StringStruct(u'CompanyName', u'{COMPANY}'),
            StringStruct(u'FileDescription', u'{description}'),
            StringStruct(u'FileVersion', u'{version}'),
            StringStruct(u'InternalName', u'{name}'),
            StringStruct(u'LegalCopyright', u'{COPYRIGHT}'),
            StringStruct(u'OriginalFilename', u'{name}.exe'),
            StringStruct(u'ProductName', u'{APP_NAME}'),
            StringStruct(u'ProductVersion', u'{version}'),
          ]
        )
      ]
    ),
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
"""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
    return output_path


def clean_build_artifacts(root_dir):
    """Remove all build artifacts for a fresh build."""
    dirs_to_remove = [
        os.path.join(root_dir, "build_temp"),
        os.path.join(root_dir, "build_debug_temp"),
        os.path.join(root_dir, "dist_debug"),
        os.path.join(root_dir, "dist"),
    ]
    files_to_remove = [
        os.path.join(root_dir, "SlapWin.spec"),
        os.path.join(root_dir, "prank.spec"),
        os.path.join(root_dir, "prank_debug.spec"),
    ]

    for d in dirs_to_remove:
        if os.path.exists(d):
            shutil.rmtree(d, ignore_errors=True)

    for f in files_to_remove:
        if os.path.exists(f):
            os.remove(f)

    # Remove any debug log files
    for log_file in ["app/prank_service_debug.log"]:
        log_path = os.path.join(root_dir, log_file)
        if os.path.exists(log_path):
            os.remove(log_path)


def build():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    app_dir = os.path.join(root_dir, "app")
    dist_dir = os.path.join(root_dir, "dist")
    build_temp_dir = os.path.join(root_dir, "build_temp")

    # Files
    main_script = os.path.join(app_dir, "main_gui.py")
    prank_script = os.path.join(app_dir, "prank_service.py")
    audio_file = os.path.join(app_dir, "daddy.mp3")
    logo_png = os.path.join(app_dir, "logo.png")
    logo_ico = os.path.join(app_dir, "logo.ico")

    # Check dependencies
    try:
        import PyInstaller
    except ImportError:
        print("ERROR: PyInstaller is not installed. Run: pip install pyinstaller")
        return False

    # Clean previous build artifacts
    print("Cleaning previous build artifacts...")
    clean_build_artifacts(root_dir)

    # Ensure output directories exist
    os.makedirs(dist_dir, exist_ok=True)
    os.makedirs(build_temp_dir, exist_ok=True)

    # Create temporary version info files
    version_dir = tempfile.mkdtemp(prefix="slapwin_version_")
    main_version_file = create_version_file("SlapWin", DESCRIPTION_MAIN, APP_VERSION, os.path.join(version_dir, "main_version.txt"))
    prank_version_file = create_version_file("prank", DESCRIPTION_PRANK, APP_VERSION, os.path.join(version_dir, "prank_version.txt"))

    print(f"\n{'='*50}")
    print(f"  SlapWin Production Build v{APP_VERSION}")
    print(f"{'='*50}")

    # Build SlapWin.exe (Main App)
    print("\n[1/2] Building SlapWin.exe (Main App)...")
    main_cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconsole",
        "--onefile",
        f"--add-data={audio_file};.",
        f"--add-data={logo_png};.",
        f"--add-data={logo_ico};.",
        f"--icon={logo_ico}",
        f"--distpath={dist_dir}",
        f"--workpath={build_temp_dir}",
        f"--version-file={main_version_file}",
        "--name=SlapWin",
        main_script
    ]

    result = subprocess.run(main_cmd, capture_output=True, text=True)
    if result.returncode == 0:
        print("  [OK] SlapWin.exe compiled successfully.")
    else:
        print("  [FAIL] Failed to compile SlapWin.exe.")
        print(result.stderr)
        return False

    # Build prank.exe (Prank Service)
    print("\n[2/2] Building prank.exe (Prank Service)...")
    prank_cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconsole",
        "--onefile",
        f"--add-data={audio_file};.",
        f"--add-data={logo_ico};.",
        f"--icon={logo_ico}",
        f"--distpath={dist_dir}",
        f"--workpath={build_temp_dir}",
        f"--version-file={prank_version_file}",
        "--name=prank",
        prank_script
    ]

    result = subprocess.run(prank_cmd, capture_output=True, text=True)
    if result.returncode == 0:
        print("  [OK] prank.exe compiled successfully.")
    else:
        print("  [FAIL] Failed to compile prank.exe.")
        print(result.stderr)
        return False

    # Clean up temp version files
    shutil.rmtree(version_dir, ignore_errors=True)

    # Clean up build_temp (not needed for distribution)
    shutil.rmtree(build_temp_dir, ignore_errors=True)

    # Remove generated .spec files from root
    for spec in ["SlapWin.spec", "prank.spec"]:
        spec_path = os.path.join(root_dir, spec)
        if os.path.exists(spec_path):
            os.remove(spec_path)

    # Verify no debug logs leaked into dist
    for f in os.listdir(dist_dir):
        if f.endswith(".log"):
            os.remove(os.path.join(dist_dir, f))

    print(f"\n{'='*50}")
    print(f"  Build Complete!")
    print(f"{'='*50}")
    print(f"\n  Output: {dist_dir}")
    print(f"    - SlapWin.exe  ({os.path.getsize(os.path.join(dist_dir, 'SlapWin.exe')) / 1024 / 1024:.1f} MB)")
    print(f"    - prank.exe    ({os.path.getsize(os.path.join(dist_dir, 'prank.exe')) / 1024 / 1024:.1f} MB)")
    print(f"\n  Ready for Gumroad distribution!")
    return True


if __name__ == "__main__":
    success = build()
    sys.exit(0 if success else 1)
