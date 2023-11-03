import os
import sys

dir_path = os.path.abspath(os.getcwd())
utils_path = dir_path + "\\src\\app_utils"
database_tool_path = dir_path + "\\src\\database_creation"
src_path = dir_path + "\\src"
data_path = dir_path + "\\data"
sys.path.append(utils_path)
sys.path.append(src_path)
sys.path.append(data_path)
sys.path.append(database_tool_path)

# COMPLETIONS_MODEL = "gpt-3.5-turbo"
# EMBEDDING_MODEL = "text-embedding-ada-002"
# config_dir = dir_path + "\\src\\utils"
# config = configparser.ConfigParser()
# config.read(os.path.join(config_dir, 'gpt_local_config.cfg'))
# openai.api_key = config.get('token', 'GPT_TOKEN')
