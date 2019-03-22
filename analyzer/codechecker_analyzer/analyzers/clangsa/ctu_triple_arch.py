# -------------------------------------------------------------------------
#                     The CodeChecker Infrastructure
#   This file is distributed under the University of Illinois Open Source
#   License. See LICENSE.TXT for details.
# -------------------------------------------------------------------------
"""
Helpers for determining triple arch of a compile action
"""
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

import shlex

from codechecker_analyzer.analyzer_env import \
    extend_analyzer_cmd_with_resource_dir

from .. import analyzer_base


def get_compile_command(action, config, source='', output=''):
    """ Generate a standardized and cleaned compile command serving as a base
    for other operations. """

    cmd = [config.analyzer_binary]
    if action.target != "":
        cmd.append("--target=" + action.target)
    extend_analyzer_cmd_with_resource_dir(cmd,
                                          config.compiler_resource_dir)
    cmd.extend(action.compiler_includes)
    cmd.append('-c')
    cmd.extend(['-x', action.lang])
    cmd.append(config.analyzer_extra_arguments)
    cmd.extend(action.analyzer_options)
    if output:
        cmd.extend(['-o', output])
    if source:
        cmd.append(source)

    if all(not opt.startswith('-std=') for opt in action.analyzer_options):
        cmd.append(action.compiler_standard)

    return cmd


def get_triple_arch(action, source, config, env):
    """Returns the architecture part of the target triple for the given
    compilation command. """

    cmd = get_compile_command(action, config, source)
    cmd.insert(1, '-###')
    cmdstr = ' '.join(cmd)
    _, stdout, stderr = analyzer_base.SourceAnalyzer.run_proc(cmdstr,
                                                              env,
                                                              action.directory)
    last_line = (stdout + stderr).splitlines()[-1]
    res_cmd = shlex.split(last_line)
    arch = ""
    i = 0
    while i < len(res_cmd) and res_cmd[i] != "-triple":
        i += 1
    if i < (len(res_cmd) - 1):
        arch = res_cmd[i + 1].split("-")[0]
    return arch
