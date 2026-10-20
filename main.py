import shutil
import os
import json
from datetime import datetime
def manage_backups():
    backup_folder = "backups"

    if not os.path.exists(backup_folder):
        print("Backup folder not found.")
        return

    backup_files = [
        name for name in os.listdir(backup_folder)
        if name.endswith(".txt")
    ]

    if not backup_files:
        print("No backup files found.")
        return

    print("\nSort backups by:")
    print("1. Latest First")
    print("2. Oldest First")

    sort_choice = input("Choose sorting option (1/2): ").strip()

    if sort_choice == "2":
        backup_files.sort()
    else:
        backup_files.sort(reverse=True)

    print("\n=== BACKUP MANAGEMENT ===")
    total_backups = len(backup_files)

    total_size = sum(
        os.path.getsize(os.path.join(backup_folder, name))
        for name in backup_files
    )

    print("\n=== BACKUP STATISTICS ===")
    print(f"Total backups: {total_backups}")
    print(f"Total storage used: {total_size / 1024:.2f} KB")
    search_name = input("Search backup filename (Enter to show all): ").strip().lower()
    backup_files = [
    name for name in backup_files
    if search_name in name.lower()
]
    if not backup_files:
        print("No matching backup files found.")
        return
    

    for index, name in enumerate(backup_files, start=1):
        file_path = os.path.join(backup_folder, name)
        size = os.path.getsize(file_path)
        modified = datetime.fromtimestamp(
            os.path.getmtime(file_path)
        ).strftime("%Y-%m-%d %H:%M:%S")

        print(f"{index}. {name}")
        print(f"   Size: {size} bytes")
        print(f"   Modified: {modified}")
    preview_choice = input(
        "\nEnter backup number to preview (or press Enter to skip): "
    ).strip()

    if preview_choice:
        try:
            preview_index = int(preview_choice)

            if 1 <= preview_index <= len(backup_files):
                selected_name = backup_files[preview_index - 1]
                selected_path = os.path.join(
                    backup_folder, selected_name
                )

                print("\n=== BACKUP PREVIEW ===")
                with open(selected_path, "r", encoding="utf-8") as file:
                    print(file.read())

                print("\n=== END OF PREVIEW ===")
            else:
                print("Invalid backup number.")

        except ValueError:
            print("Please enter a valid number.")
        except UnicodeDecodeError:
            print("This backup cannot be previewed as text.")

    delete_choice = input(
        "\nEnter backup number to delete (or press Enter to skip): "
    ).strip()

    if delete_choice:
        try:
            delete_index = int(delete_choice)

            if 1 <= delete_index <= len(backup_files):
                selected_name = backup_files[delete_index - 1]

                confirm = input(
                    f"Delete backup '{selected_name}'? Type YES to confirm: "
                )

                if confirm == "YES":
                    allowed_prefixes = (
                        "notesbackup",
                        "categorized_notesbackup",
                        "notes_backup_",
                        "categorized_notes_backup_",
                    )

                    if not selected_name.startswith(allowed_prefixes):
                        print("Safety protection: This file cannot be deleted here.")
                        return

                    selected_path = os.path.join(
                        backup_folder, selected_name
                    )
                    os.remove(selected_path)
                    print("Backup deleted successfully.")
                else:
                    print("Deletion cancelled.")
            else:
                print("Invalid backup number.")

        except ValueError:
            print("Please enter a valid number.")
        except OSError as error:
            print("Could not delete backup:", error)

def backup_health_check():
    backup_folder = "backups"

    print("\n=== BACKUP HEALTH CHECK ===")

    if not os.path.exists(backup_folder):
        print("Backup folder not found.")
        return

    backup_files = [
        name for name in os.listdir(backup_folder)
        if name.endswith(".txt")
    ]

    if not backup_files:
        print("No backup files found.")
        return

    empty_files = []
    unreadable_files = []

    for name in backup_files:
        file_path = os.path.join(backup_folder, name)

        try:
            if os.path.getsize(file_path) == 0:
                empty_files.append(name)
            else:
                with open(file_path, "r", encoding="utf-8") as file:
                    file.read(100)

        except (OSError, UnicodeDecodeError):
            unreadable_files.append(name)

    print(f"Total backup files: {len(backup_files)}")
    print(f"Empty files: {len(empty_files)}")
    print(f"Unreadable files: {len(unreadable_files)}")

    if empty_files:
        print("\nEmpty backup files:")
        for name in empty_files:
            print("-", name)

    if unreadable_files:
        print("\nUnreadable backup files:")
        for name in unreadable_files:
            print("-", name)

    if not empty_files and not unreadable_files:
        print("All backup files passed the basic health check.")
def backup_notes():
    backup_folder = "backups"

    os.makedirs(backup_folder, exist_ok=True)

    files_to_backup = [
        "notes.txt",
        "categorized_notes.txt"
    ]

    state_file = "backup_state.json"

    if os.path.exists(state_file):
        try:
            with open(state_file, "r", encoding="utf-8") as file:
                backup_state = json.load(file)
        except (json.JSONDecodeError, OSError):
            backup_state = {}
    else:
        backup_state = {}

    changed = False

    for filename in files_to_backup:
        if not os.path.exists(filename):
            continue

        with open(filename, "rb") as file:
            content = file.read()

        import hashlib
        current_hash = hashlib.sha256(content).hexdigest()

        if backup_state.get(filename) == current_hash:
            continue

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        backup_name = filename.replace(
            ".txt", f"backup{timestamp}.txt"
        )
        backup_path = os.path.join(backup_folder, backup_name)

        shutil.copy2(filename, backup_path)
        backup_state[filename] = current_hash
        changed = True

    with open(state_file, "w", encoding="utf-8") as file:
        json.dump(backup_state, file, indent=4)

    if changed:
        print("Smart backup created successfully!")
    else:
        print("No changes detected. Backup skipped.")
def backup_before_delete():
    backup_folder = "backups"
    os.makedirs(backup_folder, exist_ok=True)

    files_to_backup = ["notes.txt", "categorized_notes.txt"]
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    for filename in files_to_backup:
        if os.path.exists(filename):
            backup_name = filename.replace(
                ".txt", f"before_delete{timestamp}.txt"
            )
            backup_path = os.path.join(backup_folder, backup_name)
            shutil.copy2(filename, backup_path)

    print("Pre-delete backup created.")
def restore_backup():
    backup_folder = "backups"

    if not os.path.exists(backup_folder):
        print("Backup folder not found.")
        return

    backups = [
        name for name in os.listdir(backup_folder)
        if name.endswith(".txt")
        and name.startswith((
            "notesbackup",
            "categorized_notesbackup",
            "notes_backup_",
            "categorized_notes_backup_",
            "notesbefore_delete",
            "categorized_notesbefore_delete",
            "notesbefore_restore",
            "categorized_notesbefore_restore",
        ))
    ]

    if not backups:
        print("No backup files found.")
        return

    print("\n=== AVAILABLE BACKUPS ===")

    for index, name in enumerate(backups, start=1):
        print(f"{index}. {name}")

    try:
        selection = int(input("Enter backup number to restore: "))

        if selection < 1 or selection > len(backups):
            print("Invalid backup number.")
            return

        selected_backup = backups[selection - 1]

        if selected_backup.startswith((
            "categorized_notesbackup",
            "categorized_notes_backup_",
            "categorized_notesbefore_delete",
            "categorized_notesbefore_restore",
        )):
            target_file = "categorized_notes.txt"
        else:
            target_file = "notes.txt"

        confirm = input(
            f"Restore this backup to {target_file}? Type YES to confirm: "
        )

        if confirm != "YES":
            print("Restore cancelled.")
            return

        # Save current file before restoring
        if os.path.exists(target_file):
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            safety_file = os.path.join(
                backup_folder,
                target_file.replace(".txt", f"before_restore{timestamp}.txt")
            )
            shutil.copy2(target_file, safety_file)
            print("Safety backup created:", safety_file)

        source_path = os.path.join(backup_folder, selected_backup)
        shutil.copy2(source_path, target_file)

        # Update the hash so the next run does not create an unnecessary backup
        import hashlib

        with open(target_file, "rb") as file:
            current_hash = hashlib.sha256(file.read()).hexdigest()

        state_file = "backup_state.json"
        try:
            with open(state_file, "r", encoding="utf-8") as file:
                last_state = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            last_state = {}

        last_state[target_file] = current_hash

        with open(state_file, "w", encoding="utf-8") as file:
            json.dump(last_state, file, indent=4)

        print(f"Backup restored successfully to {target_file}!")

    except ValueError:
        print("Please enter a valid number.")

print("=== PERSONAL KNOWLEDGE ASSISTANT ===")

while True:
    print("\n1. Add Note")
    print("2. View All Notes")
    print("3. Exit")
    print("4. Delete All Notes")
    print("5. Search Notes")
    print("6. Delete Individual Note")
    print("7. Edit Individual Note")
    print("8. View Notes by Category")
    print("9. Ask a Question")
    print("10. Restore Backup")
    print("11. Backup Management")
    print("12. Backup Health Check")

    choice = input("Choose an option: ")
    if choice == "8":
        print("\nSelect category to view:")
        print("1. Study")
        print("2. Projects")
        print("3. Ideas")
        print("4. Personal")

        category_choice = input("Enter category number: ")

        categories = {
            "1": "Study",
            "2": "Projects",
            "3": "Ideas",
            "4": "Personal"
        }

        selected_category = categories.get(category_choice)

        if selected_category:
            with open("categorized_notes.txt", "r", encoding="utf-8") as file:
                found = False

                for line in file:
                    if line.startswith(selected_category + "|"):
                        print(line.strip().split("|", 1)[1])
                        found = True

                if not found:
                    print("No notes found in this category.")
        else:
            print("Invalid category!")

    elif choice == "1":
        note = input("Write your note: ")
        print("Select category:")
        print("1. Study")
        print("2. Projects")
        print("3. Ideas")
        print("4. Personal")

        category_choice = input("Enter category number: ")
        if category_choice == "1":
            category = "Study"
        elif category_choice == "2":
            category = "Projects"
        elif category_choice == "3":
            category = "Ideas"
        elif category_choice == "4":
            category = "Personal"
        else:
            category = "Uncategorized"
        with open("categorized_notes.txt", "a", encoding="utf-8") as file:
            file.write(f"{category}|{note}\n")

        with open("notes.txt", "a", encoding="utf-8") as file:
            file.write(f"[{category}] {note}\n")

        print("Note saved successfully!")
        backup_notes()
    elif choice == "2":
        print("\n=== YOUR SAVED NOTES ===")

        all_notes = []

        for filename in ["notes.txt", "categorized_notes.txt"]:
            try:
                with open(filename, "r", encoding="utf-8") as file:
                    for line in file:
                        line = line.rstrip("\n")

                        if line.strip():
                            if "|" in line:
                                category, note_text = line.split("|", 1)
                                all_notes.append(f"[{category}] {note_text}")
                            else:
                                all_notes.append(line)

            except FileNotFoundError:
                pass

        if all_notes:
            for i, note in enumerate(all_notes, start=1):
                print(f"{i}. {note}")
        else:
            print("No notes found.")
                
    elif choice == "3":
        print("Goodbye!")
        break

    elif choice == "4":
        confirm = input(
            "Delete all notes? Type YES to confirm: "
        ).strip()

        if confirm == "YES":
            backup_before_delete()

            for filename in ["notes.txt", "categorized_notes.txt"]:
                with open(filename, "w", encoding="utf-8") as file:
                    file.write("")

            backup_notes()
            print("All notes deleted successfully.")
        else:
            print("Deletion cancelled.")

    elif choice == "5":
        keyword = input("Enter keyword to search: ")

        try:
            with open("notes.txt", "r", encoding="utf-8") as file:
                notes = file.readlines()
        except FileNotFoundError:
            notes = []

        try:
            with open("categorized_notes.txt", "r", encoding="utf-8") as file:
                categorized_notes = file.readlines()
                notes.extend(categorized_notes)
        except FileNotFoundError:
            pass

        found = False

        for note in notes:
            if keyword.lower() in note.lower():
                print(note.strip())
                found = True

        if not found:
            print("No matching notes found.")

    elif choice == "6":
        files = ["notes.txt", "categorized_notes.txt"]
        notes = []

        for filename in files:
            try:
                with open(filename, "r", encoding="utf-8") as file:
                    for line_number, line in enumerate(file, start=1):
                        note = line.rstrip("\n")
                        if note.strip():
                            notes.append((filename, line_number, note))
            except FileNotFoundError:
                pass

        if not notes:
            print("No notes available to delete.")
        else:
            print("\n=== YOUR SAVED NOTES ===")

            for index, (filename, line_number, note) in enumerate(notes, start=1):
                if "|" in note:
                    category, text = note.split("|", 1)
                    print(f"{index}. [{category}] {text}")
                else:
                    print(f"{index}. {note}")

            try:
                number = int(input("Enter note number to delete: "))

                if not 1 <= number <= len(notes):
                    print("Invalid note number.")
                else:
                    filename, line_number, deleted_note = notes[number - 1]
                    confirm = input(
                        f"Delete this note? Type YES to confirm: "
                    ).strip()

                    if confirm == "YES":
                        backup_before_delete()

                        with open(filename, "r", encoding="utf-8") as file:
                            lines = file.readlines()

                        del lines[line_number - 1]

                        with open(filename, "w", encoding="utf-8") as file:
                            file.writelines(lines)

                        print("Deleted note successfully.")
                        backup_notes()
                    else:
                        print("Deletion cancelled.")

            except ValueError:
                print("Please enter a valid number.")

    elif choice == "7":
        files = ["notes.txt", "categorized_notes.txt"]
        notes = []

        for filename in files:
            try:
                with open(filename, "r", encoding="utf-8") as file:
                    for line_number, line in enumerate(file, start=1):
                        note = line.rstrip("\n")
                        if note.strip():
                            notes.append((filename, line_number, note))
            except FileNotFoundError:
                pass

        if not notes:
            print("No notes available to edit.")
        else:
            print("\n=== YOUR SAVED NOTES ===")

            for index, (filename, line_number, note) in enumerate(notes, start=1):
                if "|" in note:
                    category, text = note.split("|", 1)
                    print(f"{index}. [{category}] {text}")
                else:
                    print(f"{index}. {note}")

            try:
                number = int(input("Enter note number to edit: "))

                if not 1 <= number <= len(notes):
                    print("Invalid note number.")
                else:
                    filename, line_number, old_note = notes[number - 1]
                    new_text = input("Enter the updated note: ").strip()

                    if not new_text:
                        print("Note cannot be empty.")
                    else:
                        confirm = input(
                            "Save this change? Type YES to confirm: "
                        ).strip()

                        if confirm == "YES":
                            backup_before_delete()

                            with open(filename, "r", encoding="utf-8") as file:
                                lines = file.readlines()

                            if filename == "categorized_notes.txt":
                                category = old_note.split("|", 1)[0]
                                lines[line_number - 1] = f"{category}|{new_text}\n"
                            else:
                                if old_note.startswith("[") and "] " in old_note:
                                    category = old_note[1:].split("] ", 1)[0]
                                    lines[line_number - 1] = f"[{category}] {new_text}\n"
                                else:
                                    lines[line_number - 1] = new_text + "\n"

                            with open(filename, "w", encoding="utf-8") as file:
                                file.writelines(lines)

                            print("Note updated successfully!")
                            backup_notes()
                        else:
                            print("Edit cancelled.")

            except ValueError:
                print("Please enter a valid number.")
    elif choice == "9":
        import re

        stop_words = {
            "can", "you", "tell", "me", "about", "what", "is",
            "the", "a", "an", "please", "how", "do", "does",
            "in", "on", "to", "my", "your", "and", "of", "for",
            "i", "want", "know", "explain", "find", "show"
        }

        def tokenize(text):
            return [
                word for word in re.findall(r"\b[a-z0-9]+\b", text.lower())
                if word not in stop_words and len(word) > 1
            ]

        question = input("Ask your question: ").strip()
        query_words = set(tokenize(question))

        if not query_words:
            print("Please ask a question with meaningful keywords.")
        else:
            results = []
            seen_notes = set()

            for filename in ["notes.txt", "categorized_notes.txt"]:
                try:
                    with open(filename, "r", encoding="utf-8") as file:
                        for line in file:
                            line = line.strip()
                            if not line:
                                continue

                            if "|" in line:
                                category, note_text = line.split("|", 1)
                            elif line.startswith("[") and "] " in line:
                                category, note_text = line[1:].split("] ", 1)
                            else:
                                category, note_text = "Uncategorized", line

                            note_text = note_text.strip()
                            normalized = " ".join(note_text.lower().split())

                            if not normalized or normalized in seen_notes:
                                continue

                            seen_notes.add(normalized)
                            note_words = set(tokenize(note_text)) | set(tokenize(category))
                            matches = query_words & note_words

                            if not matches:
                                continue

                            coverage = len(matches) / len(query_words)
                            precision = len(matches) / max(len(note_words), 1)
                            score = 0.7 * coverage + 0.3 * precision

                            results.append(
                                (score, len(matches), category, note_text)
                            )

                except FileNotFoundError:
                    pass
                except OSError as error:
                    print(f"Could not read {filename}: {error}")

            results.sort(
                key=lambda item: (item[0], item[1]),
                reverse=True
            )

            if results:
                print("\n=== MOST RELEVANT NOTES ===")
                for index, (score, matched, category, note_text) in enumerate(
                    results[:5], start=1
                ):
                    print(f"\n{index}. [{category}] {note_text}")
                    print(f"   Relevance: {score * 100:.0f}%")
                    print(f"   Matching keywords: {matched}")
            else:
                print("No matching notes found. Try different keywords.")

    elif choice == "10":
        restore_backup()

    elif choice == "11":
        manage_backups()

    elif choice == "12":
        backup_health_check()