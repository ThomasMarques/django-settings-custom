import os
import pypandoc

django_settings_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
output = pypandoc.convert_file(
    source_file=os.path.join(django_settings_root, 'README.md'),
    format='markdown',
    to='rst'
)

with open('instructions.rst', 'w') as f:
    f.write(output.replace('results.gif', '../results.gif'))
    f.flush()
