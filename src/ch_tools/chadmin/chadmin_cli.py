#!/usr/bin/env python3
import logging
import os
import warnings
from typing import Any, List

warnings.filterwarnings(action="ignore", message="Python 3.6 is no longer supported")

import cloup  # noqa: E402

from ch_tools.chadmin.cli.chs3_backup_group import chs3_backup_group  # noqa: E402
from ch_tools.chadmin.cli.config_command import config_command  # noqa: E402
from ch_tools.chadmin.cli.crash_log_group import crash_log_group  # noqa: E402
from ch_tools.chadmin.cli.data_store_group import data_store_group  # noqa: E402
from ch_tools.chadmin.cli.database_group import database_group  # noqa: E402
from ch_tools.chadmin.cli.diagnostics_command import diagnostics_command  # noqa: E402
from ch_tools.chadmin.cli.dictionary_group import dictionary_group  # noqa: E402
from ch_tools.chadmin.cli.disk_group import disks_group  # noqa: E402
from ch_tools.chadmin.cli.list_async_metrics_command import (  # noqa: E402
    list_async_metrics_command,
)
from ch_tools.chadmin.cli.list_events_command import list_events_command  # noqa: E402
from ch_tools.chadmin.cli.list_functions_command import (  # noqa: E402
    list_functions_command,
)
from ch_tools.chadmin.cli.list_macros_command import list_macros_command  # noqa: E402
from ch_tools.chadmin.cli.list_metrics_command import list_metrics_command  # noqa: E402
from ch_tools.chadmin.cli.list_settings_command import (  # noqa: E402
    list_settings_command,
)
from ch_tools.chadmin.cli.merge_group import merge_group  # noqa: E402
from ch_tools.chadmin.cli.mutation_group import mutation_group  # noqa: E402
from ch_tools.chadmin.cli.object_storage_group import object_storage_group  # noqa: E402
from ch_tools.chadmin.cli.part_group import part_group  # noqa: E402
from ch_tools.chadmin.cli.part_log_group import part_log_group  # noqa: E402
from ch_tools.chadmin.cli.partition_group import partition_group  # noqa: E402
from ch_tools.chadmin.cli.process_group import process_group  # noqa: E402
from ch_tools.chadmin.cli.query_log_group import query_log_group  # noqa: E402
from ch_tools.chadmin.cli.replicated_fetch_group import (  # noqa: E402
    replicated_fetch_group,
)
from ch_tools.chadmin.cli.replication_queue_group import (  # noqa: E402
    replication_queue_group,
)
from ch_tools.chadmin.cli.restore_replica_command import (  # noqa: E402
    restore_replica_command,
)
from ch_tools.chadmin.cli.stack_trace_command import stack_trace_command  # noqa: E402
from ch_tools.chadmin.cli.table_group import table_group  # noqa: E402
from ch_tools.chadmin.cli.table_replica_group import table_replica_group  # noqa: E402
from ch_tools.chadmin.cli.thread_log_group import thread_log_group  # noqa: E402
from ch_tools.chadmin.cli.wait_started_command import wait_started_command  # noqa: E402
from ch_tools.chadmin.cli.zookeeper_group import zookeeper_group  # noqa: E402
from ch_tools.common.cli.context_settings import CONTEXT_SETTINGS  # noqa: E402
from ch_tools.common.cli.parameters import TimeSpanParamType  # noqa: E402

LOG_FILE = "/var/log/chadmin/chadmin.log"


@cloup.group(
    "chadmin",
    help="ClickHouse administration tool.",
    context_settings=CONTEXT_SETTINGS,
)
@cloup.option(
    "-f",
    "--format",
    "format_",
    type=cloup.Choice(["json", "yaml", "table"]),
    help="Output format.",
)
@cloup.option(
    "--setting",
    "settings",
    multiple=True,
    type=(str, str),
    metavar="NAME VALUE",
    help="Name and value of ClickHouse setting to override. "
    "Can be specified multiple times to override several settings.",
)
@cloup.option("--timeout", type=TimeSpanParamType(), help="Timeout for SQL queries.")
@cloup.option("--port", type=int, help="Port to connect.")
@cloup.option("-d", "--debug", is_flag=True, help="Enable debug output.")
@cloup.pass_context
def cli(ctx, format_, settings, timeout, port, debug):
    """ClickHouse administration tool."""

    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    handlers: List[logging.Handler] = [logging.FileHandler(LOG_FILE)]
    if debug:
        handlers.append(logging.StreamHandler())

    logging.basicConfig(
        level=logging.DEBUG if debug else logging.INFO,
        format="%(asctime)s [%(levelname)s]:%(message)s",
        handlers=handlers,
    )

    timeout_seconds = timeout.total_seconds() if timeout else None
    settings = {item[0]: item[1] for item in settings}

    ch_cli_conf = dict(port=port, timeout=timeout_seconds, settings=settings)

    ctx.obj = dict(chcli_conf=ch_cli_conf, format=format_, debug=debug)


commands: List[Any] = [
    config_command,
    diagnostics_command,
    list_async_metrics_command,
    list_events_command,
    list_functions_command,
    list_macros_command,
    list_metrics_command,
    list_settings_command,
    restore_replica_command,
    stack_trace_command,
    wait_started_command,
]

groups: List[Any] = [
    chs3_backup_group,
    crash_log_group,
    data_store_group,
    database_group,
    dictionary_group,
    disks_group,
    merge_group,
    mutation_group,
    object_storage_group,
    part_group,
    part_log_group,
    partition_group,
    process_group,
    query_log_group,
    replicated_fetch_group,
    replication_queue_group,
    table_group,
    table_replica_group,
    thread_log_group,
    zookeeper_group,
]

for section_title, entries in {"Commands": commands, "Groups": groups}.items():
    section = cloup.Section(section_title)
    for entry in entries:
        cli.add_command(entry, section=section)


def main():
    cli.main()
