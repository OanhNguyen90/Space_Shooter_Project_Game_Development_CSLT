# Nội dung .JSON cho phần phát triển "Save Game":
```
FUNCTION save_profiles_to_file(profiles_list, global_info):
    tmp = SAVE_FILE + ".tmp"
    backup = SAVE_FILE + ".bak"
    data = {
        "save_version": CURRENT_SAVE_VERSION,
        "meta": { "timestamp_ms": now(), "app": APP_NAME },
        "global": global_info,
        "profiles": profiles_list
    }
    TRY:
        # write JSON to tmp file
        with open(tmp, "w") as f:
            json.dump(data, f, indent=2)
        # optional: make a backup of existing save
        if exists(SAVE_FILE):
            rename_or_replace(SAVE_FILE, backup)  # os.replace is atomic on many OS
        # atomically replace tmp -> SAVE_FILE
        os.replace(tmp, SAVE_FILE)
        return True
    EXCEPT Exception as e:
        log("Save failed:", e)
        # cleanup tmp if exists
        try remove(tmp)
        return False
```

# Nội dung .JSON cho phần phát triển "Multiplayer":
```
{
  "save_version": 1,
  "meta": { "timestamp_ms": 1696065000000 },
  "session": {
    "session_id": "sess-123",
    "score": 1200,
    "level": 2,
    "difficulty": 0,
    "players": [
      {"player_id":"p1","name":"Oanh","lives":4,"pos":[640,560],"shield":false,"inventory":{}},
      {"player_id":"p2","name":"Lan","lives":3,"pos":[700,560],"shield":true,"shield_time":1696064995000}
    ],
    "boss": null
  }
}
```
