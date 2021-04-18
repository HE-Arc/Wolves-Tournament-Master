import os
for root, dirs, files in os.walk(os.getcwd()):
    for file in files:
        if file.endswith(".py"):
            with open(os.path.join(root, file)) as f:
                contents = f.read()
            if 'tensorflow' in contents:
                print(os.path.join(root, file))