import json
import sys
from contextlib import redirect_stdout

from . import STAGE_TOOLS


if __name__ == "__main__":
    tools = {tool.__name__: tool for tool in STAGE_TOOLS}
    with redirect_stdout(sys.stderr):
        result = tools[sys.argv[1]](**json.load(sys.stdin))
    print(json.dumps(result, allow_nan=False))
