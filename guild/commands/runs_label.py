# Copyright 2017 TensorHub, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import absolute_import
from __future__ import division

import click

from guild import click_util
from . import runs_support

def label_params(fn):
    click_util.append_params(fn, [
        click.Argument(("runs",), metavar="[RUN...]", nargs=-1),
        click.Argument(("label",), required=False),
    ])
    runs_support.run_scope_options(fn)
    runs_support.run_filters(fn)
    click_util.append_params(fn, [
        click.Option(
            ("--clear",),
            help="Clear the run's label.",
            is_flag=True),
        click.Option(
            ("-y", "--yes",),
            help="Do not prompt before modifying labels.",
            is_flag=True),
    ])
    return fn

@click.command()
@label_params

@click.pass_context
@click_util.use_args

def label(ctx, args):
    """Set run labels.

    This command is equivalent to ``guild label [OPTIONS]
    [RUN...] [LABEL]``
    """
    from . import runs_impl
    runs_impl.label(args, ctx)
