#!/bin/bash
set -e

# Activate virtual environment
source /opt/venv/bin/activate

# Set up Python path
export PYTHONPATH=/var/www/mail-scheduler

# Create a monkey patch module for RQ utils
cat > /tmp/patch_rq.py << 'EOF'
import logging
import os
import sys

# Define the missing class for rq_scheduler
class ColorizingStreamHandler(logging.StreamHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_tty = getattr(self.stream, 'isatty', lambda: False)()

# Patch RQ module at runtime
import rq.utils
if not hasattr(rq.utils, 'ColorizingStreamHandler'):
    print("Adding ColorizingStreamHandler to rq.utils")
    rq.utils.ColorizingStreamHandler = ColorizingStreamHandler

print("RQ utils successfully patched with ColorizingStreamHandler")
EOF

# Apply the patch at runtime using PYTHONPATH
echo "Starting RQ Scheduler with patch..."
PYTHONPATH=/tmp:$PYTHONPATH exec python -c "import patch_rq; from rq_scheduler.scripts import rqscheduler; rqscheduler.main()" --host ${REDIS_HOST:-redis} --port ${REDIS_PORT:-6379} --db 0
