
from contextlib import contextmanager
import datetime
import os
import os.path as osp
import json

from rlpyt.util.logging import logger

PROJECT_PATH = osp.abspath(osp.join(osp.dirname(__file__), '../../..'))
LOG_DIR = PROJECT_PATH + "/data"


def make_log_dir(experiment_name, sub_name=None):
    yyyymmdd = datetime.datetime.today().strftime("%Y%m%d")
    log_dir = os.path.join(LOG_DIR, "local", yyyymmdd, experiment_name)
    if sub_name is not None:
        log_dir = os.path.join(log_dir, sub_name)
    return log_dir


@contextmanager
def logger_context(log_dir, name, run_ID, log_params=None, snapshot_mode="none"):
    logger.set_snapshot_mode(snapshot_mode)
    logger.set_log_tabular_only(False)
    abs_log_dir = os.path.abspath(log_dir)
    if LOG_DIR != os.path.commonpath([abs_log_dir, LOG_DIR]):
        print(f"logger_context received log_dir outside of {LOG_DIR}: "
            f"prepending by {LOG_DIR}/local/<yyyymmdd>/")
        abs_log_dir = make_log_dir(log_dir)
    exp_dir = os.path.join(abs_log_dir, "{}_{}".format(name, run_ID))
    tabular_log_file = os.path.join(exp_dir, "progress.csv")
    text_log_file = os.path.join(exp_dir, "debug.log")
    params_log_file = os.path.join(exp_dir, "params.json")

    logger.set_snapshot_dir(exp_dir)
    logger.add_text_output(text_log_file)
    logger.add_tabular_output(tabular_log_file)
    logger.push_prefix("{}_{} ".format(name, run_ID))

    if log_params is None:
        log_params = dict()
    log_params["name"] = name
    log_params["run_ID"] = run_ID
    with open(params_log_file, "w") as f:
        json.dump(log_params, f)

    yield

    logger.remove_tabular_output(tabular_log_file)
    logger.remove_text_output(text_log_file)
    logger.pop_prefix()
