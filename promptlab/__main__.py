"""Entry point: python -m promptlab"""

import sys
from . import cli

if __name__ == "__main__":
    sys.exit(cli.main())
