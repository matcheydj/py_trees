#!/usr/bin/env python
#
# License: BSD
#   https://raw.githubusercontent.com/stonier/py_trees_suite/devel/LICENSE
#
##############################################################################
# Documentation
##############################################################################

"""
Code for the context switching demo program.
---
"""

##############################################################################
# Imports
##############################################################################

import argparse
import py_trees
import sys
import time

import py_trees.console as console

##############################################################################
# Classes
##############################################################################


def description():
    content = "Demonstrates context switching with parallels and sequences\n"
    if py_trees.console.has_colours:
        banner_line = console.green + "*" * 79 + "\n" + console.reset
        s = "\n"
        s += banner_line
        s += console.bold_white + "Context Switching".center(79) + "\n" + console.reset
        s += banner_line
        s += "\n"
        s += content
        s += "\n"
        s += banner_line
    else:
        s = content
    return s


def command_line_argument_parser():
    parser = argparse.ArgumentParser(description=description(),
                                     epilog=console.cyan + "And his noodly appendage reached forth to tickle the blessed...\n" + console.reset,
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     )
    parser.add_argument('-r', '--render', action='store_true', help='render dot tree to file')
    return parser


class ContextSwitch(py_trees.behaviour.Behaviour):
    """
    An example of a context switching class that sets *and* resets a context.
    Use in parallel with a subtree that does the work while in this context.

    Note that simply setting a pair of behaviours (set and reset context) on
    either end of a work sequence does not suffice. If the sequence is interrupted
    by a higher priority activity midstream, it will not reset the context.
    """
    def __init__(self, name="ContextSwitch"):
        super(ContextSwitch, self).__init__(name)
        self.feedback_message = "old context"

    def initialise(self):
        """
        Backup and set a new context.
        """
        self.logger.debug("%s.initialise()[switch context]" % (self.__class__.__name__))
        self.feedback_message = "new context"

    def update(self):
        """
        Just returns RUNNING while it waits for other activities to finish.
        """
        self.logger.debug("%s.update()[RUNNING][%s]" % (self.__class__.__name__, self.feedback_message))
        return py_trees.Status.RUNNING

    def terminate(self, new_status):
        """
        Restore the context with the previously backed up context.
        """
        self.logger.debug("%s.terminate()[%s->%s][restore context]" % (self.__class__.__name__, self.status, new_status))
        self.feedback_message = "old context"


def create_tree():
    root = py_trees.composites.Parallel(name="Parallel", policy=py_trees.common.ParallelPolicy.SUCCESS_ON_ONE)
    context_switch = ContextSwitch(name="Context")
    sequence = py_trees.composites.Sequence(name="Sequence")
    for job in ["Action 1", "Action 2"]:
        success_after_two = py_trees.behaviours.Count(name=job,
                                                      fail_until=0,
                                                      running_until=2,
                                                      success_until=10)
        sequence.add_child(success_after_two)
    root.add_child(context_switch)
    root.add_child(sequence)
    return root


##############################################################################
# Main
##############################################################################

def main():
    """
    Entry point for the demo context switching script.
    """
    args = command_line_argument_parser().parse_args()
    print(description())
    py_trees.logging.level = py_trees.logging.Level.DEBUG

    tree = create_tree()

    ####################
    # Rendering
    ####################
    if args.render:
        py_trees.display.render_dot_tree(tree)
        sys.exit()

    ####################
    # Execute
    ####################
    tree.setup(timeout=15)
    for i in range(1, 6):
        try:
            print("\n--------- Tick {0} ---------\n".format(i))
            tree.tick_once()
            print("\n")
            py_trees.display.print_ascii_tree(tree, show_status=True)
            time.sleep(1.0)
        except KeyboardInterrupt:
            break
    print("\n")
