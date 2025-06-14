## Description

Convert an image of code into text



# first, run setup_env.sh

pyenv install 3.13.3
pyenv global 3.13.3


mv siiv_agent venv
source venv/bin/activate
pip install -r requirements.txt

python photo_to_code_batch.py --folder photos/
