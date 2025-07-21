from agno.debug import enable_debug_mode

import logging
import sys
import argparse

from poc_agno.teams.scribe_team import scribe_team

_LOGGER = logging.getLogger(__name__)


def log_msg(msg):
    _LOGGER.info(msg)


def initializeLogging():
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('[BRANCH][PID %(process)d] %(message)s')
    handler.setFormatter(formatter)
    _LOGGER.addHandler(handler)
    _LOGGER.setLevel(logging.INFO)
    enable_debug_mode()


def main():
    log_msg("Starting Scribe")
    initializeLogging()
    input_file, output_file = parseLocalArgs()
    log_msg('Input file name provided:%s' % input_file)
    log_msg('Output file name provided:%s' % output_file)

    loaded_txt = open(input_file, "r").read()
    prompt = f"Add comments to  \n\n{loaded_txt}"
    log_msg(prompt)
    # scribe_team.print_response(f"Original source code is {input_file} and save it atping {output_file}", stream=True)
    response = scribe_team.run(prompt)
    log_msg("******COTENT*********")
    log_msg(response.content)
    log_msg("******TEAM RESPONSE*********")
    log_msg(response.member_responses)  # responses from individual team members
    log_msg("******THINKING RESPONSE*********")
    log_msg(response.thinking)  # reasoning/thought process
    log_msg("*****TOOLS RESPONSE**********")
    log_msg(response.tools)  # tool calls, if any


def parseLocalArgs():
    parser = argparse.ArgumentParser(
        usage='%(prog)s [options]',
        description="Add comments to the supplied source file and save it to specified location")

    parser.add_argument('-i', '--Input', dest="inputFile", required=True, type=str,
                        help='Path to the source code file')
    parser.add_argument('-o', '--Output', dest="outputFile", type=str, required=True,
                        help='Path to the output file where the result will be saved')

    clargs = parser.parse_args()
    return clargs.inputFile, clargs.outputFile


if __name__ == "__main__":
    main()
