# Auto Committer Script
import os
import shutil
import random
import subprocess
from datetime import datetime
import yaml

# === CONFIGURATION ===
REPO_PATH = os.path.dirname(os.path.abspath(__file__))  # Current folder
TOPICS_PATH = os.path.join(REPO_PATH, "topics")
COMMIT_FOLDER = os.path.join(REPO_PATH, "commits")
CONFIG_PATH = os.path.join(REPO_PATH, "config.yaml")
LOG_FILE = os.path.join(REPO_PATH, "commit_log.txt")

# === LOAD CONFIG ===
with open(CONFIG_PATH, 'r') as f:
    config = yaml.safe_load(f)

topics = config["topics"]
times = config["schedule"]["times"]
high_commit_days = config["schedule"]["high_commit_days"]

# === TIME HELPERS ===
today = datetime.now()
weekday = today.weekday()  # 0 = Monday
week_num = today.isocalendar()[1]  # Week of the year

# === DETERMINE COMMIT LOAD ===
commit_count = random.randint(6, 7) if weekday in high_commit_days else random.randint(2, 3)

# === DETERMINE CURRENT TOPIC BASED ON WEEK ===
topic_index = (week_num - 1) % len(topics)
current_topic = topics[topic_index]
topic_path = os.path.join(TOPICS_PATH, current_topic)

# === SELECT RANDOM FILES ===
all_files = [f for f in os.listdir(topic_path) if f.endswith(".c")]
selected_files = random.sample(all_files, min(commit_count, len(all_files)))

# === PREPARE COMMIT FOLDER ===
if os.path.exists(COMMIT_FOLDER):
    shutil.rmtree(COMMIT_FOLDER)
os.makedirs(COMMIT_FOLDER, exist_ok=True)

for filename in selected_files:
    src = os.path.join(topic_path, filename)
    dst = os.path.join(COMMIT_FOLDER, filename)
    shutil.copy(src, dst)

# === GIT OPERATIONS ===
def git_cmd(*args):
    return subprocess.run(["git", "-C", REPO_PATH] + list(args), capture_output=True, text=True)

commit_msg = f"{today.strftime('%Y-%m-%d')} - {len(selected_files)} problem(s) on {current_topic.title()}"

try:
    git_cmd("add", "commits/")
    git_cmd("commit", "-m", commit_msg)
    git_cmd("push")

    # === SUCCESS LOG ===
    with open(LOG_FILE, "a", encoding="utf-8") as log:
        log.write(f"[✓] {today} - Pushed {len(selected_files)} {current_topic} problem(s)\n")

    print(f"[✓] Committed {len(selected_files)} file(s) from topic: {current_topic}")

except subprocess.CalledProcessError as e:
    # === ERROR LOG ===
    with open(LOG_FILE, "a", encoding="utf-8") as log:
        log.write(f"[✗] {today} - ERROR: {e}\n")
    print(f"[✗] Commit failed: {e}")
