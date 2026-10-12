from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from rebuild import rebuild
if __name__=='__main__': rebuild(Path(__file__).resolve().parent)
