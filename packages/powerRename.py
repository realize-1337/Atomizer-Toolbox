import os
import re
import tqdm

class rename():
    def __init__(self) -> None:
        pass

    def walkFolder(self, path, match='.png'):
        for root, dir, files in tqdm.tqdm(os.walk(path)):
            for file in files:
                pattern = rf'frame_(\d+)({match})'
                if file.endswith(match) and file.startswith('frame'):
                    ma = re.search(pattern, file)
                    if dir:
                        pre = os.path.join(dir, file)
                        post = os.path.join(dir, f'frame_{"%04d" % int(ma.group(1))}{match}')
                    else: 
                        pre = os.path.join(root, file)
                        post = os.path.join(root, f'frame_{"%04d" % int(ma.group(1))}{match}')
                    os.rename(pre, post)
                    


if __name__ == '__main__':
    rn = rename()
    rn.walkFolder(r'M:\Duese_3\Wasser')