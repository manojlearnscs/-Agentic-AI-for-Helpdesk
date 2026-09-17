import os
import zipfile
import shutil

def archive_project():
    project_dir = os.path.dirname(os.path.abspath(__file__))
    zip_filename = "ai_it_helpdesk_agent.zip"
    scratch_zip_path = os.path.join(os.path.dirname(project_dir), zip_filename)
    artifact_dir = r"C:\Users\ELCOT\.gemini\antigravity\brain\8abc4e34-5175-4955-8c1e-e9764f82fd75"
    artifact_zip_path = os.path.join(artifact_dir, zip_filename)

    print(f"Archiving project folder: {project_dir}")

    # Exclude temporary cache/pycache files
    ignored_extensions = {".pyc", ".pyo", ".git", ".zip", ".DS_Store"}
    ignored_dirs = {"__pycache__", ".pytest_cache", ".venv", "venv", "env"}

    with zipfile.ZipFile(scratch_zip_path, 'w', zipfile.ZIP_DEFLATED) as ziph:
        for root, dirs, files in os.walk(project_dir):
            # Modify dirs in place to skip ignored directories
            dirs[:] = [d for d in dirs if d not in ignored_dirs]
            
            for file in files:
                if any(file.endswith(ext) for ext in ignored_extensions):
                    continue
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, os.path.dirname(project_dir))
                ziph.write(full_path, rel_path)
                print(f" Added: {rel_path}")

    print(f"\nZip archive created successfully at: {scratch_zip_path}")
    print(f"Archive Size: {os.path.getsize(scratch_zip_path)} bytes")

    # Copy to Artifact directory
    if os.path.exists(artifact_dir):
        shutil.copy2(scratch_zip_path, artifact_zip_path)
        print(f"Copied zip artifact to: {artifact_zip_path}")

if __name__ == "__main__":
    archive_project()
