import sys

app_py_path = 'StudentsWebApp/app.py'

with open(app_py_path, 'r') as f:
    lines = f.readlines()

output_lines = []
imports_added = False
app_created_logged = False
db_configured_logged = False
model_loading_logged = False # This was the critical one
db_create_all_logged_module_level = False # Specific for module level db.create_all()

# Standard imports to add
logging_imports = [
    "import time\n",
    "import logging\n",
    "logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')\n", # Added format
    "logger = logging.getLogger(__name__)\n",
    "logger.info(\"STARTUP: Flask application initialization begins...\")\n" # Changed message
]

line_idx = 0
while line_idx < len(lines):
    line = lines[line_idx]

    # Add logging imports before Flask app creation or first route
    if not imports_added and ('app = Flask(__name__)' in line or '@app.route' in line or 'class User(db.Model)' in line):
        output_lines.extend(logging_imports)
        imports_added = True

    output_lines.append(line)

    if 'app = Flask(__name__)' in line and not app_created_logged:
        output_lines.append("logger.info(\"STARTUP: Flask app object created.\")\n")
        app_created_logged = True

    # Check for database URI configuration
    if "app.config['SQLALCHEMY_DATABASE_URI']" in line and "if database_url:" in lines[line_idx-1]: # More specific context
        output_lines.append("logger.info(f\"STARTUP: SQLALCHEMY_DATABASE_URI set to: {app.config['SQLALCHEMY_DATABASE_URI']}\")\n")

    # Log after SQLAlchemy object initialized
    if 'db = SQLAlchemy(app)' in line and not db_configured_logged:
        output_lines.append("logger.info(\"STARTUP: SQLAlchemy object 'db' initialized.\")\n")
        db_configured_logged = True

    # AI Model Logging - Corrected variable name
    if 'gpt_pipeline = pipeline("text2text-generation"' in line and not model_loading_logged:
        # The line "gpt_pipeline = None" might appear before, we want the actual call
        # Insert before the try block for model loading
        # We need to find the "try:" associated with this pipeline call

        # Search backwards for "gpt_pipeline = None" to insert before its try block
        # This is still heuristic. A better way is to find the 'try:' for the pipeline.
        # Let's assume the structure:
        # gpt_pipeline = None
        # try:
        #    gpt_pipeline = pipeline(...)

        temp_idx = len(output_lines) -1 # current line just added
        # Find the line "gpt_pipeline = None" just before the try block for the actual model loading
        # This is tricky because "gpt_pipeline = None" also appears if loading fails.
        # The key is that the successful load is "gpt_pipeline = pipeline(...)"
        # The script needs to insert *before* the try block of this specific assignment.

        # Simplified: Assume the "try:" for model loading is a few lines before "gpt_pipeline = pipeline..."
        # This part of the original script was problematic. Let's try to make it more direct.

        # Find the 'try:' line associated with 'gpt_pipeline = pipeline(...)'
        # This requires looking ahead from 'gpt_pipeline = None' or finding the try block directly.
        # The original script's logic for model_loading_logged was too simple.

        # Let's find the "try:" that directly precedes the pipeline call.
        # This means modifying a few lines back from the current

        # Attempt to find the  statement for model loading
        try_line_offset = -1
        for i in range(len(output_lines) - 2, max(0, len(output_lines) - 5), -1):
            if output_lines[i].strip() == "try:":
                try_line_offset = i
                break

        if try_line_offset != -1:
            # Insert logging before the try block
            insert_point = try_line_offset
            output_lines.insert(insert_point, "logger.info(\"STARTUP: Attempting to load AI model 'google/flan-t5-small'...\")\n")
            output_lines.insert(insert_point + 1, "model_load_start_time = time.time()\n")

            # The original 'try:' is now at output_lines[insert_point + 2]
            # The line with 'gpt_pipeline = pipeline(...)' is output_lines[-1] (the one just added)
            # We need to add logging after it and the except block

            # This is becoming complex; the original script's approach of finding 'pipeline(' and wrapping it
            # was better if the variable name was correct and indentation handled.
            # Let's revert to a simpler strategy: add log after the line if successful, or in except.
            # This means we need to find the 'except Exception as e:' for this try block.

            # The current line is the one with
            output_lines.append("    logger.info(f\"STARTUP: AI model loaded successfully in {time.time() - model_load_start_time:.2f} seconds.\")\n")
            model_loading_logged = True # Mark as handled

            # Find the corresponding except block to add logging
            # This assumes the except block is present and follows the structure.
            except_idx = line_idx + 1
            while except_idx < len(lines):
                if lines[except_idx].strip().startswith("except Exception as e:"):
                    # We need to insert into output_lines, not lines
                    # Find where 'except Exception as e:' will be in output_lines
                    current_output_len = len(output_lines)
                    # Map except_idx from original lines to output_lines
                    # This is an approximation
                    output_except_idx = current_output_len + (except_idx - (line_idx+1))
                    output_lines.insert(output_except_idx + 1, "    logger.error(f\"STARTUP: Error loading AI model: {e}\", exc_info=True)\n")
                    break
                elif lines[except_idx].strip().startswith("try:"): # another try block, stop
                    break
                except_idx += 1
        else:
            # Fallback if try block not found as expected
            output_lines.append("logger.warning(\"STARTUP: AI model loading detected, but couldn't inject detailed start/end logs precisely.\")\n")

    # db.create_all() logging (module level)
    # The original app.py has:
    # with app.app_context():
    #    db.create_all()
    #    if not Admin.query... (this part is also DB operation)

    if 'with app.app_context():' in line:
        # Check if next non-empty line is db.create_all()
        next_code_line_idx = line_idx + 1
        while next_code_line_idx < len(lines) and lines[next_code_line_idx].strip() == "":
            next_code_line_idx += 1

        if next_code_line_idx < len(lines) and 'db.create_all()' in lines[next_code_line_idx]:
            if not db_create_all_logged_module_level: # Ensure only one set of logs for this block
                output_lines.append("logger.info(\"STARTUP: Entering app_context for module-level DB operations (db.create_all(), default admin)...\")\n")
                output_lines.append("db_ops_module_start_time = time.time()\n")
                # The db.create_all() and subsequent admin creation will execute.
                # We need to log *after* the 'with' block finishes.
                # This requires identifying the end of the 'with' block.

                # This is difficult with line-based processing.
                # For now, just log the start. Completion log would need explicit placement
                # or more advanced parsing.
                db_create_all_logged_module_level = True # Mark that we've logged the start

    # Log before entering if __name__ == '__main__'
    if 'if __name__ == "__main__":' in line or "if __name__ == '__main__':" in line:
        output_lines.append("logger.info(\"STARTUP: Reached __main__ block (for direct execution, not by Gunicorn).\")\n")
        # Add log for app.run()
        # Find app.run(...)
        main_block_lines = []
        temp_main_idx = line_idx + 1
        while temp_main_idx < len(lines):
            if not lines[temp_main_idx].startswith(" ") and not lines[temp_main_idx].startswith("\t") and lines[temp_main_idx].strip() != "":
                 break # End of main block
            main_block_lines.append(lines[temp_main_idx])
            temp_main_idx +=1

        for i, main_line in enumerate(main_block_lines):
            if "app.run(" in main_line:
                # Insert log before app.run() in the collected main_block_lines
                # This requires modifying lines that haven't been added to output_lines yet
                # This is getting too complex for simple line processing.
                # The current script inserts  (which is ) then continues.
                # So, we need to modify  or handle it in the next iterations.
                pass # Simplification: will log "Reached __main__ block"

    line_idx += 1

if not imports_added and output_lines: # If loop never ran (e.g. empty file) or condition never met
    output_lines = logging_imports + output_lines
elif not output_lines : # If file was empty
     output_lines = logging_imports

# Attempt to add a log after the module-level db operations if they were started
# This is a heuristic: find the end of the 'with app.app_context()' block
# that contains db.create_all()
if db_create_all_logged_module_level: # Means we logged the start
    final_output_lines = []
    in_db_block = False
    original_indent = -1
    for l_idx, l_content in enumerate(output_lines):
        final_output_lines.append(l_content)
        if "logger.info(\"STARTUP: Entering app_context for module-level DB operations" in l_content:
            in_db_block = True
        if in_db_block and l_content.strip().startswith("with app.app_context():"):
             # Get indent of the line after 'with'
             if l_idx + 1 < len(output_lines):
                original_indent = len(output_lines[l_idx+1]) - len(output_lines[l_idx+1].lstrip())

        if in_db_block and not l_content.startswith(" ") and not l_content.startswith("\t") and            not l_content.strip() == "" and not l_content.strip().startswith("with app.app_context():") and            not "db_ops_module_start_time =" in l_content and            not "logger.info(\"STARTUP: Entering app_context for module-level DB operations" in l_content and            (len(l_content) - len(l_content.lstrip())) < original_indent and original_indent != -1 :
            # Line is outdented relative to the block, and not part of the logging itself
            final_output_lines.insert(-1, f"logger.info(\"STARTUP: Module-level DB operations (db.create_all(), default admin) finished in {{time.time() - db_ops_module_start_time:.2f}} seconds.\")\n")
            in_db_block = False # Reset
            original_indent = -1 # Reset
    output_lines = final_output_lines


with open(app_py_path, 'w') as f:
    f.writelines(output_lines)

print(f"Finished processing {app_py_path}")
