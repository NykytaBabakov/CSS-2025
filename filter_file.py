import zstandard
import os
import json
import sys
import csv
from datetime import datetime
import logging.handlers
import traceback

# --- НАЛАШТУВАННЯ ---

# 1. Шляхи до папок з файлами .zst
input_folders = [
    r"C:\Users\Dima\Downloads\reddit\comments",
    r"C:\Users\Dima\Downloads\reddit\submissions"
]

# 2. Шлях до вихідного файлу (без розширення)
output_file = r"C:\Users\Dima\Downloads\reddit_filter"

# 4. САБРЕДДІТИ (SUBREDDITS)
# Назви без "r/". Залиште пустим [], щоб брати пости з УСІХ сабреддітів.
target_subreddits = ["Anxiety", "Depression", "MentalHealth", "SuicideWatch", 
    "Coronavirus", "COVID19_support"] 

# 5. Дати (фільтр за часом)
from_date = datetime.strptime("2005-01-01", "%Y-%m-%d")
to_date = datetime.strptime("2030-12-31", "%Y-%m-%d")

# 6. Формат виводу
output_format = "csv"

# Інші технічні налаштування
field = None 
values = ['']
exact_match = False
inverse = False
single_field = None
values_file = None
write_bad_lines = True

# -----------------------------------------------

# Налаштування логування
log = logging.getLogger("bot")
log.setLevel(logging.INFO)
log_formatter = logging.Formatter('%(asctime)s - %(levelname)s: %(message)s')
log_str_handler = logging.StreamHandler()
log_str_handler.setFormatter(log_formatter)
log.addHandler(log_str_handler)
if not os.path.exists("logs"):
    os.makedirs("logs")
log_file_handler = logging.handlers.RotatingFileHandler(os.path.join("logs", "bot.log"), maxBytes=1024*1024*16, backupCount=5)
log_file_handler.setFormatter(log_formatter)
log.addHandler(log_file_handler)


def write_line_zst(handle, line):
    handle.write(line.encode('utf-8'))
    handle.write("\n".encode('utf-8'))


def write_line_json(handle, obj):
    handle.write(json.dumps(obj))
    handle.write("\n")


def write_line_single(handle, obj, field):
    if field in obj:
        handle.write(obj[field])
    else:
        log.info(f"{field} not in object {obj['id']}")
    handle.write("\n")


def write_line_csv(writer, obj, is_submission):
    output_list = []
    output_list.append(str(obj.get('score', 0)))
    output_list.append(datetime.fromtimestamp(int(obj['created_utc'])).strftime("%Y-%m-%d"))
    
    # Subreddit column added just in case
    output_list.append(obj.get('subreddit', ''))

    if is_submission:
        output_list.append(obj.get('title', ''))
    else:
        output_list.append("") # Empty title for comments
    
    output_list.append(f"u/{obj.get('author', '[deleted]')}")
    
    if 'permalink' in obj:
        output_list.append(f"https://www.reddit.com{obj['permalink']}")
    else:
        subreddit = obj.get('subreddit', '')
        link_id = obj.get('link_id', '')
        obj_id = obj.get('id', '')
        if link_id.startswith('t3_'):
             link_id = link_id[3:]
        output_list.append(f"https://www.reddit.com/r/{subreddit}/comments/{link_id}/_/{obj_id}")

    # Text content logic
    if is_submission:
        if obj.get('is_self', False):
            if 'selftext' in obj:
                output_list.append(obj['selftext'])
            else:
                output_list.append("")
        else:
            output_list.append(obj.get('url', ''))
    else:
        output_list.append(obj.get('body', ''))
        
    writer.writerow(output_list)


def read_and_decode(reader, chunk_size, max_window_size, previous_chunk=None, bytes_read=0):
    chunk = reader.read(chunk_size)
    bytes_read += chunk_size
    if previous_chunk is not None:
        chunk = previous_chunk + chunk
    try:
        return chunk.decode()
    except UnicodeDecodeError:
        if bytes_read > max_window_size:
            raise UnicodeError(f"Unable to decode frame after reading {bytes_read:,} bytes")
        log.info(f"Decoding error with {bytes_read:,} bytes, reading another chunk")
        return read_and_decode(reader, chunk_size, max_window_size, chunk, bytes_read)


def read_lines_zst(file_name):
    with open(file_name, 'rb') as file_handle:
        buffer = ''
        reader = zstandard.ZstdDecompressor(max_window_size=2**31).stream_reader(file_handle)
        while True:
            chunk = read_and_decode(reader, 2**27, (2**29) * 2)
            if not chunk:
                break
            lines = (buffer + chunk).split("\n")
            for line in lines[:-1]:
                yield line.strip(), file_handle.tell()
            buffer = lines[-1]
        reader.close()


def process_file(input_file, handle, writer, output_format, field, values, from_date, to_date, single_field, exact_match, subreddits_lower):
    # Визначаємо тип даних за назвою файлу
    is_submission = "submission" in input_file.lower()
    log.info(f"Processing input file: {input_file} (Is submission: {is_submission})")

    file_size = os.stat(input_file).st_size
    created = None
    matched_lines = 0
    bad_lines = 0
    total_lines = 0
    
    for line, file_bytes_processed in read_lines_zst(input_file):
        total_lines += 1
        if total_lines % 100000 == 0:
            log.info(f"{created.strftime('%Y-%m-%d %H:%M:%S')} : {total_lines:,} : {matched_lines:,} : {bad_lines:,} : {file_bytes_processed:,}:{(file_bytes_processed / file_size) * 100:.0f}%")

        try:
            obj = json.loads(line)
            created = datetime.utcfromtimestamp(int(obj['created_utc']))

            # 1. Фільтр по ДАТІ
            if created < from_date:
                continue
            if created > to_date:
                continue

            # 2. Фільтр по САБРЕДДІТУ (найшвидший)
            if subreddits_lower:
                sub = obj.get('subreddit', '').lower()
                if sub not in subreddits_lower:
                    continue

            matched_lines += 1
            if output_format == "zst":
                write_line_zst(handle, line)
            elif output_format == "csv":
                write_line_csv(writer, obj, is_submission)
            elif output_format == "txt":
                if single_field is not None:
                    write_line_single(handle, obj, single_field)
                else:
                    write_line_json(handle, obj)
            else:
                log.info(f"Something went wrong, invalid output format {output_format}")
        except (KeyError, json.JSONDecodeError) as err:
            bad_lines += 1
            if write_bad_lines:
                if isinstance(err, KeyError):
                    log.warning(f"Key {field} is not in the object: {err}")
                elif isinstance(err, json.JSONDecodeError):
                    log.warning(f"Line decoding failed: {err}")
                log.warning(line)

    log.info(f"Finished file {input_file} : Matched: {matched_lines:,} : Bad: {bad_lines:,}")


if __name__ == "__main__":
    # Підготовка параметрів
    if single_field is not None:
        log.info("Single field output mode, changing output file format to txt")
        output_format = "txt"

    # Готуємо списки для швидкого пошуку (всі в нижній регістр + set для швидкості)
    subreddits_lower = set([s.lower() for s in target_subreddits])

    if values_file is not None:
        values = []
        with open(values_file, 'r') as values_handle:
            for value in values_handle:
                values.append(value.strip().lower())
        log.info(f"Loaded {len(values)} from values file {values_file}")
    else:
        values = [value.lower() for value in values]

    log.info(f"Filtering Subreddits: {subreddits_lower if subreddits_lower else 'ALL'}")
    log.info(f"From date {from_date.strftime('%Y-%m-%d')} to date {to_date.strftime('%Y-%m-%d')}")

    # --- ЗБІР ФАЙЛІВ З УСІХ ПАПОК ---
    files_to_process = []
    
    for folder in input_folders:
        if os.path.exists(folder) and os.path.isdir(folder):
            log.info(f"Scanning folder: {folder}")
            for file in os.listdir(folder):
                if file.endswith(".zst"):
                    full_path = os.path.join(folder, file)
                    files_to_process.append(full_path)
        else:
            log.warning(f"Warning: Folder not found or invalid: {folder}")
    
    if not files_to_process:
        log.error("No .zst files found in any of the provided folders!")
        sys.exit()

    log.info(f"Total files found to process: {len(files_to_process)}")

    # --- ВІДКРИТТЯ ЗАГАЛЬНОГО ФАЙЛУ ---
    output_path = f"{output_file}.{output_format}"
    handle = None
    writer = None

    try:
        if output_format == "zst":
            handle = zstandard.ZstdCompressor().stream_writer(open(output_path, 'wb'))
        elif output_format == "txt":
            handle = open(output_path, 'w', encoding='UTF-8')
        elif output_format == "csv":
            handle = open(output_path, 'w', encoding='UTF-8', newline='')
            writer = csv.writer(handle)
            
            # Універсальний заголовок (додав колонку Subreddit)
            writer.writerow(["Score", "Date", "Subreddit", "Title", "Author", "Link", "Text/Body"])
        else:
            log.error(f"Unsupported output format {output_format}")
            sys.exit()

        # Обробка всіх файлів
        for file_in in files_to_process:
            try:
                process_file(file_in, handle, writer, output_format, field, values, from_date, to_date, single_field, exact_match, subreddits_lower)
            except Exception as err:
                log.warning(f"Error processing {file_in}: {err}")
                log.warning(traceback.format_exc())
    
    finally:
        if handle:
            handle.close()
    
    log.info("ALL DONE.")