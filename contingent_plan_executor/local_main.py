from hovor.core import run_interaction
from local_run_utils import *
import sys


def run_local_conversation(output_files_path):
    run_interaction(initialize_local_run(output_files_path))


if __name__ == "__main__":
    if len(sys.argv) > 1:
        arg = sys.argv[1]
    else:
        raise ValueError("Please provide the directory to your plan4dial output files as a system argument.")
    /home/qnc/Plan4Dial/contingent-plan-executor/local_data/gold_standard_data
    #arg = "/home/qnc/Plan4Dial/plan4dial/plan4dial/local_data/conversation_alignment_bots/ijcai_bot/output_files"
    run_local_conversation(arg)
