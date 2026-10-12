# Local data

The default profile is user_memory.json, created only when Save preferences is used. It contains one dietary_preferences string. It is plaintext, single-user data, excluded from Git.

An absent file means no saved preferences. An unreadable/invalid file is an error that stops recipe generation. Repair or Forget it explicitly; the application will not discard restrictions silently.

Atomic saves use short-lived .user_memory.json.*.tmp sibling files, also ignored by Git. MEMORY_FILE can select another location; if you choose one inside the repository, make sure it is excluded before committing.

Do not put credentials or personal datasets in the repository. Automated tests and evaluations use isolated temporary profiles, not this directory.
